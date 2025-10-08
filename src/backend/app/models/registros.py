from typing import Optional
from pydantic import BaseModel

class RegistrosCreate(BaseModel):
    __entity_name__ = "Registros"
    id_registro: Optional[int] = None
    id_usuario: Optional[int] = None
    id_torniquete: Optional[int] = None
    id_operario: Optional[int] = None
    fecha_hora: Optional[str] = None
    tipo_acceso: Optional[str] = None
    imagen_capturada: Optional[str] = None
    resultado: Optional[bool] = None
    observaciones: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_registro": "INT",
            "id_usuario": "INT",
            "id_torniquete": "INT",
            "id_operario": "INT",
            "fecha_hora": "STR",
            "tipo_acceso": "STR",
            "imagen_capturada": "STR",
            "resultado": "BOOL",
            "observaciones": "STR"
        }

class RegistrosOut(RegistrosCreate):
    __entity_name__ = "Registros"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
