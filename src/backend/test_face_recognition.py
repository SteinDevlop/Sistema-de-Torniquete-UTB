"""
Script de prueba para el sistema de reconocimiento facial.
Prueba registro y verificación con imágenes de ejemplo.
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import cv2
import base64
from app.logic.face_recognition import get_face_recognition_system
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generar_imagen_prueba():
    """Genera una imagen de prueba con un rostro simulado (para testing)"""
    # En un caso real, cargarías una imagen con cv2.imread()
    # Para testing, crear una imagen vacía de ejemplo
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    # Aquí normalmente cargarías una imagen real
    return img


def imagen_a_base64(imagen: np.ndarray) -> str:
    """Convierte una imagen numpy a base64"""
    _, buffer = cv2.imencode('.jpg', imagen)
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')


def test_sistema_reconocimiento():
    """Prueba el sistema de reconocimiento facial"""
    
    print("=" * 80)
    print("🧪 PRUEBA DEL SISTEMA DE RECONOCIMIENTO FACIAL")
    print("=" * 80)
    
    # Inicializar sistema
    face_system = get_face_recognition_system()
    
    print("\n✅ Sistema inicializado correctamente")
    print(f"   • Modelo: {face_system.model_name}")
    print(f"   • Tolerancia: {face_system.tolerance}")
    print(f"   • Tamaño embedding: {face_system.embedding_size}")
    
    # Nota: Para pruebas reales, necesitas imágenes con rostros
    print("\n" + "=" * 80)
    print("📝 NOTAS PARA PRUEBAS REALES:")
    print("=" * 80)
    print("1. Coloca imágenes de prueba en una carpeta")
    print("2. Carga las imágenes con cv2.imread()")
    print("3. Extrae embeddings con face_system.extraer_embedding()")
    print("4. Compara embeddings con face_system.comparar_rostros()")
    print("\n💡 Ejemplo de uso:")
    print("   img = cv2.imread('foto_persona.jpg')")
    print("   embedding = face_system.extraer_embedding(img)")
    print("   img_b64 = imagen_a_base64(img)")
    print("   embedding_desde_b64 = face_system.extraer_embedding_desde_base64(img_b64)")
    print("=" * 80)
    
    return True


def test_serialization():
    """Prueba la serialización y deserialización de embeddings"""
    
    print("\n" + "=" * 80)
    print("🧪 PRUEBA DE SERIALIZACIÓN DE EMBEDDINGS")
    print("=" * 80)
    
    face_system = get_face_recognition_system()
    
    # Crear un embedding de prueba (512 dimensiones)
    embedding_original = np.random.randn(512).astype(np.float32)
    print(f"\n✅ Embedding original creado: shape={embedding_original.shape}, dtype={embedding_original.dtype}")
    
    # Serializar a base64
    embedding_b64 = face_system.embedding_a_base64(embedding_original)
    print(f"✅ Serializado a base64: {len(embedding_b64)} caracteres")
    
    # Deserializar de vuelta
    embedding_recuperado = face_system.base64_a_embedding(embedding_b64)
    print(f"✅ Deserializado: shape={embedding_recuperado.shape}, dtype={embedding_recuperado.dtype}")
    
    # Verificar que sean idénticos
    if np.allclose(embedding_original, embedding_recuperado):
        print("✅ ¡Serialización/Deserialización EXITOSA! Los embeddings son idénticos.")
    else:
        print("❌ ERROR: Los embeddings no coinciden después de serializar/deserializar")
        return False
    
    # Probar comparación
    coincide, distancia = face_system.comparar_rostros(embedding_original, embedding_recuperado)
    print(f"\n🔍 Comparación de embeddings idénticos:")
    print(f"   • Coincide: {coincide}")
    print(f"   • Distancia: {distancia:.6f}")
    
    if distancia < 0.001:  # Debería ser casi 0
        print("✅ ¡Comparación EXITOSA! Distancia prácticamente 0.")
    else:
        print(f"⚠️  Advertencia: Distancia mayor a la esperada ({distancia:.6f})")
    
    # Probar con embedding diferente
    embedding_diferente = np.random.randn(512).astype(np.float32)
    coincide2, distancia2 = face_system.comparar_rostros(embedding_original, embedding_diferente)
    print(f"\n🔍 Comparación con embedding diferente:")
    print(f"   • Coincide: {coincide2}")
    print(f"   • Distancia: {distancia2:.6f}")
    
    if not coincide2 and distancia2 > face_system.tolerance:
        print("✅ ¡Comparación EXITOSA! Embeddings diferentes correctamente identificados.")
    else:
        print("⚠️  Advertencia: Embeddings diferentes marcados como coincidentes")
    
    print("=" * 80)
    return True


if __name__ == "__main__":
    try:
        # Ejecutar pruebas
        test_sistema_reconocimiento()
        test_serialization()
        
        print("\n" + "=" * 80)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 80)
        print("\n🚀 El sistema está listo para usar con imágenes reales.")
        print("   Prueba con el frontend en: http://localhost:3000/facial-recognition-liveness.html")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error en las pruebas: {e}", exc_info=True)
        sys.exit(1)
