import logging
from fastapi import Query, Request, APIRouter, HTTPException
from backend.app.models.biometria import BiometriaOut
from backend.app.logic.universal_controller_instance import universal_controller as controller

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/biometria", tags=["biometria"])

@app.get("/debug/{id_usuario}")
async def debug_biometria(id_usuario: int):
    """
    Endpoint de DEBUG para ver exactamente qué datos tiene un usuario.
    """
    try:
        registro = controller.get_by_field("Biometria", "id_usuario", id_usuario)
        
        if not registro:
            return {
                "success": False,
                "message": f"No se encontró registro para usuario {id_usuario}"
            }
        
        # Mostrar información detallada
        debug_info = {
            "id_biometria": registro.get("id_biometria"),
            "id_usuario": registro.get("id_usuario"),
            "tiene_vector_facial": registro.get("vector_facial") is not None,
            "longitud_vector_facial": len(registro.get("vector_facial", "")) if registro.get("vector_facial") else 0,
            "facial_hash": registro.get("facial_hash"),
            "tiene_template_huella": registro.get("template_huella") is not None,
            "huella_hash": registro.get("huella_hash"),
            "rfid_tag": registro.get("rfid_tag"),
            "fecha_actualizacion": registro.get("fecha_actualizacion"),
        }
        
        logger.info(f"DEBUG Usuario {id_usuario}: {debug_info}")
        
        return {
            "success": True,
            "data": debug_info,
            "registro_completo": registro
        }
        
    except Exception as e:
        logger.error(f"Error en debug: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/all")
async def get_all_biometria():
    items = controller.read_all(BiometriaOut)
    logger.info(f"[GET /all] Número de Biometria encontrados: {len(items)}")
    return {
        "success": True,
        "data": items
    }

@app.get("/by_id")
def get_biometria_by_id(request: Request, id_biometria: int = Query(...)):
    unit = controller.get_by_id(BiometriaOut, id_biometria)
    if unit:
        return unit.model_dump()
    else:
        return None
