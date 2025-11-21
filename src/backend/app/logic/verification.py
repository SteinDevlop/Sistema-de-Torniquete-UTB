from app.models.access import MedioAcceso, AccesoRequest
from app.models.verificador_acceso import VerificadorAcceso
from app.logic.universal_controller_instance import universal_controller
from app.logic.face_recognition import get_face_recognition_system
import numpy as np
import base64
import hashlib
import logging
from app.models.biometria import BiometriaOut
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
    Verifica una huella dactilar contra los templates almacenados.
    Soporta tanto templates tipo imagen (SSIM) como vectores (correlación).
    """

    def __init__(self, umbral_imagen=0.85, umbral_vector=0.98):
        self.umbral_imagen = umbral_imagen
        self.umbral_vector = umbral_vector

    def _decode_image(self, b64_data: str):
        """Intenta decodificar el base64 como imagen (grayscale)."""
        try:
            data = base64.b64decode(b64_data)
            np_data = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(np_data, cv2.IMREAD_GRAYSCALE)
            return img
        except Exception:
            return None

    def _decode_vector(self, b64_data: str):
        """Decodifica el base64 como vector de bytes."""
        try:
            data = base64.b64decode(b64_data)
            return np.frombuffer(data, dtype=np.uint8).astype(np.float32)
        except Exception:
            return None

    def _similitud_vectorial(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calcula similitud por correlación normalizada."""
        min_len = min(len(v1), len(v2))
        if min_len == 0:
            return 0.0
        v1, v2 = v1[:min_len], v2[:min_len]
        return np.corrcoef(v1, v2)[0, 1]

    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Verifica si la huella enviada coincide con alguna en la DB.
        Retorna (True, id_usuario) o (False, None)
        """
        vector_in_b64 = data.get("vector")
        if not vector_in_b64:
            return False, None

        # 1️⃣ Intentar decodificar como imagen
        img_sensor = self._decode_image(vector_in_b64)
        usar_vector = img_sensor is None

        registros_db = universal_controller.read_all(BiometriaOut())
        if not registros_db:
            return False, None

        mejor_score = 0.0
        mejor_id = None

        for registro in registros_db:
            tpl_b64 = registro.get("template_huella")
            if not tpl_b64:
                continue

            if usar_vector:
                # === Comparación tipo vector ===
                v1 = self._decode_vector(vector_in_b64)
                v2 = self._decode_vector(tpl_b64)
                if v1 is None or v2 is None:
                    continue
                score = self._similitud_vectorial(v1, v2)
                umbral = self.umbral_vector
            else:
                # === Comparación tipo imagen ===
                img_db = self._decode_image(tpl_b64)
                if img_db is None:
                    continue
                h, w = img_sensor.shape
                img_db = cv2.resize(img_db, (w, h))
                score = ssim(img_sensor, img_db)
                umbral = self.umbral_imagen

            if score > mejor_score:
                mejor_score = score
                mejor_id = registro["id_usuario"]

        print(f"[DEBUG] Mejor similitud: {mejor_score:.3f} (modo {'vector' if usar_vector else 'imagen'})")
        return (mejor_score >= umbral, mejor_id if mejor_score >= umbral else None)

class VerificadorCamara(VerificadorAcceso):
    """
    Verifica un embedding facial comparando con candidatos en la base de datos.
    
    Características:
    - Usa DeepFace con modelo Facenet512 (512 dimensiones)
    - Similitud coseno para comparación
    - Umbral: 0.30 distancia (70% similitud mínima)
    - Filtrado opcional por facial_hash para optimizar búsqueda
    """

    def __init__(self):
        """Inicializar con configuración de verificación"""
        self.UMBRAL_DISTANCIA = 0.30  # Distancia máxima permitida (70% similitud)
        self.UMBRAL_SIMILITUD = 1 - self.UMBRAL_DISTANCIA  # 0.70 (70%)
        
        self.detalles_comparacion = {
            "candidatos_evaluados": 0,
            "mejor_score": 0.0,
            "mejor_usuario": None,
            "umbral": self.UMBRAL_SIMILITUD,
            "todos_scores": []
        }
        
        logger.info(f"🔐 VerificadorCamara inicializado:")
        logger.info(f"   • Umbral distancia: {self.UMBRAL_DISTANCIA} (máx)")
        logger.info(f"   • Umbral similitud: {self.UMBRAL_SIMILITUD*100:.0f}% (mín)")
    
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Verifica un rostro contra la base de datos de usuarios registrados.
        
        Args:
            data (dict): {
                "vector": "<base64_embedding>" (opcional si se envía imagen)
                "imagen_facial": "<base64_image>" (recomendado - extrae embedding real)
            }

        Returns:
            (True, id_usuario) si hay coincidencia >= umbral
            (False, None) si no hay coincidencia
        """
        # Resetear detalles de comparación
        self.detalles_comparacion = {
            "candidatos_evaluados": 0,
            "mejor_score": 0.0,
            "mejor_distancia": 1.0,
            "mejor_usuario": None,
            "umbral_similitud": self.UMBRAL_SIMILITUD,
            "umbral_distancia": self.UMBRAL_DISTANCIA,
            "todos_scores": []
        }
        
        vector_str = data.get("vector") or data.get("embedding") or data.get("vector_facial")
        imagen_facial = data.get("imagen_facial")
        
        logger.info("=" * 80)
        logger.info("🔍 VERIFICACIÓN FACIAL INICIADA")
        logger.info(f"   • Tiene vector: {vector_str is not None}")
        logger.info(f"   • Tiene imagen: {imagen_facial is not None}")
        logger.info("=" * 80)
        
        # ========================================
        # 🔹 EXTRACCIÓN DEL EMBEDDING
        # ========================================
        
        # Opción 1: Extraer desde imagen (RECOMENDADO)
        if imagen_facial and not vector_str:
            logger.info("📸 Extrayendo embedding desde imagen con DeepFace...")
            face_system = get_face_recognition_system()
            
            # Validar imagen primero
            es_valida, mensaje = face_system.validar_imagen_base64(imagen_facial)
            if not es_valida:
                logger.warning(f"❌ Imagen rechazada: {mensaje}")
                return False, None
            
            logger.info(f"✅ Imagen validada: {mensaje}")
            
            # Extraer embedding
            embedding_capturado = face_system.extraer_embedding_desde_base64(imagen_facial)
            
            if embedding_capturado is None:
                logger.warning("❌ No se pudo extraer embedding de la imagen")
                return False, None
            
            logger.info(f"✅ Embedding extraído: shape={embedding_capturado.shape}, dtype={embedding_capturado.dtype}")
        
        # Opción 2: Usar vector pre-calculado
        elif vector_str:
            logger.info("📦 Decodificando vector facial pre-calculado...")
            face_system = get_face_recognition_system()
            
            # Intentar decodificar como base64
            embedding_capturado = face_system.base64_a_embedding(vector_str)
            
            if embedding_capturado is None:
                # Intentar como JSON (compatibilidad)
                try:
                    import json
                    embedding_list = json.loads(vector_str)
                    embedding_capturado = np.array(embedding_list, dtype=np.float32)
                    logger.info(f"✅ Embedding parseado desde JSON: shape={embedding_capturado.shape}")
                except Exception as e:
                    logger.warning(f"❌ Error procesando vector facial: {e}")
                    return False, None
        
        else:
            logger.warning("❌ No se proporcionó ni vector ni imagen_facial")
            return False, None

        # ========================================
        # 🔹 VALIDACIÓN DEL EMBEDDING
        # ========================================
        
        if embedding_capturado.shape[0] not in [128, 512]:
            logger.warning(f"❌ Embedding con dimensión incorrecta: {embedding_capturado.shape[0]} (esperado: 512)")
            return False, None
        
        logger.info(f"✅ Embedding validado: {embedding_capturado.shape[0]} dimensiones")

        # ========================================
        # 🔹 BÚSQUEDA DE CANDIDATOS
        # ========================================
        
        try:
            # Calcular hash para optimizar búsqueda
            embedding_norm = embedding_capturado / (np.linalg.norm(embedding_capturado) + 1e-8)
            hash_prefix = hashlib.sha256(embedding_norm.tobytes()).hexdigest()[:8]
            logger.info(f"🔐 Hash calculado: {hash_prefix}")
            
            # Intentar buscar por hash primero
            candidatos = universal_controller.get_by_field_like("Biometria", "facial_hash", hash_prefix)
            
            if not candidatos or len(candidatos) == 0:
                logger.warning("⚠️  No se encontraron candidatos por hash. Buscando TODOS los registros...")
                from app.models.biometria import BiometriaOut
                todos_registros = universal_controller.read_all(BiometriaOut())
                
                # Filtrar solo los que tienen vector_facial
                candidatos = [r for r in todos_registros if r.get("vector_facial")]
                logger.info(f"✅ Candidatos encontrados (sin filtro hash): {len(candidatos)}")
            else:
                logger.info(f"✅ Candidatos encontrados (por hash): {len(candidatos)}")
            
        except Exception as e:
            logger.exception(f"❌ Error consultando candidatos: {e}")
            return False, None

        if not candidatos:
            logger.warning("❌ No hay usuarios con datos faciales registrados")
            return False, None

        # ========================================
        # 🔹 COMPARACIÓN DE EMBEDDINGS
        # ========================================
        
        resultado, user_id = self._comparar_embeddings_faciales(embedding_capturado, candidatos)
        
        logger.info("=" * 80)
        logger.info(f"🎯 RESULTADO FINAL: {'✅ ACCESO CONCEDIDO' if resultado else '❌ ACCESO DENEGADO'}")
        if resultado:
            logger.info(f"   • Usuario: {user_id}")
            logger.info(f"   • Similitud: {self.detalles_comparacion['mejor_score']*100:.2f}%")
        else:
            logger.info(f"   • Mejor similitud: {self.detalles_comparacion['mejor_score']*100:.2f}%")
            logger.info(f"   • Requerido: {self.UMBRAL_SIMILITUD*100:.0f}%")
        logger.info("=" * 80)
        
        return resultado, user_id

    def _comparar_embeddings_faciales(
        self, embedding_capturado: np.ndarray, candidatos: list[dict]
    ) -> tuple[bool, int | None]:
        """
        Compara el embedding facial capturado con los candidatos usando similitud coseno.
        
        Args:
            embedding_capturado: Vector numpy de 512 dimensiones (float32)
            candidatos: Lista de registros de Biometria con vector_facial
            
        Returns:
            (True, id_usuario) si hay coincidencia >= umbral
            (False, None) si no hay coincidencia
        """
        logger.info(f"🔍 Comparando embedding con {len(candidatos)} candidatos...")
        
        face_system = get_face_recognition_system()
        
        mejor_score = 0.0
        mejor_distancia = 1.0
        mejor_usuario = None
        todos_scores = []
        
        # Normalizar embedding capturado una sola vez
        norm_capturado = np.linalg.norm(embedding_capturado)
        if norm_capturado == 0:
            logger.error("❌ Embedding capturado con norma cero")
            return False, None
        
        embedding_capturado_norm = embedding_capturado / norm_capturado

        for idx, candidato in enumerate(candidatos):
            usuario_id = candidato.get("id_usuario")
            stored_vector = candidato.get("vector_facial")
            
            if not stored_vector:
                logger.debug(f"  Candidato {usuario_id}: Sin vector_facial")
                continue

            try:
                # Decodificar vector almacenado
                stored_embedding = face_system.base64_a_embedding(stored_vector)
                
                if stored_embedding is None:
                    # Intentar formato JSON (compatibilidad)
                    try:
                        import json
                        stored_list = json.loads(stored_vector)
                        stored_embedding = np.array(stored_list, dtype=np.float32)
                    except Exception as e:
                        logger.warning(f"  Candidato {usuario_id}: Error decodificando - {e}")
                        continue
                
                # Validar dimensiones
                if stored_embedding.shape[0] not in [128, 512, 1024]:
                    logger.warning(f"  Candidato {usuario_id}: Dimensión incorrecta {stored_embedding.shape[0]}")
                    continue
                
                # Si las dimensiones no coinciden, intentar arreglar duplicación
                if stored_embedding.shape[0] == embedding_capturado.shape[0] * 2:
                    logger.warning(f"  Candidato {usuario_id}: Embedding duplicado. Corrigiendo...")
                    stored_embedding = stored_embedding[:embedding_capturado.shape[0]].copy()
                elif stored_embedding.shape[0] != embedding_capturado.shape[0]:
                    logger.warning(f"  Candidato {usuario_id}: Dimensiones incompatibles {stored_embedding.shape[0]} vs {embedding_capturado.shape[0]}")
                    continue
                
                # Normalizar embedding almacenado
                norm_stored = np.linalg.norm(stored_embedding)
                if norm_stored == 0:
                    logger.warning(f"  Candidato {usuario_id}: Embedding con norma cero")
                    continue
                
                stored_embedding_norm = stored_embedding / norm_stored
                
                # Calcular similitud coseno (0 a 1, donde 1 = idéntico)
                cosine_similarity = float(np.dot(embedding_capturado_norm, stored_embedding_norm))
                
                # Asegurar que esté en rango válido
                cosine_similarity = np.clip(cosine_similarity, -1.0, 1.0)
                
                # Convertir a distancia (0 = idéntico, 1 = totalmente diferente)
                distancia = 1 - cosine_similarity
                
                # Score es la similitud (mayor es mejor)
                score = cosine_similarity
                
                porcentaje = score * 100
                
                logger.info(f"  👤 Usuario {usuario_id}: {porcentaje:.2f}% similitud (distancia: {distancia:.4f})")
                
                # Guardar para reporte
                todos_scores.append({
                    "usuario_id": usuario_id,
                    "score": round(float(score), 4),
                    "distancia": round(float(distancia), 4),
                    "porcentaje_similitud": round(float(porcentaje), 2)
                })
                
                if score > mejor_score:
                    mejor_score = score
                    mejor_distancia = distancia
                    mejor_usuario = usuario_id
                    
            except Exception as e:
                logger.warning(f"  Candidato {usuario_id}: Error en comparación - {e}")
                continue

        # Ordenar scores de mayor a menor
        todos_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Guardar detalles de comparación
        self.detalles_comparacion = {
            "candidatos_evaluados": len(todos_scores),
            "mejor_score": round(float(mejor_score), 4),
            "mejor_distancia": round(float(mejor_distancia), 4),
            "mejor_usuario": mejor_usuario,
            "umbral_similitud": self.UMBRAL_SIMILITUD,
            "umbral_distancia": self.UMBRAL_DISTANCIA,
            "todos_scores": todos_scores[:10]  # Top 10
        }
        
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DE COMPARACIÓN:")
        logger.info(f"   • Candidatos evaluados: {len(todos_scores)}")
        logger.info(f"   • Mejor similitud: {mejor_score*100:.2f}% (distancia: {mejor_distancia:.4f})")
        logger.info(f"   • Mejor usuario: {mejor_usuario}")
        logger.info(f"   • Umbral requerido: ≥ {self.UMBRAL_SIMILITUD*100:.0f}% (distancia ≤ {self.UMBRAL_DISTANCIA:.2f})")
        logger.info("=" * 60)
        
        if todos_scores:
            logger.info("🏆 Top 5 Mejores Coincidencias:")
            for i, resultado in enumerate(todos_scores[:5], 1):
                emoji = "✅" if resultado['score'] >= self.UMBRAL_SIMILITUD else "❌"
                logger.info(f"   {emoji} {i}. Usuario {resultado['usuario_id']}: {resultado['porcentaje_similitud']:.2f}%")

        # Decisión final
        if mejor_score >= self.UMBRAL_SIMILITUD:
            logger.info(f"✅ ACCESO CONCEDIDO: Usuario {mejor_usuario} ({mejor_score*100:.2f}%)")
            return True, mejor_usuario

        logger.info(f"❌ ACCESO DENEGADO: Similitud insuficiente ({mejor_score*100:.2f}% < {self.UMBRAL_SIMILITUD*100:.0f}%)")
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
