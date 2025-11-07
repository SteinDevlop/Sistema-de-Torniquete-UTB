import os
import logging
import time
from typing import Any, List, Dict, Optional
import psycopg2
from psycopg2 import sql, OperationalError, IntegrityError
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Configuración desde entorno (valores por defecto compatibles con docker-compose)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "db"))
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", 5432)))
POSTGRES_DB = os.getenv("POSTGRES_DB", os.getenv("DB", "postgres_db"))
POSTGRES_USER = os.getenv("POSTGRES_USER", os.getenv("DB_USER", os.getenv("USER", "postgres")))
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", os.getenv("PASSWORD", "")))

# Pool de conexiones global
_conn_pool: Optional[pool.SimpleConnectionPool] = None


def _ensure_pool(retries: int = 5, delay: float = 1.0):
    global _conn_pool
    if _conn_pool is not None:
        return
    minconn = 1
    maxconn = int(os.getenv("DB_POOL_MAX", 10))
    dsn = {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
    }
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            _conn_pool = pool.SimpleConnectionPool(minconn, maxconn, **dsn)
            logger.info("DB pool creado (host=%s db=%s)", POSTGRES_HOST, POSTGRES_DB)
            return
        except Exception as e:
            last_exc = e
            logger.warning("Intento %d/%d crear DB pool fallido: %s", attempt, retries, e)
            time.sleep(min(delay * (2 ** (attempt - 1)), 10.0))
    # Si no se pudo crear, propagar excepción para que la llamada lo maneje.
    raise OperationalError(f"Error inicializando pool de DB: {last_exc}")


def _get_conn():
    # Lazy init: crear pool sólo al pedir conexión; permite que app arranque sin DB disponible.
    _ensure_pool()
    assert _conn_pool is not None
    try:
        return _conn_pool.getconn()
    except Exception as e:
        raise OperationalError(f"Could not get connection from pool: {e}")


def _put_conn(conn):
    global _conn_pool
    if _conn_pool and conn:
        try:
            _conn_pool.putconn(conn)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass


class UniversalController:
    """Universal controller for CRUD operations using PostgreSQL via psycopg2 pool."""

    def __init__(self):
        # NO crear pool en import; se creará al primer uso de DB.
        logger.debug("UniversalController inicializado (pool creado al primer uso)")
        return

    def _get_table_name(self, obj: Any) -> str:
        """Retrieve the table name based on the object's class."""
        if hasattr(obj, "__entity_name__"):
            return obj.__entity_name__
        elif hasattr(obj.__class__, "__entity_name__"):
            return obj.__class__.__entity_name__
        else:
            raise ValueError("El objeto o su clase no tienen definido '__entity_name__'.")

    def _ensure_table_exists(self, obj: Any):
        """Ensure that the table exists in the database; create it if it doesn't."""
        table = self._get_table_name(obj)
        fields = obj.get_fields()  # Espera dict {column: type_definition}
        columns = []
        for k, v in fields.items():
            columns.append(f"{k} {v}")
        columns_sql = ", ".join(columns)
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({cols})").format(
            table=sql.Identifier(table),
            cols=sql.SQL(columns_sql),
        )
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()
        finally:
            _put_conn(conn)

    def add(self, obj: Any) -> Any:
        """Add a new object to the database."""
        self._ensure_table_exists(obj)
        table = self._get_table_name(obj)
        data = obj.to_dict()
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["%s"] * len(values))

        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES (" + placeholders + ")").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
        )
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute(query, values)
                except IntegrityError as e:
                    conn.rollback()
                    raise ValueError(f"Integrity error inserting into '{table}': {e}")
            conn.commit()
        finally:
            _put_conn(conn)
        return obj

    def read_all(self, obj: Any) -> List[Dict]:
        """Retrieve all objects from a table."""
        self._ensure_table_exists(obj)
        table = self._get_table_name(obj)
        query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table))
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        finally:
            _put_conn(conn)

    def get_by_id(self, model, id):
        """Retrieve a single record by ID and return an instance of model (if possible)."""
        self._ensure_table_exists(model)
        table = model.__entity_name__
        fields = model.get_fields()
        primary_key = list(fields.keys())[0]
        query = sql.SQL("SELECT * FROM {table} WHERE {pk} = %s").format(
            table=sql.Identifier(table),
            pk=sql.Identifier(primary_key),
        )
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (id,))
                row = cur.fetchone()
                if not row:
                    return None
                data = dict(row)
                try:
                    return model(**data)
                except Exception:
                    return data
        finally:
            _put_conn(conn)

    def update(self, obj: Any) -> Any:
        """Update an existing object."""
        self._ensure_table_exists(obj)
        table = self._get_table_name(obj)
        data = obj.to_dict()
        id_field = list(data.keys())[0]  # primary key field name
        assignments = [f"{k} = %s" for k in data if k != id_field]
        values = [v for k, v in data.items() if k != id_field]
        values.append(data[id_field])

        set_clause = ", ".join(assignments)
        query = sql.SQL("UPDATE {table} SET " + set_clause + " WHERE {id_field} = %s").format(
            table=sql.Identifier(table),
            id_field=sql.Identifier(id_field),
        )
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
                if cur.rowcount == 0:
                    conn.rollback()
                    raise ValueError(f"No se encontró un registro con {id_field} = {data[id_field]} en la tabla '{table}'.")
            conn.commit()
        finally:
            _put_conn(conn)
        return obj

    def delete(self, obj: Any) -> bool:
        """Delete an object by its ID."""
        self._ensure_table_exists(obj)
        table = self._get_table_name(obj)
        data = obj.to_dict()
        id_field = list(data.keys())[0]

        query = sql.SQL("DELETE FROM {table} WHERE {id_field} = %s").format(
            table=sql.Identifier(table),
            id_field=sql.Identifier(id_field),
        )
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (data[id_field],))
                if cur.rowcount == 0:
                    conn.rollback()
                    raise ValueError(f"No se encontró un registro con {id_field} = {data[id_field]} en la tabla '{table}'.")
            conn.commit()
        finally:
            _put_conn(conn)
        return True

    def clear_tables(self):
        """Delete all data from all user tables in the database (no drop)."""
        # Excluir tablas del sistema
        query_tables = """
            SELECT tablename FROM pg_catalog.pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query_tables)
                tables = [row[0] for row in cur.fetchall()]
                for t in tables:
                    cur.execute(sql.SQL("TRUNCATE TABLE {table} RESTART IDENTITY CASCADE").format(table=sql.Identifier(t)))
            conn.commit()
        finally:
            _put_conn(conn)

    def get_by_field(self, table: str, field: str, value: Any) -> Optional[Dict]:
        """Retrieve a single record by a specific field."""
        query = sql.SQL("SELECT * FROM {table} WHERE {field} = %s LIMIT 1").format(
            table=sql.Identifier(table),
            field=sql.Identifier(field),
        )
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (value,))
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            _put_conn(conn)

    def get_by_field_like(self, table: str, field: str, value_prefix: str) -> List[Dict]:
        """Retrieve records where a specific field starts with a given prefix."""
        like_pattern = f"{value_prefix}%"
        query = sql.SQL("SELECT * FROM {table} WHERE {field} LIKE %s").format(
            table=sql.Identifier(table),
            field=sql.Identifier(field),
        )
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (like_pattern,))
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        finally:
            _put_conn(conn)

    def close(self):
        """Close the connection pool."""
        global _conn_pool
        if _conn_pool:
            try:
                _conn_pool.closeall()
            finally:
                _conn_pool = None