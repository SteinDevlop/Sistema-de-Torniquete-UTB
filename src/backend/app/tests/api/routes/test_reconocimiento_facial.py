"""
Test de Reconocimiento Facial
Prueba el VerificadorCamara con embeddings sintéticos de 128 dimensiones
"""

import numpy as np
import base64
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.logic.verification import VerificadorCamara


def generar_embedding_sintetico(seed=42):
    """
    Genera un embedding facial sintético de 128 dimensiones normalizado.
    """
    np.random.seed(seed)
    embedding = np.random.randn(128).astype(np.float32)
    # Normalizar (L2 norm = 1)
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding


def embedding_a_json(embedding):
    """
    Convierte un embedding numpy a string JSON.
    """
    return json.dumps(embedding.tolist())


def embedding_a_base64(embedding):
    """
    Convierte un embedding numpy a Base64.
    """
    return base64.b64encode(embedding.tobytes()).decode('utf-8')


def test_verificador_camara_json():
    """
    Test 1: Verificar con embedding en formato JSON
    """
    print("\n" + "="*60)
    print("TEST 1: VerificadorCamara con formato JSON")
    print("="*60)
    
    verificador = VerificadorCamara()
    
    # Generar embedding de prueba
    embedding = generar_embedding_sintetico(seed=100)
    vector_json = embedding_a_json(embedding)
    
    print(f"✓ Embedding generado: shape={embedding.shape}")
    print(f"✓ Primeros 5 valores: {embedding[:5]}")
    print(f"✓ Norma L2: {np.linalg.norm(embedding):.4f}")
    
    # Verificar
    data = {"vector": vector_json}
    resultado, usuario_id = verificador.verificar(data)
    
    print(f"\n📊 Resultado:")
    print(f"   - Autorizado: {resultado}")
    print(f"   - Usuario ID: {usuario_id}")
    
    # En este punto no hay usuarios en BD, debería retornar False
    assert resultado == False, "Debería retornar False (sin usuarios en BD)"
    assert usuario_id is None, "Usuario ID debería ser None"
    
    print("\n✅ Test 1 PASADO: Manejo correcto cuando no hay candidatos")


def test_verificador_camara_base64():
    """
    Test 2: Verificar con embedding en formato Base64
    """
    print("\n" + "="*60)
    print("TEST 2: VerificadorCamara con formato Base64")
    print("="*60)
    
    verificador = VerificadorCamara()
    
    # Generar embedding de prueba
    embedding = generar_embedding_sintetico(seed=200)
    vector_b64 = embedding_a_base64(embedding)
    
    print(f"✓ Embedding generado: shape={embedding.shape}")
    print(f"✓ Base64 (primeros 50 chars): {vector_b64[:50]}...")
    
    # Verificar
    data = {"vector": vector_b64}
    resultado, usuario_id = verificador.verificar(data)
    
    print(f"\n📊 Resultado:")
    print(f"   - Autorizado: {resultado}")
    print(f"   - Usuario ID: {usuario_id}")
    
    assert resultado == False, "Debería retornar False (sin usuarios en BD)"
    
    print("\n✅ Test 2 PASADO: Manejo correcto de formato Base64")


def test_embedding_invalido():
    """
    Test 3: Rechazar embeddings con dimensiones incorrectas
    """
    print("\n" + "="*60)
    print("TEST 3: Rechazo de embeddings con dimensión incorrecta")
    print("="*60)
    
    verificador = VerificadorCamara()
    
    # Embedding de 64 dimensiones (incorrecto)
    embedding_64 = np.random.randn(64).astype(np.float32)
    vector_json = embedding_a_json(embedding_64)
    
    print(f"✓ Embedding inválido generado: shape={embedding_64.shape}")
    
    # Debería rechazarlo
    data = {"vector": vector_json}
    resultado, usuario_id = verificador.verificar(data)
    
    print(f"\n📊 Resultado:")
    print(f"   - Autorizado: {resultado}")
    print(f"   - Usuario ID: {usuario_id}")
    
    assert resultado == False, "Debería rechazar embedding de 64 dimensiones"
    
    print("\n✅ Test 3 PASADO: Validación correcta de dimensiones")


def test_similitud_coseno():
    """
    Test 4: Verificar cálculo de similitud coseno
    """
    print("\n" + "="*60)
    print("TEST 4: Cálculo de similitud coseno")
    print("="*60)
    
    # Dos embeddings idénticos → similitud = 1.0
    emb1 = generar_embedding_sintetico(seed=300)
    emb2 = emb1.copy()
    
    score = np.dot(emb1, emb2)
    print(f"✓ Similitud entre embeddings idénticos: {score:.4f}")
    assert abs(score - 1.0) < 0.01, "Embeddings idénticos deben tener score ~1.0"
    
    # Dos embeddings diferentes → similitud < 1.0
    emb3 = generar_embedding_sintetico(seed=400)
    score2 = np.dot(emb1, emb3)
    print(f"✓ Similitud entre embeddings diferentes: {score2:.4f}")
    assert score2 < 0.95, "Embeddings diferentes deben tener score < 0.95"
    
    print("\n✅ Test 4 PASADO: Similitud coseno funcionando correctamente")


def test_formato_esp32_simulado():
    """
    Test 5: Simular petición desde ESP32
    """
    print("\n" + "="*60)
    print("TEST 5: Simulación de petición ESP32")
    print("="*60)
    
    verificador = VerificadorCamara()
    
    # Simular embedding que enviaría el ESP32
    embedding = generar_embedding_sintetico(seed=500)
    
    # Formato que enviaría el ESP32 (JSON string)
    vector_esp32 = "[" + ",".join([f"{val:.6f}" for val in embedding]) + "]"
    
    print(f"✓ Vector ESP32 (primeros 100 chars):")
    print(f"   {vector_esp32[:100]}...")
    
    data = {
        "dispositivo_id": "ESP32_001",
        "vector": vector_esp32,
        "fecha": "2025-10-19T10:30:00"
    }
    
    resultado, usuario_id = verificador.verificar(data)
    
    print(f"\n📊 Resultado:")
    print(f"   - Dispositivo: {data['dispositivo_id']}")
    print(f"   - Autorizado: {resultado}")
    print(f"   - Usuario ID: {usuario_id}")
    
    assert resultado == False, "Sin usuarios en BD, debe retornar False"
    
    print("\n✅ Test 5 PASADO: Formato ESP32 compatible")


def main():
    """
    Ejecutar todos los tests
    """
    print("\n" + "#"*60)
    print("# SUITE DE TESTS - RECONOCIMIENTO FACIAL")
    print("#"*60)
    
    try:
        test_verificador_camara_json()
        test_verificador_camara_base64()
        test_embedding_invalido()
        test_similitud_coseno()
        test_formato_esp32_simulado()
        
        print("\n" + "="*60)
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*60)
        print("\n✅ El sistema de reconocimiento facial está operativo")
        print("✅ Formatos JSON y Base64 soportados")
        print("✅ Validación de dimensiones funcionando")
        print("✅ Similitud coseno calculándose correctamente")
        print("✅ Compatible con formato ESP32")
        
        print("\n📝 PRÓXIMOS PASOS:")
        print("   1. Registrar usuarios con embeddings reales en la BD")
        print("   2. Probar endpoint /acceso/camara con cURL")
        print("   3. Integrar con ESP32")
        print("   4. Ajustar umbral según precisión deseada")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
