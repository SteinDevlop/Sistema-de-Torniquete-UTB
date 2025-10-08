import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.usuarios import UsuariosCreate, UsuariosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/usuarios", tags=["usuarios"])

@app.post("/create")
async def create_usuarios(
    nombre_completo: str = Form(...),
    cargo: str = Form(...),
    estado: bool = Form(...),
    fecha_registro: str = Form(...)
):
    try:
        item = UsuariosCreate(nombre_completo=nombre_completo, cargo=cargo, estado=estado, fecha_registro=fecha_registro)
        controller.add(item)
        logger.info(f"[POST /create] Usuarios creado exitosamente: {item}")
        return {
            "operation": "create",
            "success": True,
            "data": UsuariosOut(**item.model_dump()).model_dump(),
            "message": "Usuarios created successfully."
        }
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_usuarios(
    id_usuario: int = Form(...),
    nombre_completo: str = Form(...),
    cargo: str = Form(...),
    estado: bool = Form(...),
    fecha_registro: str = Form(...)
):
    try:
        existing = controller.get_by_id(UsuariosOut, id_usuario)
        if not existing:
            raise HTTPException(status_code=404, detail="Usuarios not found")
        item = UsuariosCreate(id_usuario=id_usuario, nombre_completo=nombre_completo, cargo=cargo, estado=estado, fecha_registro=fecha_registro)
        controller.update(item)
        return {
            "operation": "update",
            "success": True,
            "data": UsuariosOut(**item.model_dump()).model_dump(),
            "message": f"Usuarios { id_usuario } updated successfully."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete")
async def delete_usuarios(id_usuario: int = Form(...)):
    try:
        existing = controller.get_by_id(UsuariosOut, id_usuario)
        if not existing:
            raise HTTPException(status_code=404, detail="Usuarios not found")
        controller.delete(existing)
        return {"operation": "delete", "success": True, "message": f"Usuarios { id_usuario } deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
