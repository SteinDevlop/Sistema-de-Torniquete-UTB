       import API_URL from './api_root.js';
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
                <div class="modal-backdrop"></div>
                <div class="modal" style="display: block;">
                    <div class="info-modal">
                        <div class="info-modal-header">
                            <div class="info-modal-icon ${isSuccess ? 'success' : 'error'}">
                                <i class="fas fa-${isSuccess ? 'check-circle' : 'times-circle'}"></i>
                            </div>
                            <h3 style="color: ${isSuccess ? 'var(--green-light)' : 'var(--red-light)'}; margin-bottom: 0.5rem;">
                                ${isSuccess ? '✅ Operación Exitosa' : '❌ Error'}
                            </h3>
                            <p style="color: var(--text-secondary); font-size: 0.875rem;">${data.mensaje || data.message || 'Proceso completado'}</p>
                        </div>
                        
                        <div class="info-modal-content">
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
                        
                        <button class="btn ${isSuccess ? 'btn-success' : 'btn-danger'}" style="width: 100%; margin-top: 1rem;" onclick="cerrarModalInfo()">
                            <i class="fas fa-check me-2"></i>Cerrar
                        </button>
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

                const usuariosData = usuarios.data || [];
                const registrosData = registros.data || [];
                const biometriaData = biometria.data || [];
                const torniquetesData = torniquetes.data || [];

                console.log('📊 Datos para estadísticas:', { 
                    usuarios: usuariosData.length, 
                    registros: registrosData.length,
                    biometria: biometriaData.length,
                    torniquetes: torniquetesData.length
                });

                // Estadísticas básicas
                const usuariosActivos = usuariosData.filter(u => u.estado === true || u.estado === 'activo').length;
                const registrosHoy = registrosData.filter(r => {
                    if (!r.fecha_hora && !r.fecha) return false;
                    const fechaReg = new Date(r.fecha_hora || r.fecha);
                    const hoy = new Date();
                    return fechaReg.toDateString() === hoy.toDateString();
                }).length;
                // CORRECCIÓN: usar 'resultado' en lugar de 'status'
                const registrosExitosos = registrosData.filter(r => r.resultado === true || r.resultado === 1 || r.resultado === '1').length;
                const porcentajeExito = registrosData.length > 0 ? Math.round((registrosExitosos / registrosData.length) * 100) : 0;

                document.getElementById('totalUsuarios').textContent = usuariosData.length;
                document.getElementById('usuariosActivos').textContent = usuariosActivos;
                document.getElementById('totalRegistros').textContent = registrosHoy;
                document.getElementById('porcentajeExito').textContent = porcentajeExito;
                document.getElementById('totalBiometria').textContent = biometriaData.length;
                document.getElementById('porcentajeBiometria').textContent = usuariosData.length > 0 ? Math.round((biometriaData.length / usuariosData.length) * 100) : 0;
                document.getElementById('totalTorniquetes').textContent = torniquetesData.length;
                document.getElementById('torniquetesOnline').textContent = torniquetesData.filter(t => t.estado === 'activo' || t.estado === true).length;

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
            const ctx = document.getElementById('chartMetodos');
            if (!ctx) return;

            const metodos = biometriaData.reduce((acc, b) => {
                acc[b.tipo_biometria] = (acc[b.tipo_biometria] || 0) + 1;
                return acc;
            }, {});

            if (chartMetodos) chartMetodos.destroy();
            chartMetodos = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(metodos),
                    datasets: [{
                        data: Object.values(metodos),
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { 
                            display: true,
                            position: 'bottom',
                            labels: { color: '#e2e8f0', padding: 15 }
                        }
                    }
                }
            });
        }

        function crearGraficaAccesos(registrosData) {
            const ctx = document.getElementById('chartAccesos');
            if (!ctx) return;

            // Últimos 7 días
            const hoy = new Date();
            const labels = [];
            const datos = [];

            for (let i = 6; i >= 0; i--) {
                const fecha = new Date(hoy);
                fecha.setDate(fecha.getDate() - i);
                const fechaStr = fecha.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric' });
                labels.push(fechaStr);

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
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Accesos',
                        data: datos,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        x: { 
                            ticks: { color: '#94a3b8' },
                            grid: { display: false }
                        }
                    }
                }
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
                data: {
                    labels: ['Activos', 'Inactivos'],
                    datasets: [{
                        data: [activos, inactivos],
                        backgroundColor: ['#10b981', '#ef4444'],
                        borderWidth: 0,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        x: { 
                            ticks: { color: '#94a3b8' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }

        function crearGraficaExito(registrosData) {
            const ctx = document.getElementById('chartExito');
            if (!ctx) return;

            // CORRECCIÓN: usar 'resultado' en lugar de 'status'
            const exitosos = registrosData.filter(r => r.resultado === true || r.resultado === 1 || r.resultado === '1').length;
            const fallidos = registrosData.length - exitosos;

            if (chartExito) chartExito.destroy();
            chartExito = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Exitosos', 'Fallidos'],
                    datasets: [{
                        data: [exitosos, fallidos],
                        backgroundColor: ['#10b981', '#ef4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { 
                            display: true,
                            position: 'bottom',
                            labels: { color: '#e2e8f0', padding: 15 }
                        }
                    }
                }
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
                
                // Guardar todos los usuarios y biometrías en variables globales
                todosLosUsuarios = dataUsuarios.success && dataUsuarios.data ? dataUsuarios.data : [];
                todasLasBiometrias = dataBiometrias.success && dataBiometrias.data ? dataBiometrias.data : [];
                
                console.log(`📊 Cargados ${todosLosUsuarios.length} usuarios y ${todasLasBiometrias.length} registros biométricos`);
                console.log('👥 Usuarios:', todosLosUsuarios);
                
                // Renderizar usuarios
                renderizarUsuarios(todosLosUsuarios);
            } catch (err) {
                console.error('❌ Error completo:', err);
                console.error('❌ Stack:', err.stack);
                document.getElementById('tablaUsuarios').innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--red-400);">Error al cargar usuarios. Revisa la consola para más detalles.</td></tr>';
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
                            <td>${u.nombre_completo || u.nombre || '-'}</td>
                            <td>${u.cargo || '-'}</td>
                            <td>${rfidData ? `<span class="badge badge-info" style="background: #0ea5e9;">${rfidData.dato_biometrico || 'Registrado'}</span>` : '<span class="badge badge-secondary" style="background: #64748b;">No registrado</span>'}</td>
                            <td>${facialData ? '<span class="badge badge-success" style="background: #10b981;">Activado</span>' : '<span class="badge badge-secondary" style="background: #64748b;">Desactivado</span>'}</td>
                            <td>${huellaData ? '<span class="badge badge-success" style="background: #10b981;">Activado</span>' : '<span class="badge badge-secondary" style="background: #64748b;">Desactivado</span>'}</td>
                            <td>
                                <span class="badge ${u.estado === 'activo' || u.estado === true ? 'badge-success' : 'badge-danger'}" style="background: ${u.estado === true || u.estado === 'activo' ? '#10b981' : '#ef4444'};">
                                    ${u.estado === true || u.estado === 'activo' ? 'Activo' : 'Inactivo'}
                                </span>
                            </td>
                            <td>${u.fecha_registro || '-'}</td>
                            <td>
                                <button class="btn btn-primary btn-sm" onclick="editarUsuario(${u.id_usuario})" title="Editar usuario">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="eliminarUsuarioRapido(${u.id_usuario}, '${(u.nombre_completo || u.nombre || 'Usuario').replace(/'/g, "\\'")}');" title="Eliminar usuario">
                                    <i class="fas fa-times"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem; color: var(--slate-500);">No hay usuarios que coincidan con los filtros</td></tr>';
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
                    url = `${API_URL}/usuarios/update`;
                    formData.append("id_usuario", userId);
                }
                
                const res = await fetch(url, {
                    method: "POST",
                    headers: getAuthHeadersFormData(),  // Cambiado para FormData
                    body: formData
                });
                const data = await res.json();
                
                if (data.success) {
                    cerrarModalUsuario();
                    cargarUsuarios();
                    cargarEstadisticas();
                    
                    // Mostrar modal informativo
                    mostrarModalInfo({
                        success: true,
                        mensaje: 'Usuario guardado exitosamente',
                        nombre_completo: nombre,
                        cargo: cargo
                    }, userId ? 'Actualización de Usuario' : 'Creación de Usuario');
                } else {
                    mostrarModalInfo({ success: false, mensaje: data.message || 'No se pudo guardar' }, 'Error');
                }
            } catch (err) {
                hideLoading();
                mostrarModalInfo({ success: false, mensaje: 'Error de conexión: ' + err.message }, 'Error');
            }
        }

        async function eliminarUsuario(id) {
            if (!confirm("¿Está seguro de eliminar este usuario?")) return;
            
            showLoading();
            try {
                const formData = new FormData();
                formData.append("id_usuario", id);
                
                const res = await fetch(`${API_URL}/usuarios/delete`, {
                    method: "POST",
                    headers: getAuthHeadersFormData(),  // Cambiado para FormData
                    body: formData
                });
                const data = await res.json();
                
                hideLoading();
                
                if (data.success) {
                    cargarUsuarios();
                    cargarEstadisticas();
                    mostrarModalInfo({ success: true, mensaje: 'Usuario eliminado exitosamente', usuario_id: id }, 'Eliminación de Usuario');
                } else {
                    mostrarModalInfo({ success: false, mensaje: data.message || 'No se pudo eliminar' }, 'Error');
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
            notif.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${tipo === 'success' ? 'rgba(16, 185, 129, 0.95)' : 'rgba(239, 68, 68, 0.95)'};
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                z-index: 10000;
                font-weight: 600;
                animation: slideIn 0.3s ease-out;
            `;
            notif.textContent = mensaje;
            document.body.appendChild(notif);
            
            setTimeout(() => {
                notif.style.animation = 'slideOut 0.3s ease-out';
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
                
                if (data.success && data.data && data.data.length > 0) {
                    tbody.innerHTML = data.data.map(r => {
                        // El campo correcto es 'resultado', no 'status'
                        const esExitoso = r.resultado === true || r.resultado === 1 || r.resultado === '1';
                        const medio = r.tipo_acceso || r.medio || '-';
                        const fecha = r.fecha_hora || r.fecha || '-';
                        
                        return `
                            <tr>
                                <td>${r.id_registro || '-'}</td>
                                <td>${r.id_usuario || '-'}</td>
                                <td><span class="badge badge-info" style="background: #3b82f6;">${medio}</span></td>
                                <td>
                                    <span class="badge ${esExitoso ? 'badge-success' : 'badge-danger'}" style="background: ${esExitoso ? '#10b981' : '#ef4444'};">
                                        ${esExitoso ? 'Permitido' : 'Denegado'}
                                    </span>
                                </td>
                                <td>${fecha}</td>
                                <td>${r.id_torniquete || '-'}</td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--slate-500);">No hay registros disponibles</td></tr>';
                }
            } catch (err) {
                console.error('Error:', err);
                document.getElementById('tablaRegistros').innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--red-400);">Error al cargar registros</td></tr>';
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
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--slate-500);">No hay torniquetes registrados</td></tr>';
                }
            } catch (err) {
                console.error('Error:', err);
                document.getElementById('tablaTorniquetes').innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--red-400);">Error al cargar torniquetes</td></tr>';
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

        // Initialize
        window.addEventListener('load', () => {
            cargarEstadisticas();
        });