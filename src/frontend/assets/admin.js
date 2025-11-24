const API_URL = "http://localhost:8000";
        function getAuthHeaders() {
            const headers = { 'Content-Type': 'application/json' };
            const token = sessionStorage.getItem('token');
            if (token) headers['Authorization'] = `Bearer ${token}`;
            return headers;
        }

        // Para FormData - NO incluir Content-Type
        function getAuthHeadersFormData() {
            const headers = {};
            const token = sessionStorage.getItem('token');
            if (token) headers['Authorization'] = `Bearer ${token}`;
            return headers;
        }

        // Obtener colores desde las variables CSS del tema para mantener consistencia
        const theme = (() => {
            try {
                const s = getComputedStyle(document.documentElement);
                return {
                    primary: (s.getPropertyValue('--primary') || '#0ea5e9').trim(),
                    success: (s.getPropertyValue('--success') || '#10b981').trim(),
                    warning: (s.getPropertyValue('--warning') || '#f59e0b').trim(),
                    danger: (s.getPropertyValue('--danger') || '#ef4444').trim(),
                    textMuted: (s.getPropertyValue('--text-muted') || '#64748b').trim(),
                    surface: (s.getPropertyValue('--surface') || '#ffffff').trim()
                };
            } catch (e) {
                return { primary: '#0ea5e9', success: '#10b981', warning: '#f59e0b', danger: '#ef4444', textMuted: '#64748b', surface: '#ffffff' };
            }
        })();

        function hexToRgba(hex, alpha) {
            let h = hex.replace('#', '').trim();
            if (h.length === 3) h = h.split('').map(c => c + c).join('');
            const bigint = parseInt(h, 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }

        // Obtener nombre de usuario en forma robusta
        function getUserDisplayName(u) {
            if (!u) return '-';
            const candidates = [u.nombre_completo, u.nombre, u.full_name, u.username, u.nombre_usuario];
            for (const c of candidates) {
                if (c && c.toString().trim() !== '') return c.toString();
            }
            // Intentar concatenar nombre + apellido si existen
            if (u.nombre && u.apellido) return `${u.nombre} ${u.apellido}`;
            return `Usuario ${u.id_usuario || u.id || ''}`.trim();
        }

        // Formato de fecha amigable: DD/MM/YYYY HH:MM
        function formatDateFriendly(dateStr) {
            if (!dateStr) return '-';
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr; // fallback al original
            const pad = n => n.toString().padStart(2, '0');
            const day = pad(d.getDate());
            const month = pad(d.getMonth() + 1);
            const year = d.getFullYear();
            const hours = pad(d.getHours());
            const minutes = pad(d.getMinutes());
            return `${day}/${month}/${year} ${hours}:${minutes}`;
        }

        // Safe setter: asigna textContent si el elemento existe
        function safeSetText(id, value) {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        }

        // Normalizar respuestas de la API: aceptar Array o { data: Array } o { success, data }
        function normalizeApiArray(resp) {
            if (!resp) return [];
            if (Array.isArray(resp)) return resp;
            if (resp.data && Array.isArray(resp.data)) return resp.data;
            if (resp.result && Array.isArray(resp.result)) return resp.result;
            return [];
        }

        function showLoading() {
            document.getElementById('loadingOverlay').classList.add('active');
        }

        function hideLoading() {
            document.getElementById('loadingOverlay').classList.remove('active');
        }
        
        // ===== MODALES INFORMATIVOS =====
        function mostrarModalInfo(data, tipo) {
            const isSuccess = data.success || data.status;
            
            const modalHtml = `
                <div class="modal-overlay active" id="infoModalOverlay">
                    <div class="modal info-modal">
                        <div class="modal-header">
                            <div class="info-modal-header-left">
                                <div class="info-modal-icon ${isSuccess ? 'success' : 'error'}">
                                    <i class="fas fa-${isSuccess ? 'check-circle' : 'times-circle'}"></i>
                                </div>
                                <div>
                                    <h3 class="info-modal-title ${isSuccess ? 'success' : 'error'}">${isSuccess ? '✅ Operación Exitosa' : '❌ Error'}</h3>
                                    <p class="info-modal-subtext">${data.mensaje || data.message || 'Proceso completado'}</p>
                                </div>
                            </div>
                            <button class="btn btn-close" onclick="cerrarModalInfo()">&times;</button>
                        </div>

                        <div class="modal-body info-modal-content">
                            <div class="info-modal-row">
                                <span class="info-modal-label"><i class="fas fa-cog me-2"></i>Tipo</span>
                                <span class="info-modal-value">${tipo}</span>
                            </div>
                            ${data.usuario_id || data.id_usuario ? `
                                <div class="info-modal-row">
                                    <span class="info-modal-label"><i class="fas fa-user me-2"></i>ID Usuario</span>
                                    <span class="info-modal-value">#${data.usuario_id || data.id_usuario}</span>
                                </div>
                            ` : ''}
                            ${data.nombre || data.nombre_completo ? `
                                <div class="info-modal-row">
                                    <span class="info-modal-label"><i class="fas fa-id-card me-2"></i>Nombre</span>
                                    <span class="info-modal-value">${data.nombre || data.nombre_completo}</span>
                                </div>
                            ` : ''}
                            ${data.cargo ? `
                                <div class="info-modal-row">
                                    <span class="info-modal-label"><i class="fas fa-briefcase me-2"></i>Cargo</span>
                                    <span class="info-modal-value">${data.cargo}</span>
                                </div>
                            ` : ''}
                            <div class="info-modal-row">
                                <span class="info-modal-label"><i class="fas fa-clock me-2"></i>Hora</span>
                                <span class="info-modal-value">${new Date().toLocaleTimeString('es-ES')}</span>
                            </div>
                        </div>

                        <div class="modal-footer">
                            <button class="btn ${isSuccess ? 'btn-success' : 'btn-danger'} btn-full" onclick="cerrarModalInfo()">
                                <i class="fas fa-check me-2"></i>Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            const modalContainer = document.createElement('div');
            modalContainer.id = 'infoModal';
            modalContainer.innerHTML = modalHtml;
            document.body.appendChild(modalContainer);
        }
        
        function cerrarModalInfo() {
            const modal = document.getElementById('infoModal');
            if (modal) modal.remove();
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const section = item.dataset.section;
                
                // Update nav
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                item.classList.add('active');
                
                // Update sections
                document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                document.getElementById(section).classList.add('active');
                
                // Load data if needed
                if (section === 'usuarios') cargarUsuarios();
                if (section === 'registros') cargarRegistros();
                if (section === 'torniquetes') cargarTorniquetes();
            });
        });

        // Cargar Estadísticas
        async function cargarEstadisticas() {
            try {
                const [usuarios, registros, biometria, torniquetes] = await Promise.all([
                    fetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() }).then(r => r.json()),
                    fetch(`${API_URL}/registros/all`, { headers: getAuthHeaders() }).then(r => r.json()),
                    fetch(`${API_URL}/biometria/all`, { headers: getAuthHeaders() }).then(r => r.json()),
                    fetch(`${API_URL}/torniquetes/all`, { headers: getAuthHeaders() }).then(r => r.json())
                ]);

                let usuariosData = normalizeApiArray(usuarios);
                const registrosData = normalizeApiArray(registros);
                const biometriaData = normalizeApiArray(biometria);
                const torniquetesData = normalizeApiArray(torniquetes);

                // Si la llamada a usuarios devuelve vacío (posible por permisos o token no presente),
                // intentar usar la cache local `todosLosUsuarios` que puede haber sido cargada por `cargarUsuarios()`
                if ((!usuariosData || usuariosData.length === 0) && Array.isArray(todosLosUsuarios) && todosLosUsuarios.length > 0) {
                    usuariosData = todosLosUsuarios;
                }

                console.log('📊 Datos para estadísticas:', { 
                    usuarios: usuariosData.length, 
                    registros: registrosData.length,
                    biometria: biometriaData.length,
                    torniquetes: torniquetesData.length
                });

                // Estadísticas básicas
                const usuariosActivos = usuariosData.filter(u => u.estado === true || u.estado === 'activo').length;
                // Sólo contar accesos del día para las tarjetas "Accesos Hoy" y el porcentaje
                const hoy = new Date();
                const registrosHoyArray = registrosData.filter(r => {
                    const fechaVal = r.fecha_hora || r.fecha || r.created_at || r.timestamp;
                    if (!fechaVal) return false;
                    const fechaReg = new Date(fechaVal);
                    return fechaReg.toDateString() === hoy.toDateString();
                });
                const registrosHoy = registrosHoyArray.length;
                const registrosExitososHoy = registrosHoyArray.filter(r => r.resultado === true || r.resultado === 1 || r.resultado === '1').length;
                const porcentajeExito = registrosHoy > 0 ? Math.round((registrosExitososHoy / registrosHoy) * 100) : 0;

                safeSetText('totalUsuarios', usuariosData.length);
                safeSetText('usuariosActivos', usuariosActivos);
                safeSetText('totalRegistros', registrosHoy);
                safeSetText('porcentajeExito', porcentajeExito);
                safeSetText('totalBiometria', biometriaData.length);
                // porcentajeBiometria may have been removed from the template; set only if present
                safeSetText('porcentajeBiometria', usuariosData.length > 0 ? Math.round((biometriaData.length / usuariosData.length) * 100) : 0);
                safeSetText('totalTorniquetes', torniquetesData.length);
                safeSetText('torniquetesOnline', torniquetesData.filter(t => t.estado === 'activo' || t.estado === true).length);

                // Crear gráficas
                crearGraficaMetodos(biometriaData);
                crearGraficaAccesos(registrosData);
                crearGraficaEstados(usuariosData);
                crearGraficaExito(registrosData);
            } catch (err) {
                console.error('Error cargando estadísticas:', err);
            }
        }

        // Gráficas con Chart.js
        let chartMetodos, chartAccesos, chartEstados, chartExito;

        function crearGraficaMetodos(biometriaData) {
                    // Renderizamos aquí una checklist simple con los 3 métodos esperados
                    const canvas = document.getElementById('chartMetodos');
                    if (!canvas) return;

                    // Clasificar cada registro biométrico con heurísticas para determinar su método probable
                    let countRFID = 0, countFACIAL = 0, countHUELLA = 0, countUnknown = 0;

                    const looksLikeBase64 = s => /^(?:[A-Za-z0-9+\/]{4})*(?:[A-Za-z0-9+\/]{2}==|[A-Za-z0-9+\/]{3}=)?$/.test(s.replace(/\s+/g, ''));

                    biometriaData.forEach(b => {
                        if (!b) { countUnknown++; return; }
                        // Combine keys and string values for quick search
                        const sampleText = JSON.stringify(b).toUpperCase();

                        // Direct keyword checks
                        if (sampleText.includes('RFID') || sampleText.includes('TAG') || sampleText.includes('DATO_BIOMETRICO') || ('rfid' in b) || ('dato_biometrico' in b)) {
                            countRFID++;
                            return;
                        }

                        if (sampleText.includes('FACIAL') || sampleText.includes('FACE') || sampleText.includes('IMAGEN') || sampleText.includes('ARCHIVO') || sampleText.includes('BASE64') || ('archivo' in b) || ('imagen' in b) || ('foto' in b)) {
                            // If value seems like base64 or file path, consider facial
                            countFACIAL++;
                            return;
                        }

                        if (sampleText.includes('HUELLA') || sampleText.includes('FINGER') || sampleText.includes('TEMPLATE') || ('huella' in b) || ('template' in b) || ('finger' in b) || ('fingerprint' in b)) {
                            countHUELLA++;
                            return;
                        }

                        // If there's a numeric 'tipo' try to infer by looking at other fields in same sample
                        if ('tipo' in b || 'tipo_biometria' in b) {
                            const t = String(b.tipo || b.tipo_biometria || '').toLowerCase();
                            if (t === '1' || t.includes('1')) { countRFID++; return; }
                            if (t === '2' || t.includes('2')) { countFACIAL++; return; }
                            if (t === '3' || t.includes('3')) { countHUELLA++; return; }
                        }

                        // Heuristic: if any string field is long and base64-like, treat as facial
                        const vals = Object.values(b);
                        for (const v of vals) {
                            if (typeof v === 'string' && v.length > 80 && looksLikeBase64(v.trim())) { countFACIAL++; return; }
                        }

                        // Fallback unknown
                        countUnknown++;
                    });

                    const finalRFID = countRFID > 0;
                    const finalFACIAL = countFACIAL > 0;
                    const finalHUELLA = countHUELLA > 0;

                    // Crear HTML de checklist dentro del panel padre del canvas
                    const panel = canvas.parentElement;
                    if (!panel) return;

                    const checklistHtml = `
                        <div class="method-checklist">
                            <div class="method-item">
                                <i class="fas ${finalRFID ? 'fa-check-circle status-ok' : 'fa-times-circle status-err'}"></i>
                                <div class="method-label">RFID</div>
                                <div class="method-status">${finalRFID ? `Registrado (${countRFID})` : 'No registrado'}</div>
                            </div>
                            <div class="method-item">
                                <i class="fas ${finalFACIAL ? 'fa-check-circle status-ok' : 'fa-times-circle status-err'}"></i>
                                <div class="method-label">Reconocimiento Facial</div>
                                <div class="method-status">${finalFACIAL ? `Registrado (${countFACIAL})` : 'No registrado'}</div>
                            </div>
                            <div class="method-item">
                                <i class="fas ${finalHUELLA ? 'fa-check-circle status-ok' : 'fa-times-circle status-err'}"></i>
                                <div class="method-label">Huella</div>
                                <div class="method-status">${finalHUELLA ? `Registrado (${countHUELLA})` : 'No registrado'}</div>
                            </div>
                        </div>
                    `;

                    // Vaciar cualquier gráfico Chart.js previo y sustituir por checklist
                    try {
                        if (chartMetodos) { chartMetodos.destroy(); chartMetodos = null; }
                    } catch (e) { /* no bloquear si falla */ }

                    // Asegurarnos que el canvas no muestre el gráfico, y colocar checklist debajo
                    canvas.style.display = 'none';
                    // Colocar checklist (si ya existía, reemplazar)
                    const existing = panel.querySelector('.method-checklist');
                    if (existing) existing.remove();
                    panel.insertAdjacentHTML('beforeend', checklistHtml);
        }

        function crearGraficaAccesos(registrosData) {
            const ctx = document.getElementById('chartAccesos');
            if (!ctx) return;

            const hoy = new Date();
            const labels = [];
            const datos = [];

            for (let i = 6; i >= 0; i--) {
                const fecha = new Date(hoy);
                fecha.setDate(fecha.getDate() - i);
                labels.push(fecha.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric' }));

                const count = registrosData.filter(r => {
                    if (!r.fecha) return false;
                    const fechaReg = new Date(r.fecha);
                    return fechaReg.toDateString() === fecha.toDateString();
                }).length;
                datos.push(count);
            }

            if (chartAccesos) chartAccesos.destroy();
            chartAccesos = new Chart(ctx, {
                type: 'line',
                data: { labels, datasets: [{ label: 'Accesos', data: datos, borderColor: theme.success, backgroundColor: hexToRgba(theme.success, 0.08), tension: 0.4, fill: true }] },
                options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: theme.textMuted }, grid: { color: hexToRgba(theme.textMuted, 0.08) } }, x: { ticks: { color: theme.textMuted }, grid: { display: false } } } }
            });
        }

        function crearGraficaEstados(usuariosData) {
            const ctx = document.getElementById('chartEstados');
            if (!ctx) return;

            const activos = usuariosData.filter(u => u.estado === true || u.estado === 'activo').length;
            const inactivos = usuariosData.length - activos;

            if (chartEstados) chartEstados.destroy();
            chartEstados = new Chart(ctx, {
                type: 'bar',
                data: { labels: ['Activos', 'Inactivos'], datasets: [{ data: [activos, inactivos], backgroundColor: [theme.success, theme.danger], borderWidth: 0, borderRadius: 8 }] },
                options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: theme.textMuted }, grid: { color: hexToRgba(theme.textMuted, 0.08) } }, x: { ticks: { color: theme.textMuted }, grid: { display: false } } } }
            });
        }

        function crearGraficaExito(registrosData) {
            const ctx = document.getElementById('chartExito');
            if (!ctx) return;

            const exitosos = registrosData.filter(r => r.resultado === true || r.resultado === 1 || r.resultado === '1').length;
            const fallidos = registrosData.length - exitosos;

            if (chartExito) chartExito.destroy();
            chartExito = new Chart(ctx, {
                type: 'doughnut',
                data: { labels: ['Exitosos', 'Fallidos'], datasets: [{ data: [exitosos, fallidos], backgroundColor: [theme.success, theme.danger], borderWidth: 0 }] },
                options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: true, position: 'bottom', labels: { color: theme.textMuted, padding: 15 } } } }
            });
        }

        // USUARIOS
        let todosLosUsuarios = []; // Variable global para almacenar todos los usuarios
        let todasLasBiometrias = []; // Variable global para biometrías
        
        async function cargarUsuarios() {
            showLoading();
            try {
                console.log('🔍 Iniciando carga de usuarios...');
                console.log('📡 URL API:', API_URL);
                
                // Cargar usuarios y biometrías en paralelo
                const [resUsuarios, resBiometrias] = await Promise.all([
                    fetch(`${API_URL}/usuarios/all`, { headers: getAuthHeaders() }),
                    fetch(`${API_URL}/biometria/all`, { headers: getAuthHeaders() })
                ]);
                
                console.log('📥 Respuesta usuarios:', resUsuarios.status, resUsuarios.statusText);
                console.log('📥 Respuesta biometrías:', resBiometrias.status, resBiometrias.statusText);
                
                const dataUsuarios = await resUsuarios.json();
                const dataBiometrias = await resBiometrias.json();

                console.log('📦 Data usuarios:', dataUsuarios);
                console.log('📦 Data biometrías:', dataBiometrias);

                // Guardar todos los usuarios y biometrías en variables globales (soportar distintos formatos)
                todosLosUsuarios = normalizeApiArray(dataUsuarios);
                todasLasBiometrias = normalizeApiArray(dataBiometrias);
                
                console.log(`📊 Cargados ${todosLosUsuarios.length} usuarios y ${todasLasBiometrias.length} registros biométricos`);
                console.log('👥 Usuarios:', todosLosUsuarios);
                
                // Renderizar usuarios
                renderizarUsuarios(todosLosUsuarios);
            } catch (err) {
                console.error('❌ Error completo:', err);
                console.error('❌ Stack:', err.stack);
                document.getElementById('tablaUsuarios').innerHTML = '<tr><td colspan="9" class="table-error-cell">Error al cargar usuarios. Revisa la consola para más detalles.</td></tr>';
                todosLosUsuarios = [];
                todasLasBiometrias = [];
            } finally {
                hideLoading();
            }
        }
        
        // Función para renderizar usuarios en la tabla
        function renderizarUsuarios(usuarios) {
            const tbody = document.getElementById('tablaUsuarios');
            
            console.log('🎨 Renderizando usuarios:', usuarios ? usuarios.length : 0);
            
            if (usuarios && usuarios.length > 0) {
                tbody.innerHTML = usuarios.map(u => {
                    // Buscar biometrías del usuario
                    const bioUsuario = todasLasBiometrias.filter(b => b.id_usuario === u.id_usuario);
                    const rfidData = bioUsuario.find(b => b.tipo_biometria === 'RFID');
                    const facialData = bioUsuario.find(b => b.tipo_biometria === 'FACIAL');
                    const huellaData = bioUsuario.find(b => b.tipo_biometria === 'HUELLA');
                    
                    return `
                        <tr id="usuario-row-${u.id_usuario}">
                            <td><strong>${u.id_usuario || '-'}</strong></td>
                            <td>${getUserDisplayName(u)}</td>
                            <td>${u.cargo || '-'}</td>
                            <td>${rfidData ? `<span class="badge badge-info">${(rfidData.dato_biometrico && rfidData.dato_biometrico !== 'null') ? rfidData.dato_biometrico : 'Registrado'}</span>` : '<span class="badge badge-secondary">No registrado</span>'}</td>
                            <td>${facialData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                            <td>${huellaData ? '<span class="badge badge-success">Activado</span>' : '<span class="badge badge-secondary">Desactivado</span>'}</td>
                            <td>
                                <span class="badge ${u.estado === 'activo' || u.estado === true ? 'badge-success' : 'badge-danger'}">
                                    ${u.estado === true || u.estado === 'activo' ? 'Activo' : 'Inactivo'}
                                </span>
                            </td>
                            <td>${formatDateFriendly(u.fecha_registro || u.fecha || '-')}</td>
                            <td>
                                <button class="btn btn-primary btn-sm" onclick="(window.editarUsuarioAdmin || (()=>{}))(${u.id_usuario})" title="Editar usuario">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="eliminarUsuarioRapido(${u.id_usuario}, '${(getUserDisplayName(u) || 'Usuario').replace(/'/g, "\\'")}');" title="Eliminar usuario">
                                    <i class="fas fa-times"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="9" class="table-empty-cell">No hay usuarios que coincidan con los filtros</td></tr>';
            }
        }
        
        // Función para filtrar usuarios
        function filtrarUsuarios() {
            const searchNombre = document.getElementById('searchNombre').value.toLowerCase().trim();
            const searchCargo = document.getElementById('searchCargo').value.toLowerCase().trim();
            const searchEstado = document.getElementById('searchEstado').value.trim();
            
            console.log('🔍 Filtrando:', { nombre: searchNombre, cargo: searchCargo, estado: searchEstado });
            
            let usuariosFiltrados = todosLosUsuarios;
            
            // Filtrar por nombre
            if (searchNombre) {
                usuariosFiltrados = usuariosFiltrados.filter(u => {
                    const nombre = (u.nombre_completo || u.nombre || '').toLowerCase();
                    return nombre.includes(searchNombre);
                });
            }
            
            // Filtrar por cargo
            if (searchCargo) {
                usuariosFiltrados = usuariosFiltrados.filter(u => {
                    const cargo = (u.cargo || '').toLowerCase();
                    return cargo === searchCargo;
                });
            }
            
            // Filtrar por estado
            if (searchEstado) {
                const estadoBuscado = searchEstado === 'true';
                usuariosFiltrados = usuariosFiltrados.filter(u => {
                    const estado = u.estado === true || u.estado === 'activo';
                    return estado === estadoBuscado;
                });
            }
            
            console.log(`✅ Encontrados ${usuariosFiltrados.length} de ${todosLosUsuarios.length} usuarios`);
            renderizarUsuarios(usuariosFiltrados);
        }
        
        // Función para limpiar filtros
        function limpiarFiltros() {
            document.getElementById('searchNombre').value = '';
            document.getElementById('searchCargo').value = '';
            document.getElementById('searchEstado').value = '';
            renderizarUsuarios(todosLosUsuarios);
            console.log('🧹 Filtros limpiados');
        }

        function abrirModalUsuario(id = null) {
            document.getElementById('modalUsuarioTitle').textContent = id ? 'Editar Usuario' : 'Nuevo Usuario';
            document.getElementById('userId').value = id || '';
            
            if (!id) {
                document.getElementById('formUsuario').reset();
                document.getElementById('fecha_registro').valueAsDate = new Date();
            }
            
            document.getElementById('modalUsuario').classList.add('active');
        }

        function cerrarModalUsuario() {
            document.getElementById('modalUsuario').classList.remove('active');
        }

        async function editarUsuario(id) {
            showLoading();
            try {
                const res = await fetch(`${API_URL}/usuarios/by_id?id_usuario=${id}`, { headers: getAuthHeaders() });
                const data = await res.json();
                
                if (data.success && data.data) {
                    const u = data.data;
                    document.getElementById('userId').value = u.id_usuario;
                    document.getElementById('nombre').value = u.nombre || '';
                    document.getElementById('email').value = u.email || '';
                    document.getElementById('cargo').value = u.cargo || '';
                    document.getElementById('estado').value = u.estado || 'activo';
                    document.getElementById('fecha_registro').value = u.fecha_registro || '';
                    
                    abrirModalUsuario(id);
                } else {
                    mostrarModalInfo({ success: false, mensaje: 'No se pudo cargar el usuario' }, 'Error');
                }
            } catch (err) {
                hideLoading();
                mostrarModalInfo({ success: false, mensaje: 'Error al cargar usuario: ' + err.message }, 'Error');
            } finally {
                hideLoading();
            }
        }

        // Expose admin-specific editor to avoid collisions with operador page
        window.editarUsuarioAdmin = editarUsuario;

        async function guardarUsuario() {
            const userId = document.getElementById('userId').value;
            const nombre = document.getElementById('nombre').value;
            const email = document.getElementById('email').value;
            const cargo = document.getElementById('cargo').value;
            const estado = document.getElementById('estado').value;
            const fecha = document.getElementById('fecha_registro').value;

            if (!nombre || !email || !cargo) {
                alert('Por favor complete todos los campos obligatorios');
                return;
            }

            showLoading();
            try {
                const formData = new FormData();
                formData.append("nombre", nombre);
                formData.append("email", email);
                formData.append("cargo", cargo);
                formData.append("estado", estado);
                formData.append("fecha_registro", fecha);

                let url = `${API_URL}/usuarios/create`;
                if (userId) {
                    formData.append('id_usuario', userId);
                    url = `${API_URL}/usuarios/update`;
                }

                const res = await fetch(url, {
                    method: 'POST',
                    headers: getAuthHeadersFormData(),
                    body: formData
                });

                const data = await res.json();
                hideLoading();

                if (data.success) {
                    cerrarModalUsuario();
                    cargarUsuarios();
                    cargarEstadisticas();
                    mostrarModalInfo({ success: true, mensaje: userId ? 'Usuario actualizado correctamente' : 'Usuario creado correctamente' }, userId ? 'Actualización' : 'Creación');
                } else {
                    mostrarModalInfo({ success: false, mensaje: data.message || 'No se pudo guardar el usuario' }, 'Error');
                }
            } catch (err) {
                hideLoading();
                mostrarModalInfo({ success: false, mensaje: 'Error de conexión: ' + err.message }, 'Error');
            }
        }
        
        // NUEVA FUNCIÓN: Eliminación rápida sin confirmación con auto-refresh
        async function eliminarUsuarioRapido(id, nombre) {
            const row = document.getElementById(`usuario-row-${id}`);
            
            // Animación de eliminación
            if (row) {
                row.style.opacity = '0.5';
                row.style.transition = 'opacity 0.3s';
            }
            
            try {
                const formData = new FormData();
                formData.append("id_usuario", id);
                
                const res = await fetch(`${API_URL}/usuarios/delete`, {
                    method: "POST",
                    headers: getAuthHeadersFormData(),
                    body: formData
                });
                const data = await res.json();
                
                if (data.success) {
                    // Eliminar de la lista local
                    todosLosUsuarios = todosLosUsuarios.filter(u => u.id_usuario !== id);
                    
                    // Eliminar fila con animación
                    if (row) {
                        row.style.opacity = '0';
                        row.style.transform = 'translateX(-20px)';
                        setTimeout(() => {
                            row.remove();
                            // Re-renderizar para actualizar índices
                            filtrarUsuarios(); // Aplica filtros actuales
                        }, 300);
                    }
                    
                    // Actualizar estadísticas sin recargar todo
                    cargarEstadisticas();
                    
                    // Mostrar notificación sutil
                    mostrarNotificacion(`✅ ${nombre} eliminado correctamente`, 'success');
                } else {
                    // Restaurar fila si falla
                    if (row) {
                        row.style.opacity = '1';
                    }
                    mostrarNotificacion(`❌ Error: ${data.message || 'No se pudo eliminar'}`, 'error');
                }
            } catch (err) {
                // Restaurar fila si hay error
                if (row) {
                    row.style.opacity = '1';
                }
                mostrarNotificacion(`❌ Error de conexión: ${err.message}`, 'error');
            }
        }
        
        // Función para mostrar notificaciones temporales
        function mostrarNotificacion(mensaje, tipo = 'success') {
            const notif = document.createElement('div');
            notif.className = `floating-notif ${tipo === 'success' ? 'success' : 'error'}`;

            // Exponer conteos para debugging en la consola (no obligatorio)
            try { window.__bio_counts = { rfid: countRFID, facial: countFACIAL, huella: countHUELLA, unknown: countUnknown }; } catch(e) {}
            notif.textContent = mensaje;
            document.body.appendChild(notif);

            setTimeout(() => {
                notif.classList.add('hide');
                setTimeout(() => notif.remove(), 300);
            }, 3000);
        }
        
        // Agregar estilos de animación
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        // REGISTROS
        async function cargarRegistros() {
            showLoading();
            try {
                const res = await fetch(`${API_URL}/registros/all`, { headers: getAuthHeaders() });
                const data = await res.json();
                const tbody = document.getElementById('tablaRegistros');

                console.log('📋 Registros recibidos:', data);

                const registrosArray = normalizeApiArray(data);

                if (registrosArray && registrosArray.length > 0) {
                    tbody.innerHTML = registrosArray.map(r => {
                        // El campo correcto es 'resultado', no 'status'
                        const esExitoso = r.resultado === true || r.resultado === 1 || r.resultado === '1';
                        const medio = r.tipo_acceso || r.medio || '-';
                        const fecha = r.fecha_hora || r.fecha || '-';

                        // Buscar nombre de usuario si está cargado
                        const usuario = todosLosUsuarios.find(u => (u.id_usuario || u.id || '').toString() === (r.id_usuario || r.usuario || '').toString());
                        const nombreUsuario = usuario ? getUserDisplayName(usuario) : (r.nombre_usuario || r.nombre || r.id_usuario || '-');

                        return `
                            <tr>
                                <td>${r.id_registro || '-'}</td>
                                <td>${nombreUsuario}</td>
                                <td><span class="badge badge-info">${medio}</span></td>
                                <td>
                                    <span class="badge ${esExitoso ? 'badge-success' : 'badge-danger'}">
                                        ${esExitoso ? 'Permitido' : 'Denegado'}
                                    </span>
                                </td>
                                <td>${formatDateFriendly(fecha)}</td>
                                <td>${r.id_torniquete || '-'}</td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" class="table-empty-cell">No hay registros disponibles</td></tr>';
                }
            } catch (err) {
                console.error('Error:', err);
                document.getElementById('tablaRegistros').innerHTML = '<tr><td colspan="6" class="table-error-cell">Error al cargar registros</td></tr>';
            } finally {
                hideLoading();
            }
        }

        // TORNIQUETES
        async function cargarTorniquetes() {
            showLoading();
            try {
                const res = await fetch(`${API_URL}/torniquetes/all`, { headers: getAuthHeaders() });
                const data = await res.json();
                const tbody = document.getElementById('tablaTorniquetes');
                
                if (data.success && data.data && data.data.length > 0) {
                    tbody.innerHTML = data.data.map(t => `
                        <tr>
                            <td>${t.id_torniquete || '-'}</td>
                            <td>${t.nombre || '-'}</td>
                            <td>${t.ubicacion || '-'}</td>
                            <td>
                                <span class="badge ${t.estado === 'activo' ? 'badge-success' : 'badge-danger'}">
                                    ${t.estado || 'N/A'}
                                </span>
                            </td>
                            <td>${t.tipo || '-'}</td>
                            <td>
                                <button class="btn btn-danger btn-sm" onclick="eliminarTorniquete(${t.id_torniquete})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" class="table-empty-cell">No hay torniquetes registrados</td></tr>';
                }
            } catch (err) {
                console.error('Error:', err);
                document.getElementById('tablaTorniquetes').innerHTML = '<tr><td colspan="6" class="table-error-cell">Error al cargar torniquetes</td></tr>';
            } finally {
                hideLoading();
            }
        }

        function abrirModalTorniquete() {
            document.getElementById('formTorniquete').reset();
            document.getElementById('modalTorniquete').classList.add('active');
        }

        function cerrarModalTorniquete() {
            document.getElementById('modalTorniquete').classList.remove('active');
        }

        async function guardarTorniquete() {
            const nombre = document.getElementById('torniquete_nombre').value;
            const ubicacion = document.getElementById('torniquete_ubicacion').value;
            const estado = document.getElementById('torniquete_estado').value;
            const tipo = document.getElementById('torniquete_tipo').value;

            if (!nombre || !ubicacion) {
                mostrarModalInfo({ success: false, mensaje: 'Complete todos los campos' }, 'Validación');
                return;
            }

            showLoading();
            try {
                const res = await fetch(`${API_URL}/torniquetes/create`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ nombre, ubicacion, estado, tipo })
                });
                
                const data = await res.json();
                hideLoading();
                
                if (data.success) {
                    cerrarModalTorniquete();
                    cargarTorniquetes();
                    cargarEstadisticas();
                    mostrarModalInfo({ success: true, mensaje: 'Torniquete creado exitosamente' }, 'Creación de Torniquete');
                } else {
                    mostrarModalInfo({ success: false, mensaje: data.message || 'No se pudo crear' }, 'Error');
                }
            } catch (err) {
                hideLoading();
                mostrarModalInfo({ success: false, mensaje: 'Error: ' + err.message }, 'Error');
            }
        }

        async function eliminarTorniquete(id) {
            if (!confirm('¿Eliminar este torniquete?')) return;
            
            showLoading();
            try {
                const res = await fetch(`${API_URL}/torniquetes/delete/${id}`, {
                    method: 'POST',
                    headers: getAuthHeaders()
                });
                
                const data = await res.json();
                hideLoading();
                
                if (data.success) {
                    cargarTorniquetes();
                    cargarEstadisticas();
                    mostrarModalInfo({ success: true, mensaje: 'Torniquete eliminado exitosamente' }, 'Eliminación de Torniquete');
                } else {
                    mostrarModalInfo({ success: false, mensaje: data.message || 'No se pudo eliminar' }, 'Error');
                }
            } catch (err) {
                hideLoading();
                mostrarModalInfo({ success: false, mensaje: 'Error: ' + err.message }, 'Error');
            }
        }

        function cerrarSesion() {
            if (confirm('¿Desea cerrar sesión?')) {
                sessionStorage.clear();
                window.location.href = 'login.html';
            }
        }

        // Initialize: cargar primero usuarios/biometrías y luego estadísticas para asegurar datos cache
        window.addEventListener('load', async () => {
            try {
                // Intentar cargar usuarios y biometrías para poblar cache
                await cargarUsuarios();
            } catch (e) {
                console.warn('No se pudo cargar usuarios en init:', e);
            }
            // Luego cargar estadísticas (usa cache si es necesario)
            cargarEstadisticas();
        });