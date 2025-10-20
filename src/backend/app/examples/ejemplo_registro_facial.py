"""
Script de Ejemplo: Registrar Usuario con Embedding Facial

Este script muestra cómo registrar un usuario en la base de datos
con su embedding facial de 128 dimensiones.

Uso:
    python ejemplo_registro_facial.py
"""

import requests
import numpy as np
import json


def generar_embedding_ejemplo(usuario_id):
    """
    Genera un embedding sintético único para cada usuario.
    En producción, esto vendría del modelo de reconocimiento facial.
    """
    np.random.seed(usuario_id)  # Seed basado en ID para reproducibilidad
    embedding = np.random.randn(128).astype(np.float32)
    # Normalizar (L2 norm = 1)
    embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
    return embedding


def registrar_usuario_con_facial(
    servidor_url: str,
    id_usuario: int,
    embedding: np.ndarray,
    rfid_tag: str = None
):
    """
    Registra un usuario en la base de datos con su embedding facial.
    
    Args:
        servidor_url: URL del servidor (ej: http://localhost:8000)
        id_usuario: ID del usuario a registrar
        embedding: Array numpy de 128 dimensiones
        rfid_tag: Opcional, tag RFID del usuario
    
    Returns:
        dict: Respuesta del servidor
    """
    
    # Validar dimensiones
    if embedding.shape[0] != 128:
        raise ValueError(f"El embedding debe tener 128 dimensiones, recibido: {embedding.shape[0]}")
    
    # Convertir embedding a JSON string
    vector_json = json.dumps(embedding.tolist())
    
    # Preparar datos
    data = {
        "id_usuario": id_usuario,
        "vector_facial": vector_json,
    }
    
    if rfid_tag:
        data["rfid_tag"] = rfid_tag
    
    # Enviar petición
    url = f"{servidor_url}/biometria/create"
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"✅ Usuario {id_usuario} registrado exitosamente")
        return response.json()
    else:
        print(f"❌ Error al registrar usuario: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None


def verificar_acceso_facial(
    servidor_url: str,
    dispositivo_id: str,
    embedding: np.ndarray
):
    """
    Prueba verificar acceso con un embedding facial.
    
    Args:
        servidor_url: URL del servidor
        dispositivo_id: ID del dispositivo ESP32
        embedding: Array numpy de 128 dimensiones
    
    Returns:
        dict: Respuesta del servidor con status de acceso
    """
    
    # Convertir embedding a JSON string
    vector_json = json.dumps(embedding.tolist())
    
    # Preparar datos
    data = {
        "dispositivo_id": dispositivo_id,
        "vector": vector_json,
    }
    
    # Enviar petición
    url = f"{servidor_url}/acceso/camara"
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        if result["status"]:
            print(f"✅ ACCESO CONCEDIDO - Usuario ID: {result['usuario_id']}")
        else:
            print(f"❌ ACCESO DENEGADO")
        return result
    else:
        print(f"❌ Error en verificación: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return None


def main():
    """
    Ejemplo de uso completo:
    1. Registrar varios usuarios
    2. Intentar verificar acceso
    """
    
    # Configuración
    SERVIDOR_URL = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("EJEMPLO: Registro y Verificación Facial")
    print("="*60)
    
    # Primero, crear los usuarios en la tabla Usuarios
    print("\n📝 Paso 1: Crear usuarios en la tabla Usuarios")
    print("   (Esto normalmente se haría desde otro endpoint)")
    
    # Registrar 3 usuarios con embeddings faciales
    print("\n📸 Paso 2: Registrar embeddings faciales")
    
    usuarios = [
        {"id": 1, "nombre": "Juan Pérez", "rfid": "ABC123"},
        {"id": 2, "nombre": "María García", "rfid": "DEF456"},
        {"id": 3, "nombre": "Carlos López", "rfid": "GHI789"},
    ]
    
    embeddings_almacenados = {}
    
    for usuario in usuarios:
        print(f"\n   → Registrando: {usuario['nombre']} (ID: {usuario['id']})")
        
        # Generar embedding sintético
        embedding = generar_embedding_ejemplo(usuario['id'])
        embeddings_almacenados[usuario['id']] = embedding
        
        # Registrar en BD
        try:
            result = registrar_usuario_con_facial(
                SERVIDOR_URL,
                usuario['id'],
                embedding,
                usuario['rfid']
            )
            if result and result.get("success"):
                print(f"      ✓ Embedding: primeros 5 valores = {embedding[:5]}")
        except requests.exceptions.ConnectionError:
            print(f"      ⚠️  No se pudo conectar al servidor en {SERVIDOR_URL}")
            print(f"      ⚠️  Asegúrate de que el servidor esté corriendo")
            return
    
    # Intentar verificar acceso
    print("\n\n🔐 Paso 3: Verificar acceso facial")
    
    # Test 1: Usuario registrado (debería CONCEDER acceso)
    print("\n   Test 1: Usuario registrado (Juan Pérez)")
    embedding_juan = embeddings_almacenados[1]
    verificar_acceso_facial(SERVIDOR_URL, "ESP32_001", embedding_juan)
    
    # Test 2: Mismo usuario, ligera variación (debería CONCEDER acceso)
    print("\n   Test 2: Mismo usuario con pequeña variación")
    embedding_juan_variado = embedding_juan + np.random.randn(128) * 0.05
    embedding_juan_variado = embedding_juan_variado / np.linalg.norm(embedding_juan_variado)
    verificar_acceso_facial(SERVIDOR_URL, "ESP32_001", embedding_juan_variado)
    
    # Test 3: Usuario no registrado (debería DENEGAR acceso)
    print("\n   Test 3: Usuario NO registrado")
    embedding_desconocido = generar_embedding_ejemplo(999)
    verificar_acceso_facial(SERVIDOR_URL, "ESP32_001", embedding_desconocido)
    
    print("\n" + "="*60)
    print("✅ EJEMPLO COMPLETADO")
    print("="*60)
    
    print("\n📊 Resumen:")
    print(f"   - Usuarios registrados: {len(usuarios)}")
    print(f"   - Embeddings almacenados: {len(embeddings_almacenados)}")
    print(f"   - Dimensiones: 128 valores por embedding")
    print(f"   - Servidor: {SERVIDOR_URL}")
    
    print("\n💡 Próximos pasos:")
    print("   1. Integrar con modelo real de reconocimiento facial")
    print("   2. Capturar embeddings desde ESP32/cámara")
    print("   3. Ajustar umbral de similitud según necesidad")
    print("   4. Implementar registro facial desde interfaz web")


if __name__ == "__main__":
    main()
