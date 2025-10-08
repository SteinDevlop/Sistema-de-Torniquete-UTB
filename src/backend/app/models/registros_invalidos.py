from typing import Optional
from pydantic import BaseModel

class RegistrosInvalidosCreate(BaseModel):
    __entity_name__ = "RegistrosInvalidos"
    id_invalido: Optional[int] = None
    id_registro: Optional[int] = None
    motivo: Optional[str] = None
    fecha_invalido: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_invalido": "INT",
            "id_registro": "INT",
            "motivo": "STR",
            "fecha_invalido": "STR"
        }

class RegistrosInvalidosOut(RegistrosInvalidosCreate):
    __entity_name__ = "RegistrosInvalidos"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
