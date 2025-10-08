import logging
from fastapi import Query, Request, APIRouter
from backend.app.models.biometria import BiometriaOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/biometria", tags=["biometria"])

@app.get("/all")
async def get_all_biometria():
    items = controller.read_all(BiometriaOut)
    logger.info(f"[GET /all] Número de Biometria encontrados: {len(items)}")
    return items

@app.get("/by_id")
def get_biometria_by_id(request: Request, id_biometria: int = Query(...)):
    unit = controller.get_by_id(BiometriaOut, id_biometria)
    if unit:
        return unit.model_dump()
    else:
        return None
