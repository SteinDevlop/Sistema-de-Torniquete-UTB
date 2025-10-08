import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.biometria import BiometriaCreate, BiometriaOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/biometria", tags=["biometria"])

@app.post("/create")
async def create_biometria(
    id_usuario: int = Form(...),
    vector_facial: str = Form(...),
    huella_hash: str = Form(...),
    rfid_tag: str = Form(...),
    fecha_actualizacion: str = Form(...)
):
    try:
        item = BiometriaCreate(id_usuario=id_usuario, vector_facial=vector_facial, huella_hash=huella_hash, rfid_tag=rfid_tag, fecha_actualizacion=fecha_actualizacion)
        controller.add(item)
        logger.info(f"[POST /create] Biometria creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": "Biometria created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_biometria(
    id_biometria: int = Form(...),
    id_usuario: int = Form(...),
    vector_facial: str = Form(...),
    huella_hash: str = Form(...),
    rfid_tag: str = Form(...),
    fecha_actualizacion: str = Form(...)
):
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria not found")
        item = BiometriaCreate(id_biometria=id_biometria, id_usuario=id_usuario, vector_facial=vector_facial, huella_hash=huella_hash, rfid_tag=rfid_tag, fecha_actualizacion=fecha_actualizacion)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": f"Biometria { id_biometria } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_biometria(id_biometria: int = Form(...)):
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"Biometria { id_biometria } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
