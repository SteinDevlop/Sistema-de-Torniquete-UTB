import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.usuarios import UsuariosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/usuarios", tags=["usuarios"])

@app.get("/all")
async def get_all_usuarios():
    items = controller.read_all(UsuariosOut)
    logger.info(f"[GET /all] Número de Usuarios encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_usuarios_by_id(request: Request, id_usuario: int = Query(...)):
    unit = controller.get_by_id(UsuariosOut, id_usuario)
    if unit:
        return unit.model_dump()
    else:
        return None
