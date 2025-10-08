import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.torniquetes import TorniquetesOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/torniquetes", tags=["torniquetes"])

@app.get("/all")
async def get_all_torniquetes():
    items = controller.read_all(TorniquetesOut)
    logger.info(f"[GET /all] Número de Torniquetes encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_torniquetes_by_id(request: Request, id_torniquete: int = Query(...)):
    unit = controller.get_by_id(TorniquetesOut, id_torniquete)
    if unit:
        return unit.model_dump()
    else:
        return None
