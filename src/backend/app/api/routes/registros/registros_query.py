import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.registros import RegistrosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/registros", tags=["registros"])

@app.get("/all")
async def get_all_registros():
    items = controller.read_all(RegistrosOut)
    logger.info(f"[GET /all] Número de Registros encontrados: {len(items)}")
    return {"success": True, "data": items}

@app.get("/by_id")
def get_registros_by_id(request: Request, id_registro: int = Query(...)):
    unit = controller.get_by_id(RegistrosOut, id_registro)
    if unit:
        return unit.model_dump()
    else:
        return None
