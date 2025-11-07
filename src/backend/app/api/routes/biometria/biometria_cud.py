import logging
from fastapi import Form, HTTPException, APIRouter
from backend.app.models.biometria import BiometriaCreate, BiometriaOut
from backend.app.logic.universal_controller_instance import universal_controller as controller
from backend.app.logic.face_recognition import get_face_recognition_system
import hashlib
import base64
import numpy as np
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/biometria", tags=["biometria"])


@app.post("/create")
async def create_biometria(
    id_usuario: int = Form(...),
    vector_facial: str = Form(None),
    imagen_facial: str = Form(None),  # Nueva: imagen en base64 para extraer embedding real
    rfid_tag: str = Form(None),
    fecha_actualizacion: str = Form(None),
    template_huella: str = Form(None),
):
    """
    Crea un registro biométrico.
    - Si se proporciona imagen_facial (base64), extrae el embedding real con DeepFace
    - Si se proporciona vector_facial directamente, lo usa (para compatibilidad)
    - Si se proporciona template_huella, genera huella_hash
    - Si se proporciona rfid_tag, lo almacena
    """
    try:
        huella_hash = None
        facial_hash = None
        embedding_final = None

        # 🔹 Si se proporciona una imagen, extraer embedding real con DeepFace
        if imagen_facial and not vector_facial:
            logger.info("Extrayendo embedding facial desde imagen con DeepFace...")
            face_system = get_face_recognition_system()
            embedding_array = face_system.extraer_embedding_desde_base64(imagen_facial)
            
            if embedding_array is None:
                raise HTTPException(
                    status_code=400, 
                    detail="No se pudo detectar un rostro en la imagen. Asegúrate de que la foto muestre claramente tu cara."
                )
            
            logger.info(f"✅ Embedding extraído exitosamente. Shape original: {embedding_array.shape}, dtype: {embedding_array.dtype}")
            logger.info(f"   Primeros 5 valores: {embedding_array[:5]}")
            
            # 🔧 CRÍTICO: Convertir a float32 para consistencia (DeepFace retorna float64)
            embedding_array = embedding_array.astype(np.float32)
            logger.info(f"   Convertido a dtype: {embedding_array.dtype}")
            
            # Convertir embedding a base64 para almacenar
            embedding_bytes = embedding_array.tobytes()
            logger.info(f"   Bytes generados: {len(embedding_bytes)} bytes ({embedding_array.shape[0]} floats * 4 bytes)")
            
            embedding_final = base64.b64encode(embedding_bytes).decode('utf-8')
            logger.info(f"   Base64 generado: {len(embedding_final)} caracteres")
            
            # VERIFICAR: decodificar para confirmar que no se duplicó
            test_decode = np.frombuffer(base64.b64decode(embedding_final), dtype=np.float32)
            logger.info(f"   ✅ VERIFICACIÓN: Shape después de decodificar = {test_decode.shape} (debe ser 512)")
        
        # 🔹 Si se proporciona vector_facial directamente (modo sintético/compatibilidad)
        elif vector_facial:
            embedding_final = vector_facial
            logger.info("Usando vector_facial proporcionado directamente")
        
        # 🔹 Calcular hash de huella si se proporciona
        if template_huella:
            padded_template = template_huella + '=' * (-len(template_huella) % 4)
            huella_hash = hashlib.sha256(base64.b64decode(padded_template)).hexdigest()[:8]
            logger.info(f"Hash de huella calculado: {huella_hash}")

        # 🔹 Calcular hash de vector facial si existe
        if embedding_final:
            try:
                # Intentar decodificar como Base64 (numpy serializado)
                try:
                    padded_vector = embedding_final + '=' * (-len(embedding_final) % 4)
                    vector_bytes = base64.b64decode(padded_vector)
                    embedding = np.frombuffer(vector_bytes, dtype=np.float32)
                except Exception:
                    # Si falla, asumir formato JSON
                    embedding = np.array(json.loads(embedding_final), dtype=np.float32)
                
                # Normalizar y calcular hash
                embedding_norm = embedding / (np.linalg.norm(embedding) + 1e-8)
                facial_hash = hashlib.sha256(embedding_norm.tobytes()).hexdigest()[:8]
                logger.info(f"Hash facial calculado: {facial_hash}")
            except Exception as e:
                logger.warning(f"Error calculando facial_hash: {e}")

        item = BiometriaCreate(
            id_usuario=id_usuario,
            vector_facial=embedding_final,
            facial_hash=facial_hash,
            huella_hash=huella_hash,
            rfid_tag=rfid_tag,
            fecha_actualizacion=fecha_actualizacion,
            template_huella=template_huella,
        )

        controller.add(item)
        logger.info(f"[POST /create] Biometria creada exitosamente para usuario {id_usuario}")

        return {
            "operation": "create",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": "Biometria creada correctamente con reconocimiento facial real.",
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"[POST /create] Error interno: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update")
async def update_biometria(
    id_biometria: int = Form(...),
    id_usuario: int = Form(...),
    vector_facial: str = Form(None),
    rfid_tag: str = Form(None),
    fecha_actualizacion: str = Form(None),
    template_huella: str = Form(None),
):
    """
    Actualiza un registro biométrico existente.
    """
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria no encontrada")

        huella_hash = None
        facial_hash = None

        # 🔹 Calcular hash de huella si se proporciona
        if template_huella:
            padded_template = template_huella + '=' * (-len(template_huella) % 4)
            huella_hash = hashlib.sha256(base64.b64decode(padded_template)).hexdigest()[:8]

        # 🔹 Calcular hash de vector facial si se proporciona
        if vector_facial:
            try:
                # Intentar decodificar como Base64 (numpy serializado)
                try:
                    padded_vector = vector_facial + '=' * (-len(vector_facial) % 4)
                    vector_bytes = base64.b64decode(padded_vector)
                    embedding = np.frombuffer(vector_bytes, dtype=np.float32)
                except Exception:
                    # Si falla, asumir formato JSON
                    embedding = np.array(json.loads(vector_facial), dtype=np.float32)
                # Normalizar y calcular hash
                embedding_norm = embedding / (np.linalg.norm(embedding) + 1e-8)
                facial_hash = hashlib.sha256(embedding_norm.tobytes()).hexdigest()[:8]
            except Exception as e:
                logger.warning(f"Error calculando facial_hash: {e}")

        item = BiometriaCreate(
            id_biometria=id_biometria,
            id_usuario=id_usuario,
            vector_facial=vector_facial,
            facial_hash=facial_hash,
            huella_hash=huella_hash,
            rfid_tag=rfid_tag,
            fecha_actualizacion=fecha_actualizacion,
            template_huella=template_huella,
        )

        controller.update(item)

        return {
            "operation": "update",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": f"Biometria {id_biometria} actualizada correctamente.",
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete")
async def delete_biometria(id_biometria: int = Form(...)):
    """
    Elimina un registro biométrico por ID.
    """
    try:
        existing = controller.get_by_id(BiometriaOut, id_biometria)
        if not existing:
            raise HTTPException(status_code=404, detail="Biometria no encontrada")

        controller.delete(existing)

        return {
            "operation": "delete",
            "success": True,
            "message": f"Biometria {id_biometria} eliminada correctamente.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
