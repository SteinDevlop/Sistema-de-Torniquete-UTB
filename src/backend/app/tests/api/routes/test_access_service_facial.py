import base64
import numpy as np
from fastapi.testclient import TestClient
from backend.app.api.main import app
from urllib.parse import quote

client = TestClient(app)

def test_crear_usuario_y_acceso_facial():
    """Caso 1: Acceso exitoso con embedding facial válido"""
    # Generar embedding facial realista (128 floats)
    embedding = np.random.rand(128).astype(np.float32)
    embedding_b64 = base64.b64encode(embedding.tobytes()).decode()

    # Crear usuario biométrico
    response = client.post(
        "/biometria/create",
        data={
            "id_usuario": 123,
            "vector_facial": embedding_b64,
            "rfid_tag": "RFID123",
            "fecha_actualizacion": "2025-10-20T20:00:00"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    print(f"✅ Usuario creado con embedding: {embedding_b64[:50]}...")

    # Probar acceso con el mismo embedding
    # Usar params en lugar de query string para evitar problemas de encoding
    acceso = client.post(
        "/acceso/camara",
        params={
            "dispositivo_id": "test",
            "vector": embedding_b64,
            "fecha": "2025-10-20T20:01:00"
        }
    )
    data = acceso.json()
    print(f"✅ Respuesta de acceso: {data}")
    assert data["status"] is True
    assert data["usuario_id"] == 123
    assert data["medio"] == "camara"


def test_acceso_denegado_embedding_incorrecto():
    """Caso 2: Acceso denegado con embedding facial incorrecto"""
    # Crear usuario con un embedding
    embedding_correcto = np.random.rand(128).astype(np.float32)
    embedding_correcto_b64 = base64.b64encode(embedding_correcto.tobytes()).decode()
    
    response = client.post(
        "/biometria/create",
        data={
            "id_usuario": 456,
            "vector_facial": embedding_correcto_b64,
            "rfid_tag": "RFID456",
            "fecha_actualizacion": "2025-10-20T20:00:00"
        }
    )
    assert response.status_code == 200
    print(f"✅ Usuario 456 creado")

    # Intentar acceso con embedding diferente
    embedding_incorrecto = np.random.rand(128).astype(np.float32)
    embedding_incorrecto_b64 = base64.b64encode(embedding_incorrecto.tobytes()).decode()
    
    acceso = client.post(
        "/acceso/camara",
        params={
            "dispositivo_id": "test",
            "vector": embedding_incorrecto_b64,
            "fecha": "2025-10-20T20:01:00"
        }
    )
    data = acceso.json()
    print(f"✅ Acceso denegado correctamente: {data}")
    assert data["status"] is False
    assert data["usuario_id"] is None
    assert data["medio"] == "camara"


def test_acceso_vector_malformado():
    """Caso 3: Acceso con vector facial malformado (no Base64 ni JSON)"""
    acceso = client.post(
        "/acceso/camara",
        params={
            "dispositivo_id": "test",
            "vector": "string_invalido",
            "fecha": "2025-10-20T20:00:00"
        }
    )
    data = acceso.json()
    print(f"✅ Vector malformado rechazado: {data}")
    assert data["status"] is False
    assert data["usuario_id"] is None
    assert data["medio"] == "camara"


def test_acceso_sin_vector():
    """Caso 4: Acceso sin vector facial (parámetro requerido)"""
    acceso = client.post(
        "/acceso/camara",
        params={
            "dispositivo_id": "test",
            "fecha": "2025-10-20T20:00:00"
        }
    )
    # El endpoint debería devolver error 422 porque 'vector' es requerido
    assert acceso.status_code == 422
    data = acceso.json()
    print(f"✅ Vector requerido - Error 422: {data}")
    assert "detail" in data