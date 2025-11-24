"""
Sistema de Detección de Liveness (Anti-Spoofing) Unificado.
Soporta dos modos:
1. Pasivo: Análisis de textura, movimiento y profundidad (sin interacción).
2. Activo: Detección de parpadeo (Challenge-Response).

Author: Sistema Torniquete UTB
"""

import logging
import numpy as np
import cv2
import time
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class LivenessScore:
    """Resultado del análisis de liveness"""
    is_live: bool
    confidence: float  # 0.0 - 1.0
    mode: str          # 'active' or 'passive'
    details: Dict[str, any]

class LivenessDetector:
    """
    Detector de liveness unificado.
    """
    
    def __init__(
        self,
        # Configuración Pasiva
        min_frames_passive: int = 15,
        texture_threshold: float = 0.25,
        depth_threshold: float = 0.25,
        # Configuración Activa
        consecutive_frames_active: int = 2,
        required_blinks: int = 1
    ):
        # Config Pasiva
        self.min_frames_passive = min_frames_passive
        self.texture_threshold = texture_threshold
        self.depth_threshold = depth_threshold
        
        # Config Activa
        self.consecutive_frames_active = consecutive_frames_active
        self.required_blinks = required_blinks
        
        # Buffers Pasivos
        self.frame_buffer = deque(maxlen=min_frames_passive)
        self.motion_scores = deque(maxlen=min_frames_passive)
        self.texture_scores = deque(maxlen=min_frames_passive)
        self.depth_scores = deque(maxlen=min_frames_passive)
        self.prev_gray = None
        
        # Estado Activo (Blink)
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.blink_counter = 0
        self.total_blinks = 0
        self.eyes_visible_prev = True
        
        logger.info("LivenessDetector Unificado inicializado")
    
    def reset(self):
        """Resetea todos los estados"""
        # Pasivo
        self.frame_buffer.clear()
        self.motion_scores.clear()
        self.texture_scores.clear()
        self.depth_scores.clear()
        self.prev_gray = None
        
        # Activo
        self.blink_counter = 0
        self.total_blinks = 0
        self.eyes_visible_prev = True
        
        logger.debug("LivenessDetector reseteado")

    def add_frame(self, frame: np.ndarray, face_bbox: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Agrega un frame y realiza análisis preliminar.
        Retorna True si hay suficientes datos para el modo pasivo.
        """
        if frame is None: return False
        
        # --- Lógica Pasiva (Acumular métricas) ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if face_bbox:
            x, y, w, h = face_bbox
            gray_roi = gray[y:y+h, x:x+w]
            frame_roi = frame[y:y+h, x:x+w]
        else:
            gray_roi = gray
            frame_roi = frame
            
        self.frame_buffer.append(gray_roi)
        
        # Movimiento
        if self.prev_gray is not None:
             # Resize if needed
            if self.prev_gray.shape != gray_roi.shape:
                gray_roi = cv2.resize(gray_roi, (self.prev_gray.shape[1], self.prev_gray.shape[0]))
            
            motion = self._analyze_motion(self.prev_gray, gray_roi)
            self.motion_scores.append(motion)
            
        self.prev_gray = gray_roi
        
        # Textura y Profundidad
        self.texture_scores.append(self._analyze_texture(gray_roi))
        self.depth_scores.append(self._analyze_depth(frame_roi))
        
        # --- Lógica Activa (Detectar parpadeo en tiempo real) ---
        self._process_blink(gray_roi)
        
        return len(self.frame_buffer) >= self.min_frames_passive

    def _process_blink(self, gray_frame):
        """Procesa parpadeo usando Haar Cascades"""
        if self.eye_cascade.empty(): return
        
        eyes = self.eye_cascade.detectMultiScale(gray_frame, 1.1, 5, minSize=(30, 30))
        eyes_visible = len(eyes) >= 1
        
        if not eyes_visible and self.eyes_visible_prev:
            self.blink_counter += 1
        
        if eyes_visible and not self.eyes_visible_prev:
            if self.blink_counter >= 1:
                self.total_blinks += 1
                self.blink_counter = 0
        
        self.eyes_visible_prev = eyes_visible

    # --- Métodos de Análisis Pasivo (Restaurados) ---
    def _analyze_motion(self, prev, curr):
        try:
            flow = cv2.calcOpticalFlowFarneback(prev, curr, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            mean_mag = np.mean(mag)
            return min(1.0, max(0.0, mean_mag)) # Simplificado para brevedad
        except: return 0.0

    def _analyze_texture(self, gray):
        try:
            # Detección simple de alta frecuencia (bordes)
            edges = cv2.Canny(gray, 50, 150)
            density = np.sum(edges > 0) / edges.size
            # Fotos suelen tener bordes muy definidos o muy suaves (desenfocados)
            # Piel real tiene textura media.
            score = 1.0 - abs(density - 0.1) * 5 # Heurística simple
            return min(1.0, max(0.0, score))
        except: return 0.5

    def _analyze_depth(self, bgr):
        # Placeholder para análisis de profundidad (requiere algoritmos más complejos)
        return 0.6 

    def get_liveness_score(self, mode: str = 'passive') -> LivenessScore:
        """
        Retorna el score basado en el modo seleccionado.
        """
        if mode == 'active':
            is_live = self.total_blinks >= self.required_blinks
            return LivenessScore(
                is_live=is_live,
                confidence=1.0 if is_live else 0.0,
                mode='active',
                details={'blinks': self.total_blinks, 'required': self.required_blinks}
            )
        else: # Passive
            if not self.motion_scores: return None
            
            avg_motion = np.mean(self.motion_scores)
            avg_texture = np.mean(self.texture_scores)
            
            # Lógica pasiva simple
            final_score = (avg_motion * 0.3 + avg_texture * 0.7)
            is_live = final_score > 0.5
            
            return LivenessScore(
                is_live=is_live,
                confidence=final_score,
                mode='passive',
                details={'motion': avg_motion, 'texture': avg_texture}
            )

# Singleton
_liveness_detector = None
def get_liveness_detector() -> LivenessDetector:
    global _liveness_detector
    if _liveness_detector is None:
        _liveness_detector = LivenessDetector()
    return _liveness_detector

