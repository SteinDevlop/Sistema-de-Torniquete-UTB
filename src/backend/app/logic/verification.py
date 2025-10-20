from backend.app.models.access import MedioAcceso, AccesoRequest
from backend.app.models.verificador_acceso import VerificadorAcceso
from backend.app.logic.universal_controller_instance import universal_controller
import numpy as np
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def _comparar_templates(self, t1: bytes, t2: bytes) -> float:
    """
    Calcula similitud (0–1) entre dos plantillas.
    - Si los bytes son idénticos → similitud = 1.0 (modo test)
    - Si no, usa similitud coseno (modo real)
    """
    try:
        logger.debug("Entrando en _comparar_templates: len(t1)=%d, len(t2)=%d", len(t1), len(t2))
    except Exception:
        logger.debug("Entrando en _comparar_templates: no se pudo medir longitudes")

    # Comparación exacta rápida (útil en tests)
    if t1 == t2:
        logger.info("Comparación exacta: plantillas idénticas -> score=1.0")
        return 1.0

    n = min(len(t1), len(t2))
    if n == 0:
        logger.warning("Comparación de templates: alguno tiene longitud 0, devolviendo 0.0")
        return 0.0

    try:
        a = np.frombuffer(t1[:n], dtype=np.uint8).astype(np.float32)
        b = np.frombuffer(t2[:n], dtype=np.uint8).astype(np.float32)
        num = np.dot(a, b)
        den = np.linalg.norm(a) * np.linalg.norm(b)
        score = float(num / den) if den != 0 else 0.0
        logger.debug("Score calculado (coseno): num=%f den=%f score=%f", num, den, score)
        return score
    except Exception as e:
        logger.exception("Error calculando similitud entre templates: %s", e)
        return 0.0

def _comparar_con_candidatos(
        self, template_capturada: bytes, candidatos: list[dict]
    ) -> tuple[bool, int | None]:
    """
    Compara la plantilla capturada con una lista de candidatos filtrados.
    Returns: (True, id_usuario) si hay coincidencia, (False, None) si no.
    """
    logger.info("Iniciando comparación con candidatos: %d candidatos recibidos", len(candidatos) if candidatos else 0)

    if not candidatos:
        logger.info("No se encontraron candidatos con hash similar.")
        return False, None

    mejor_score = 0.0
    mejor_usuario = None

    for idx, c in enumerate(candidatos):
        usuario_id = c.get("id_usuario")
        logger.debug("Comparando contra candidato %d: id_usuario=%s", idx, str(usuario_id))
        stored_b64 = c.get("huella_template") or c.get("template_huella") or c.get("template")
        if not stored_b64:
            logger.debug("Candidato %s no tiene plantilla almacenada, saltando.", str(usuario_id))
            continue

        try:
            logger.info(stored_b64)
            stored_template = base64.b64decode(stored_b64)
            logger.debug("Candidato %s: plantilla decodificada len=%d", str(usuario_id), len(stored_template))
        except Exception as e:
            logger.warning("Error decodificando plantilla del candidato %s: %s", str(usuario_id), e)
            continue

        try:
            score = _comparar_templates(self, template_capturada, stored_template)
            logger.debug("Score con candidato %s = %f", str(usuario_id), score)
            if score > mejor_score:
                mejor_score = score
                mejor_usuario = usuario_id
        except Exception as e:
            logger.warning("Error comparando templates con candidato %s: %s", str(usuario_id), e)

    UMBRAL = 0.85
    logger.info("Mejor score encontrado = %f (umbral=%f) -> usuario=%s", mejor_score, UMBRAL, str(mejor_usuario))

    if mejor_score >= UMBRAL:
        logger.info("Coincidencia aceptada con usuario %s (score=%f)", str(mejor_usuario), mejor_score)
        return True, mejor_usuario

    logger.info("No hubo coincidencia válida. Mejor score=%f", mejor_score)
    return False, None

class VerificadorRFID:
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Verifica si el RFID proporcionado pertenece a un usuario registrado en la tabla Biometria.
        Args:
            data (dict): Diccionario que contiene el valor del RFID bajo la clave 'rfid_tag'.
        Returns:
            tuple[bool, int | None]: (True, id_usuario) si se encuentra el RFID;
            (False, None) en caso contrario.
        """
        rfid_tag = data.get("rfid_tag")
        logger.debug("VerificadorRFID.verificar llamado con rfid_tag=%s", str(rfid_tag))
        if not rfid_tag:
            logger.info("RFID no proporcionado en la petición.")
            return False, None
        try:
            biometria = universal_controller.get_by_field("Biometria", "rfid_tag", rfid_tag)
            if biometria:
                logger.info("RFID encontrado. id_usuario=%s", str(biometria.get("id_usuario")))
                return True, biometria["id_usuario"]
            logger.info("RFID no encontrado en la base de datos.")
            return False, None
        except Exception as e:
            logger.exception("Error buscando RFID en la DB: %s", e)
            return False, None

class VerificadorHuella:
    """
    Verifica una huella comparando con un subconjunto de candidatos
    filtrados mediante un hash parcial (huella_hash).
    """

    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Args:
            data (dict): {"vector": "<base64_template>"}

        Returns:
            (True, id_usuario) si hay coincidencia, (False, None) si no.
        """
        vector_b64 = data.get("vector") or data.get("template") or data.get("template_huella")
        logger.debug("VerificadorHuella.verificar recibido. keys=%s", list(data.keys()))
        if not vector_b64:
            logger.info("No se proporcionó vector de huella en la petición.")
            return False, None

        try:
            template_capturada = base64.b64decode(vector_b64)
            logger.info("Template capturada decodificada. len=%d", len(template_capturada))
        except Exception as e:
            logger.warning("Error decodificando vector de huella: %s", e)
            return False, None

        try:
            hash_prefix = hashlib.sha256(template_capturada).hexdigest()[:8]
            logger.debug("Hash prefix calculado: %s", hash_prefix)
        except Exception as e:
            logger.exception("Error calculando hash de la plantilla capturada: %s", e)
            return False, None
        
        logger.info("Buscando candidatos con huella_hash similar: %s", hash_prefix)

        try:
            candidatos = universal_controller.get_by_field_like(
                "Biometria", "huella_hash", hash_prefix
            )
            logger.info("Candidatos recuperados: %d", len(candidatos) if candidatos else 0)
            logger.debug("Candidatos sample: %s", str(candidatos[:3]) if candidatos else "[]")
        except Exception as e:
            logger.exception("Error consultando candidatos en la DB: %s", e)
            return False, None

        if not candidatos:
            logger.info("No se encontraron candidatos con hash similar.")
            return False, None

        resultado, user_id = _comparar_con_candidatos(self, template_capturada, candidatos)
        logger.info("Resultado comparación final: matched=%s user_id=%s", str(resultado), str(user_id))
        return resultado, user_id

class VerificadorCamara(VerificadorAcceso):
    """
    Verifica un embedding facial (vector de 128 decimales) comparando con candidatos
    filtrados mediante un hash parcial (facial_hash).
    Similar a VerificadorHuella pero para reconocimiento facial.
    """

    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Args:
            data (dict): {"vector": "[0.123, -0.456, ...]"} - String JSON con 128 decimales
                        o Base64 del array numpy serializado

        Returns:
            (True, id_usuario) si hay coincidencia, (False, None) si no.
        """
        vector_str = data.get("vector") or data.get("embedding") or data.get("vector_facial")
        logger.debug("VerificadorCamara.verificar recibido. keys=%s", list(data.keys()))
        
        if not vector_str:
            logger.info("No se proporcionó vector facial en la petición.")
            return False, None

        try:
            # Intentar decodificar como Base64 primero (formato numpy serializado)
            try:
                vector_bytes = base64.b64decode(vector_str)
                embedding_capturado = np.frombuffer(vector_bytes, dtype=np.float32)
                logger.info("Embedding decodificado desde Base64. Shape: %s", embedding_capturado.shape)
            except Exception:
                # Si falla, asumir que es un string JSON "[0.123, -0.456, ...]"
                import json
                embedding_list = json.loads(vector_str)
                embedding_capturado = np.array(embedding_list, dtype=np.float32)
                logger.info("Embedding parseado desde JSON. Shape: %s", embedding_capturado.shape)
            
            # Validar que sea un vector de 128 dimensiones
            if embedding_capturado.shape[0] != 128:
                logger.warning("El embedding facial debe tener 128 dimensiones, recibido: %d", embedding_capturado.shape[0])
                return False, None
                
        except Exception as e:
            logger.warning("Error procesando vector facial: %s", e)
            return False, None

        try:
            # Serializar embedding para calcular hash (normalizar primero)
            embedding_norm = embedding_capturado / (np.linalg.norm(embedding_capturado) + 1e-8)
            embedding_bytes = embedding_norm.tobytes()
            hash_prefix = hashlib.sha256(embedding_bytes).hexdigest()[:8]
            logger.debug("Hash prefix calculado para embedding facial: %s", hash_prefix)
        except Exception as e:
            logger.exception("Error calculando hash del embedding facial: %s", e)
            return False, None
        
        logger.info("Buscando candidatos con facial_hash similar: %s", hash_prefix)

        try:
            candidatos = universal_controller.get_by_field_like(
                "Biometria", "facial_hash", hash_prefix
            )
            logger.info("Candidatos faciales recuperados: %d", len(candidatos) if candidatos else 0)
            logger.debug("Candidatos sample: %s", str(candidatos[:3]) if candidatos else "[]")
        except Exception as e:
            logger.exception("Error consultando candidatos faciales en la DB: %s", e)
            return False, None

        if not candidatos:
            logger.info("No se encontraron candidatos con facial_hash similar.")
            return False, None

        # Comparar embeddings usando similitud coseno
        resultado, user_id = self._comparar_embeddings_faciales(embedding_capturado, candidatos)
        logger.info("Resultado comparación facial final: matched=%s user_id=%s", str(resultado), str(user_id))
        return resultado, user_id

    def _comparar_embeddings_faciales(
        self, embedding_capturado: np.ndarray, candidatos: list[dict]
    ) -> tuple[bool, int | None]:
        """
        Compara el embedding facial capturado con los candidatos usando similitud coseno.
        
        Args:
            embedding_capturado: Vector numpy de 128 dimensiones
            candidatos: Lista de registros de Biometria con vector_facial
            
        Returns:
            (True, id_usuario) si hay coincidencia >= umbral, (False, None) si no.
        """
        logger.info("Iniciando comparación de embeddings faciales: %d candidatos", len(candidatos))
        
        mejor_score = 0.0
        mejor_usuario = None
        
        # Normalizar embedding capturado
        embedding_capturado_norm = embedding_capturado / (np.linalg.norm(embedding_capturado) + 1e-8)

        for idx, c in enumerate(candidatos):
            usuario_id = c.get("id_usuario")
            logger.debug("Comparando contra candidato facial %d: id_usuario=%s", idx, str(usuario_id))
            
            stored_vector = c.get("vector_facial")
            if not stored_vector:
                logger.debug("Candidato %s no tiene vector_facial almacenado, saltando.", str(usuario_id))
                continue

            try:
                # Decodificar vector almacenado (puede ser Base64 o JSON)
                try:
                    stored_bytes = base64.b64decode(stored_vector)
                    stored_embedding = np.frombuffer(stored_bytes, dtype=np.float32)
                except Exception:
                    import json
                    stored_list = json.loads(stored_vector)
                    stored_embedding = np.array(stored_list, dtype=np.float32)
                
                logger.debug("Candidato %s: embedding decodificado shape=%s", str(usuario_id), stored_embedding.shape)
                
                if stored_embedding.shape[0] != 128:
                    logger.warning("Candidato %s tiene embedding con dimensión incorrecta: %d", 
                                 str(usuario_id), stored_embedding.shape[0])
                    continue
                    
            except Exception as e:
                logger.warning("Error decodificando embedding del candidato %s: %s", str(usuario_id), e)
                continue

            try:
                # Normalizar embedding almacenado
                stored_embedding_norm = stored_embedding / (np.linalg.norm(stored_embedding) + 1e-8)
                
                # Calcular similitud coseno
                score = float(np.dot(embedding_capturado_norm, stored_embedding_norm))
                
                logger.debug("Score facial con candidato %s = %f", str(usuario_id), score)
                
                if score > mejor_score:
                    mejor_score = score
                    mejor_usuario = usuario_id
                    
            except Exception as e:
                logger.warning("Error comparando embeddings con candidato %s: %s", str(usuario_id), e)

        # Umbral para reconocimiento facial (ajustable según precisión deseada)
        UMBRAL = 0.70  # Para embeddings normalizados, 0.70 es un buen umbral
        logger.info("Mejor score facial encontrado = %f (umbral=%f) -> usuario=%s", 
                   mejor_score, UMBRAL, str(mejor_usuario))

        if mejor_score >= UMBRAL:
            logger.info("Coincidencia facial aceptada con usuario %s (score=%f)", str(mejor_usuario), mejor_score)
            return True, mejor_usuario

        logger.info("No hubo coincidencia facial válida. Mejor score=%f", mejor_score)
        return False, None

class VerificadorFactory:
    @staticmethod
    def obtener(medio: MedioAcceso) -> VerificadorAcceso:
        logger.debug("VerificadorFactory.obtener: medio=%s", str(medio))
        if medio == MedioAcceso.rfid:
            return VerificadorRFID()
        elif medio == MedioAcceso.huella:
            return VerificadorHuella()
        elif medio == MedioAcceso.camara:
            return VerificadorCamara()
        raise ValueError("Medio no soportado")