from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from pathlib import Path
from backend.app.api.routes.access_service import app as access_router
from backend.app.logic.universal_controller_instance import UniversalController
from backend.app.core.conf import headers
from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.models.biometria import BiometriaCreate
import logging
import base64
import numpy as np
import pytest
import hashlib
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# ===============================
# CONFIGURACIÓN DE PRUEBAS
# ===============================

# Crear instancia del controlador de pruebas
test_controller = UniversalController()

# Sobrescribir el controlador si se usa dentro del servicio
# (solo necesario si AccessService lo usa internamente)
# from backend.app.logic.access_logic import AccessService
# AccessService.controller = test_controller

# App de prueba
app_for_test = FastAPI()
app_for_test.include_router(access_router)

client = TestClient(app_for_test)

# Limpiar base de datos antes y después de cada test
def setup_function():
    test_controller.clear_tables()

def teardown_function():
    test_controller.clear_tables()


app_for_test = FastAPI()
app_for_test.include_router(access_router)
# ===============================
# PRUEBAS: ENDPOINTS DE ACCESO
# ===============================
def generar_template_y_hash(contenido: bytes):
    template_b64 = base64.b64encode(contenido).decode()
    hash_prefix = hashlib.sha256(contenido).hexdigest()[:8]
    return template_b64, hash_prefix
client = TestClient(app_for_test)
def test_acceso_rfid_exitoso():
    test_controller.add(BiometriaCreate(id_biometria=1, id_usuario=1, rfid_tag="VALID123"))
    response = client.post("/acceso/rfid", params={"rfid_tag": "VALID123"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Respuesta RFID exitosa: {data}")
    assert data["status"] is True

def test_acceso_rfid_fallido():
    test_controller.add(BiometriaCreate(id_biometria=1, id_usuario=1, rfid_tag="VALID123"))
    response = client.post("/acceso/rfid", params={"rfid_tag": "INVALID"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is False

# Ruta del template base
TEMPLATE_PATH = Path("backend/app/tests/data/template_b64.txt")
def cargar_template_base() -> str:
    """Lee el template base64 desde el archivo."""
    content = TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    return "".join(content.split())

def generar_hash_parcial(template_b64: str) -> str:
    data = base64.b64decode(template_b64)
    return hashlib.sha256(data).hexdigest()[:8]

def modificar_template(template_b64: str, flips: int = 50, seed: int = 42) -> str:
    """
    Genera un template con ligeras modificaciones byte a byte
    para simular una huella similar pero no idéntica.
    """
    raw = bytearray(base64.b64decode(template_b64))
    rng = np.random.default_rng(seed)
    n = len(raw)
    if n == 0:
        return template_b64
    indices = rng.choice(n, size=min(flips, n), replace=False)
    for i in indices:
        raw[i] = (raw[i] + rng.integers(1, 255)) % 256
    return base64.b64encode(bytes(raw)).decode()

def generar_template_diferente(size: int = 512, seed: int = 999) -> str:
    """Genera un template completamente distinto."""
    rng = np.random.default_rng(seed)
    data = rng.integers(0, 256, size, dtype=np.uint8).tobytes()
    return base64.b64encode(data).decode()

@pytest.fixture(autouse=True)
def limpiar_db():
    """Limpia la base antes y después de cada test."""
    test_controller.clear_tables()
    yield
    test_controller.clear_tables()

# ======================================================
# TEST 1: CASO DE ÉXITO TOTAL
# ======================================================
def test_huella_exito_total():
    """
    Caso de éxito total: el template recibido es idéntico al guardado.
    """
    tpl = cargar_template_base()
    huella_hash = generar_hash_parcial(tpl)

    test_controller.add(BiometriaCreate(
        id_biometria=1,
        id_usuario=1,
        template_huella=tpl,
        huella_hash=huella_hash
    ))

    resp = client.post(
        "/acceso/huella",
        json={  # 🔹 ahora se envía por JSON
            "dispositivo_id": "TEST_OK",
            "vector": tpl,
            "fecha": "2025-10-20T10:00:00"
        },
        headers=headers
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    logger.info(f"✅ Caso éxito total: {data}")
    assert data["status"] is True
    assert data.get("usuario_id") == 1

# ======================================================
# TEST 2: CASO DE SIMILITUD PARCIAL
# ======================================================
def test_huella_similitud_parcial():
    """
    Caso de similitud parcial: el template tiene ligeras diferencias.
    """
    tpl = cargar_template_base()
    tpl_parcial = modificar_template(tpl)
    huella_hash = generar_hash_parcial(tpl)

    test_controller.add(BiometriaCreate(
        id_biometria=2,
        id_usuario=2,
        template_huella=tpl,
        huella_hash=huella_hash
    ))

    resp = client.post(
        "/acceso/huella",
        json={  # 🔹 por JSON, no en query
            "dispositivo_id": "TEST_PARTIAL",
            "vector": tpl_parcial,
            "fecha": "2025-10-20T10:05:00"
        },
        headers=headers
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    logger.info(f"⚠️ Caso similitud parcial: {data}")
    # Si el umbral del verificador es estricto (≥0.95), debería fallar
    assert data["status"] is False

# ======================================================
# TEST 3: CASO DE FRACASO TOTAL
# ======================================================
def test_huella_fracaso_total():
    """
    Caso de fracaso total: el template es completamente distinto.
    """
    tpl = cargar_template_base()
    tpl_fail = generar_template_diferente()
    huella_hash = generar_hash_parcial(tpl)

    test_controller.add(BiometriaCreate(
        id_biometria=3,
        id_usuario=3,
        template_huella=tpl,
        huella_hash=huella_hash
    ))

    resp = client.post(
        "/acceso/huella",
        json={  # 🔹 por JSON, no params
            "dispositivo_id": "TEST_FAIL",
            "vector": tpl_fail,
            "fecha": "2025-10-20T10:10:00"
        },
        headers=headers
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    logger.info(f"❌ Caso fracaso total: {data}")
    assert data["status"] is False
    assert data.get("usuario_id") is None