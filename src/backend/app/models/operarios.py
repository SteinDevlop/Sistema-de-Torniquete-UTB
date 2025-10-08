from typing import Optional
from pydantic import BaseModel

class OperariosCreate(BaseModel):
    __entity_name__ = "Operarios"
    id_operario: Optional[int] = None
    nombre_operario: Optional[str] = None
    usuario_sistema: Optional[str] = None
    contraseña_hash: Optional[str] = None
    activo: Optional[bool] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_operario": "INT",
            "nombre_operario": "STR",
            "usuario_sistema": "STR",
            "contraseña_hash": "STR",
            "activo": "BOOL"
        }

class OperariosOut(OperariosCreate):
    __entity_name__ = "Operarios"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
