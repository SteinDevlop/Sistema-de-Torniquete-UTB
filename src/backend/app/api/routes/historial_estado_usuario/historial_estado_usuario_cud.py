import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.historial_estado_usuario import HistorialEstadoUsuarioCreate, HistorialEstadoUsuarioOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/historial_estado_usuario", tags=["historial_estado_usuario"])

@app.post("/create")
async def create_historial_estado_usuario(
    id_usuario: int = Form(...),
    estado_anterior: bool = Form(...),
    estado_nuevo: bool = Form(...),
    fecha_cambio: str = Form(...),
    motivo: str = Form(...)
):
    try:
        item = HistorialEstadoUsuarioCreate(id_usuario=id_usuario, estado_anterior=estado_anterior, estado_nuevo=estado_nuevo, fecha_cambio=fecha_cambio, motivo=motivo)
        controller.add(item)
        logger.info(f"[POST /create] HistorialEstadoUsuario creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": HistorialEstadoUsuarioOut(**item.model_dump()).model_dump(),
            "message": "HistorialEstadoUsuario created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_historial_estado_usuario(
    id_historial: int = Form(...),
    id_usuario: int = Form(...),
    estado_anterior: bool = Form(...),
    estado_nuevo: bool = Form(...),
    fecha_cambio: str = Form(...),
    motivo: str = Form(...)
):
    try:
        existing = controller.get_by_id(HistorialEstadoUsuarioOut, id_historial)
        if not existing:
            raise HTTPException(status_code=404, detail="HistorialEstadoUsuario not found")
        item = HistorialEstadoUsuarioCreate(id_historial=id_historial, id_usuario=id_usuario, estado_anterior=estado_anterior, estado_nuevo=estado_nuevo, fecha_cambio=fecha_cambio, motivo=motivo)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": HistorialEstadoUsuarioOut(**item.model_dump()).model_dump(),
            "message": f"HistorialEstadoUsuario { id_historial } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_historial_estado_usuario(id_historial: int = Form(...)):
    try:
        existing = controller.get_by_id(HistorialEstadoUsuarioOut, id_historial)
        if not existing:
            raise HTTPException(status_code=404, detail="HistorialEstadoUsuario not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"HistorialEstadoUsuario { id_historial } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
