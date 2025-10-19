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
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        logger.debug("VerificadorCamara.verificar llamado (sin implementar). data keys=%s", list(data.keys()))
        # Implementación pendiente
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