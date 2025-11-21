import API_URL from './api_root.js';

        function getAuthHeaders() {
            const headers = { 'Content-Type': 'application/json' };
            const token = sessionStorage.getItem('token');
            if (token) headers['Authorization'] = `Bearer ${token}`;
            return headers;
        }

        // Manejar el envío del formulario
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorAlert = document.getElementById('errorAlert');
            const submitBtn = e.target.querySelector('.btn-login');
            
            errorAlert.style.display = 'none';
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            try {
                const res = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify({ username, password })
                });

                if (!res.ok) {
                    throw new Error('Credenciales inválidas');
                }
                
                const json = await res.json();
                const token = json.access_token || json.token || json.data?.token;
                const user = json.user || json.data?.user || { username };

                if (token) {
                    sessionStorage.setItem('token', token);
                    sessionStorage.setItem('usuario', JSON.stringify(user));
                    
                    // Redirigir según rol
                    const role = user.role || user.tipo || (username === 'admin' ? 'administrador' : 'operador');
                    
                    setTimeout(() => {
                        if (role && role.toLowerCase().includes('admin')) {
                            window.location.href = 'admin.html';
                        } else {
                            window.location.href = 'operador.html';
                        }
                    }, 300);
                    return;
                }

                throw new Error('Respuesta inesperada del servidor');
                
            } catch (err) {
                console.error('Login error:', err);
                errorAlert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${err.message || 'Error de conexión'}`;
                errorAlert.style.display = 'block';
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
            }
        });

        // Auto-focus en el campo de usuario al cargar
        window.addEventListener('load', () => {
            document.getElementById('username').focus();
        });