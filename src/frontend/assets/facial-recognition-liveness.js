import API_URL from './api_root.js';
        const API_BASE = API_URL;

        function getAuthHeaders() {
            const token = sessionStorage.getItem('token');
            const headers = {};
            if (token) headers['Authorization'] = `Bearer ${token}`;
            return headers;
        }
        let streamRegister = null;
        let streamVerify = null;
        let livenessSessionId = null;
        let frameInterval = null;
        let framesCollected = 0;
        let minFramesRequired = 15;  // Aumentado de 10 a 15 para mejor análisis

        // Activar cámara
        async function startCamera(mode) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: { ideal: 640 },
                        height: { ideal: 480 }
                    } 
                });
                
                if (mode === 'register') {
                    streamRegister = stream;
                    document.getElementById('videoRegister').srcObject = stream;
                    document.getElementById('btnCapture').disabled = false;
                } else if (mode === 'verify') {
                    streamVerify = stream;
                    document.getElementById('videoVerify').srcObject = stream;
                }
                
                console.log(`Cámara activada para ${mode}`);
            } catch (error) {
                console.error('Error activando cámara:', error);
                alert('No se pudo acceder a la cámara. Verifica los permisos.');
            }
        }

        // Capturar imagen del video
        function captureImage(videoId, canvasId) {
            const video = document.getElementById(videoId);
            const canvas = document.getElementById(canvasId);
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            return canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
        }

        // Registrar usuario
        async function captureAndRegister() {
            const userId = document.getElementById('userIdRegister').value;
            if (!userId) {
                alert('Por favor ingresa un ID de usuario');
                return;
            }

            const imageB64 = captureImage('videoRegister', 'canvasRegister');
            
            const formData = new FormData();
            formData.append('id_usuario', userId);
            formData.append('imagen_facial', imageB64);

            try {
                const response = await fetch(`${API_BASE}/biometria/create`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('registerResult').innerHTML = `
                        <div class="alert alert-success">
                            ✅ Usuario ${userId} registrado exitosamente<br>
                            Hash facial: ${data.data.facial_hash}
                        </div>
                    `;
                    loadBiometricRecords();
                } else {
                    document.getElementById('registerResult').innerHTML = `
                        <div class="alert alert-danger">
                            ❌ Error: ${data.detail}
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('registerResult').innerHTML = `
                    <div class="alert alert-danger">
                        ❌ Error de conexión: ${error.message}
                    </div>
                `;
            }
        }

        // Iniciar verificación con liveness
        async function startLivenessVerification() {
            // Activar cámara si no está activa
            if (!streamVerify) {
                await startCamera('verify');
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // Generar ID de sesión único
            livenessSessionId = 'session_' + Date.now();
            framesCollected = 0;

            try {
                // Iniciar sesión de liveness
                const formData = new FormData();
                formData.append('session_id', livenessSessionId);

                const response = await fetch(`${API_BASE}/liveness/start`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                const data = await response.json();
                minFramesRequired = data.min_frames || 10;
                document.getElementById('minFrames').textContent = minFramesRequired;

                // Mostrar indicadores
                document.getElementById('progressContainer').style.display = 'block';
                document.getElementById('livenessIndicator').style.display = 'block';
                document.getElementById('livenessIndicator').className = 'liveness-indicator liveness-analyzing';
                document.getElementById('livenessIndicator').innerHTML = '🔍 Analizando frames...';

                // Deshabilitar botón de inicio, habilitar botón de detener
                document.getElementById('btnStartLiveness').disabled = true;
                document.getElementById('btnStopLiveness').disabled = false;

                // Comenzar a enviar frames cada 200ms
                frameInterval = setInterval(sendFrame, 200);

                console.log('Sesión de liveness iniciada:', livenessSessionId);
            } catch (error) {
                console.error('Error iniciando liveness:', error);
                alert('Error iniciando verificación: ' + error.message);
            }
        }

        // Enviar frame para análisis
        async function sendFrame() {
            if (!streamVerify || !livenessSessionId) return;

            try {
                const imageB64 = captureImage('videoVerify', 'canvasVerify');
                
                const formData = new FormData();
                formData.append('session_id', livenessSessionId);
                formData.append('frame_b64', imageB64);

                const response = await fetch(`${API_BASE}/liveness/add-frame`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                const data = await response.json();
                
                framesCollected = data.frames_received;
                document.getElementById('frameCount').textContent = framesCollected;
                
                // Actualizar barra de progreso
                const progress = (framesCollected / minFramesRequired) * 100;
                document.getElementById('frameProgress').style.width = progress + '%';

                // Si ya tenemos suficientes frames, analizar
                if (data.ready_for_analysis) {
                    clearInterval(frameInterval);
                    await analyzeLiveness();
                }
            } catch (error) {
                console.error('Error enviando frame:', error);
            }
        }

        // Analizar liveness
        async function analyzeLiveness() {
            try {
                document.getElementById('livenessIndicator').innerHTML = '⏳ Procesando análisis...';

                const formData = new FormData();
                formData.append('session_id', livenessSessionId);

                const response = await fetch(`${API_BASE}/liveness/analyze`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                const data = await response.json();

                if (data.success && data.is_live) {
                    // ✅ LIVENESS PASADO - Proceder con verificación facial
                    document.getElementById('livenessIndicator').className = 'liveness-indicator liveness-real';
                    document.getElementById('livenessIndicator').innerHTML = `
                        ✅ PERSONA REAL DETECTADA<br>
                        Confianza: ${data.confidence_percentage}%
                    `;

                    // Mostrar métricas
                    displayLivenessMetrics(data);

                    // Proceder con verificación facial
                    await performFacialVerification();

                } else {
                    // ❌ LIVENESS FALLIDO
                    document.getElementById('livenessIndicator').className = 'liveness-indicator liveness-fake';
                    document.getElementById('livenessIndicator').innerHTML = `
                        ❌ ${data.message}<br>
                        Confianza: ${data.confidence_percentage}%
                    `;

                    displayLivenessMetrics(data);

                    document.getElementById('verifyResult').innerHTML = `
                        <div class="alert alert-danger">
                            ❌ Acceso denegado: No se detectó una persona real
                        </div>
                    `;
                }

                // Resetear
                stopLivenessVerification();

            } catch (error) {
                console.error('Error analizando liveness:', error);
                document.getElementById('livenessIndicator').className = 'liveness-indicator liveness-fake';
                document.getElementById('livenessIndicator').innerHTML = '❌ Error en análisis';
                stopLivenessVerification();
            }
        }

        // Mostrar métricas de liveness
        function displayLivenessMetrics(data) {
            const getMetricClass = (score) => {
                if (score >= 0.7) return 'metric-high';
                if (score >= 0.4) return 'metric-medium';
                return 'metric-low';
            };

            document.getElementById('livenessMetrics').innerHTML = `
                <div class="metric-badge ${getMetricClass(data.motion_score)}">
                    🏃 Movimiento: ${(data.motion_score * 100).toFixed(1)}%
                </div>
                <div class="metric-badge ${getMetricClass(data.texture_score)}">
                    🎨 Textura: ${(data.texture_score * 100).toFixed(1)}%
                </div>
                <div class="metric-badge ${getMetricClass(data.depth_score)}">
                    📐 Profundidad: ${(data.depth_score * 100).toFixed(1)}%
                </div>
                <p class="mt-2 small text-muted">
                    Frames analizados: ${data.details.frames_analizados}
                </p>
            `;
        }

        // Realizar verificación facial (después de pasar liveness)
        async function performFacialVerification() {
            try {
                const imageB64 = captureImage('videoVerify', 'canvasVerify');
                
                const formData = new FormData();
                formData.append('dispositivo_id', 'web_liveness');
                formData.append('imagen_facial', imageB64);

                const response = await fetch(`${API_BASE}/acceso/camara`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: formData
                });

                const data = await response.json();

                if (data.status) {
                    document.getElementById('verifyResult').innerHTML = `
                        <div class="alert alert-success">
                            <h5>✅ ACCESO CONCEDIDO</h5>
                            <p><strong>Usuario:</strong> ${data.usuario_id}</p>
                            <p><strong>Similitud:</strong> ${data.score ? (data.score * 100).toFixed(2) + '%' : 'N/A'}</p>
                            <p><strong>Mensaje:</strong> ${data.mensaje}</p>
                        </div>
                    `;

                    if (data.detalles_verificacion) {
                        const d = data.detalles_verificacion;
                        document.getElementById('verifyResult').innerHTML += `
                            <div class="card mt-2">
                                <div class="card-body">
                                    <h6>Detalles de Comparación:</h6>
                                    <p>Candidatos evaluados: ${d.candidatos_evaluados}</p>
                                    <p>Mejor distancia: ${d.mejor_distancia ? d.mejor_distancia.toFixed(4) : 'N/A'}</p>
                                    <p>Umbral: ${d.umbral_distancia || 'N/A'}</p>
                                </div>
                            </div>
                        `;
                    }
                } else {
                    document.getElementById('verifyResult').innerHTML = `
                        <div class="alert alert-danger">
                            <h5>❌ ACCESO DENEGADO</h5>
                            <p><strong>Mensaje:</strong> ${data.mensaje}</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error en verificación facial:', error);
                document.getElementById('verifyResult').innerHTML = `
                    <div class="alert alert-danger">
                        ❌ Error de conexión: ${error.message}
                    </div>
                `;
            }
        }

        // Detener verificación
        function stopLivenessVerification() {
            if (frameInterval) {
                clearInterval(frameInterval);
                frameInterval = null;
            }
            
            document.getElementById('btnStartLiveness').disabled = false;
            document.getElementById('btnStopLiveness').disabled = true;
            document.getElementById('progressContainer').style.display = 'none';
            
            livenessSessionId = null;
            framesCollected = 0;
        }

        // Cargar registros biométricos
        async function loadBiometricRecords() {
            try {
                console.log('Cargando registros biométricos...');
                const response = await fetch(`${API_BASE}/biometria/all`, { headers: getAuthHeaders() });
                const data = await response.json();
                
                console.log('Respuesta del servidor:', data);

                if (data.success && data.data && data.data.length > 0) {
                    let html = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>ID Usuario</th><th>Hash Facial</th><th>Fecha</th><th>Acciones</th></tr></thead><tbody>';
                    
                    data.data.forEach(record => {
                        html += `
                            <tr>
                                <td>${record.id_usuario}</td>
                                <td>${record.facial_hash || 'N/A'}</td>
                                <td>${record.fecha_actualizacion || 'N/A'}</td>
                                <td>
                                    <button class="btn btn-sm btn-danger" onclick="deleteBiometric(${record.id_biometria})">
                                        🗑️ Eliminar
                                    </button>
                                </td>
                            </tr>
                        `;
                    });
                    
                    html += '</tbody></table></div>';
                    document.getElementById('biometricList').innerHTML = html;
                    console.log(`✅ ${data.data.length} registros cargados`);
                } else {
                    document.getElementById('biometricList').innerHTML = '<p class="text-muted">No hay registros biométricos.</p>';
                    console.log('No hay registros para mostrar');
                }
            } catch (error) {
                console.error('Error cargando registros:', error);
                document.getElementById('biometricList').innerHTML = '<p class="text-danger">Error cargando registros. Ver consola.</p>';
            }
        }

        // Eliminar registro biométrico
        async function deleteBiometric(id) {
            if (!confirm('¿Estás seguro de eliminar este registro?')) return;

            try {
                const formData = new FormData();
                formData.append('id_biometria', id);

                const response = await fetch(`${API_BASE}/biometria/delete`, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    alert('Registro eliminado exitosamente');
                    loadBiometricRecords();
                }
            } catch (error) {
                console.error('Error eliminando registro:', error);
                alert('Error eliminando registro');
            }
        }

        // Cargar registros al iniciar
        window.onload = () => {
            loadBiometricRecords();
        };