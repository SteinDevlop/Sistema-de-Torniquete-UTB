import logging
from fastapi import Form, HTTPException, APIRouter
from app.models.biometria import BiometriaCreate, BiometriaOut
from app.logic.universal_controller_instance import universal_controller as controller
from app.logic.face_recognition import get_face_recognition_system
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
    imagen_facial: str = Form(None),  # Imagen en base64 para extraer embedding real
    rfid_tag: str = Form(None),
    fecha_actualizacion: str = Form(None),
    template_huella: str = Form(None),
):
    """
    Crea un registro biométrico.
    
    Parámetros:
        - id_usuario: ID del usuario en la tabla Usuarios
        - imagen_facial: Imagen en base64 (RECOMENDADO - extrae embedding con DeepFace)
        - vector_facial: Embedding pre-calculado en base64 (solo para compatibilidad)
        - template_huella: Template de huella dactilar en base64
        - rfid_tag: Código RFID del usuario
        - fecha_actualizacion: Fecha de actualización (opcional)
    
    Retorna:
        - success: True/False
        - data: Registro biométrico creado
        - message: Mensaje descriptivo
    """
    try:
        huella_hash = None
        facial_hash = None
        embedding_final = None

        # ========================================
        # 🔹 PROCESAMIENTO DE DATOS FACIALES
        # ========================================
        
        # Opción 1: Si se proporciona una imagen, extraer embedding real con DeepFace (RECOMENDADO)
        if imagen_facial and not vector_facial:
            logger.info("=" * 80)
            logger.info("📸 REGISTRO FACIAL: Extrayendo embedding desde imagen con DeepFace")
            logger.info("=" * 80)
            
            face_system = get_face_recognition_system()
            
            # Validar calidad de la imagen primero
            es_valida, mensaje = face_system.validar_imagen_base64(imagen_facial)
            if not es_valida:
                logger.warning(f"❌ Imagen rechazada: {mensaje}")
                raise HTTPException(status_code=400, detail=mensaje)
            
            logger.info(f"✅ Imagen validada: {mensaje}")
            
            # Extraer embedding
            embedding_array = face_system.extraer_embedding_desde_base64(imagen_facial)
            
            if embedding_array is None:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo extraer el embedding facial. Verifica que la imagen muestre claramente un rostro."
                )
            
            # Convertir embedding a base64 para almacenar
            embedding_final = face_system.embedding_a_base64(embedding_array)
            
            logger.info(f"✅ Embedding procesado y serializado correctamente")
            logger.info(f"   • Dimensión: {embedding_array.shape[0]}")
            logger.info(f"   • Tipo: {embedding_array.dtype}")
            logger.info(f"   • Base64 length: {len(embedding_final)} caracteres")
            
            # Verificar que no se haya duplicado (debe ser ~2730 caracteres para 512 floats)
            expected_length = (512 * 4 * 4) // 3  # 512 floats * 4 bytes * 4/3 (base64)
            if abs(len(embedding_final) - expected_length) > 100:
                logger.warning(f"⚠️  Longitud inesperada de base64: {len(embedding_final)} (esperado ~{expected_length})")
        
        # Opción 2: Si se proporciona vector_facial directamente (modo compatibilidad)
        elif vector_facial:
            embedding_final = vector_facial
            logger.info("📦 Usando vector_facial proporcionado directamente")
            logger.info(f"   • Base64 length: {len(embedding_final)} caracteres")
        
        # ========================================
        # 🔹 PROCESAMIENTO DE HUELLA DACTILAR
        # ========================================
        
        if template_huella:
            padded_template = template_huella + '=' * (-len(template_huella) % 4)
            huella_hash = hashlib.sha256(base64.b64decode(padded_template)).hexdigest()[:8]
            logger.info(f"🔐 Hash de huella calculado: {huella_hash}")

        # ========================================
        # 🔹 CÁLCULO DE HASH FACIAL
        # ========================================
        
        if embedding_final:
            try:
                face_system = get_face_recognition_system()
                
                # Decodificar embedding desde base64
                embedding = face_system.base64_a_embedding(embedding_final)
                
                if embedding is not None:
                    # Normalizar y calcular hash
                    embedding_norm = embedding / (np.linalg.norm(embedding) + 1e-8)
                    facial_hash = hashlib.sha256(embedding_norm.tobytes()).hexdigest()[:8]
                    logger.info(f"🔐 Hash facial calculado: {facial_hash}")
                else:
                    logger.warning("⚠️  No se pudo decodificar embedding para calcular hash")
                    
            except Exception as e:
                logger.warning(f"⚠️  Error calculando facial_hash: {e}")

        # ========================================
        # 🔹 CREACIÓN DEL REGISTRO
        # ========================================
        
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
        
        logger.info("=" * 80)
        logger.info(f"✅ REGISTRO BIOMÉTRICO CREADO EXITOSAMENTE")
        logger.info(f"   • Usuario ID: {id_usuario}")
        logger.info(f"   • Tiene vector facial: {embedding_final is not None}")
        logger.info(f"   • Tiene huella: {template_huella is not None}")
        logger.info(f"   • Tiene RFID: {rfid_tag is not None}")
        logger.info("=" * 80)

        return {
            "operation": "create",
            "success": True,
            "data": BiometriaOut(**item.model_dump()).model_dump(),
            "message": "✅ Registro biométrico creado correctamente con reconocimiento facial DeepFace.",
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error interno en /biometria/create: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


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
