import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.operarios import OperariosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/operarios", tags=["operarios"])

@app.get("/all")
async def get_all_operarios():
    items = controller.read_all(OperariosOut)
    logger.info(f"[GET /all] Número de Operarios encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_operarios_by_id(request: Request, id_operario: int = Query(...)):
    unit = controller.get_by_id(OperariosOut, id_operario)
    if unit:
        return unit.model_dump()
    else:
        return None
