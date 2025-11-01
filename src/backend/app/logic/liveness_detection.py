"""
Sistema de Detección de Liveness (Anti-Spoofing) para reconocimiento facial.

Implementa técnicas pasivas que no requieren acción del usuario:
1. Análisis de micro-movimientos entre frames
2. Detección de textura (fotos vs rostro real)
3. Análisis de profundidad y gradientes
4. Modelo anti-spoofing basado en CNN (opcional)

Author: Sistema Torniquete UTB
"""

import logging
import numpy as np
import cv2
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class LivenessScore:
    """Resultado del análisis de liveness"""
    is_live: bool
    confidence: float  # 0.0 - 1.0
    motion_score: float
    texture_score: float
    depth_score: float
    details: Dict[str, any]


class LivenessDetector:
    """
    Detector de liveness que analiza múltiples frames en tiempo real.
    
    Usa técnicas pasivas (no requiere acción del usuario):
    - Análisis de flujo óptico (micro-movimientos)
    - Detección de patrones moiré (fotos de pantallas)
    - Análisis de textura (fotos impresas)
    - Gradientes de profundidad (2D vs 3D)
    """
    
    def __init__(
        self,
        min_frames: int = 15,
        motion_threshold: float = 0.2,
        texture_threshold: float = 0.25,
        depth_threshold: float = 0.25,
        liveness_threshold: float = 0.65
    ):
        """
        Args:
            min_frames: Número mínimo de frames a analizar (AUMENTADO a 15 para mejor análisis)
            motion_threshold: Umbral para detectar movimiento natural
            texture_threshold: Umbral para detectar textura real vs foto
            depth_threshold: Umbral para detectar profundidad 3D
            liveness_threshold: Umbral final para considerar "vivo" (0.65 = 65%)
        """
        self.min_frames = min_frames
        self.motion_threshold = motion_threshold
        self.texture_threshold = texture_threshold
        self.depth_threshold = depth_threshold
        self.liveness_threshold = liveness_threshold
        
        # Buffers para análisis temporal
        self.frame_buffer = deque(maxlen=min_frames)
        self.motion_scores = deque(maxlen=min_frames)
        self.texture_scores = deque(maxlen=min_frames)
        self.depth_scores = deque(maxlen=min_frames)
        
        # Para cálculo de flujo óptico
        self.prev_gray = None
        
        logger.info(f"LivenessDetector inicializado: min_frames={min_frames}, threshold={liveness_threshold}")
    
    def reset(self):
        """Resetea los buffers para un nuevo análisis"""
        self.frame_buffer.clear()
        self.motion_scores.clear()
        self.texture_scores.clear()
        self.depth_scores.clear()
        self.prev_gray = None
        logger.debug("Buffers reseteados")
    
    def add_frame(self, frame: np.ndarray, face_bbox: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Agrega un frame al buffer para análisis.
        
        Args:
            frame: Frame BGR de OpenCV
            face_bbox: (x, y, w, h) del rostro detectado (opcional)
            
        Returns:
            bool: True si ya hay suficientes frames para análisis
        """
        if frame is None or frame.size == 0:
            logger.warning("Frame inválido recibido")
            return False
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Si hay bbox, recortar solo la región del rostro
        if face_bbox:
            x, y, w, h = face_bbox
            gray = gray[y:y+h, x:x+w]
            frame = frame[y:y+h, x:x+w]
        
        # Agregar al buffer
        self.frame_buffer.append(gray)
        
        # Analizar movimiento si hay frame anterior
        if self.prev_gray is not None:
            motion_score = self._analyze_motion(self.prev_gray, gray)
            self.motion_scores.append(motion_score)
        
        # Analizar textura
        texture_score = self._analyze_texture(gray)
        self.texture_scores.append(texture_score)
        
        # Analizar profundidad
        depth_score = self._analyze_depth(frame)
        self.depth_scores.append(depth_score)
        
        self.prev_gray = gray
        
        return len(self.frame_buffer) >= self.min_frames
    
    def _analyze_motion(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        """
        Analiza el flujo óptico entre dos frames consecutivos.
        
        Micro-movimientos naturales (respiración, micro-expresiones) generan
        flujo óptico característico. Una foto estática no tiene movimiento.
        
        Returns:
            float: Score de movimiento (0-1), mayor = más movimiento natural
        """
        try:
            # Verificar que los frames tengan el mismo tamaño
            if prev_frame.shape != curr_frame.shape:
                logger.warning(f"Frames con diferentes tamaños: {prev_frame.shape} vs {curr_frame.shape}")
                # Redimensionar curr_frame para que coincida con prev_frame
                curr_frame = cv2.resize(curr_frame, (prev_frame.shape[1], prev_frame.shape[0]))
            
            # Calcular flujo óptico denso (Farneback)
            flow = cv2.calcOpticalFlowFarneback(
                prev_frame, curr_frame,
                None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Calcular magnitud del flujo
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # Estadísticas del movimiento
            mean_magnitude = np.mean(magnitude)
            std_magnitude = np.std(magnitude)
            max_magnitude = np.max(magnitude)
            
            # DETECCIÓN MEJORADA ANTI-SPOOFING:
            # - Fotos de pantallas: movimiento artificial alto y uniforme
            # - Fotos impresas sostenidas: movimiento global coherente (todo se mueve igual)
            # - Rostros reales: movimiento localizado e irregular (parpadeo, micro-expresiones)
            
            # Calcular coherencia del movimiento (qué tan uniforme es)
            # Fotos tienen movimiento muy uniforme, rostros reales tienen variación
            coherence = std_magnitude / (mean_magnitude + 1e-8)
            
            # Movimientos naturales:
            # - Magnitud baja a media (0.5-3.0)
            # - Alta variación espacial (coherence > 0.5)
            # - No demasiado uniforme
            
            if mean_magnitude < 0.3:  
                # Muy poco movimiento (posible foto estática bien sostenida)
                score = mean_magnitude * 0.5  # Penalizar fuertemente
            elif mean_magnitude > 5.0:  
                # Demasiado movimiento (posible video de pantalla o foto moviéndose)
                score = max(0, 0.3 - (mean_magnitude - 5.0) / 20.0)  # Penalizar
            elif coherence < 0.3:
                # Movimiento muy uniforme = foto siendo movida
                score = 0.2
            else:  
                # Rango aceptable con buena variación
                # Dar más peso a la coherencia (variación espacial)
                score = min(1.0, (coherence * 0.7) + (std_magnitude / 5.0) * 0.3)
            
            logger.debug(f"Motion analysis: mean={mean_magnitude:.3f}, std={std_magnitude:.3f}, "
                        f"coherence={coherence:.3f}, score={score:.3f}")
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.warning(f"Error calculando flujo óptico: {e}")
            return 0.0
    
    def _analyze_texture(self, gray_frame: np.ndarray) -> float:
        """
        Analiza la textura de la imagen para detectar fotos impresas o pantallas.
        
        - Fotos impresas tienen textura de papel (alta frecuencia)
        - Pantallas generan patrones moiré (frecuencias específicas)
        - Piel real tiene textura suave con variación natural
        
        Returns:
            float: Score de textura real (0-1), mayor = más probable que sea piel real
        """
        try:
            # 1. Análisis de frecuencia (FFT) para detectar patrones moiré
            dft = cv2.dft(np.float32(gray_frame), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]) + 1)
            
            # Detectar picos de alta frecuencia (característicos de pantallas/impresiones)
            high_freq_energy = np.mean(magnitude_spectrum[magnitude_spectrum > np.percentile(magnitude_spectrum, 90)])
            
            # 2. Análisis de varianza local (LBP - Local Binary Patterns concept)
            blur = cv2.GaussianBlur(gray_frame, (5, 5), 0)
            variance = cv2.Laplacian(blur, cv2.CV_64F).var()
            
            # 3. Detección de bordes (fotos tienen bordes más definidos)
            edges = cv2.Canny(gray_frame, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Score: piel real tiene frecuencias moderadas, varianza media, bordes suaves
            freq_score = 1.0 - min(1.0, high_freq_energy / 100.0)
            variance_score = min(1.0, variance / 1000.0)  # Piel real ~200-800
            edge_score = 1.0 - min(1.0, edge_density * 5)
            
            # Combinar scores
            texture_score = (freq_score * 0.4 + variance_score * 0.4 + edge_score * 0.2)
            
            return min(1.0, max(0.0, texture_score))
            
        except Exception as e:
            logger.warning(f"Error analizando textura: {e}")
            return 0.5
    
    def _analyze_depth(self, bgr_frame: np.ndarray) -> float:
        """
        Analiza gradientes de profundidad para detectar rostros 3D vs 2D.
        
        Un rostro real 3D tiene:
        - Gradientes de iluminación suaves
        - Sombras naturales en nariz, mejillas, frente
        - Variación de color/intensidad por curvatura
        
        Una foto 2D:
        - Iluminación plana
        - Sin variación de profundidad
        - Posibles reflejos de luz ambiente
        
        Returns:
            float: Score de profundidad 3D (0-1), mayor = más probable que sea 3D real
        """
        try:
            gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Calcular gradientes en X e Y
            gradient_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gradient_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # 2. Magnitud del gradiente
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # 3. Analizar distribución de gradientes
            # Rostros 3D reales tienen distribución más uniforme
            # Fotos tienen gradientes concentrados en bordes
            gradient_std = np.std(gradient_magnitude)
            gradient_mean = np.mean(gradient_magnitude)
            
            # 4. Analizar variación de intensidad (simulación de profundidad)
            # Dividir en regiones y analizar varianza entre regiones
            h, w = gray.shape
            regions = []
            for i in range(3):
                for j in range(3):
                    region = gray[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
                    regions.append(np.mean(region))
            
            region_variance = np.std(regions)
            
            # Score: rostros 3D tienen gradientes suaves pero con variación regional
            gradient_score = min(1.0, gradient_std / 50.0)  # Normalizar
            variance_score = min(1.0, region_variance / 30.0)
            
            depth_score = (gradient_score * 0.6 + variance_score * 0.4)
            
            return min(1.0, max(0.0, depth_score))
            
        except Exception as e:
            logger.warning(f"Error analizando profundidad: {e}")
            return 0.5
    
    def get_liveness_score(self) -> Optional[LivenessScore]:
        """
        Calcula el score final de liveness basado en todos los frames analizados.
        
        Returns:
            LivenessScore con resultado final, o None si no hay suficientes frames
        """
        if len(self.frame_buffer) < self.min_frames:
            logger.warning(f"Insuficientes frames: {len(self.frame_buffer)}/{self.min_frames}")
            return None
        
        # Promediar scores de todos los frames
        avg_motion = np.mean(self.motion_scores) if self.motion_scores else 0.0
        avg_texture = np.mean(self.texture_scores) if self.texture_scores else 0.0
        avg_depth = np.mean(self.depth_scores) if self.depth_scores else 0.0
        
        # Score final ponderado
        # AJUSTADO PARA ANTI-SPOOFING:
        # - Textura es MUY CONFIABLE para detectar pantallas/fotos (peso alto)
        # - Movimiento puede ser engañado moviendo la foto (peso reducido)
        # - Profundidad puede dar falsos positivos con pantallas curvas (peso medio)
        final_score = (
            avg_motion * 0.20 +      # Movimiento (reducido, puede ser engañado)
            avg_texture * 0.50 +     # Textura (AUMENTADO, muy confiable)
            avg_depth * 0.30         # Profundidad (medio)
        )
        
        # REGLA ADICIONAL: Si textura es muy baja (<0.25), denegar automáticamente
        # Esto evita que movimiento/profundidad compensen una mala textura
        if avg_texture < 0.25:
            logger.warning(f"⚠️  ANTI-SPOOFING: Textura muy baja ({avg_texture:.3f}) - posible foto/pantalla")
            is_live = False
            final_score = min(final_score, 0.40)  # Limitar score máximo
        else:
            is_live = final_score >= self.liveness_threshold
        
        details = {
            "frames_analizados": len(self.frame_buffer),
            "motion_avg": round(float(avg_motion), 4),
            "texture_avg": round(float(avg_texture), 4),
            "depth_avg": round(float(avg_depth), 4),
            "motion_threshold": self.motion_threshold,
            "texture_threshold": self.texture_threshold,
            "depth_threshold": self.depth_threshold,
            "liveness_threshold": self.liveness_threshold
        }
        
        logger.info(f"🎭 Liveness Score: {final_score:.3f} {'✅ REAL' if is_live else '❌ FAKE'}")
        logger.info(f"   Motion: {avg_motion:.3f}, Texture: {avg_texture:.3f}, Depth: {avg_depth:.3f}")
        
        return LivenessScore(
            is_live=is_live,
            confidence=final_score,
            motion_score=avg_motion,
            texture_score=avg_texture,
            depth_score=avg_depth,
            details=details
        )


# Singleton global
_liveness_detector = None


def get_liveness_detector() -> LivenessDetector:
    """Retorna la instancia singleton del detector de liveness"""
    global _liveness_detector
    if _liveness_detector is None:
        _liveness_detector = LivenessDetector()
    return _liveness_detector
