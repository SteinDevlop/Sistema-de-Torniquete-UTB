from typing import Optional
from pydantic import BaseModel

class TorniquetesCreate(BaseModel):
    __entity_name__ = "Torniquetes"
    id_torniquete: Optional[int] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    estado: Optional[bool] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_torniquete": "INT",
            "tipo": "STR",
            "ubicacion": "STR",
            "estado": "BOOL"
        }

class TorniquetesOut(TorniquetesCreate):
    __entity_name__ = "Torniquetes"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
