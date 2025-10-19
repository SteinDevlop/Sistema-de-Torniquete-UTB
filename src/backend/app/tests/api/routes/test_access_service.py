from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from backend.app.api.routes.access_service import app as access_router
from backend.app.logic.universal_controller_instance import UniversalController
from backend.app.core.conf import headers
from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.models.biometria import BiometriaCreate
import logging
import base64
import hashlib
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# ===============================
# CONFIGURACIÓN DE PRUEBAS
# ===============================

# Crear instancia del controlador de pruebas
test_controller = UniversalController()

# Sobrescribir el controlador si se usa dentro del servicio
# (solo necesario si AccessService lo usa internamente)
# from backend.app.logic.access_logic import AccessService
# AccessService.controller = test_controller

# App de prueba
app_for_test = FastAPI()
app_for_test.include_router(access_router)

client = TestClient(app_for_test)

# Limpiar base de datos antes y después de cada test
def setup_function():
    test_controller.clear_tables()

def teardown_function():
    test_controller.clear_tables()


app_for_test = FastAPI()
app_for_test.include_router(access_router)
# ===============================
# PRUEBAS: ENDPOINTS DE ACCESO
# ===============================
def generar_template_y_hash(contenido: bytes):
    template_b64 = base64.b64encode(contenido).decode()
    hash_prefix = hashlib.sha256(contenido).hexdigest()[:8]
    return template_b64, hash_prefix
client = TestClient(app_for_test)
def test_acceso_rfid_exitoso():
    test_controller.add(BiometriaCreate(id_biometria=1, id_usuario=1, rfid_tag="VALID123"))
    response = client.post("/acceso/rfid", params={"rfid_tag": "VALID123"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    logger.info(f"Respuesta RFID exitosa: {data}")
    assert data["status"] is True

def test_acceso_rfid_fallido():
    test_controller.add(BiometriaCreate(id_biometria=1, id_usuario=1, rfid_tag="VALID123"))
    response = client.post("/acceso/rfid", params={"rfid_tag": "INVALID"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is False

def test_acceso_huella_exitoso():
    """
    Simula una huella válida registrada en base de datos y una nueva lectura idéntica.
    """
    # 🔹 Simulamos una plantilla binaria y la convertimos a Base64
    template_b64, hash_prefix = generar_template_y_hash(b"plantilla_simulada_valida")
    print(f"Template B64: {template_b64}, Hash Prefix: {hash_prefix}")
    test_controller.add(
    BiometriaCreate(
        id_usuario=3,
        template_huella=template_b64,
        huella_hash=hash_prefix
    )
)
    # 🔹 Enviamos la misma plantilla simulando el lector
    response = client.post("/acceso/huella", params={"dispositivo_id": "SENSOR123","vector": template_b64,"fecha": "2025-10-19T12:00:00"}, headers=headers)
    assert response.status_code == 200

    data = response.json()
    print(data)
    assert data["status"] is True


def test_acceso_huella_fallido():
    """
    Simula una huella que no coincide con ninguna almacenada.
    """
    # 🔹 Simulamos una huella registrada
    template_b64, hash_prefix = generar_template_y_hash(b"plantilla_simulada_valida")
    test_controller.add(
    BiometriaCreate(
        id_usuario=3,
        template_huella=template_b64,
        huella_hash=hash_prefix
    )
)

    # 🔹 Enviamos una huella diferente
    template_falsa = base64.b64encode(b"huella_incorrecta").decode()
    response = client.post("/acceso/huella", params={"dispositivo_id": "SENSOR123","vector": template_falsa,"fecha": "2025-10-19T12:00:00",}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(f"Respuesta HUELLAS fallida: {data}")
    assert data["status"] is False
def test_acceso_camara_exitoso():
    response = client.post("/acceso/camara", params={"vector": "ROSTRO_OK"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is True
    assert "cámara" in data["mensaje"].lower()

def test_acceso_camara_fallido():
    response = client.post("/acceso/camara", params={"vector": "FAIL"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is False