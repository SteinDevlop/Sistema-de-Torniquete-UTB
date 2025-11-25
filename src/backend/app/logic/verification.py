from backend.app.models.access import MedioAcceso, AccesoRequest
from backend.app.models.verificador_acceso import VerificadorAcceso
from backend.app.logic.universal_controller_instance import universal_controller
from backend.app.logic.face_recognition import get_face_recognition_system
import numpy as np
import base64
import hashlib
import logging
from backend.app.models.biometria import BiometriaOut
import cv2
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    Verificador para fingerprints provenientes del sensor AS608.
    Los templates llegan en formato binario (base64).
    """

    UMBRAL_MATCH = 0.90  # 90%

    def _decode_template(self, b64_data: str) -> bytes | None:
        try:
            padded = b64_data + '=' * (-len(b64_data) % 4)
            raw = base64.b64decode(padded)
            logger.debug(f"[DECODE] Base64 length={len(b64_data)}, padded={len(padded)}, bytes={len(raw)}")
            return raw
        except Exception as e:
            logger.error(f"[DECODE ERROR] No se pudo decodificar base64: {e}")
            return None

    def _similaridad_templates(self, t1: bytes, t2: bytes) -> float:
        l1, l2 = len(t1), len(t2)
        logger.debug(f"[SIMILITUD] len(t1)={l1}, len(t2)={l2}")

        if l1 == 0 or l2 == 0:
            return 0.0

        min_len = min(l1, l2)
        iguales = sum(b1 == b2 for b1, b2 in zip(t1[:min_len], t2[:min_len]))

        logger.debug(f"[SIMILITUD] bytes_iguales={iguales}, comparados={min_len}")
        return iguales / min_len

    def verificar(self, data: dict) -> tuple[bool, int | None]:
        logger.info("INICIANDO VERIFICACION DE HUELLA ===")

        tpl_in = data.get("vector") or data.get("template")
        logger.debug(f"[INPUT] Template recibido: {tpl_in[:50]}... (len={len(tpl_in) if tpl_in else 0})")

        if not tpl_in:
            logger.warning("[INPUT] No se recibió template")
            return False, None

        tpl_sensor = self._decode_template(tpl_in)
        if tpl_sensor is None:
            logger.error("[INPUT] No se pudo decodificar el template recibido")
            return False, None

        logger.debug(f"[INPUT] Bytes sensor: {tpl_sensor[:20]}... total={len(tpl_sensor)}")

        registros_db = universal_controller.read_all(BiometriaOut())
        logger.debug(f"[DB] Se cargaron {len(registros_db)} registros biométricos")

        mejor_score = 0
        mejor_id = None

        for registro in registros_db:
            tpl_b64_db = registro.get("template_huella")
            uid = registro.get("id_usuario")

            if not tpl_b64_db:
                logger.debug(f"[DB] Usuario {uid} sin template de huella, se omite")
                continue

            logger.debug(f"[DB] Comparando contra usuario {uid}")
            tpl_db = self._decode_template(tpl_b64_db)

            if tpl_db is None:
                logger.error(f"[DB] Error decodificando template del usuario {uid}")
                continue

            logger.debug(f"[DB] Bytes BD: {tpl_db[:20]}... total={len(tpl_db)}")

            # CASO 1 — COINCIDENCIA EXACTA
            if tpl_db == tpl_sensor:
                logger.info(f"🎯 MATCH PERFECTO — Usuario {uid}")
                return True, uid

            # CASO 2 — COMPARACIÓN DE SIMILITUD
            score = self._similaridad_templates(tpl_sensor, tpl_db)
            logger.debug(f"[SCORE] Usuario {uid}: score={score:.4f}")

            if score > mejor_score:
                mejor_score = score
                mejor_id = uid

        logger.info(f"[RESULTADO] Mejor score={mejor_score:.4f} (umbral={self.UMBRAL_MATCH})")

        if mejor_score >= self.UMBRAL_MATCH:
            logger.info(f"MATCH POR SIMILITUD — Usuario {mejor_id}")
            return True, mejor_id

        logger.warning("Ningún template alcanzó el umbral")
        return False, None


class VerificadorCamara(VerificadorAcceso):
    """
    Verifica un embedding facial (vector de 128 decimales) comparando con candidatos
    filtrados mediante un hash parcial (facial_hash).
    Similar a VerificadorHuella pero para reconocimiento facial.
    """

    def __init__(self):
        """Inicializar con dict para almacenar detalles de comparación"""
        self.detalles_comparacion = {
            "candidatos_evaluados": 0,
            "mejor_score": 0.0,
            "mejor_usuario": None,
            "umbral": 0.70,
            "todos_scores": []
        }
    
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Args:
            data (dict): {
                "vector": "[0.123, -0.456, ...]" (base64 o JSON) - opcional si se envía imagen
                "imagen_facial": "<base64_image>" - imagen para extraer embedding real
            }

        Returns:
            (True, id_usuario) si hay coincidencia, (False, None) si no.
        """
        # Resetear detalles de comparación
        self.detalles_comparacion = {
            "candidatos_evaluados": 0,
            "mejor_score": 0.0,
            "mejor_usuario": None,
            "umbral": 0.70,
            "todos_scores": []
        }
        
        vector_str = data.get("vector") or data.get("embedding") or data.get("vector_facial")
        imagen_facial = data.get("imagen_facial")
        
        logger.info("=" * 80)
        logger.info("🔍 INICIANDO VERIFICACIÓN FACIAL")
        logger.info(f"   Tiene vector_str: {vector_str is not None}")
        logger.info(f"   Tiene imagen_facial: {imagen_facial is not None}")
        logger.debug("VerificadorCamara.verificar recibido. keys=%s", list(data.keys()))
        
        # 🔹 Si se proporciona imagen, extraer embedding real con DeepFace
        if imagen_facial and not vector_str:
            logger.info("Extrayendo embedding facial desde imagen con DeepFace para verificación...")
            face_system = get_face_recognition_system()
            embedding_capturado = face_system.extraer_embedding_desde_base64(imagen_facial)
            
            if embedding_capturado is None:
                logger.warning("No se pudo detectar rostro en la imagen de verificación")
                return False, None
            
            logger.info(f"Embedding extraído desde imagen. Shape: {embedding_capturado.shape}")
        
        # 🔹 Si se proporciona vector directamente (modo compatibilidad)
        elif vector_str:
            if not vector_str:
                logger.info("No se proporcionó vector facial ni imagen en la petición.")
                return False, None

            try:
                # Intentar decodificar como Base64 primero (formato numpy serializado)
                try:
                    padded_vector = vector_str + '=' * (-len(vector_str) % 4)
                    vector_bytes = base64.b64decode(padded_vector)
                    embedding_capturado = np.frombuffer(vector_bytes, dtype=np.float32)
                    logger.info("Embedding decodificado desde Base64. Shape: %s", embedding_capturado.shape)
                except Exception:
                    # Si falla, asumir que es un string JSON "[0.123, -0.456, ...]"
                    import json
                    embedding_list = json.loads(vector_str)
                    embedding_capturado = np.array(embedding_list, dtype=np.float32)
                    logger.info("Embedding parseado desde JSON. Shape: %s", embedding_capturado.shape)
                
            except Exception as e:
                logger.warning("Error procesando vector facial: %s", e)
                return False, None
        else:
            logger.warning("No se proporcionó ni vector ni imagen_facial")
            return False, None

        # Validar dimensiones del embedding
        if embedding_capturado.shape[0] not in [128, 512]:  # Facenet512 genera 512, Facenet genera 128
            logger.warning("El embedding facial tiene dimensión incorrecta: %d (esperado 128 o 512)", embedding_capturado.shape[0])
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
            logger.info("Candidatos faciales recuperados por hash: %d", len(candidatos) if candidatos else 0)
            
            # Si no hay candidatos por hash, buscar TODOS los registros con vector_facial
            if not candidatos or len(candidatos) == 0:
                logger.warning("⚠️  No se encontraron candidatos por facial_hash. Buscando TODOS los usuarios con vector_facial...")
                from backend.app.models.biometria import BiometriaOut
                todos_registros = universal_controller.read_all(BiometriaOut())
                
                logger.info(f"   Total de registros en DB: {len(todos_registros)}")
                
                # Filtrar solo los que tienen vector_facial
                candidatos = [r for r in todos_registros if r.get("vector_facial")]
                logger.info(f"✅ Candidatos faciales encontrados (sin filtro hash): {len(candidatos)}")
                
                # Mostrar detalles de cada candidato
                for i, c in enumerate(candidatos, 1):
                    logger.info(f"   Candidato {i}: Usuario {c.get('id_usuario')}, Hash: {c.get('facial_hash')}, Tiene vector: {c.get('vector_facial') is not None}")
            else:
                logger.info(f"✅ Encontrados {len(candidatos)} candidatos por facial_hash")
            
            logger.debug("Candidatos sample: %s", str(candidatos[:3]) if candidatos else "[]")
        except Exception as e:
            logger.exception("Error consultando candidatos faciales en la DB: %s", e)
            return False, None

        if not candidatos:
            logger.info("No se encontraron candidatos con vector_facial en la base de datos.")
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
            embedding_capturado: Vector numpy de 128 o 512 dimensiones
            candidatos: Lista de registros de Biometria con vector_facial
            
        Returns:
            (True, id_usuario) si hay coincidencia >= umbral, (False, None) si no.
        """
        logger.info("Iniciando comparación de embeddings faciales: %d candidatos", len(candidatos))
        
        mejor_score = 0.0
        mejor_usuario = None
        todos_scores = []
        
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
                    padded_stored = stored_vector + '=' * (-len(stored_vector) % 4)
                    stored_bytes = base64.b64decode(padded_stored)
                    stored_embedding = np.frombuffer(stored_bytes, dtype=np.float32)
                except Exception:
                    import json
                    stored_list = json.loads(stored_vector)
                    stored_embedding = np.array(stored_list, dtype=np.float32)
                
                logger.debug("Candidato %s: embedding decodificado shape=%s", str(usuario_id), stored_embedding.shape)
                
                # Validar dimensiones (128, 512, o 1024 dependiendo del modelo)
                if stored_embedding.shape[0] not in [128, 512, 1024, 2048]:
                    logger.warning("Candidato %s tiene embedding con dimensión incorrecta: %d", 
                                 str(usuario_id), stored_embedding.shape[0])
                    continue
                
                # Si las dimensiones no coinciden exactamente, intentar ajustar
                if stored_embedding.shape[0] != embedding_capturado.shape[0]:
                    # Si el almacenado es el doble, tomar solo la primera mitad
                    if stored_embedding.shape[0] == embedding_capturado.shape[0] * 2:
                        logger.warning("Candidato %s tiene embedding duplicado (dim=%d). Tomando primera mitad...",
                                     str(usuario_id), stored_embedding.shape[0])
                        logger.info(f"   ANTES del slice: shape={stored_embedding.shape}, primeros 3 valores={stored_embedding[:3]}")
                        stored_embedding = stored_embedding[:embedding_capturado.shape[0]].copy()
                        logger.info(f"   DESPUÉS del slice: shape={stored_embedding.shape}, primeros 3 valores={stored_embedding[:3]}")
                        logger.info(f"   Embedding capturado: shape={embedding_capturado.shape}, primeros 3 valores={embedding_capturado[:3]}")
                    else:
                        logger.warning("Candidato %s tiene diferente dimensión de embedding: %d vs %d (no compatible)",
                                     str(usuario_id), stored_embedding.shape[0], embedding_capturado.shape[0])
                        continue
                    
            except Exception as e:
                logger.warning("Error decodificando embedding del candidato %s: %s", str(usuario_id), e)
                continue

            try:
                # Normalizar embedding almacenado
                stored_embedding_norm = stored_embedding / (np.linalg.norm(stored_embedding) + 1e-8)
                
                # Calcular similitud coseno (score de 0 a 1)
                score = float(np.dot(embedding_capturado_norm, stored_embedding_norm))
                
                # Convertir a distancia para compatibilidad (0 = idéntico, 1 = totalmente diferente)
                distancia = 1 - score
                
                logger.info(f"👤 Usuario {usuario_id}: Score={score:.4f} (Distancia={distancia:.4f})")
                
                # Guardar para reporte detallado
                todos_scores.append({
                    "usuario_id": usuario_id,
                    "score": round(float(score), 4),
                    "distancia": round(float(distancia), 4),
                    "porcentaje_similitud": round(float(score * 100), 2)
                })
                
                if score > mejor_score:
                    mejor_score = score
                    mejor_usuario = usuario_id
                    
            except Exception as e:
                logger.warning("Error comparando embeddings con candidato %s: %s", str(usuario_id), e)

        # Ordenar scores de mayor a menor
        todos_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Umbral para reconocimiento facial
        UMBRAL = 0.70  # Similarity threshold (70%)
        UMBRAL_DISTANCIA = 1 - UMBRAL  # Distance threshold (0.30)
        
        # Guardar detalles de comparación
        self.detalles_comparacion = {
            "candidatos_evaluados": len(todos_scores),
            "mejor_score": round(float(mejor_score), 4),
            "mejor_distancia": round(float(1 - mejor_score), 4),
            "mejor_usuario": mejor_usuario,
            "umbral_score": UMBRAL,
            "umbral_distancia": UMBRAL_DISTANCIA,
            "todos_scores": todos_scores[:10]  # Top 10 mejores coincidencias
        }
        
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DE COMPARACIÓN FACIAL:")
        logger.info(f"   Candidatos evaluados: {len(todos_scores)}")
        logger.info(f"   Mejor score: {mejor_score:.4f} (Distancia: {1-mejor_score:.4f})")
        logger.info(f"   Mejor usuario: {mejor_usuario}")
        logger.info(f"   Umbral requerido: Score >= {UMBRAL:.2f} (Distancia <= {UMBRAL_DISTANCIA:.2f})")
        logger.info("=" * 60)
        
        if todos_scores:
            logger.info("🏆 Top 5 Mejores Coincidencias:")
            for i, resultado in enumerate(todos_scores[:5], 1):
                logger.info(f"   {i}. Usuario {resultado['usuario_id']}: {resultado['porcentaje_similitud']:.1f}% (Score: {resultado['score']:.4f})")

        if mejor_score >= UMBRAL:
            logger.info(f"✅ ACCESO CONCEDIDO: Usuario {mejor_usuario} (Score: {mejor_score:.4f})")
            return True, mejor_usuario

        logger.info(f"❌ ACCESO DENEGADO: Score insuficiente ({mejor_score:.4f} < {UMBRAL:.2f})")
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
