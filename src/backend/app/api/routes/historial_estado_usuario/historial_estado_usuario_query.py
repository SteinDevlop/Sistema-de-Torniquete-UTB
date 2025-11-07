import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.historial_estado_usuario import HistorialEstadoUsuarioOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/historial_estado_usuario", tags=["historial_estado_usuario"])

@app.get("/all")
async def get_all_historial_estado_usuario():
    items = controller.read_all(HistorialEstadoUsuarioOut)
    logger.info(f"[GET /all] Número de HistorialEstadoUsuario encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_historial_estado_usuario_by_id(request: Request, id_historial: int = Query(...)):
    unit = controller.get_by_id(HistorialEstadoUsuarioOut, id_historial)
    if unit:
        return unit.model_dump()
    else:
        return None
