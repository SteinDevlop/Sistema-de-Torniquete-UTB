"""
Módulo de reconocimiento facial usando DeepFace.
Maneja la detección, extracción de embeddings y comparación de rostros.
"""
import numpy as np
import cv2
from typing import Optional, Tuple
from deepface import DeepFace
import warnings
import os
import tempfile
import logging

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class FaceRecognitionSystem:
    """
    Sistema de reconocimiento facial que utiliza embeddings usando DeepFace.
    No almacena imágenes, solo vectores de características faciales.
    """
    
    def __init__(self, tolerance: float = 0.4, model: str = "Facenet512"):
        """
        Inicializa el sistema de reconocimiento facial.
        
        Args:
            tolerance: Umbral de similitud (0.4 por defecto)
                      Valores más bajos = más estricto
            model: Modelo de embedding ("Facenet512", "VGG-Face", "OpenFace", "DeepFace")
        """
        self.tolerance = tolerance
        self.model_name = model
        self.detector_backend = "opencv"  # Usar opencv para detección (más rápido)
        logger.info(f"FaceRecognitionSystem inicializado con modelo={model}, tolerance={tolerance}")
    
    def detectar_rostro(self, image: np.ndarray) -> bool:
        """
        Detecta si hay un rostro en la imagen.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            bool: True si se detectó un rostro, False en caso contrario
        """
        try:
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face.jpg')
            cv2.imwrite(temp_file, image)
            
            # Detectar rostros usando DeepFace
            faces = DeepFace.extract_faces(
                img_path=temp_file,
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return len(faces) > 0 and faces[0]['confidence'] > 0.9
            
        except Exception as e:
            logger.error(f"Error al detectar rostro: {e}")
            return False
    
    def extraer_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extrae el embedding facial de una imagen usando DeepFace.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            np.ndarray: Vector de características o None si no se detectó rostro
        """
        try:
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face.jpg')
            cv2.imwrite(temp_file, image)
            
            # Extraer embedding usando DeepFace
            embedding_objs = DeepFace.represent(
                img_path=temp_file,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=True  # Forzar detección de rostro
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if len(embedding_objs) > 0:
                embedding = np.array(embedding_objs[0]['embedding'])
                logger.info(f"Embedding extraído exitosamente. Shape: {embedding.shape}")
                return embedding
            else:
                logger.warning("No se pudo extraer embedding de la imagen")
                return None
            
        except Exception as e:
            logger.error(f"Error al extraer embedding: {e}")
            # Limpiar archivo temporal en caso de error
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face.jpg')
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return None
    
    def extraer_embedding_desde_base64(self, imagen_b64: str) -> Optional[np.ndarray]:
        """
        Extrae embedding desde una imagen codificada en base64.
        
        Args:
            imagen_b64: Imagen codificada en base64
            
        Returns:
            np.ndarray: Vector de características o None si no se detectó rostro
        """
        try:
            import base64
            # Decodificar base64 a bytes
            img_bytes = base64.b64decode(imagen_b64)
            # Convertir bytes a numpy array
            nparr = np.frombuffer(img_bytes, np.uint8)
            # Decodificar imagen
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("No se pudo decodificar la imagen desde base64")
                return None
            
            # Extraer embedding
            return self.extraer_embedding(image)
            
        except Exception as e:
            logger.error(f"Error al extraer embedding desde base64: {e}")
            return None
    
    def comparar_rostros(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Tuple[bool, float]:
        """
        Compara dos embeddings faciales y determina si pertenecen a la misma persona.
        
        Args:
            embedding1: Primer vector de características
            embedding2: Segundo vector de características
            
        Returns:
            tuple: (coincide, distancia)
                   coincide: True si son la misma persona
                   distancia: Distancia entre los vectores
        """
        try:
            # Calcular distancia coseno
            from numpy.linalg import norm
            
            # Normalizar vectores
            embedding1_norm = embedding1 / (norm(embedding1) + 1e-8)
            embedding2_norm = embedding2 / (norm(embedding2) + 1e-8)
            
            # Calcular similitud coseno
            cosine_similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # Convertir a distancia (0 = idéntico, 1 = totalmente diferente)
            distancia = 1 - cosine_similarity
            
            # Determinar si coinciden según el umbral
            coincide = distancia <= self.tolerance
            
            logger.debug(f"Comparación de rostros: distancia={distancia:.4f}, coincide={coincide}")
            return coincide, float(distancia)
            
        except Exception as e:
            logger.error(f"Error al comparar rostros: {e}")
            return False, 1.0
    
    def validar_calidad_imagen(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Valida la calidad de la imagen para reconocimiento facial.
        
        Args:
            image: Imagen en formato numpy array
            
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
                return False, "Imagen demasiado pequeña (mínimo 100x100)"
            
            # Guardar temporalmente la imagen
            temp_file = os.path.join(tempfile.gettempdir(), 'temp_face.jpg')
            cv2.imwrite(temp_file, image)
            
            # Detectar rostros
            faces = DeepFace.extract_faces(
                img_path=temp_file,
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if len(faces) == 0:
                return False, "No se detectó ningún rostro"
            
            if len(faces) > 1:
                return False, "Se detectaron múltiples rostros (debe haber solo uno)"
            
            # Verificar confianza de detección
            if faces[0]['confidence'] < 0.9:
                return False, "Rostro detectado con baja confianza (mejor iluminación necesaria)"
            
            # Verificar tamaño del rostro detectado
            facial_area = faces[0]['facial_area']
            face_width = facial_area['w']
            face_height = facial_area['h']
            
            if face_width < 50 or face_height < 50:
                return False, "Rostro demasiado pequeño (acércate más a la cámara)"
            
            return True, "Imagen válida"
            
        except Exception as e:
            return False, f"Error al validar imagen: {e}"


# Instancia global del sistema de reconocimiento facial
_face_system_instance = None


def get_face_recognition_system() -> FaceRecognitionSystem:
    """
    Obtiene la instancia singleton del sistema de reconocimiento facial.
    
    Returns:
        FaceRecognitionSystem: Instancia del sistema
    """
    global _face_system_instance
    if _face_system_instance is None:
        _face_system_instance = FaceRecognitionSystem(tolerance=0.4, model="Facenet512")
    return _face_system_instance
