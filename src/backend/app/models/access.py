from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

# Enum de medios soportados
# Enum de medios
class MedioAcceso(str, Enum):
    camara = "camara"
    huella = "huella"
    rfid = "rfid"

# Request genérico
class AccesoRequest(BaseModel):
    medio: MedioAcceso
    data: Dict[str, Any]   # Solo un medio a la vez

# Response estandarizada
class AccesoResponse(BaseModel):
    status: Optional[bool] = None
    medio: MedioAcceso
    usuario_id: Optional[int] = None
    mensaje: Optional[str] = None
    score: Optional[float] = None  # Score de similitud (para reconocimiento facial)
    detalles_verificacion: Optional[Dict[str, Any]] = None  # Detalles adicionales de la verificación