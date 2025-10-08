from typing import Optional
from pydantic import BaseModel

class UsuariosCreate(BaseModel):
    __entity_name__ = "Usuarios"
    id_usuario: Optional[int] = None
    nombre_completo: Optional[str] = None
    cargo: Optional[str] = None
    estado: Optional[bool] = None
    fecha_registro: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_usuario": "INT",
            "nombre_completo": "STR",
            "cargo": "STR",
            "estado": "BOOL",
            "fecha_registro": "STR"
        }

class UsuariosOut(UsuariosCreate):
    __entity_name__ = "Usuarios"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
