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
async def solicitar_acceso(dispositivo_id: str, vector: str, fecha: str = None ):
    """
    Endpoint para solicitar acceso con un medio específico.
    - medio: "huella"
    - vector: template del usuario codigificado en base64
    - dispositivo_id: ID del dispositivo que captura la huella
    - fecha: Fecha y hora de la captura
    """
    request = AccesoRequest(medio="huella", data={"dispositivo_id":dispositivo_id,"vector": vector,"fecha":fecha})
    return AccessService.solicitar_acceso(request)
@app.post("/acceso/camara", response_model=AccesoResponse)
async def solicitar_acceso_camara(dispositivo_id: str, vector: str, fecha: str = None):
    """
    Endpoint para solicitar acceso mediante reconocimiento facial.
    
    Args:
        - dispositivo_id: ID del dispositivo ESP32 que captura la imagen
        - vector: Embedding facial de 128 dimensiones. Puede ser:
                  * String JSON: "[0.123, -0.456, 0.789, ...]"
                  * Base64 del array numpy serializado
        - fecha: Fecha y hora de la captura (opcional)
    
    Returns:
        AccesoResponse con status, usuario_id y mensaje
    
    Ejemplo de uso desde ESP32:
        POST /acceso/camara
        {
            "dispositivo_id": "ESP32_001",
            "vector": "[0.123, -0.456, 0.789, ...]",  // 128 valores decimales
            "fecha": "2025-10-19T10:30:00"
        }
    """
    request = AccesoRequest(
        medio="camara", 
        data={
            "dispositivo_id": dispositivo_id,
            "vector": vector,
            "fecha": fecha
        }
    )
    return AccessService.solicitar_acceso(request)