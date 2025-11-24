const API_URL = "http://localhost:8000";
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
        let validacionPollInterval = null;
        
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
                        document.body.style.overflow = 'auto';
                    }

            // Detener verificación de parpadeos si estaba activa
            try { detenerVerificacion(); } catch(e) { /* ignore if not defined */ }

            // Detener cámara si estaba activa
            if (cameraStream) {
                try { cameraStream.getTracks().forEach(t => t.stop()); } catch (e) { /* ignore */ }
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
                    // Refrescar lista de usuarios si está visible
                    try { buscarUsuarios(); } catch(e) {}
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
        
        // Helper seguro para llamadas fetch: maneja status HTTP y parsing JSON robusto
        async function safeFetch(url, options = {}) {
            try {
                const res = await fetch(url, options);
                const text = await res.text().catch(() => '');
                let data = null;
                try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { raw: text }; }

                if (!res.ok) {
                    const err = new Error(`HTTP ${res.status} ${res.statusText}` + (text ? `: ${text}` : ''));
                    err.status = res.status;
                    err.body = data;
                    throw err;
                }

                return data;
            } catch (err) {
                throw err;
            }
        }
        function showLoading() { document.getElementById("loadingOverlay").classList.add("show"); }
        function hideLoading() { document.getElementById("loadingOverlay").classList.remove("show"); }
        
        
        // ===== MODALES INFORMATIVOS DE ACCESO =====
        function mostrarModalAcceso(data) {
            // Normalizar distintos formatos de respuesta: success, status, resultado, operation
            const isSuccess = !!(
                data?.status === true ||
                data?.success === true ||
                data?.resultado === true ||
                (data?.operation === 'create' && data?.success !== false)
            );
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
                                <span class="access-modal-value">${data.nombre || data.nombre_completo || data.usuario || data.usuario_id || 'Desconocido'}</span>
                            </div>
                            <div class="access-modal-row">
                                <span class="access-modal-label"><i class="fas fa-id-card me-2"></i>ID</span>
                                <span class="access-modal-value">#${data.usuario_id || data.id_usuario || data.id || 'N/A'}</span>
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
                        
                        <div style="display:flex; gap:.5rem; margin-top:1rem;">
                            <button class="btn btn-${isSuccess ? 'success' : 'danger'} w-100" onclick="cerrarModalAcceso()">
                                <i class="fas fa-check me-2"></i>Entendido
                            </button>
                            ${ (data.usuario_id || data.id_usuario || data.id) ? `<button class="btn btn-secondary" onclick="(window.editarUsuarioOperador || (()=>{}))(${data.usuario_id || data.id_usuario || data.id}); cerrarModalAcceso();">Editar Perfil</button>` : ''}
                        </div>
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
        }

        // Actualizar UI con información real del usuario después de verificar/registrar
        function actualizarInfoUsuario(userData) {
            try {
                console.log('🔄 Actualizando UI con usuario:', userData);
                if (!userData) return;

                // Actualizar currentUserId si viene en la respuesta
                if (userData.usuario_id) {
                    currentUserId = userData.usuario_id;
                }

                const panel = document.getElementById('userInfoPanel');
                const nameEl = document.getElementById('userInfoName');
                const cargoEl = document.getElementById('userInfoCargo');
                const idEl = document.getElementById('userInfoId');
                const photoImg = document.getElementById('userPhotoImg');

                if (panel) panel.classList.add('show');
                if (nameEl) nameEl.textContent = userData.nombre || userData.nombre_completo || ('Usuario ' + (userData.usuario_id || userData.id || '')); 
                if (cargoEl) cargoEl.innerHTML = `<i class="fas fa-briefcase"></i> <span>${userData.cargo || ''}</span>`;
                if (idEl) idEl.textContent = 'ID: ' + (userData.usuario_id || userData.id || '—');

                if (photoImg && userData.foto) {
                    photoImg.src = userData.foto.startsWith('data:') ? userData.foto : ('data:image/jpeg;base64,' + userData.foto);
                    photoImg.classList.remove('photo-hidden');
                    const placeholder = document.querySelector('.photo-placeholder');
                    if (placeholder) placeholder.style.display = 'none';
                }

                // Actualizar resumen compacto si existe
                const compact = document.getElementById('usuarioCreadoCompact');
                if (compact) {
                    compact.innerHTML = `
                        <div style="font-weight:700; font-size:1rem;">${userData.nombre || userData.nombre_completo || ''}</div>
                        <div style="color:var(--text-secondary); font-size:0.9rem;">${userData.cargo || ''} • ID #${userData.usuario_id || userData.id || ''}</div>
                    `;
                }

                // Actualizar campo visible de ID en sección biometría
                const usuarioIdBioEl = document.getElementById('usuarioIdBio');
                if (usuarioIdBioEl) usuarioIdBioEl.textContent = userData.usuario_id || userData.id || currentUserId || '';

            } catch (e) {
                console.warn('actualizarInfoUsuario error:', e);
            }
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
            
            if (tabName === "validacion") {
                cargarUltimosAccesos();
                // Iniciar polling ligero para mostrar accesos en tiempo real
                try {
                    if (validacionPollInterval) clearInterval(validacionPollInterval);
                    validacionPollInterval = setInterval(() => cargarUltimosAccesos(), 2000);
                } catch(e) { console.warn('start validacion poll failed', e); }
                // Focus al input oculto para lectores RFID (si existe)
                try { setTimeout(() => document.getElementById('rfidHiddenInput')?.focus(), 300); } catch(e) {}
            } else {
                if (validacionPollInterval) { clearInterval(validacionPollInterval); validacionPollInterval = null; }
            }
            if (tabName === "busqueda") buscarUsuarios(); // Cargar todos los usuarios al abrir
        }
        async function verificarRFID() {
            // Crear modal para ingresar RFID
            const modalHtml = `
                <div class="modal-backdrop" onclick="cerrarModalRFID()"></div>
                <div class="modal-dialog" style="max-width: 400px;">
                    <div style="background: var(--bg-secondary); border-radius: 16px; padding: 2rem; border: 1px solid var(--border);">
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                                        <div class="rfid-icon-circle">
                                            <i class="fas fa-id-card rfid-icon"></i>
                                        </div>
                                        <h3 class="rfid-title">Verificación RFID</h3>
                                        <p class="rfid-subtitle">Ingrese el código de la tarjeta RFID</p>
                        </div>
                        
                        <input 
                            type="text" 
                            id="rfidInput" 
                            placeholder="Ej: ABC123456789"
                            class="form-control"
                            autofocus
                        />
                        
                        <div class="rfid-actions">
                            <button onclick="cerrarModalRFID()" class="btn btn-secondary rfid-action"> <i class="fas fa-times me-2"></i>Cancelar</button>
                            <button onclick="procesarRFID()" class="btn btn-primary rfid-action"> <i class="fas fa-check me-2"></i>Verificar</button>
                        </div>
                    </div>
                </div>
            `;
            
            const modalContainer = document.createElement('div');
            modalContainer.id = 'modalRFID';
            // marcar como modal para que herede estilos (.modal.show) y backdrop funcione
            modalContainer.className = 'modal show';
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);
            
            // Focus en el input
            setTimeout(() => document.getElementById('rfidInput')?.focus(), 100);
            
            // Enter para verificar (adjuntar con guard)
            const rfidEl = document.getElementById('rfidInput');
            if (rfidEl) {
                rfidEl.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') procesarRFID();
                });
            }
        }
        
        function cerrarModalRFID() {
            const modal = document.getElementById('modalRFID');
            if (modal) modal.remove();
            document.body.style.overflow = 'auto';
        }

        async function procesarRFID() {
            const tag = document.getElementById('rfidInput')?.value.trim();
            return procesarRFIDValue(tag);
        }

        // Procesa un valor de tag RFID (puede venir del modal o de un input oculto)
        async function procesarRFIDValue(tag) {
            if (!tag) {
                const el = document.getElementById('rfidInput');
                if (el) el.style.borderColor = 'var(--red)';
                return;
            }

            // Si existe modal abierto, cerrarlo para mostrar resultado
            try { cerrarModalRFID(); } catch(e){}
            showLoading();

            try {
                const res = await fetch(`${API_URL}/acceso/rfid?rfid_tag=${encodeURIComponent(tag)}`, {
                    method: 'POST', headers: getAuthHeaders()
                });

                const text = await res.text().catch(() => '');
                let data = {};
                try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { raw: text }; }

                hideLoading();
                console.log('📥 Respuesta RFID (status ' + res.status + '):', data);
                if (data && data.raw) console.log('📥 Respuesta RFID (raw text):', data.raw);

                const nested = (data && data.data && typeof data.data === 'object') ? data.data : {};
                const usuarioId = data.usuario_id || data.id_usuario || data.id || nested.usuario_id || nested.id_usuario || nested.id || null;

                let isSuccess = !!(data.success === true || data.status === true || data.resultado === true);
                if (!isSuccess && (data.operation === 'create' && data.success !== false)) isSuccess = true;
                if (!isSuccess && String(data.resultado).toLowerCase() === 'permitido') isSuccess = true;

                data.usuario_id = usuarioId;
                data.metodo = 'RFID';
                data.success = isSuccess;

                mostrarModalAcceso(data);
                try { cargarUltimosAccesos(); } catch(e) {}
            } catch (err) {
                hideLoading();
                console.error('❌ Error procesando RFID:', err);
                mostrarModalRegistro({ success: false, mensaje: 'Error de conexión: ' + (err.message || err) }, 'Error');
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
            // Auto-iniciar cámara por defecto para detección en tiempo real (sin pulsar 'Iniciar')
            try {
                startCameraWithDevice(null);
            } catch (e) { console.warn('No se pudo iniciar cámara automáticamente:', e); }
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
            // Para registro queremos iniciar la cámara y mostrar el botón de captura automáticamente
            try { startCameraWithDevice(null); } catch(e) { console.warn('Auto-start camera for registro failed:', e); }
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
                    let videoInputs = devices.filter(d => d.kind === 'videoinput');

                    console.info('Listado de dispositivos (raw):', devices); // DEBUG

                    // Si no hay labels (sin permiso), solicitar permiso temporal para obtener nombres
                    const needsPermission = videoInputs.every(d => !d.label);
                    if (needsPermission && navigator.mediaDevices.getUserMedia) {
                        const tmpStream = await navigator.mediaDevices.getUserMedia({ video: true });
                        tmpStream.getTracks().forEach(t => t.stop());
                        devices = await navigator.mediaDevices.enumerateDevices();
                        videoInputs = devices.filter(d => d.kind === 'videoinput');
                    }

                    // Añadir opciones mostrando deviceId parcial para identificar cámaras virtuales
                    videoInputs.forEach((d, idx) => {
                        const opt = document.createElement('option');
                        const shortId = d.deviceId ? d.deviceId.substr(0, 8) : `dev${idx+1}`;
                        opt.value = d.deviceId;
                        opt.textContent = d.label ? `${d.label} (${shortId})` : `Cámara ${idx + 1} (${shortId})`;
                        select.appendChild(opt);
                    });

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
                    // Fallback: intentar usar deviceId sin exact
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
                        document.getElementById("verificationResult").innerHTML = `
                            <button class="btn btn-success w-100 mt-2" onclick="capturarImagenRegistro()">
                                <i class="fas fa-camera me-2"></i>Capturar y Registrar Rostro
                            </button>
                        `;
                    }
                };
            } catch (err) {
                console.error("Error al iniciar la cámara seleccionada:", err);
                try { console.info('Enumerando dispositivos al fallar startCameraWithDevice:'); console.table(await navigator.mediaDevices.enumerateDevices()); } catch(e){}
                alert("No se pudo iniciar la cámara: " + (err.message || err) + ". Revisa que la cámara virtual de OBS esté activa y que el navegador tenga permisos.");
            }
        }
        
        // Iniciar detección automática (simulada o real según parche)
        async function iniciarVerificacion() {
            if (isVerifying) return;
            
            isVerifying = true;
            blinkCount = 0;
            previousEyeState = 'open';
            
            document.getElementById("verificationResult").innerHTML = '';
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

        // Función principal de detección de parpadeo y rostro (simulada si no hay backend de liveness)
        async function detectBlinkAndFace() {
            if (!isVerifying || !cameraStream) return;
            
            const video = document.getElementById('cameraVideo');
            if (!video || !video.videoWidth) return;
            const canvas = document.getElementById('cameraCanvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            // Simulación mejorada de detección facial para demo
            const faceDetectedNow = Math.random() > 0.05; // 95% probabilidad

            if (faceDetectedNow) {
                faceDetected = true;
                
                const videoWidth = video.videoWidth;
                const videoHeight = video.videoHeight;
                
                if (currentFaceX === null) {
                    currentFaceX = videoWidth / 2;
                    currentFaceY = videoHeight / 2;
                }

                targetFaceX = videoWidth / 2 + (Math.random() - 0.5) * 60;
                targetFaceY = videoHeight / 2 + (Math.random() - 0.5) * 40;

                if (currentFaceX === null) {
                    currentFaceX = targetFaceX;
                    currentFaceY = targetFaceY;
                } else {
                    currentFaceX += (targetFaceX - currentFaceX) * smoothingFactor;
                    currentFaceY += (targetFaceY - currentFaceY) * smoothingFactor;
                }

                updateFaceBox('face-detected', {
                    x: currentFaceX - 80,
                    y: currentFaceY - 80,
                    width: 160,
                    height: 160
                });

                // Simular detección de ojo/parpadeo
                const isEyeClosed = Math.random() > 0.85; // 15% cerrado en una iteración
                if (previousEyeState === 'open' && isEyeClosed) {
                    previousEyeState = 'closed';
                    console.log('👁️ Ojo detectado como CERRADO');
                } else if (previousEyeState === 'closed' && !isEyeClosed) {
                    blinkCount++;
                    previousEyeState = 'open';
                    console.log(`✅ Parpadeo ${blinkCount} detectado!`);
                    updateBlinkUI();
                    
                    if (navigator.vibrate) navigator.vibrate(50);
                    
                    if (blinkCount >= requiredBlinks) {
                        console.log('🎉 Parpadeos completados! Verificando usuario...');
                        clearInterval(blinkDetectionInterval);
                        await realizarVerificacionFacial();
                    }
                }
            } else {
                faceDetected = false;
                currentFaceX = null;
                currentFaceY = null;
                updateFaceBox('no-face');
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
                    // Backend espera `id_usuario` en el form
                    formData.append("id_usuario", currentUserId);
                }
                
                const endpoint = verificationType === "registro" ? "/biometria/create" : "/acceso/camara";
                const response = await fetch(`${API_URL}${endpoint}`, {
                    method: "POST",
                    headers: getAuthHeaders(),
                    body: formData
                });
                
                // Intentar parsear JSON de forma tolerante
                let data = null;
                try { data = await response.json(); } catch (e) { const text = await response.text(); data = { raw: text }; }
                
                console.log("📥 Respuesta del backend (verificación facial):", data);
                
                if (data && (data.status === true || data.success === true)) {
                    updateFaceBox('face-recognized');
                    let userData = {
                        nombre: data.nombre || data.nombre_completo || `Usuario ${data.usuario_id || data.id_usuario}`,
                        cargo: data.cargo || 'Sin especificar',
                        usuario_id: data.usuario_id || data.id_usuario || data.id,
                        foto: data.foto || data.imagen_facial || imageB64
                    };

                    actualizarInfoUsuario(userData);

                    document.getElementById("verificationResult").innerHTML = `\n                        <div class="alert alert-success">\n                            <strong>✅ ${verificationType === "registro" ? "Registro Exitoso" : "Acceso Permitido"}</strong> - ${userData.nombre}\n                        </div>`;

                    setTimeout(async () => {
                        cerrarModal();
                        if (verificationType === "acceso") {
                            mostrarModalAcceso({ ...data, ...userData, metodo: "Reconocimiento Facial", foto: userData.foto });
                            cargarUltimosAccesos();
                        } else {
                            mostrarModalRegistro({ ...data, ...userData }, "Reconocimiento Facial");
                            try { await buscarUsuarios(); } catch(e) { console.warn(e); }
                            try { localStorage.setItem('users_updated', String(Date.now())); } catch(e) {}
                        }
                    }, 1200);
                } else {
                    updateFaceBox('no-face');
                    document.getElementById("verificationResult").innerHTML = `\n                        <div class="alert alert-danger">\n                            <strong>❌ ${verificationType === "registro" ? "Registro Fallido" : "Acceso Denegado"}</strong>\n                            <div>${data?.mensaje || data?.message || data?.raw || 'No se pudo verificar el rostro'}</div>\n                        </div>`;

                    setTimeout(() => { detenerVerificacion(); if (verificationType === 'acceso') mostrarModalAcceso({ ...data, metodo: 'Reconocimiento Facial' }); else mostrarModalRegistro(data, 'Reconocimiento Facial'); }, 1500);
                }
            } catch (error) {
                console.error('Error en verificación facial:', error);
                document.getElementById("verificationResult").innerHTML = `<div class="alert alert-danger">Error: ${error.message || error}</div>`;
                detenerVerificacion();
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
                
                const data = await safeFetch(`${API_URL}/biometria/create`, {
                    method: "POST",
                    headers: getAuthHeaders(),
                    body: formData
                });
                
                console.log("📥 Respuesta RFID:", data);
                
                hideLoading();
                
                // Agregar ID de usuario a la respuesta
                data.id_usuario = currentUserId;
                
                // Mostrar modal informativo
                mostrarModalRegistro(data, "RFID");
                
                if (data.success) {
                    document.getElementById("bioRFID").value = ""; // Limpiar input
                        // Refrescar usuarios y biometrias en la tabla
                        try { await buscarUsuarios(); } catch(e) { console.warn(e); }
                    try { localStorage.setItem('users_updated', String(Date.now())); } catch(e) {}
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

            // Preparar input oculto para lectores RFID (emulan teclado) en pestaña Validación
            try {
                let hidden = document.getElementById('rfidHiddenInput');
                if (!hidden) {
                    hidden = document.createElement('input');
                    hidden.id = 'rfidHiddenInput';
                    hidden.type = 'text';
                    hidden.autocomplete = 'off';
                    hidden.style.position = 'absolute';
                    hidden.style.left = '-9999px';
                    hidden.style.width = '1px';
                    hidden.style.height = '1px';
                    document.body.appendChild(hidden);
                }
                hidden.addEventListener('keydown', async (e) => {
                    if (e.key === 'Enter') {
                        const tag = hidden.value.trim();
                        hidden.value = '';
                        await procesarRFIDValue(tag);
                    }
                });
            } catch(e) { console.warn('rfid hidden init failed', e); }
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

// ===== FUNCIONES FALTANTES (restauradas desde backup) =====
// Captura manual para registro (imagen) - toma foto del video y la envía como base64
async function capturarImagenRegistro() {
    const video = document.getElementById("cameraVideo");
    const canvas = document.getElementById("cameraCanvas");
    if (!video || !canvas) return;
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
        
        const data = await safeFetch(`${API_URL}/biometria/create`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: formData
        });
        
        if (data.success) {
            alert(`✅ Rostro registrado exitosamente para el usuario ${currentUserId}`);
            cerrarModal();
            document.getElementById("verificationResult").innerHTML = "";
            try { await buscarUsuarios(); } catch(e) { console.warn(e); }
            try { localStorage.setItem('users_updated', String(Date.now())); } catch(e) {}
        } else {
            alert("❌ Error: " + (data.message || "No se pudo registrar"));
        }
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        hideLoading();
    }
}

// Cargar últimos accesos (usa /registros/all y mapea nombres desde /usuarios/all)
async function cargarUltimosAccesos() {
    try {
        const dataReg = await safeFetch(`${API_URL}/registros/all`, { headers: getAuthHeaders() });
        const dataUsr = await safeFetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() });

        const registros = Array.isArray(dataReg) ? dataReg : (dataReg.data || []);
        const usuarios = Array.isArray(dataUsr) ? dataUsr : (dataUsr.data || []);

        // Ordenar por fecha_hora desc (si existe) y tomar los 10 más recientes
        registros.sort((a,b) => {
            const A = a.fecha_hora ? new Date(a.fecha_hora).getTime() : 0;
            const B = b.fecha_hora ? new Date(b.fecha_hora).getTime() : 0;
            return B - A;
        });
        const recent = registros.slice(0, 10);

        const tbody = document.getElementById('ultimosAccesos');
        if (!tbody) return;

        if (!recent.length) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-state"><i class="fas fa-inbox"></i><p>No hay registros recientes</p></td></tr>`;
            return;
        }

        tbody.innerHTML = recent.map(r => {
            const usuario = usuarios.find(u => Number(u.id_usuario) === Number(r.id_usuario)) || {};
            const nombre = usuario.nombre_completo || usuario.nombre || (`#${r.id_usuario}`) || 'Desconocido';
            const fecha = r.fecha_hora ? new Date(r.fecha_hora).toLocaleString('es-ES') : '-';
            const metodo = r.tipo_acceso || r.tipo || 'Desconocido';
            const estado = (r.resultado === true) ? '<span class="badge badge-success">Permitido</span>' : '<span class="badge badge-danger">Denegado</span>';
            return `
                <tr>
                    <td>${fecha}</td>
                    <td>${nombre}</td>
                    <td>${metodo}</td>
                    <td>${estado}</td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error('Error cargando últimos accesos:', err);
    }
}

// Búsqueda de usuarios (para pestaña de búsqueda) - carga usuarios y biometrías
        async function buscarUsuarios() {
    const nombre = (document.getElementById("searchNombre")?.value || "").trim().toLowerCase();
    const codigo = (document.getElementById("searchCodigo")?.value || "").trim();
    const estado = (document.getElementById("searchEstado")?.value || "");
    try {
        const dataUsuarios = await safeFetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() });
        const dataBiometrias = await safeFetch(`${API_URL}/biometria/all`, { headers: getAuthHeaders() });
        let usuarios = Array.isArray(dataUsuarios) ? dataUsuarios : (dataUsuarios.data || []);
        const biometriasRaw = Array.isArray(dataBiometrias) ? dataBiometrias : (dataBiometrias.data || []);

        // Normalizar biometrias para evitar discrepancias en los nombres de campos devueltos por el backend
        const biometrias = biometriasRaw.map(b => ({
            id: b.id || b.id_biometria || null,
            id_usuario: b.id_usuario || b.usuario_id || b.id || b.idUsuario || null,
            tipo: (b.tipo_biometria || b.tipo || b.nombre || '').toString().toUpperCase(),
            dato: b.dato_biometrico || b.dato || b.archivo || b.imagen || b.valor || '',
            raw: b
        }));

        if (nombre) usuarios = usuarios.filter(u => (u.nombre_completo || u.nombre || '').toLowerCase().includes(nombre));
        if (codigo) usuarios = usuarios.filter(u => String(u.id_usuario).includes(codigo));
        if (estado) usuarios = usuarios.filter(u => String(u.estado) === estado);

        usuarios = usuarios.slice(0, 50);

        const tbody = document.getElementById("resultadosBusqueda");
        if (!tbody) return;
        if (usuarios.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-state"><i class="fas fa-search"></i><p>No se encontraron resultados</p></td></tr>`;
            return;
        }

        tbody.innerHTML = usuarios.map(u => {
            const uid = u.id_usuario || u.id || u.usuario_id || u.idUsuario;
            const bioUsuario = biometrias.filter(b => String(b.id_usuario) === String(uid));
            const rfidData = bioUsuario.find(b => b.tipo.includes('RFID') || (b.dato && b.dato.toString().length > 3));
            const facialData = bioUsuario.find(b => b.tipo.includes('FACIAL') || (b.dato && b.dato.toString().length > 50));
            const huellaData = bioUsuario.find(b => b.tipo.includes('HUELLA') || b.tipo.includes('FINGER'));

            return `
                <tr>
                    <td><strong>${u.id_usuario}</strong></td>
                    <td>${u.nombre_completo || u.nombre || '-'}</td>
                    <td>${u.cargo || '-'}</td>
                    <td>${rfidData ? `<span class="badge badge-info">${rfidData.dato || 'Registrado'}</span>` : '<span class="badge badge-secondary">No registrado</span>'}</td>
                    <td>${huellaData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                    <td>${facialData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                    <td><span class="badge ${u.estado ? "badge-success" : "badge-danger"}">${u.estado ? "Activo" : "Inactivo"}</span></td>
                    <td>${u.num_accesos || '-'}</td>
                    <td style="white-space:nowrap;"><button class="btn btn-sm btn-primary" onclick="window.editarUsuarioOperador && window.editarUsuarioOperador(${u.id_usuario})">Editar</button></td>
                </tr>
            `;
        }).join("");
    } catch (err) {
        console.error("Error buscando usuarios:", err);
        const tbody = document.getElementById("resultadosBusqueda");
        if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Error cargando datos</p></td></tr>`;
    }
}


// Escuchar cambios en localStorage para refrescar listas entre pestañas (admin <-> operador)
window.addEventListener('storage', (e) => {
    if (e.key === 'users_updated') {
        try { buscarUsuarios(); cargarUltimosAccesos(); } catch(err){ console.warn('refresh on storage event failed', err); }
    }
});
// Crear usuario base (restaurada) — similar al backup
async function crearUsuarioBase() {
    const nombre = (document.getElementById("regNombre")?.value || "").trim();
    const cargo = (document.getElementById("regCargo")?.value || "");
    
    if (!nombre || !cargo) {
        mostrarModalRegistro({ success: false, mensaje: "Nombre y cargo son obligatorios" }, "Usuario");
        return;
    }
    
    showLoading();
    try {
        const estado = true;
        const fecha = new Date().toISOString().split("T")[0];
        const formData = new FormData();
        formData.append("nombre_completo", nombre);
        formData.append("cargo", cargo);
        formData.append("estado", estado);
        formData.append("fecha_registro", fecha);
        
        const data = await safeFetch(`${API_URL}/usuarios/create`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: formData
        });
        hideLoading();

        if (data.success) {
            let userId = data.data?.id_usuario || data.id_usuario || data.data?.id || null;
            if (!userId) {
                console.warn("ID no encontrado en respuesta, buscando último usuario...");
                const usuariosData = await safeFetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() });
                const usuarios = Array.isArray(usuariosData) ? usuariosData : (usuariosData.data || []);
                const usuarioCreado = usuarios.find(u => (u.nombre_completo || u.nombre) === nombre && u.cargo === cargo);
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
                const usuarioIdBioEl = document.getElementById("usuarioIdBio");
                if (usuarioIdBioEl) usuarioIdBioEl.textContent = currentUserId;
                const seccionBiometria = document.getElementById("seccionBiometria");
                if (seccionBiometria) {
                    seccionBiometria.classList.remove('d-none');
                    seccionBiometria.style.display = 'block';
                }
                const compact = document.getElementById('usuarioCreadoCompact');
                if (compact) {
                    compact.innerHTML = `
                        <div style="font-weight:700; font-size:1rem;">${nombre}</div>
                        <div style="color:var(--text-secondary); font-size:0.9rem;">${cargo} • ID #${currentUserId}</div>
                    `;
                }

                document.getElementById("regNombre").value = "";
                document.getElementById("regCargo").value = "";

                mostrarModalRegistro({ success: true, mensaje: "Usuario registrado correctamente en el sistema", usuario_id: currentUserId, nombre: nombre }, "Usuario Base");
                try { localStorage.setItem('users_updated', String(Date.now())); } catch(e) {}
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

// Abrir flujo de edición/biometría para un usuario existente
async function editarUsuario(id_usuario) {
    try {
        showLoading();
        const res = await fetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() });
        const data = await res.json();
        const usuarios = Array.isArray(data) ? data : (data.data || []);
        const usuario = usuarios.find(u => String(u.id_usuario) === String(id_usuario));
        hideLoading();
        if (!usuario) {
            alert('Usuario no encontrado');
            return;
        }

        currentUserId = usuario.id_usuario;
        // Mostrar sección de biometría
        const seccion = document.getElementById('seccionBiometria');
        if (seccion) {
            seccion.classList.remove('d-none');
            seccion.style.display = 'block';
        }

        // Mostrar ID y resumen compacto
        const usuarioIdBioEl = document.getElementById('usuarioIdBio');
        if (usuarioIdBioEl) usuarioIdBioEl.textContent = currentUserId;

        const compact = document.getElementById('usuarioCreadoCompact');
        if (compact) {
            compact.innerHTML = `
                <div style="font-weight:700; font-size:1rem;">${usuario.nombre_completo || usuario.nombre}</div>
                <div style="color:var(--text-secondary); font-size:0.9rem;">${usuario.cargo || ''} • ID #${currentUserId}</div>
            `;
        }

        // Alternativamente abrir la pestaña de registro
        try { showTab('registro'); } catch(e){}
        // Refresh biometrias list (so UI shows current status)
        try { await buscarUsuarios(); } catch(e){ console.warn(e); }
        // Scroll to biometrics section
        setTimeout(() => {
            const el = document.getElementById('seccionBiometria');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 150);
    } catch (err) {
        hideLoading();
        console.error('editarUsuario error:', err);
        alert('Error al cargar usuario: ' + (err.message || err));
    }
}
// Exponer con nombre específico para evitar colisiones globales con otras páginas
window.editarUsuarioOperador = editarUsuario;