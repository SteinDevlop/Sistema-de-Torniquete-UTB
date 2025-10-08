from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from backend.app.api.routes.access_service import app as access_router
from backend.app.logic.universal_controller_server import UniversalController
from backend.app.core.conf import headers
from backend.app.models.access import AccesoRequest, AccesoResponse

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


# ===============================
# MOCK: Reemplazar AccessService temporalmente
# ===============================
from backend.app.logic import access_logic

class MockAccessService:
    @staticmethod
    def solicitar_acceso(request: AccesoRequest) -> dict:
        if request.medio == "rfid" and request.data.get("rfid_tag") == "VALID123":
            return {"autorizado": True, "mensaje": "Acceso concedido (RFID)"}

# Inyectar mock
access_logic.AccessService = MockAccessService


# ===============================
# PRUEBAS: ENDPOINTS DE ACCESO
# ===============================

def test_acceso_rfid_exitoso():
    response = client.post("/acceso/rfid", params={"rfid_tag": "VALID123"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is True
    assert "RFID" in data["mensaje"]

def test_acceso_rfid_fallido():
    response = client.post("/acceso/rfid", params={"rfid_tag": "INVALID"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is False

def test_acceso_huella_exitoso():
    response = client.post("/acceso/huella", params={"vector": "HUELLA_OK"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is True
    assert "huella" in data["mensaje"].lower()

def test_acceso_huella_fallido():
    response = client.post("/acceso/huella", params={"vector": "FAIL"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["autorizado"] is False

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
