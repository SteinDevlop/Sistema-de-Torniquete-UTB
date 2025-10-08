from typing import Optional
from pydantic import BaseModel

class BiometriaCreate(BaseModel):
    __entity_name__ = "Biometria"
    id_biometria: Optional[int] = None
    id_usuario: Optional[int] = None
    vector_facial: Optional[str] = None
    huella_hash: Optional[str] = None
    rfid_tag: Optional[str] = None
    fecha_actualizacion: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def get_fields(cls) -> dict:
        return {
            "id_biometria": "INT",
            "id_usuario": "INT",
            "vector_facial": "STR",
            "huella_hash": "STR",
            "rfid_tag": "STR",
            "fecha_actualizacion": "STR"
        }

class BiometriaOut(BiometriaCreate):
    __entity_name__ = "Biometria"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
