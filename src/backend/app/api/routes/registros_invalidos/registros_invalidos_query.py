import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.registros_invalidos import RegistrosInvalidosOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/registros_invalidos", tags=["registros_invalidos"])

@app.get("/all")
async def get_all_registros_invalidos():
    items = controller.read_all(RegistrosInvalidosOut)
    logger.info(f"[GET /all] Número de RegistrosInvalidos encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_registros_invalidos_by_id(request: Request, id_invalido: int = Query(...)):
    unit = controller.get_by_id(RegistrosInvalidosOut, id_invalido)
    if unit:
        return unit.model_dump()
    else:
        return None
