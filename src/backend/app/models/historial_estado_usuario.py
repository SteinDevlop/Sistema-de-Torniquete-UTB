from typing import Optional
from pydantic import BaseModel

class HistorialEstadoUsuarioCreate(BaseModel):
    __entity_name__ = "HistorialEstadoUsuario"
    id_historial: Optional[int] = None
    id_usuario: Optional[int] = None
    estado_anterior: Optional[bool] = None
    estado_nuevo: Optional[bool] = None
    fecha_cambio: Optional[str] = None
    motivo: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_historial": "INT",
            "id_usuario": "INT",
            "estado_anterior": "BOOL",
            "estado_nuevo": "BOOL",
            "fecha_cambio": "STR",
            "motivo": "STR"
        }

class HistorialEstadoUsuarioOut(HistorialEstadoUsuarioCreate):
    __entity_name__ = "HistorialEstadoUsuario"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
