"""
Módulo de reconocimiento facial usando DeepFace.
Maneja la detección, extracción de embeddings y comparación de rostros.
"""
import numpy as np
import cv2
from typing import Optional, Tuple, Dict
from deepface import DeepFace
import warnings
import os
import tempfile
import logging
import base64

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class FaceRecognitionSystem:
    """
    Sistema de reconocimiento facial que utiliza embeddings usando DeepFace.
    No almacena imágenes, solo vectores de características faciales (embeddings).
    
    Características:
    - Modelo: Facenet512 (genera embeddings de 512 dimensiones)
    - Detección: OpenCV (rápido y confiable)
    - Distancia: Coseno (0 = idéntico, 1 = totalmente diferente)
    - Umbral: 0.30 (equivalente a 70% de similitud)
    """
    
    def __init__(self, tolerance: float = 0.30, model: str = "Facenet512"):
        """
        Inicializa el sistema de reconocimiento facial.
        
        Args:
            tolerance: Umbral de distancia coseno (0.30 por defecto = 70% similitud)
                      Valores más bajos = más estricto
                      0.20 = 80% similitud (muy estricto)
                      0.30 = 70% similitud (recomendado)
                      0.40 = 60% similitud (permisivo)
            model: Modelo de embedding ("Facenet512" recomendado)
        """
        self.tolerance = tolerance
        self.model_name = model
        self.detector_backend = "opencv"  # Usar opencv para detección (más rápido)
        self.embedding_size = 512  # Facenet512 genera vectores de 512 dimensiones
        logger.info(f"🤖 FaceRecognitionSystem inicializado:")
        logger.info(f"   • Modelo: {model}")
        logger.info(f"   • Tolerancia (distancia): {tolerance} ({(1-tolerance)*100:.0f}% similitud mínima)")
        logger.info(f"   • Tamaño embedding: {self.embedding_size}")
    
    def detectar_rostro(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """
        Detecta si hay un rostro en la imagen y retorna información detallada.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            tuple: (detectado, info_dict)
                detectado: True si se detectó exactamente un rostro válido
                info_dict: {
                    'rostros_encontrados': int,
                    'confianza': float,
                    'area_facial': dict,
                    'mensaje': str
                }
        """
        try:
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face_detect.jpg')
            cv2.imwrite(temp_file, image)
            
            # Detectar rostros usando DeepFace
            faces = DeepFace.extract_faces(
                img_path=temp_file,
                detector_backend=self.detector_backend,
                enforce_detection=False,
                align=True
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            num_faces = len(faces)
            
            # No se detectó ningún rostro
            if num_faces == 0:
                return False, {
                    'rostros_encontrados': 0,
                    'confianza': 0.0,
                    'area_facial': None,
                    'mensaje': 'No se detectó ningún rostro. Por favor, posiciona tu cara frente a la cámara.'
                }
            
            # Se detectaron múltiples rostros
            if num_faces > 1:
                return False, {
                    'rostros_encontrados': num_faces,
                    'confianza': faces[0]['confidence'],
                    'area_facial': faces[0]['facial_area'],
                    'mensaje': f'Se detectaron {num_faces} rostros. Por favor, asegúrate de estar solo frente a la cámara.'
                }
            
            # Un solo rostro detectado
            face = faces[0]
            confianza = face['confidence']
            
            # Verificar confianza de detección
            if confianza < 0.90:
                return False, {
                    'rostros_encontrados': 1,
                    'confianza': confianza,
                    'area_facial': face['facial_area'],
                    'mensaje': f'Rostro detectado con baja confianza ({confianza*100:.0f}%). Mejora la iluminación.'
                }
            
            # Verificar tamaño del rostro
            facial_area = face['facial_area']
            face_width = facial_area['w']
            face_height = facial_area['h']
            
            if face_width < 80 or face_height < 80:
                return False, {
                    'rostros_encontrados': 1,
                    'confianza': confianza,
                    'area_facial': facial_area,
                    'mensaje': 'Rostro demasiado pequeño. Por favor, acércate más a la cámara.'
                }
            
            # Todo está bien
            return True, {
                'rostros_encontrados': 1,
                'confianza': confianza,
                'area_facial': facial_area,
                'mensaje': 'Rostro detectado correctamente.'
            }
            
        except Exception as e:
            logger.error(f"Error al detectar rostro: {e}")
            return False, {
                'rostros_encontrados': 0,
                'confianza': 0.0,
                'area_facial': None,
                'mensaje': f'Error en detección: {str(e)}'
            }
    
    def extraer_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extrae el embedding facial de una imagen usando DeepFace.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            np.ndarray: Vector de características float32[512] o None si no se detectó rostro
        """
        temp_file = None
        try:
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face_embed.jpg')
            cv2.imwrite(temp_file, image)
            
            logger.info("📸 Extrayendo embedding facial con DeepFace...")
            
            # Extraer embedding usando DeepFace
            embedding_objs = DeepFace.represent(
                img_path=temp_file,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=True,  # Forzar detección de rostro
                align=True  # Alinear rostro para mejor precisión
            )
            
            if len(embedding_objs) == 0:
                logger.warning("❌ No se detectó ningún rostro en la imagen")
                return None
            
            if len(embedding_objs) > 1:
                logger.warning(f"⚠️  Se detectaron {len(embedding_objs)} rostros. Usando el primero.")
            
            # Obtener el embedding (DeepFace retorna float64, convertir a float32)
            embedding = np.array(embedding_objs[0]['embedding'], dtype=np.float32)
            
            # Validar dimensiones
            if embedding.shape[0] != self.embedding_size:
                logger.error(f"❌ Embedding con dimensión incorrecta: {embedding.shape[0]} (esperado: {self.embedding_size})")
                return None
            
            logger.info(f"✅ Embedding extraído exitosamente:")
            logger.info(f"   • Shape: {embedding.shape}")
            logger.info(f"   • Dtype: {embedding.dtype}")
            logger.info(f"   • Rango: [{embedding.min():.4f}, {embedding.max():.4f}]")
            logger.info(f"   • Norm: {np.linalg.norm(embedding):.4f}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error al extraer embedding: {e}")
            return None
            
        finally:
            # Limpiar archivo temporal
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo temporal: {e}")
    
    def extraer_embedding_desde_base64(self, imagen_b64: str) -> Optional[np.ndarray]:
        """
        Extrae embedding desde una imagen codificada en base64.
        
        Args:
            imagen_b64: Imagen codificada en base64 (sin prefijo data:image)
            
        Returns:
            np.ndarray: Vector de características float32[512] o None si no se detectó rostro
        """
        try:
            # Remover prefijo si existe
            if ',' in imagen_b64:
                imagen_b64 = imagen_b64.split(',')[1]
            
            # Decodificar base64 a bytes
            img_bytes = base64.b64decode(imagen_b64)
            
            # Convertir bytes a numpy array
            nparr = np.frombuffer(img_bytes, np.uint8)
            
            # Decodificar imagen
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("❌ No se pudo decodificar la imagen desde base64")
                return None
            
            logger.info(f"📷 Imagen decodificada: {image.shape[1]}x{image.shape[0]} px")
            
            # Extraer embedding
            return self.extraer_embedding(image)
            
        except Exception as e:
            logger.error(f"❌ Error al extraer embedding desde base64: {e}")
            return None
    
    def comparar_rostros(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Tuple[bool, float]:
        """
        Compara dos embeddings faciales y determina si pertenecen a la misma persona.
        
        Args:
            embedding1: Primer vector de características (float32[512])
            embedding2: Segundo vector de características (float32[512])
            
        Returns:
            tuple: (coincide, distancia)
                   coincide: True si son la misma persona (distancia <= tolerance)
                   distancia: Distancia coseno entre los vectores (0 = idéntico, 1 = diferente)
        """
        try:
            # Validar que ambos embeddings tengan la misma dimensión
            if embedding1.shape[0] != embedding2.shape[0]:
                logger.error(f"❌ Embeddings con dimensiones diferentes: {embedding1.shape[0]} vs {embedding2.shape[0]}")
                return False, 1.0
            
            # Normalizar vectores
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                logger.error("❌ Embedding con norma cero (vector inválido)")
                return False, 1.0
            
            embedding1_norm = embedding1 / norm1
            embedding2_norm = embedding2 / norm2
            
            # Calcular similitud coseno (-1 a 1, donde 1 = idéntico)
            cosine_similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # Convertir a distancia (0 = idéntico, 1 = totalmente diferente)
            distancia = float(1 - cosine_similarity)
            
            # Calcular porcentaje de similitud
            similitud_porcentaje = (1 - distancia) * 100
            
            # Determinar si coinciden según el umbral
            coincide = distancia <= self.tolerance
            
            logger.debug(f"🔍 Comparación de rostros:")
            logger.debug(f"   • Distancia: {distancia:.4f}")
            logger.debug(f"   • Similitud: {similitud_porcentaje:.2f}%")
            logger.debug(f"   • Umbral: {self.tolerance:.4f} ({(1-self.tolerance)*100:.0f}%)")
            logger.debug(f"   • Resultado: {'✅ COINCIDE' if coincide else '❌ NO COINCIDE'}")
            
            return coincide, distancia
            
        except Exception as e:
            logger.error(f"❌ Error al comparar rostros: {e}")
            return False, 1.0
    
    def embedding_a_base64(self, embedding: np.ndarray) -> str:
        """
        Convierte un embedding numpy a string base64 para almacenamiento.
        
        Args:
            embedding: Vector numpy (float32[512])
            
        Returns:
            str: Embedding codificado en base64
        """
        # Asegurar que sea float32
        embedding = embedding.astype(np.float32)
        
        # Convertir a bytes
        embedding_bytes = embedding.tobytes()
        
        # Codificar en base64
        embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')
        
        logger.debug(f"📦 Embedding serializado: {len(embedding_b64)} caracteres base64")
        
        return embedding_b64
    
    def base64_a_embedding(self, embedding_b64: str) -> Optional[np.ndarray]:
        """
        Convierte un string base64 de vuelta a embedding numpy.
        
        Args:
            embedding_b64: Embedding codificado en base64
            
        Returns:
            np.ndarray: Vector numpy (float32[512]) o None si hay error
        """
        try:
            # Agregar padding si es necesario
            padding = (4 - len(embedding_b64) % 4) % 4
            embedding_b64_padded = embedding_b64 + ('=' * padding)
            
            # Decodificar base64 a bytes
            embedding_bytes = base64.b64decode(embedding_b64_padded)
            
            # Convertir bytes a numpy array
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            
            # Validar dimensiones
            if embedding.shape[0] != self.embedding_size:
                logger.error(f"❌ Embedding deserializado con dimensión incorrecta: {embedding.shape[0]} (esperado: {self.embedding_size})")
                return None
            
            logger.debug(f"📦 Embedding deserializado: shape={embedding.shape}, dtype={embedding.dtype}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error al deserializar embedding: {e}")
            return None
    
    def validar_calidad_imagen(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Valida la calidad de la imagen para reconocimiento facial.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            tuple: (es_valida, mensaje)
        """
        try:
            # Verificar que la imagen no esté vacía
            if image is None or image.size == 0:
                return False, "Imagen vacía"
            
            # Verificar dimensiones mínimas
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                return False, f"Imagen demasiado pequeña ({width}x{height}). Mínimo: 100x100 px"
            
            # Detectar rostro y obtener información detallada
            detectado, info = self.detectar_rostro(image)
            
            if not detectado:
                return False, info['mensaje']
            
            return True, info['mensaje']
            
        except Exception as e:
            return False, f"Error al validar imagen: {str(e)}"
    
    def validar_imagen_base64(self, imagen_b64: str) -> Tuple[bool, str]:
        """
        Valida una imagen en base64 antes de procesarla.
        
        Args:
            imagen_b64: Imagen codificada en base64
            
        Returns:
            tuple: (es_valida, mensaje)
        """
        try:
            # Remover prefijo si existe
            if ',' in imagen_b64:
                imagen_b64 = imagen_b64.split(',')[1]
            
            # Decodificar
            img_bytes = base64.b64decode(imagen_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return False, "No se pudo decodificar la imagen"
            
            # Validar calidad
            return self.validar_calidad_imagen(image)
            
        except Exception as e:
            return False, f"Error al validar imagen base64: {str(e)}"
    
    def detectar_rostro_con_coordenadas(self, image: np.ndarray) -> Tuple[bool, Dict]:
        """
        Detecta rostro y retorna las coordenadas del cuadro delimitador para dibujar en el frontend.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            tuple: (detectado, info_dict)
                detectado: True si se detectó exactamente un rostro válido
                info_dict: {
                    'rostros_encontrados': int,
                    'confianza': float,
                    'coordenadas': {'x': int, 'y': int, 'w': int, 'h': int},
                    'mensaje': str
                }
        """
        try:
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face_coords.jpg')
            cv2.imwrite(temp_file, image)
            
            # Detectar rostros usando DeepFace
            faces = DeepFace.extract_faces(
                img_path=temp_file,
                detector_backend=self.detector_backend,
                enforce_detection=False,
                align=False  # No alinear para obtener coordenadas originales
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            num_faces = len(faces)
            
            # No se detectó ningún rostro
            if num_faces == 0:
                return False, {
                    'rostros_encontrados': 0,
                    'confianza': 0.0,
                    'coordenadas': None,
                    'mensaje': 'No se detectó ningún rostro'
                }
            
            # Obtener el rostro principal (el más grande o de mayor confianza)
            face = faces[0]
            confianza = face['confidence']
            facial_area = face['facial_area']
            
            # Convertir coordenadas
            coordenadas = {
                'x': int(facial_area['x']),
                'y': int(facial_area['y']),
                'w': int(facial_area['w']),
                'h': int(facial_area['h'])
            }
            
            # Verificar confianza de detección
            if confianza < 0.85:
                return False, {
                    'rostros_encontrados': num_faces,
                    'confianza': float(confianza),
                    'coordenadas': coordenadas,
                    'mensaje': f'Confianza baja ({confianza*100:.0f}%)'
                }
            
            # Verificar tamaño del rostro
            face_width = facial_area['w']
            face_height = facial_area['h']
            
            if face_width < 80 or face_height < 80:
                return False, {
                    'rostros_encontrados': num_faces,
                    'confianza': float(confianza),
                    'coordenadas': coordenadas,
                    'mensaje': 'Rostro muy pequeño. Acércate más'
                }
            
            # Todo está bien
            return True, {
                'rostros_encontrados': num_faces,
                'confianza': float(confianza),
                'coordenadas': coordenadas,
                'mensaje': 'Rostro detectado' if num_faces == 1 else f'{num_faces} rostros detectados'
            }
            
        except Exception as e:
            logger.error(f"Error al detectar rostro con coordenadas: {e}")
            return False, {
                'rostros_encontrados': 0,
                'confianza': 0.0,
                'coordenadas': None,
                'mensaje': f'Error: {str(e)}'
            }


# Instancia global del sistema de reconocimiento facial (Singleton)
_face_system_instance = None


def get_face_recognition_system(tolerance: float = 0.30) -> FaceRecognitionSystem:
    """
    Obtiene la instancia singleton del sistema de reconocimiento facial.
    
    Args:
        tolerance: Umbral de distancia coseno (solo se usa en la primera inicialización)
                   0.30 = 70% similitud (recomendado)
    
    Returns:
        FaceRecognitionSystem: Instancia del sistema
    """
    global _face_system_instance
    if _face_system_instance is None:
        _face_system_instance = FaceRecognitionSystem(tolerance=tolerance, model="Facenet512")
        logger.info("✅ Sistema de reconocimiento facial inicializado (Singleton)")
    return _face_system_instance
