from fastapi import APIRouter
from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.logic.access_logic import AccessService

app = APIRouter(tags=["Acceso"])

@app.post("/acceso", response_model=AccesoResponse)
def solicitar_acceso(request: AccesoRequest):
    """
    Endpoint para solicitar acceso con un medio específico.
    - medio: "rfid", "huella" o "camara"
    - data: información asociada al medio
    """
    return AccessService.solicitar_acceso(request)