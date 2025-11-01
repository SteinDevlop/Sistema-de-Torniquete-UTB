from fastapi import APIRouter, Form
from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.logic.access_logic import AccessService
from backend.app.logic.verification import VerificadorHuella, VerificadorCamara, VerificadorRFID
from typing import Optional
import logging

logger = logging.getLogger(__name__)

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
from pydantic import BaseModel

class HuellaRequest(BaseModel):
    dispositivo_id: str
    vector: str
    fecha: str | None = None

@app.post("/acceso/huella", response_model=AccesoResponse)
async def solicitar_acceso(req: HuellaRequest):
    """
    Endpoint para solicitar acceso con huella dactilar.
    """
    request = AccesoRequest(
        medio="huella",
        data={
            "dispositivo_id": req.dispositivo_id,
            "vector": req.vector,
            "fecha": req.fecha
        }
    )
    return AccessService.solicitar_acceso(request)
@app.post("/acceso/camara", response_model=AccesoResponse)
async def solicitar_acceso_camara(
    dispositivo_id: Optional[str] = Form("web_liveness"), 
    vector: Optional[str] = Form(None), 
    imagen_facial: Optional[str] = Form(None),
    fecha: Optional[str] = Form(None)
):
    """
    Endpoint para solicitar acceso mediante reconocimiento facial.
    
    Args:
        - dispositivo_id: ID del dispositivo que captura la imagen
        - vector: Embedding facial (Base64 o JSON). Opcional si se envía imagen_facial
        - imagen_facial: Imagen en base64 para extraer embedding con DeepFace
        - fecha: Fecha y hora de la captura (opcional)
    
    Returns:
        AccesoResponse con status, usuario_id, mensaje y score de similitud
    
    Ejemplo 1 (con vector pre-calculado):
        POST /acceso/camara
        Form: dispositivo_id=web_test, vector=<base64>
        
    Ejemplo 2 (con imagen para extraer embedding real):
        POST /acceso/camara
        Form: dispositivo_id=web_test, imagen_facial=<base64_image>
    """
    logger.info(f"Solicitud de acceso facial recibida: dispositivo={dispositivo_id}, tiene_vector={vector is not None}, tiene_imagen={imagen_facial is not None}")
    
    request = AccesoRequest(
        medio="camara", 
        data={
            "dispositivo_id": dispositivo_id,
            "vector": vector,
            "imagen_facial": imagen_facial,
            "fecha": fecha
        }
    )
    
    response = AccessService.solicitar_acceso(request)
    logger.info(f"Respuesta de verificación facial: status={response.status}, usuario_id={response.usuario_id}, mensaje={response.mensaje}")
    
    return response