import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.biometria import BiometriaCreate, BiometriaOut
from backend.app.logic.universal_controller_instance import universal_controller as controller
import hashlib
import base64
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/biometria", tags=["biometria"])


@app.post("/create")
async def create_biometria(
    id_usuario: int = Form(...),
    vector_facial: str = Form(None),
    rfid_tag: str = Form(None),
    fecha_actualizacion: str = Form(None),
    template_huella: str = Form(...),
):
    """
    Crea un registro biométrico con huella codificada en Base64.
    Genera hash parcial para búsqueda rápida.
    """
    try:
        # 🔹 Calculamos hash parcial a partir del template (Base64 codificado)
        huella_hash = hashlib.sha256(base64.b64decode(template_huella)).hexdigest()[:8]

        item = BiometriaCreate(
            id_usuario=id_usuario,
            vector_facial=vector_facial,
            huella_hash=huella_hash,
            rfid_tag=rfid_tag,
            fecha_actualizacion=fecha_actualizacion,
            template_huella=template_huella,
        )

        controller.add(item)
        logger.info(f"[POST /create] Biometria creada exitosamente: {item}")

        return {
            "operation": "create",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": "Biometria creada correctamente.",
        }

    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update")
async def update_biometria(
    id_biometria: int = Form(...),
    id_usuario: int = Form(...),
    vector_facial: str = Form(None),
    rfid_tag: str = Form(None),
    fecha_actualizacion: str = Form(None),
    template_huella: str = Form(...),
):
    """
    Actualiza un registro biométrico existente.
    """
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria no encontrada")

        huella_hash = hashlib.sha256(base64.b64decode(template_huella)).hexdigest()[:8]

        item = BiometriaCreate(
            id_biometria=id_biometria,
            id_usuario=id_usuario,
            vector_facial=vector_facial,
            huella_hash=huella_hash,
            rfid_tag=rfid_tag,
            fecha_actualizacion=fecha_actualizacion,
            template_huella=template_huella,
        )

        controller.update(item)

        return {
            "operation": "update",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": f"Biometria {id_biometria} actualizada correctamente.",
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete")
async def delete_biometria(id_biometria: int = Form(...)):
    """
    Elimina un registro biométrico por ID.
    """
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria no encontrada")

        controller.delete(existing)

        return {
            "operation": "delete",
            "success": True,
            "message": f"Biometria {id_biometria} eliminada correctamente.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
