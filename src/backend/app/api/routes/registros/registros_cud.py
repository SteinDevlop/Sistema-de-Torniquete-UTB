import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.registros import RegistrosCreate, RegistrosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/registros", tags=["registros"])

@app.post("/create")
async def create_registros(
    id_usuario: int = Form(...),
    id_torniquete: int = Form(...),
    id_operario: int = Form(...),
    fecha_hora: str = Form(...),
    tipo_acceso: str = Form(...),
    imagen_capturada: str = Form(...),
    resultado: bool = Form(...),
    observaciones: str = Form(...)
):
    try:
        item = RegistrosCreate(id_usuario=id_usuario, id_torniquete=id_torniquete, id_operario=id_operario, fecha_hora=fecha_hora, tipo_acceso=tipo_acceso, imagen_capturada=imagen_capturada, resultado=resultado, observaciones=observaciones)
        controller.add(item)
        logger.info(f"[POST /create] Registros creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": RegistrosOut(**item.model_dump()).model_dump(),
            "message": "Registros created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_registros(
    id_registro: int = Form(...),
    id_usuario: int = Form(...),
    id_torniquete: int = Form(...),
    id_operario: int = Form(...),
    fecha_hora: str = Form(...),
    tipo_acceso: str = Form(...),
    imagen_capturada: str = Form(...),
    resultado: bool = Form(...),
    observaciones: str = Form(...)
):
    try:
        existing = controller.get_by_id(RegistrosOut, id_registro)
        if not existing:
            raise HTTPException(status_code=404, detail="Registros not found")
        item = RegistrosCreate(id_registro=id_registro, id_usuario=id_usuario, id_torniquete=id_torniquete, id_operario=id_operario, fecha_hora=fecha_hora, tipo_acceso=tipo_acceso, imagen_capturada=imagen_capturada, resultado=resultado, observaciones=observaciones)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": RegistrosOut(**item.model_dump()).model_dump(),
            "message": f"Registros { id_registro } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_registros(id_registro: int = Form(...)):
    try:
        existing = controller.get_by_id(RegistrosOut, id_registro)
        if not existing:
            raise HTTPException(status_code=404, detail="Registros not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"Registros { id_registro } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
