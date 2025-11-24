"""
Servicio de detección de liveness en tiempo real.

Recibe múltiples frames del cliente y analiza si corresponden a una persona real.
"""

import logging
from fastapi import APIRouter, Form, HTTPException
from typing import Optional
import base64
import numpy as np
import cv2
from backend.app.logic.liveness_detection import get_liveness_detector
from backend.app.logic.face_recognition import get_face_recognition_system

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = APIRouter(prefix="/liveness", tags=["liveness"])


# Almacenar sesiones de liveness (en memoria, para desarrollo)
# En producción, usar Redis o similar
liveness_sessions = {}


@app.post("/start")
async def start_liveness_session(session_id: str = Form(...)):
    """
    Inicia una nueva sesión de detección de liveness.
    
    El cliente debe llamar a este endpoint antes de enviar frames.
    """
    try:
        detector = get_liveness_detector()
        detector.reset()
        
        liveness_sessions[session_id] = {
            "frames_received": 0,
            "detector": detector
        }
        
        logger.info(f"🎬 Nueva sesión de liveness iniciada: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Sesión de liveness iniciada. Envíe frames para análisis.",
            "min_frames": 3  # Valor fijo, no del detector
        }
        
    except Exception as e:
        logger.exception(f"Error iniciando sesión de liveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-frame")
async def add_liveness_frame(
    session_id: str = Form(...),
    frame_b64: str = Form(...)
):
    """
    Agrega un frame a la sesión de liveness para análisis.
    
    Args:
        session_id: ID de la sesión activa
        frame_b64: Frame de video codificado en base64 (JPEG)
        
    Returns:
        Estado actual del análisis (suficientes frames o no)
    """
    try:
        # Verificar que la sesión existe
        if session_id not in liveness_sessions:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada. Debe llamar a /liveness/start primero."
            )
        
        session = liveness_sessions[session_id]
        detector = session["detector"]
        
        # Decodificar frame
        img_bytes = base64.b64decode(frame_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="No se pudo decodificar el frame")
        
        # NO recortar el rostro - usar frame completo para evitar problemas de tamaño
        # en el análisis de flujo óptico
        face_bbox = None
        
        # Agregar frame al detector
        has_enough_frames = detector.add_frame(frame, face_bbox)
        
        session["frames_received"] += 1
        
        logger.debug(f"Frame {session['frames_received']} agregado a sesión {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "frames_received": session["frames_received"],
            "min_frames": detector.min_frames,
            "ready_for_analysis": has_enough_frames
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error agregando frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_liveness(
    session_id: str = Form(...),
    mode: str = Form("active") # 'active' or 'passive'
):
    """
    Analiza los frames recibidos y retorna el score de liveness.
    """
    try:
        # Verificar que la sesión existe
        if session_id not in liveness_sessions:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada. Debe llamar a /liveness/start primero."
            )
        
        session = liveness_sessions[session_id]
        detector = session["detector"]
        
        # Obtener score de liveness según el modo
        liveness_result = detector.get_liveness_score(mode=mode)
        
        if liveness_result is None:
            return {
                "success": False,
                "message": f"Insuficientes frames para análisis.",
                "frames_received": session["frames_received"]
            }
        
        # Limpiar sesión
        del liveness_sessions[session_id]
        
        logger.info(f"✅ Análisis de liveness ({mode}) completado: {liveness_result.confidence:.3f}")
        
        return {
            "success": True,
            "is_live": bool(liveness_result.is_live),
            "confidence": round(float(liveness_result.confidence), 4),
            "mode": mode,
            "details": liveness_result.details,
            "message": "✅ Persona real detectada" if liveness_result.is_live else "❌ Prueba de vida fallida"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error analizando liveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_liveness_session(session_id: str = Form(...)):
    """Resetea una sesión de liveness existente"""
    try:
        if session_id in liveness_sessions:
            session = liveness_sessions[session_id]
            session["detector"].reset()
            session["frames_received"] = 0
            logger.info(f"🔄 Sesión {session_id} reseteada")
            
        return {
            "success": True,
            "session_id": session_id,
            "message": "Sesión reseteada"
        }
        
    except Exception as e:
        logger.exception(f"Error reseteando sesión: {e}")
        raise HTTPException(status_code=500, detail=str(e))
