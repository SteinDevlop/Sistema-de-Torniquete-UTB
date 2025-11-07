import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.operarios import OperariosCreate, OperariosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/operarios", tags=["operarios"])

@app.post("/create")
async def create_operarios(
    nombre_operario: str = Form(...),
    usuario_sistema: str = Form(...),
    contraseña_hash: str = Form(...),
    activo: bool = Form(...)
):
    try:
        item = OperariosCreate(nombre_operario=nombre_operario, usuario_sistema=usuario_sistema, contraseña_hash=contraseña_hash, activo=activo)
        controller.add(item)
        logger.info(f"[POST /create] Operarios creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": OperariosOut(**item.model_dump()).model_dump(),
            "message": "Operarios created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_operarios(
    id_operario: int = Form(...),
    nombre_operario: str = Form(...),
    usuario_sistema: str = Form(...),
    contraseña_hash: str = Form(...),
    activo: bool = Form(...)
):
    try:
        existing = controller.get_by_id(OperariosOut, id_operario)
        if not existing:
            raise HTTPException(status_code=404, detail="Operarios not found")
        item = OperariosCreate(id_operario=id_operario, nombre_operario=nombre_operario, usuario_sistema=usuario_sistema, contraseña_hash=contraseña_hash, activo=activo)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": OperariosOut(**item.model_dump()).model_dump(),
            "message": f"Operarios { id_operario } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_operarios(id_operario: int = Form(...)):
    try:
        existing = controller.get_by_id(OperariosOut, id_operario)
        if not existing:
            raise HTTPException(status_code=404, detail="Operarios not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"Operarios { id_operario } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
