import API_URL from './api_root.js';
        let currentUserId = null;
        let cameraStream = null;
        
        // Variables para detección de parpadeo
        let blinkDetectionInterval = null;
        let blinkCount = 0;
        let requiredBlinks = 3;
        let isVerifying = false;
        let faceDetected = false;
        let previousEyeState = 'open';
        let verificationType = 'acceso'; // 'acceso' o 'registro'
        
        // Variables para suavizar movimiento del cuadro
        let currentFaceX = null;
        let currentFaceY = null;
        let targetFaceX = null;
        let targetFaceY = null;
        const smoothingFactor = 0.3; // Cuanto más bajo, más suave (0.1 = muy suave, 1 = instantáneo)
        
        // ===== FUNCIONES DE MODAL PERSONALIZADAS (SIN BOOTSTRAP) =====
        function abrirModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                document.body.style.overflow = 'hidden'; // Prevent scroll
            }
        }
        
        function cerrarModal() {
            const modal = document.getElementById('cameraModal');
            if (modal) {
                modal.classList.remove('show');
                document.body.style.overflow = ''; // Restore scroll
            }
            
            // Detener verificación y liberar cámara
            detenerVerificacion();
            
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
        }
        
        function closeModalOnBackdrop(event) {
            // Cerrar solo si se hace click en el fondo (no en el contenido)
            if (event.target === event.currentTarget) {
                cerrarModal();
            }
        }
        
        // Cerrar modal con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                cerrarModal();
            }
        });
        
        // ===== FUNCIONES AUXILIARES =====
        function getAuthHeaders() {
            const token = sessionStorage.getItem("token");
            const headers = {};
            if (token) headers["Authorization"] = `Bearer ${token}`;
            return headers;
        }
        function showLoading() { document.getElementById("loadingOverlay").classList.add("show"); }
        function hideLoading() { document.getElementById("loadingOverlay").classList.remove("show"); }
        
        // ===== MODALES INFORMATIVOS DE ACCESO =====
        function mostrarModalAcceso(data) {
            const isSuccess = data.status || data.success;
            const tiempoValidez = data.tiempo_validez || 30; // segundos
            
            const modalHtml = `
                <div class="modal-backdrop"></div>
                <div class="modal-dialog" style="max-width: 500px;">
                    <div class="access-modal">
                        <div class="access-modal-header">
                            <div class="access-modal-icon ${isSuccess ? 'success' : 'error'}">
                                <i class="fas fa-${isSuccess ? 'check-circle' : 'times-circle'}"></i>
                            </div>
                            <h3 style="color: ${isSuccess ? 'var(--green-light)' : 'var(--red-light)'}; margin-bottom: 0.5rem;">
                                ${isSuccess ? '✅ Acceso Permitido' : '❌ Acceso Denegado'}
                            </h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">${data.mensaje || 'Verificación completada'}</p>
                        </div>
                        
                        ${isSuccess && data.foto ? `

                            <div class="access-modal-photo success">
                                <img src="data:image/jpeg;base64,${data.foto}" alt="Foto usuario" />
                            </div>
                        ` : ''}
                        
                        <div class="access-modal-info">
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-user me-2"></i>Usuario</span>
                                <span class="access-modal-value">${data.nombre || data.usuario_id || 'Desconocido'}</span>
                            </div>
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-id-card me-2"></i>ID</span>
                                <span class="access-modal-value">#${data.usuario_id || 'N/A'}</span>
                            </div>
                            ${data.cargo ? `
                                <div class="access-modal-row">
                                    <span class="access-modal-label"><i class="fas fa-briefcase me-2"></i>Cargo</span>
                                    <span class="access-modal-value">${data.cargo}</span>
                                </div>
                            ` : ''}
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-clock me-2"></i>Hora</span>
                                <span class="access-modal-value">${new Date().toLocaleTimeString('es-ES')}</span>
                            </div>
                            ${data.metodo ? `
                                <div class="access-modal-row">
                                    <span class="access-modal-label"><i class="fas fa-fingerprint me-2"></i>Método</span>
                                    <span class="access-modal-value">${data.metodo}</span>
                                </div>
                            ` : ''}
                        </div>
                        
                        ${isSuccess ? `
                            <div class="access-countdown">
                                <div class="access-modal-label mb-2">Acceso válido por</div>
                                <div class="access-countdown-number" id="countdownNumber">${tiempoValidez}</div>
                                <div class="access-modal-label">segundos</div>
                            </div>
                        ` : ''}
                        
                        <button class="btn btn-${isSuccess ? 'success' : 'danger'} w-100 mt-3" onclick="cerrarModalAcceso()">
                            <i class="fas fa-check me-2"></i>Entendido
                        </button>
                    </div>
                </div>
            `;
            
            const modalContainer = document.createElement('div');
            modalContainer.id = 'accessModal';
            modalContainer.className = 'modal show';
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);
            
            // Iniciar countdown si es acceso exitoso
            if (isSuccess) {
                let countdown = tiempoValidez;
                const countdownInterval = setInterval(() => {
                    countdown--;
                    const countdownEl = document.getElementById('countdownNumber');
                    if (countdownEl) {
                        countdownEl.textContent = countdown;
                        if (countdown <= 0) {
                            clearInterval(countdownInterval);
                            cerrarModalAcceso();
                        }
                    } else {
                        clearInterval(countdownInterval);
                    }
                }, 1000);
            }
        }
        
        function cerrarModalAcceso() {
            const modal = document.getElementById('accessModal');
            if (modal) modal.remove();
        }
        
        function mostrarModalRegistro(data, tipo) {
            const isSuccess = data.success || data.status;
            
            const modalHtml = `
                <div class="modal-backdrop"></div>
                <div class="modal-dialog" style="max-width: 500px;">
                    <div class="access-modal">
                        <div class="access-modal-header">
                            <div class="access-modal-icon ${isSuccess ? 'success' : 'error'}">
                                <i class="fas fa-${isSuccess ? 'check-circle' : 'times-circle'}"></i>
                            </div>
                            <h3 style="color: ${isSuccess ? 'var(--green-light)' : 'var(--red-light)'}; margin-bottom: 0.5rem;">
                                ${isSuccess ? '✅ Registro Exitoso' : '❌ Error en Registro'}
                            </h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">${data.mensaje || data.message || 'Proceso completado'}</p>
                        </div>
                        
                        <div class="access-modal-info">
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-fingerprint me-2"></i>Tipo</span>
                                <span class="access-modal-value">${tipo}</span>
                            </div>
                            ${data.usuario_id || data.id_usuario ? `
                                <div class="access-modal-row">
                                    <span class="access-modal-label"><i class="fas fa-user me-2"></i>Usuario ID</span>
                                    <span class="access-modal-value">#${data.usuario_id || data.id_usuario}</span>
                                </div>
                            ` : ''}
                            ${data.nombre ? `
                                <div class="access-modal-row">
                                    <span class="access-modal-label"><i class="fas fa-id-card me-2"></i>Nombre</span>
                                    <span class="access-modal-value">${data.nombre}</span>
                                </div>
                            ` : ''}
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-clock me-2"></i>Hora</span>
                                <span class="access-modal-value">${new Date().toLocaleTimeString('es-ES')}</span>
                            </div>
                        </div>
                        
                        <button class="btn btn-${isSuccess ? 'success' : 'danger'} w-100 mt-3" onclick="cerrarModalRegistro()">
                            <i class="fas fa-check me-2"></i>Cerrar
                        </button>
                    </div>
                </div>
            `;
            
            const modalContainer = document.createElement('div');
            modalContainer.id = 'registroModal';
            modalContainer.className = 'modal show';
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);
        }
        
        function cerrarModalRegistro() {
            const modal = document.getElementById('registroModal');
            if (modal) modal.remove();
        }
        
        function showTab(tabName) {
            document.querySelectorAll(".tab-content").forEach(t => t.style.display = "none");
            document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
            document.getElementById(tabName + "-tab").style.display = "block";
            document.querySelector(`[data-section="${tabName}"]`).classList.add("active");
            
            // Limpiar panel de información de usuario al cambiar de pestaña (privacidad)
            const userInfoPanel = document.getElementById("userInfoPanel");
            if (userInfoPanel) {
                userInfoPanel.classList.remove('show');
                userInfoPanel.innerHTML = '';
            }
            
            if (tabName === "validacion") cargarUltimosAccesos();
            if (tabName === "busqueda") buscarUsuarios(); // Cargar todos los usuarios al abrir
        }
        async function verificarRFID() {
            // Crear modal para ingresar RFID
            const modalHtml = `
                <div class="modal-backdrop" onclick="cerrarModalRFID()"></div>
                <div class="modal-dialog" style="max-width: 400px;">
                    <div style="background: var(--bg-secondary); border-radius: 16px; padding: 2rem; border: 1px solid var(--border);">
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <div style="width: 64px; height: 64px; background: linear-gradient(135deg, #3b82f6, #2563eb); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;">
                                <i class="fas fa-id-card" style="font-size: 2rem; color: white;"></i>
                            </div>
                            <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Verificación RFID</h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">Ingrese el código de la tarjeta RFID</p>
                        </div>
                        
                        <input 
                            type="text" 
                            id="rfidInput" 
                            placeholder="Ej: ABC123456789"
                            style="width: 100%; padding: 0.75rem 1rem; background: var(--bg-tertiary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 1rem; margin-bottom: 1.5rem;"
                            autofocus
                        />
                        
                        <div style="display: flex; gap: 0.75rem;">
                            <button onclick="cerrarModalRFID()" class="btn btn-secondary" style="flex: 1;">
                                <i class="fas fa-times me-2"></i>Cancelar
                            </button>
                            <button onclick="procesarRFID()" class="btn btn-primary" style="flex: 1;">
                                <i class="fas fa-check me-2"></i>Verificar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            const modalContainer = document.createElement('div');
            modalContainer.id = 'modalRFID';
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);
            
            // Focus en el input
            setTimeout(() => document.getElementById('rfidInput')?.focus(), 100);
            
            // Enter para verificar
            document.getElementById('rfidInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') procesarRFID();
            });
        }
        
        function cerrarModalRFID() {
            const modal = document.getElementById('modalRFID');
            if (modal) modal.remove();
        }
        
        async function procesarRFID() {
            const tag = document.getElementById('rfidInput')?.value.trim();
            if (!tag) {
                document.getElementById('rfidInput').style.borderColor = 'var(--red)';
                return;
            }
            
            cerrarModalRFID();
            showLoading();
            
            try {
                const res = await fetch(`${API_URL}/acceso/rfid?rfid_tag=${encodeURIComponent(tag)}`, {
                    method: "POST", headers: getAuthHeaders()
                });
                const data = await res.json();
                hideLoading();
                
                // Agregar información del método
                data.metodo = "RFID";
                
                // Mostrar modal informativo
                mostrarModalAcceso(data);
                cargarUltimosAccesos();
            } catch (err) {
                hideLoading();
                mostrarModalRegistro({ success: false, mensaje: "Error de conexión: " + err.message }, "Error");
            }
        }
        async function verificarHuella() {
            mostrarModalRegistro({ 
                success: false, 
                mensaje: "Funcionalidad de huella requiere hardware especializado" 
            }, "Huella Dactilar");
        }

        // Nuevo flujo: abrir selector y permitir elegir cámara antes de iniciar
        async function verificarFacial() {
            verificationType = "acceso";
            
            // Resetear estado
            blinkCount = 0;
            isVerifying = false;
            faceDetected = false;
            document.getElementById("verificationResult").innerHTML = '';
            document.getElementById("userInfoPanel").classList.remove('show');
            updateBlinkUI();
            
            // Abrir modal y popular lista de cámaras; el usuario iniciará la cámara manualmente
            abrirModal("cameraModal");
            await populateCameraList();
        }

        // Para registro: igual flujo (usuario elige cámara)
        async function capturarRostro() {
            if (!currentUserId) {
                alert("Primero cree el usuario base");
                return;
            }
            
            // Para registro, usar captura simple sin liveness (el usuario aún no tiene rostro en BD)
            verificationType = "registro";
            document.getElementById("cameraModalTitle").textContent = "Registrar Rostro del Usuario";
            
            // Ocultar controles de liveness para registro
            const livenessEl = document.getElementById("livenessIndicator");
            if (livenessEl) livenessEl.style.display = "none";
            const progressEl = document.getElementById("progressContainer");
            if (progressEl) progressEl.style.display = "none";
            
            abrirModal("cameraModal");
            await populateCameraList();
        }

        // ===== Gestión de dispositivos de vídeo y arranque por dispositivo seleccionado =====
        async function populateCameraList() {
            const select = document.getElementById('cameraSelect');
            const startBtn = document.getElementById('btnStartCamera');
            const refreshBtn = document.getElementById('btnRefreshCams');

            if (!select || !startBtn || !refreshBtn) return;

            // Limpiar opciones
            select.innerHTML = '<option value="">Usar cámara por defecto...</option>';

            async function enumerateAndFill() {
                try {
                    let devices = await navigator.mediaDevices.enumerateDevices();
                    let videoInputs = devices;

                    console.info('Listado de dispositivos (raw):', devices); // DEBUG

                    // Si no hay labels (sin permiso), solicitar permiso temporal para obtener nombres
                    const needsPermission = videoInputs.every(d => !d.label);
                    if (needsPermission && navigator.mediaDevices.getUserMedia) {
                        const tmpStream = await navigator.mediaDevices.getUserMedia({ video: true });
                        tmpStream.getTracks().forEach(t => t.stop());
                        devices = await navigator.mediaDevices.enumerateDevices();
                        videoInputs = devices;
                    }

                    // Añadir opciones mostrando deviceId parcial para identificar cámaras virtuales
                    videoInputs.forEach((d, idx) => {
                        const opt = document.createElement('option');
                        // Mostrar label si existe, sino mostrar identificador parcial para ayudar a identificar OBS
                        const shortId = d.deviceId ? d.deviceId.substr(0, 8) : `dev${idx+1}`;
                        opt.value = d.deviceId;
                        opt.textContent = d.label ? `${d.label} (${shortId})` : `Cámara ${idx + 1} (${shortId})`;
                        select.appendChild(opt);
                    });

                    // Si solo hay una cámara y ninguna seleccionada, mantener la opción por defecto
                } catch (err) {
                    console.warn("No se pudieron listar dispositivos de cámara:", err);
                }
            }

            // acciones
            refreshBtn.onclick = () => enumerateAndFill();
            startBtn.onclick = () => {
                const deviceId = select.value || null;
                startCameraWithDevice(deviceId);
            };

            // Soporta Enter en el select para iniciar
            select.onkeydown = (e) => { if (e.key === 'Enter') startBtn.click(); };

            await enumerateAndFill();
        }

        async function startCameraWithDevice(deviceId) {
            try {
                // Si ya existe stream, detenerlo antes
                if (cameraStream) {
                    cameraStream.getTracks().forEach(t => t.stop());
                    cameraStream = null;
                }

                const constraintsExact = deviceId
                    ? { video: { deviceId: { exact: deviceId }, width: { ideal: 640 }, height: { ideal: 480 } } }
                    : { video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' } };

                // Intento principal (con exact si se pasó deviceId)
                try {
                    cameraStream = await navigator.mediaDevices.getUserMedia(constraintsExact);
                } catch (err) {
                    console.warn('Fallo con constraint exact, intentando fallback sin "exact":', err);
                    // Fallback: intentar usar deviceId sin exact (algunos navegadores/drivers funcionan mejor así)
                    const constraintsFallback = deviceId
                        ? { video: { deviceId: deviceId, width: { ideal: 640 }, height: { ideal: 480 } } }
                        : { video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' } };
                    cameraStream = await navigator.mediaDevices.getUserMedia(constraintsFallback);
                }

                const video = document.getElementById("cameraVideo");
                video.srcObject = cameraStream;
                video.onloadedmetadata = () => {
                    video.play();
                    console.log("✅ Video iniciado correctamente con dispositivo:", deviceId || 'default');
                    // iniciar verificación o mostrar botón de captura según tipo
                    if (verificationType === "acceso") {
                        setTimeout(() => iniciarVerificacion(), 300);
                    } else if (verificationType === "registro") {
                        // mostrar botón de captura manual para registro (si no existe ya)
                        document.getElementById("verificationResult").innerHTML = `
                            <button class="btn btn-success w-100 mt-2" onclick="capturarImagenRegistro()">
                                <i class="fas fa-camera me-2"></i>Capturar y Registrar Rostro
                            </button>
                        `;
                    }
                };
            } catch (err) {
                console.error("Error al iniciar la cámara seleccionada:", err);
                // Intentar listar dispositivos para debug adicional
                try { console.info('Enumerando dispositivos al fallar startCameraWithDevice:'); console.table(await navigator.mediaDevices.enumerateDevices()); } catch(e){}
                alert("No se pudo iniciar la cámara: " + (err.message || err) + ". Revisa que la cámara virtual de OBS esté activa y que el navegador tenga permisos.");
            }
        }

        // ===== NUEVA LÓGICA DE DETECCIÓN DE PARPADEO =====
        async function iniciarVerificacion() {
            if (isVerifying) return;
            
            isVerifying = true;
            blinkCount = 0;
            previousEyeState = 'open';
            
            document.getElementById("verificationResult").innerHTML = '';
            
            // Actualizar UI de parpadeo
            updateBlinkUI();
            
            console.log("🎬 Iniciando detección automática...");
            
            // Iniciar detección de parpadeo cada 100ms
            blinkDetectionInterval = setInterval(detectBlinkAndFace, 100);
        }
        
        function detenerVerificacion() {
            isVerifying = false;
            
            if (blinkDetectionInterval) {
                clearInterval(blinkDetectionInterval);
                blinkDetectionInterval = null;
            }
            
            updateFaceBox('no-face');
            document.getElementById("userInfoPanel")?.classList.remove('show');
        }
        
        // Función principal de detección de parpadeo y rostro
        async function detectBlinkAndFace() {
            if (!isVerifying || !cameraStream) return;
            
            const video = document.getElementById('cameraVideo');
            if (!video || !video.videoWidth) return;
            const canvas = document.getElementById('cameraCanvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            // ⚠️ SIMULACIÓN MEJORADA de detección facial (PARA DEMOSTRACIÓN)
            // ⚠️ En producción REAL, integrar face-api.js o TensorFlow.js
            
            // ✅ MEJORADO: Simulación más realista con mayor probabilidad de detección
            const faceDetectedNow = Math.random() > 0.05; // 95% probabilidad
            
            if (faceDetectedNow) {
                faceDetected = true;
                
                // Simular posición de la cara con movimiento SUAVE
                const videoWidth = video.videoWidth;
                const videoHeight = video.videoHeight;
                
                // Si es la primera detección, inicializar en el centro
                if (currentFaceX === null) {
                    currentFaceX = videoWidth / 2;
                    currentFaceY = videoHeight / 2;
                }
                
                // Generar nueva posición objetivo con menos variación
                targetFaceX = videoWidth / 2 + (Math.random() - 0.5) * 60; // ±30px
                targetFaceY = videoHeight / 2 + (Math.random() - 0.5) * 40; // ±20px
                
                // Interpolar suavemente hacia la posición objetivo
                currentFaceX += (targetFaceX - currentFaceX) * smoothingFactor;
                currentFaceY += (targetFaceY - currentFaceY) * smoothingFactor;
                
                const faceWidth = 300;
                const faceHeight = 350;
                
                // Actualizar posición del cuadro
                updateFaceBox('face-detected', {
                    x: currentFaceX - faceWidth / 2,
                    y: currentFaceY - faceHeight / 2,
                    width: faceWidth,
                    height: faceHeight
                });
                
                // Simulación de detección de parpadeo MEJORADA
                const isEyeClosed = Math.random() > 0.75; // 25% probabilidad
                
                // Detectar transición de abierto → cerrado → abierto
                if (previousEyeState === 'open' && isEyeClosed) {
                    previousEyeState = 'closed';
                    console.log('👁️ Ojo detectado como CERRADO');
                } else if (previousEyeState === 'closed' && !isEyeClosed) {
                    // ¡Parpadeo completado!
                    blinkCount++;
                    previousEyeState = 'open';
                    console.log(`✅ Parpadeo ${blinkCount} detectado!`);
                    updateBlinkUI();
                    
                    // Vibración táctil si está disponible
                    if (navigator.vibrate) {
                        navigator.vibrate(50);
                    }
                    
                    if (blinkCount >= requiredBlinks) {
                        // Parpadeos completados, proceder con verificación
                        console.log('🎉 3 parpadeos completados! Verificando usuario...');
                        clearInterval(blinkDetectionInterval);
                        await realizarVerificacionFacial();
                    }
                }
            } else {
                faceDetected = false;
                currentFaceX = null; // Reset para próxima detección
                currentFaceY = null;
                updateFaceBox('no-face');
            }
        }
        
        // Actualizar UI del contador de parpadeos
        function updateBlinkUI() {
            const blinkCountEl = document.getElementById('blinkCount');
            const status = document.getElementById('blinkStatus');

            if (blinkCountEl) blinkCountEl.textContent = `${blinkCount} / ${requiredBlinks}`;
            if (!status) return;

            if (blinkCount === 0) {
                status.className = 'blink-status waiting';
                status.innerHTML = '<i class="fas fa-eye"></i> Mira a la cámara y parpadea 3 veces';
            } else if (blinkCount < requiredBlinks) {
                status.className = 'blink-status verifying';
                status.innerHTML = `<i class="fas fa-eye-slash"></i> ¡Bien! Parpadea ${requiredBlinks - blinkCount} vez más`;
            } else {
                status.className = 'blink-status success';
                status.innerHTML = '<i class="fas fa-check-circle"></i> ¡Parpadeos completados! Verificando...';
            }
        }
        
        // Actualizar cuadro de detección facial (rojo/amarillo/verde)
        function updateFaceBox(state, position = null) {
            const box = document.getElementById('faceBox');
            const label = document.getElementById('detectionLabel');
            if (!box || !label) return;
            
            box.className = 'face-detection-box ' + state;
            
            // Si hay posición, mover el cuadro
            if (position) {
                box.style.left = `${position.x}px`;
                box.style.top = `${position.y}px`;
                box.style.width = `${position.width}px`;
                box.style.height = `${position.height}px`;
                box.style.transform = '';
            } else {
                // Posición centrada por defecto
                box.style.left = '50%';
                box.style.top = '50%';
                box.style.transform = 'translate(-50%, -50%)';
                box.style.width = '';
                box.style.height = '';
            }
            
            if (state === 'no-face') {
                label.innerHTML = '<i class="fas fa-user-slash"></i> Sin rostro detectado';
                document.getElementById("userInfoPanel")?.classList.remove('show');
            } else if (state === 'face-detected') {
                label.innerHTML = '<i class="fas fa-user"></i> Rostro detectado';
                // Mostrar panel de info (con datos de ejemplo por ahora)
                mostrarInfoUsuarioSimulada();
            } else if (state === 'face-recognized') {
                label.innerHTML = '<i class="fas fa-check-circle"></i> Usuario reconocido';
            }
        }
        
        // Función para mostrar información simulada del usuario
        function mostrarInfoUsuarioSimulada() {
            const panel = document.getElementById("userInfoPanel");
            const nameEl = document.getElementById("userInfoName");
            const cargoEl = document.getElementById("userInfoCargo");
            const idEl = document.getElementById("userInfoId");

            if (!panel) return; // Si el panel no está en el DOM, salir sin lanzar error

            // Comprobar y actualizar solo los elementos existentes
            if (nameEl) nameEl.textContent = "Analizando...";
            if (cargoEl) cargoEl.innerHTML = `
                <i class="fas fa-briefcase"></i>
                <span>Verificando identidad...</span>
            `;
            if (idEl) idEl.textContent = "ID: Reconociendo...";

            panel.classList.add('show');
        }
        
        // Función para actualizar info real del usuario tras reconocimiento
        function actualizarInfoUsuario(userData) {
            const nameEl = document.getElementById("userInfoName");
            const cargoEl = document.getElementById("userInfoCargo");
            const idEl = document.getElementById("userInfoId");
            const photoImg = document.getElementById("userPhotoImg");

            if (nameEl) nameEl.textContent = userData.nombre || "Usuario desconocido";
            if (cargoEl) cargoEl.innerHTML = `
                <i class="fas fa-briefcase"></i>
                <span>${userData.cargo || 'Sin cargo'}</span>
            `;
            if (idEl) idEl.textContent = `ID: #${userData.usuario_id || 'N/A'}`;

            // Mostrar foto si existe y si el elemento está presente
            if (userData.foto && photoImg) {
                photoImg.src = `data:image/jpeg;base64,${userData.foto}`;
                photoImg.style.display = 'block';
                const placeholder = photoImg.parentElement?.querySelector('div');
                if (placeholder) placeholder.style.display = 'none';
            }
        }
        
        // Realizar verificación facial final (después de parpadeos)
        async function realizarVerificacionFacial() {
            try {
                updateFaceBox('face-detected');
                
                const video = document.getElementById("cameraVideo");
                const canvas = document.getElementById("cameraCanvas");
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext("2d").drawImage(video, 0, 0);
                const imageB64 = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
                
                const formData = new FormData();
                formData.append("imagen_facial", imageB64);
                formData.append("dispositivo_id", "web_operador_blink");

                if (verificationType === "registro" && currentUserId) {
                    formData.append("usuario_id", currentUserId);
                }
                
                const endpoint = verificationType === "registro" ? "/biometria/create" : "/acceso/camara";
                const response = await fetch(`${API_URL}${endpoint}`, {
                    method: "POST",
                    headers: getAuthHeaders(),
                    body: formData
                });
                
                const data = await response.json();
                
                console.log("📥 Respuesta del backend:", data); // Debug
                
                if (data.status || data.success) {
                    updateFaceBox('face-recognized');
                    
                    // Obtener datos completos del usuario si solo tenemos el ID
                    let userData = {
                        nombre: data.nombre || data.nombre_completo || `Usuario ${data.usuario_id}`,
                        cargo: data.cargo || 'Sin especificar',
                        usuario_id: data.usuario_id || data.id_usuario,
                        foto: data.foto || data.imagen_facial || imageB64
                    };
                    
                    // Si solo tenemos ID, consultar datos completos
                    if (!data.nombre && !data.nombre_completo && data.usuario_id) {
                        try {
                            const userRes = await fetch(`${API_URL}/usuarios/all`, { 
                                headers: getAuthHeaders() 
                            });
                            const usersData = await userRes.json();
                            const users = usersData.data || usersData;
                            const foundUser = users.find(u => u.id_usuario === data.usuario_id);
                            
                            if (foundUser) {
                                userData = {
                                    nombre: foundUser.nombre_completo || foundUser.nombre || `Usuario ${data.usuario_id}`,
                                    cargo: foundUser.cargo || 'Sin especificar',
                                    usuario_id: data.usuario_id,
                                    foto: foundUser.imagen_facial || imageB64
                                };
                                console.log("✅ Datos de usuario obtenidos:", userData);
                            }
                        } catch (err) {
                            console.warn("⚠️ No se pudieron obtener datos adicionales del usuario");
                        }
                    }
                    
                    // Actualizar panel de información con datos reales
                    actualizarInfoUsuario(userData);
                    
                    document.getElementById("verificationResult").innerHTML = `
                        <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">
                            <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--green-400); margin-bottom: 1rem;"></i>
                            <h3 style="color: var(--green-400); margin-bottom: 0.5rem;">✅ ${verificationType === "registro" ? "Registro Exitoso" : "Acceso Permitido"}</h3>
                            <p style="color: white; font-size: 1.125rem; margin-bottom: 0.5rem;">${userData.nombre}</p>
                            <p style="color: var(--slate-300); font-size: 0.875rem;">${userData.cargo} - ID: ${userData.usuario_id}</p>
                        </div>
                    `;
                    
                    // Esperar 3 segundos para ver la info antes de cerrar
                    setTimeout(() => {
                        cerrarModal();
                        
                        // Mostrar modal informativo según el tipo de operación
                        if (verificationType === "acceso") {
                            // Pasar datos completos al modal
                            mostrarModalAcceso({
                                ...data,
                                ...userData,
                                metodo: "Reconocimiento Facial",
                                foto: userData.foto
                            });
                            cargarUltimosAccesos();
                        } else {
                            mostrarModalRegistro({
                                ...data,
                                ...userData
                            }, "Reconocimiento Facial");
                        }
                    }, 3000);
                } else {
                    updateFaceBox('no-face');
                    document.getElementById("verificationResult").innerHTML = `
                        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">
                            <i class="fas fa-times-circle" style="font-size: 3rem; color: var(--red-400); margin-bottom: 1rem;"></i>
                            <h3 style="color: var(--red-400); margin-bottom: 0.5rem;">❌ ${verificationType === "registro" ? "Registro Fallido" : "Acceso Denegado"}</h3>
                            <p style="color: var(--slate-300); font-size: 0.875rem;">${data.mensaje || data.message || "No se pudo verificar el rostro"}</p>
                        </div>
                    `;
                    
                    setTimeout(() => {
                        detenerVerificacion();
                        // Mostrar modal de error
                        data.metodo = "Reconocimiento Facial";
                        if (verificationType === "acceso") {
                            mostrarModalAcceso(data);
                        } else {
                            mostrarModalRegistro(data, "Reconocimiento Facial");
                        }
                    }, 2000);
                }
            } catch (error) {
                console.error('Error en verificación facial:', error);
                document.getElementById("verificationResult").innerHTML = `
                    <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--red-400); margin-bottom: 1rem;"></i>
                        <h3 style="color: var(--red-400);">Error</h3>
                        <p style="color: var(--slate-300); font-size: 0.875rem;">${error.message || error}</p>
                    </div>
                `;
                detenerVerificacion();
            }
        }

        // Captura manual para registro
        async function capturarImagenRegistro() {
            const video = document.getElementById("cameraVideo");
            const canvas = document.getElementById("cameraCanvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext("2d").drawImage(video, 0, 0);
            const imageB64 = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
            
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
            
            showLoading();
            try {
                const formData = new FormData();
                formData.append("id_usuario", currentUserId);
                formData.append("imagen_facial", imageB64);
                
                const res = await fetch(`${API_URL}/biometria/create`, {
                    method: "POST",
                    headers: getAuthHeaders(),
                    body: formData
                });
                
                const data = await res.json();
                
                if (data.success) {
                    alert(`✅ Rostro registrado exitosamente para el usuario ${currentUserId}`);
                    cerrarModal();
                    document.getElementById("verificationResult").innerHTML = "";
                } else {
                    alert("❌ Error: " + (data.message || "No se pudo registrar"));
                }
            } catch (err) {
                alert("Error: " + err.message);
            } finally {
                hideLoading();
            }
        }
        
        async function buscarUsuarios() {
            const nombre = document.getElementById("searchNombre").value.trim().toLowerCase();
            const codigo = document.getElementById("searchCodigo").value.trim();
            const estado = document.getElementById("searchEstado").value;
            
            try {
                // Cargar usuarios y biometrías en paralelo
                const [resUsuarios, resBiometrias] = await Promise.all([
                    fetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() }),
                    fetch(`${API_URL}/biometria/all`, { headers: getAuthHeaders() })
                ]);
                
                const dataUsuarios = await resUsuarios.json();
                const dataBiometrias = await resBiometrias.json();
                
                let usuarios = Array.isArray(dataUsuarios) ? dataUsuarios : (dataUsuarios.data || []);
                const biometrias = Array.isArray(dataBiometrias) ? dataBiometrias : (dataBiometrias.data || []);
                
                // Aplicar filtros en tiempo real
                if (nombre) usuarios = usuarios.filter(u => u.nombre_completo.toLowerCase().includes(nombre));
                if (codigo) usuarios = usuarios.filter(u => String(u.id_usuario).includes(codigo));
                if (estado) usuarios = usuarios.filter(u => String(u.estado) === estado);
                
                // Limitar a 50 resultados
                usuarios = usuarios.slice(0, 50);
                
                const tbody = document.getElementById("resultadosBusqueda");
                if (usuarios.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" class="empty-state"><i class="fas fa-search"></i><p>No se encontraron resultados</p></td></tr>`;
                    return;
                }
                
                tbody.innerHTML = usuarios.map(u => {
                    // Buscar biometrías del usuario
                    const bioUsuario = biometrias.filter(b => b.id_usuario === u.id_usuario);
                    const rfidData = bioUsuario.find(b => b.tipo_biometria === 'RFID');
                    const facialData = bioUsuario.find(b => b.tipo_biometria === 'FACIAL');
                    const huellaData = bioUsuario.find(b => b.tipo_biometria === 'HUELLA');
                    
                    return `
                        <tr>
                            <td><strong>${u.id_usuario}</strong></td>
                            <td>${u.nombre_completo}</td>
                            <td>${u.cargo}</td>
                            <td>${rfidData ? `<span class="badge badge-info">${rfidData.dato_biometrico || 'Registrado'}</span>` : '<span class="badge badge-secondary">No registrado</span>'}</td>
                            <td>${facialData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                            <td>${huellaData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                            <td><span class="badge ${u.estado ? "badge-success" : "badge-danger"}">${u.estado ? "Activo" : "Inactivo"}</span></td>
                            <td>${u.fecha_registro || '-'}</td>
                        </tr>
                    `;
                }).join("");
            } catch (err) {
                console.error("Error buscando usuarios:", err);
                const tbody = document.getElementById("resultadosBusqueda");
                tbody.innerHTML = `<tr><td colspan="8" class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error cargando datos</p></td></tr>`;
            }
        }
        async function crearUsuarioBase() {
            const nombre = document.getElementById("regNombre").value.trim();
            const cargo = document.getElementById("regCargo").value;
            
            if (!nombre || !cargo) {
                mostrarModalRegistro({ success: false, mensaje: "Nombre y cargo son obligatorios" }, "Usuario");
                return;
            }
            
            showLoading();
            try {
                // Valores automáticos
                const estado = true; // Siempre activo al crear
                const fecha = new Date().toISOString().split("T")[0]; // Fecha de hoy
                
                const formData = new FormData();
                formData.append("nombre_completo", nombre);
                formData.append("cargo", cargo);
                formData.append("estado", estado);
                formData.append("fecha_registro", fecha);
                
                const res = await fetch(`${API_URL}/usuarios/create`, {
                    method: "POST", 
                    headers: getAuthHeaders(), 
                    body: formData
                });
                const data = await res.json();
                
                console.log("Respuesta del servidor:", data); // Debug
                
                hideLoading();
                
                if (data.success) {
                    // Intentar obtener el ID de diferentes formas
                    let userId = data.data?.id_usuario || data.id_usuario || data.data?.id || null;
                    
                    // Si no viene el ID, buscar el último usuario creado
                    if (!userId) {
                        console.warn("ID no encontrado en respuesta, buscando último usuario...");
                        const usuariosRes = await fetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() });
                        const usuariosData = await usuariosRes.json();
                        const usuarios = Array.isArray(usuariosData) ? usuariosData : (usuariosData.data || []);
                        
                        // Buscar el usuario que acabamos de crear por nombre
                        const usuarioCreado = usuarios.find(u => u.nombre_completo === nombre && u.cargo === cargo);
                        userId = usuarioCreado?.id_usuario;
                    }
                    
                    if (userId) {
                        currentUserId = userId;
                        document.getElementById("usuarioCreado").innerHTML = `
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>
                                <strong>✅ Usuario creado exitosamente</strong><br>
                                <div class="mt-2">
                                    <strong>ID:</strong> ${currentUserId}<br>
                                    <strong>Nombre:</strong> ${nombre}<br>
                                    <strong>Cargo:</strong> ${cargo}<br>
                                    <strong>Estado:</strong> <span class="badge badge-success">Activo</span>
                                </div>
                            </div>`;
                        document.getElementById("usuarioIdBio").textContent = currentUserId;
                        document.getElementById("seccionBiometria").style.display = "block";
                        
                        // Limpiar formulario
                        document.getElementById("regNombre").value = "";
                        document.getElementById("regCargo").value = "";
                        
                        // Mostrar modal de éxito
                        mostrarModalRegistro({
                            success: true,
                            mensaje: "Usuario registrado correctamente en el sistema",
                            usuario_id: currentUserId,
                            nombre: nombre
                        }, "Usuario Base");
                    } else {
                        mostrarModalRegistro({ success: false, mensaje: "Usuario creado pero no se pudo obtener el ID. Recarga la página y busca el usuario." }, "Usuario");
                    }
                } else {
                    mostrarModalRegistro({ success: false, mensaje: data.message || "No se pudo crear usuario" }, "Usuario");
                }
            } catch (err) {
                console.error("Error completo:", err);
                hideLoading();
                mostrarModalRegistro({ success: false, mensaje: "Error de conexión: " + err.message }, "Usuario");
            }
        }
        async function registrarRFID() {
            const rfid = document.getElementById("bioRFID").value.trim();
            if (!rfid || !currentUserId) {
                mostrarModalRegistro({ success: false, mensaje: "Ingrese un TAG RFID válido" }, "RFID");
                return;
            }
            showLoading();
            try {
                const formData = new FormData();
                formData.append("id_usuario", currentUserId);  // ✅ Backend espera "id_usuario"
                formData.append("rfid_tag", rfid);
                
                console.log("📤 Registrando RFID:", { id_usuario: currentUserId, rfid_tag: rfid });
                
                const res = await fetch(`${API_URL}/biometria/create`, {
                    method: "POST", 
                    headers: getAuthHeaders(), 
                    body: formData
                });
                const data = await res.json();
                
                console.log("📥 Respuesta RFID:", data);
                
                hideLoading();
                
                // Agregar ID de usuario a la respuesta
                data.id_usuario = currentUserId;
                
                // Mostrar modal informativo
                mostrarModalRegistro(data, "RFID");
                
                if (data.success) {
                    document.getElementById("bioRFID").value = ""; // Limpiar input
                }
            } catch (err) {
                console.error("❌ Error registrando RFID:", err);
                hideLoading();
                mostrarModalRegistro({ success: false, mensaje: "Error de conexión: " + err.message }, "RFID");
            }
        }
        async function capturarHuella() {
            alert("Funcionalidad de huella requiere hardware especializado");
        }
        function logout() {
            if (confirm("¿Cerrar sesión?")) {
                sessionStorage.clear();
                window.location.href = "login.html";
            }
        }
        document.addEventListener("DOMContentLoaded", () => {
            // Cerrar cualquier modal que haya quedado abierto
            hideLoading();
            const modals = document.querySelectorAll('.modal-backdrop, .access-modal, .info-modal');
            modals.forEach(m => m.remove());
            document.body.style.overflow = 'auto';
            
            const user = JSON.parse(sessionStorage.getItem("usuario") || "{}");
            if (user.nombre) {
                document.getElementById("userName").textContent = user.nombre;
                document.getElementById("userAvatar").textContent = user.nombre.charAt(0).toUpperCase();
            }
            
            // Activar tab de validación por defecto
            showTab('validacion');
            
            cargarUltimosAccesos();
            
            // Event listeners para búsqueda en tiempo real
            document.getElementById("searchNombre").addEventListener("input", buscarUsuarios);
            document.getElementById("searchCodigo").addEventListener("input", buscarUsuarios);
            document.getElementById("searchEstado").addEventListener("change", buscarUsuarios);
        });
        
        /* DEBUG: forzar permiso, listar dispositivos y mostrar settings del track */
async function listCamerasDebug() {
    try {
        console.log("➡️ Comprobando estado de permiso para cámara...");
        // Estado de permiso (si el navegador soporta Permissions API)
        if (navigator.permissions && navigator.permissions.query) {
            try {
                const p = await navigator.permissions.query({ name: 'camera' });
                console.log("Permission state for camera:", p.state);
            } catch (e) {
                console.log("Permissions API (camera) no disponible o denegada:", e);
            }
        }

        // Forzar prompt de permiso y obtener stream temporal
        let tmpStream = null;
        try {
            tmpStream = await navigator.mediaDevices.getUserMedia({ video: true });
            console.log("✅ getUserMedia OK — stream obtenido. Deteniendo pistas...");
            tmpStream.getTracks().forEach(t => t.stop());
        } catch (err) {
            console.warn("❌ getUserMedia falló o permiso denegado:", err);
            // continuar para intentar enumerateDevices de todas formas
        }

        // Enumerar dispositivos tras (posible) permiso
        const devices = await navigator.mediaDevices.enumerateDevices();
        console.table(devices);

        // Si hay al menos un track de video en tmpStream, mostrar settings
        if (tmpStream) {
            const vTracks = tmpStream.getVideoTracks();
            if (vTracks.length) {
                console.log("Video track settings:", vTracks[0].getSettings());
                console.log("Video track constraints:", vTracks[0].getConstraints());
            }
        }

        // Consejos contextuales
        const videoInputs = devices.filter(d => d.kind === 'videoinput');
        if (videoInputs.length === 0) {
            alert('No se detectaron cámaras. Asegúrate de que OBS Virtual Camera esté iniciada y de que la página tenga permiso de cámara.');
        } else {
            const unlabeled = videoInputs.every(d => !d.label);
            if (unlabeled) {
                alert('Las cámaras aparecen sin etiqueta. Asegura permiso de cámara para este sitio (candado → Cámara) y recarga la página.');
            } else {
                alert('Listado de cámaras en consola (F12). Revisa labels para identificar la cámara virtual de OBS.');
            }
        }

        return devices;
    } catch (e) {
        console.error("Error en listCamerasDebug:", e);
        alert("Error al listar cámaras: " + (e.message || e));
        return [];
    }
}

/* Helper que intenta iniciar la cámara virtual por deviceId parcial (debug) */
async function tryStartByPartialId(partial) {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputs = devices.filter(d => d.kind === 'videoinput');
        const found = videoInputs.find(d => (d.label && d.label.toLowerCase().includes(partial.toLowerCase())) || (d.deviceId && d.deviceId.includes(partial)));
        if (!found) {
            alert("No se encontró cámara que coincida con: " + partial + ". Revisa console.table(enumerateDevices).");
            return;
        }
        console.log("Intentando iniciar cámara encontrada:", found);
        await startCameraWithDevice(found.deviceId);
    } catch (e) {
        console.error("tryStartByPartialId error:", e);
        alert("Error al intentar iniciar cámara: " + (e.message || e));
    }
}

// Exponer helpers globalmente para invocarlos desde la consola
window.listCamerasDebug = listCamerasDebug;
window.tryStartByPartialId = tryStartByPartialId;