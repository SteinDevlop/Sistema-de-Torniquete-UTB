import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.registros_invalidos import RegistrosInvalidosCreate, RegistrosInvalidosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/registros_invalidos", tags=["registros_invalidos"])

@app.post("/create")
async def create_registros_invalidos(
    id_registro: int = Form(...),
    motivo: str = Form(...),
    fecha_invalido: str = Form(...)
):
    try:
        item = RegistrosInvalidosCreate(id_registro=id_registro, motivo=motivo, fecha_invalido=fecha_invalido)
        controller.add(item)
        logger.info(f"[POST /create] RegistrosInvalidos creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": RegistrosInvalidosOut(**item.model_dump()).model_dump(),
            "message": "RegistrosInvalidos created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_registros_invalidos(
    id_invalido: int = Form(...),
    id_registro: int = Form(...),
    motivo: str = Form(...),
    fecha_invalido: str = Form(...)
):
    try:
        existing = controller.get_by_id(RegistrosInvalidosOut, id_invalido)
        if not existing:
            raise HTTPException(status_code=404, detail="RegistrosInvalidos not found")
        item = RegistrosInvalidosCreate(id_invalido=id_invalido, id_registro=id_registro, motivo=motivo, fecha_invalido=fecha_invalido)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": RegistrosInvalidosOut(**item.model_dump()).model_dump(),
            "message": f"RegistrosInvalidos { id_invalido } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_registros_invalidos(id_invalido: int = Form(...)):
    try:
        existing = controller.get_by_id(RegistrosInvalidosOut, id_invalido)
        if not existing:
            raise HTTPException(status_code=404, detail="RegistrosInvalidos not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"RegistrosInvalidos { id_invalido } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
