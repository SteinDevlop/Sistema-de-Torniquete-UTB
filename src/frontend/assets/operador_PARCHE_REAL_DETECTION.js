// ===== CÓDIGO CORRECTO PARA DETECCIÓN REAL DE PARPADEOS =====
// Este archivo contiene SOLO las funciones que necesitas reemplazar en operador.js

// 1. REEMPLAZAR la función iniciarVerificacion (línea ~478)
async function iniciarVerificacion() {
    if (isVerifying) return;
    
    isVerifying = true;
    blinkCount = 0;
    previousEyeState = 'open';
    
    document.getElementById("verificationResult").innerHTML = '';
    updateBlinkUI();
    
    console.log("🎬 Iniciando detección REAL con backend...");
    
    try {
        // 1. Iniciar sesión de liveness con el backend
        const res = await fetch(`${API_URL}/liveness/start?mode=active`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await res.json();
        
        if (!data.session_id) {
            throw new Error('No se recibió session_id del backend');
        }
        
        window.currentLivenessSession = data.session_id;
        console.log('✅ Sesión de liveness iniciada:', data.session_id);
        
        // 2. Iniciar detección continua con backend
        blinkDetectionInterval = setInterval(async () => {
            await detectBlinkAndFace();
        }, 200); // Cada 200ms
        
    } catch (err) {
        console.error('❌ Error iniciando liveness:', err);
        isVerifying = false;
        alert('Error al iniciar verificación: ' + err.message);
    }
}

// 2. REEMPLAZAR la función detectBlinkAndFace (línea ~507)
async function detectBlinkAndFace() {
    if (!isVerifying || !cameraStream) return;
    
    const video = document.getElementById('cameraVideo');
    if (!video || !video.videoWidth) return;
    
    const canvas = document.getElementById('cameraCanvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convertir frame a base64
    const frameBase64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];
    
    try {
        // Enviar frame al backend para análisis REAL
        const res = await fetch(`${API_URL}/liveness/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            },
            body: JSON.stringify({
                session_id: window.currentLivenessSession,
                frame: frameBase64
            })
        });
        
        const result = await res.json();
        
        // Actualizar UI con respuesta REAL del backend
        if (result.face_detected) {
            faceDetected = true;
            
            // Usar bounding box del backend si existe
            if (result.face_bbox) {
                const bbox = result.face_bbox;
                const videoWidth = video.videoWidth;
                const videoHeight = video.videoHeight;
                
                // Convertir coordenadas si están normalizadas
                const x = bbox.x < 1 ? bbox.x * videoWidth : bbox.x;
                const y = bbox.y < 1 ? bbox.y * videoHeight : bbox.y;
                const width = bbox.width < 1 ? bbox.width * videoWidth : bbox.width;
                const height = bbox.height < 1 ? bbox.height * videoHeight : bbox.height;
                
                // Suavizar movimiento
                const targetX = x + width / 2;
                const targetY = y + height / 2;
                
                if (currentFaceX === null) {
                    currentFaceX = targetX;
                    currentFaceY = targetY;
                } else {
                    currentFaceX += (targetX - currentFaceX) * smoothingFactor;
                    currentFaceY += (targetY - currentFaceY) * smoothingFactor;
                }
                
                updateFaceBox('face-detected', {
                    x: currentFaceX - width / 2,
                    y: currentFaceY - height / 2,
                    width: width,
                    height: height
                });
            } else {
                updateFaceBox('face-detected');
            }
            
            // Detección REAL de parpadeos desde backend
            if (result.blink_detected) {
                if (previousEyeState === 'open') {
                    blinkCount++;
                    previousEyeState = 'closed';
                    console.log(`✅ Parpadeo REAL ${blinkCount} detectado por backend!`);
                    updateBlinkUI();
                    
                    if (navigator.vibrate) {
                        navigator.vibrate(50);
                    }
                    
                    setTimeout(() => { previousEyeState = 'open'; }, 300);
                    
                    if (blinkCount >= requiredBlinks) {
                        console.log('🎉 3 parpadeos REALES completados!');
                        clearInterval(blinkDetectionInterval);
                        await realizarVerificacionFacial();
                    }
                }
            }
        } else {
            faceDetected = false;
            currentFaceX = null;
            currentFaceY = null;
            updateFaceBox('no-face');
        }
    } catch (err) {
        console.error('Error en detección:', err);
    }
}
