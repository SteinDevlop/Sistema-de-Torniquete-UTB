import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.torniquetes import TorniquetesCreate, TorniquetesOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/torniquetes", tags=["torniquetes"])

@app.post("/create")
async def create_torniquetes(
    tipo: str = Form(...),
    ubicacion: str = Form(...),
    estado: bool = Form(...)
):
    try:
        item = TorniquetesCreate(tipo=tipo, ubicacion=ubicacion, estado=estado)
        controller.add(item)
        logger.info(f"[POST /create] Torniquetes creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": TorniquetesOut(**item.model_dump()).model_dump(),
            "message": "Torniquetes created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_torniquetes(
    id_torniquete: int = Form(...),
    tipo: str = Form(...),
    ubicacion: str = Form(...),
    estado: bool = Form(...)
):
    try:
        existing = controller.get_by_id(TorniquetesOut, id_torniquete)
        if not existing:
            raise HTTPException(status_code=404, detail="Torniquetes not found")
        item = TorniquetesCreate(id_torniquete=id_torniquete, tipo=tipo, ubicacion=ubicacion, estado=estado)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": TorniquetesOut(**item.model_dump()).model_dump(),
            "message": f"Torniquetes { id_torniquete } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_torniquetes(id_torniquete: int = Form(...)):
    try:
        existing = controller.get_by_id(TorniquetesOut, id_torniquete)
        if not existing:
            raise HTTPException(status_code=404, detail="Torniquetes not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"Torniquetes { id_torniquete } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
