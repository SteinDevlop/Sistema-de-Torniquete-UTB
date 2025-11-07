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
from app.logic.liveness_detection import get_liveness_detector
from app.logic.face_recognition import get_face_recognition_system

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
            "min_frames": detector.min_frames
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
async def analyze_liveness(session_id: str = Form(...)):
    """
    Analiza los frames recibidos y retorna el score de liveness.
    
    Args:
        session_id: ID de la sesión activa
        
    Returns:
        Resultado del análisis de liveness
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
        
        # Obtener score de liveness
        liveness_result = detector.get_liveness_score()
        
        if liveness_result is None:
            return {
                "success": False,
                "message": f"Insuficientes frames para análisis. Recibidos: {session['frames_received']}, requeridos: {detector.min_frames}",
                "frames_received": session["frames_received"],
                "min_frames": detector.min_frames
            }
        
        # Limpiar sesión
        del liveness_sessions[session_id]
        
        logger.info(f"✅ Análisis de liveness completado para sesión {session_id}: {liveness_result.confidence:.3f}")
        
        # Convertir todos los valores a tipos nativos de Python para serialización JSON
        return {
            "success": True,
            "is_live": bool(liveness_result.is_live),
            "confidence": round(float(liveness_result.confidence), 4),
            "confidence_percentage": round(float(liveness_result.confidence) * 100, 2),
            "motion_score": round(float(liveness_result.motion_score), 4),
            "texture_score": round(float(liveness_result.texture_score), 4),
            "depth_score": round(float(liveness_result.depth_score), 4),
            "details": {k: (int(v) if isinstance(v, (np.integer, np.int32, np.int64)) else 
                           float(v) if isinstance(v, (np.floating, np.float32, np.float64)) else v) 
                       for k, v in liveness_result.details.items()},
            "message": "✅ Persona real detectada" if liveness_result.is_live else "❌ Posible foto o video detectado"
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
