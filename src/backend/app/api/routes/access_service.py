from fastapi import APIRouter
from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.logic.access_logic import AccessService
from backend.app.logic.verification import VerificadorHuella, VerificadorCamara, VerificadorRFID

app = APIRouter(tags=["Acceso"])

@app.post("/acceso/rfid", response_model=AccesoResponse)
async def solicitar_acceso(rfid_tag: str):
    """
    Endpoint para solicitar acceso con un medio específico.
    - medio: "rfid"
    - rfid_tag: Código RFID del usuario
    """
    request = AccesoRequest(medio="rfid", data={"rfid_tag": rfid_tag})
    return AccessService.solicitar_acceso(request)
@app.post("/acceso/huella", response_model=AccesoResponse)
async def solicitar_acceso(vector: str):
    """
    Endpoint para solicitar acceso con un medio específico.
    - medio: "huella"
    - vector: vector de huella del usuario
    """
    request = AccesoRequest(medio="huella", data={"vector": vector})
    return AccessService.solicitar_acceso(request)
@app.post("/acceso/camara", response_model=AccesoResponse)
async def solicitar_acceso(vector: str):
    """
    Endpoint para solicitar acceso con un medio específico.
    - medio: "camara"
    - vector: vector de rostro del usuario
    """
    request = AccesoRequest(medio="camara", data={"vector": vector})
    return AccessService.solicitar_acceso(request)