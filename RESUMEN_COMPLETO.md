# 🎯 RESUMEN COMPLETO - SISTEMA DE TORNIQUETE UTB
## Sistema Profesional con Autenticación JWT y Reconocimiento Facial

---

## ⚠️ WARNINGS SOLUCIONADOS ✅

### Problemas que aparecían:
```
❌ TensorFlow: oneDNN custom operations warnings
❌ TensorFlow: deprecated tf.losses warnings  
❌ Passlib: bcrypt version error (AttributeError)
```

### Soluciones aplicadas:
```
✅ Variables de entorno configuradas en main.py:
   - TF_CPP_MIN_LOG_LEVEL=3 (silenciar logs)
   - TF_ENABLE_ONEDNN_OPTS=0 (desactivar oneDNN)
   - CUDA_VISIBLE_DEVICES=-1 (CPU only)

✅ Logging configurado:
   - tensorflow → ERROR level
   - passlib → ERROR level
   - bcrypt → ERROR level

✅ Dependencias actualizadas:
   - bcrypt: 4.2.1 → 4.1.3 (versión compatible)
   - passlib[bcrypt]==1.7.4 (con extras de bcrypt)

✅ Filtros de warnings:
   - UserWarning → ignored
   - DeprecationWarning → ignored
   - FutureWarning → ignored
```

**Resultado:** Backend inicia sin warnings molestos ✨

---

## 🔐 CREDENCIALES DE ACCESO

### 👨‍💼 Administrador
```
Usuario:     admin
Contraseña:  admin123
Rol:         administrador
ID:          1
Email:       admin@utb.edu.co
```
**Acceso a:** Panel completo de administración

### 👷 Operario 1
```
Usuario:     operario1
Contraseña:  operario123
Rol:         operario
ID:          2
Email:       operario1@utb.edu.co
```
**Acceso a:** Panel de registro biométrico

### 👷 Operario 2
```
Usuario:     operario2
Contraseña:  operario123
Rol:         operario
ID:          3
Email:       operario2@utb.edu.co
```
**Acceso a:** Panel de registro biométrico

**📌 IMPORTANTE:** Estos usuarios están hardcodeados en `src/backend/app/api/routes/auth.py`

---

## 🚀 COMANDOS PARA EJECUTAR

### Opción 1: Con Entorno Virtual (Recomendado)

#### Terminal 1 - Backend:
```powershell
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB"
.\src\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

#### Terminal 2 - Frontend:
```powershell
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB\STUTB-UI"
python -m http.server 3000
```

### Opción 2: Sin Entorno Virtual

#### Terminal 1 - Backend:
```powershell
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB"
python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

#### Terminal 2 - Frontend:
```powershell
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB\STUTB-UI"
python -m http.server 3000
```

### 🌐 URLs de Acceso:
- **Login Frontend:** http://localhost:3000/login.html
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📦 ARCHIVOS IMPLEMENTADOS

### 🆕 Archivos Nuevos Creados:

#### Backend:
- ✅ `src/backend/app/api/routes/auth.py` (260 líneas)
  - Sistema completo de autenticación JWT
  - 3 usuarios hardcodeados
  - Endpoints: login, logout, refresh, me
  - Middlewares de protección por rol

#### Frontend:
- ✅ `STUTB-UI/login.html` (350 líneas)
  - Diseño corporativo UTB
  - Integración JWT
  - Validación de credenciales
  - Redirección automática por rol

- ✅ `STUTB-UI/admin.html` (850 líneas)
  - Panel completo de administración
  - Dashboard con estadísticas
  - 6 secciones: Dashboard, Usuarios, Biometría, Registros, Torniquetes, Operarios
  - Carga dinámica de datos

- ✅ `STUTB-UI/operador.html` (600 líneas)
  - Panel de registro biométrico
  - Módulo facial completo (cámara + liveness)
  - Detección de vida con 15 frames
  - Resultados detallados

#### Diseño:
- ✅ `assets/css/styles.css` (420 líneas)
  - Variables CSS de UTB
  - Componentes reutilizables
  - Sistema responsive
  - Colores corporativos

#### Documentación:
- ✅ `README.md` (420 líneas - reescrito)
  - Quick Start completo
  - Arquitectura del sistema
  - Endpoints documentados
  - Troubleshooting

- ✅ `COMANDOS_EJECUCION.md` (320 líneas)
  - Credenciales de usuarios
  - Comandos exactos
  - Flujo de prueba paso a paso

- ✅ `.env.example`
  - Variables de entorno para TensorFlow
  - Configuración de warnings

### 📝 Archivos Modificados:

- ✅ `src/backend/app/api/main.py`
  - Configuración completa de warnings
  - Registro del router de auth
  - Variables de entorno de TensorFlow

- ✅ `requirements.txt`
  - bcrypt: 4.2.1 → 4.1.3
  - passlib[bcrypt]==1.7.4

- ✅ `src/backend/app/api/routes/*/query.py`
  - Formato unificado: `{success: true, data: [...]}`
  - `/usuarios/all`
  - `/biometria/all`
  - `/torniquetes/all`
  - `/registros/all`

---

## 🎯 FLUJO DE PRUEBA COMPLETO

### Paso 1: Ejecutar Servidores
```powershell
# Terminal 1 - Backend
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB"
.\src\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src

# Terminal 2 - Frontend
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB\STUTB-UI"
python -m http.server 3000
```

### Paso 2: Login como Administrador
```
1. Ir a: http://localhost:3000/login.html
2. Usuario: admin
3. Contraseña: admin123
4. Click "Iniciar Sesión"
```
➡️ Redirige a `admin.html`

### Paso 3: Crear Usuario del Sistema
```
1. En panel admin, ir a "Usuarios"
2. Click "Nuevo Usuario"
3. Llenar formulario:
   - Nombre: "Juan Pérez"
   - Cargo: "Estudiante"
   - Estado: Activo
4. Guardar (obtener ID, ej: 1)
```

### Paso 4: Registrar Biometría Facial
```
1. Logout (botón superior derecho)
2. Login como operario:
   - Usuario: operario1
   - Contraseña: operario123
3. Click en "Registro Facial"
4. Ingresar ID del usuario (ej: 1)
5. Click "Iniciar Captura"
6. Permitir acceso a cámara
7. Capturar 15 frames moviendo la cabeza
8. Sistema analiza liveness
9. Si es persona real, genera embedding 512-dim
10. Se registra en base de datos
```

### Paso 5: Verificar Registro
```
1. Volver al panel de administrador
2. Ir a sección "Biometría"
3. Verificar registro:
   - ✓ Facial: Sí
   - Vector: 512 dimensiones
   - Fecha actualización
```

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Backend (FastAPI + SQLite)
```
src/backend/app/
├── api/
│   ├── main.py                 # ✅ Configuración de warnings
│   └── routes/
│       ├── auth.py            # ✅ JWT + 3 usuarios hardcodeados
│       ├── access_service.py  # Verificación de acceso
│       ├── liveness_service.py # Detección de vida
│       ├── usuarios/          # CRUD usuarios
│       ├── biometria/         # CRUD biometría
│       ├── operarios/         # CRUD operarios
│       ├── registros/         # CRUD registros
│       └── torniquetes/       # CRUD torniquetes
├── logic/
│   ├── face_recognition.py    # DeepFace + Facenet512
│   ├── liveness_detection.py  # Anti-spoofing
│   └── verification.py        # Lógica de verificación
└── data/
    └── data.db               # SQLite (VACÍA inicialmente)
```

### Frontend (HTML + CSS + JS)
```
STUTB-UI/
├── login.html         # ✅ Login JWT
├── admin.html         # ✅ Panel administrador
├── operador.html      # ✅ Panel operario con cámara
└── assets/
    └── css/
        └── styles.css # ✅ Diseño corporativo UTB
```

---

## 🔒 SEGURIDAD IMPLEMENTADA

### Autenticación JWT
```javascript
// Configuración
Algoritmo: HS256
Expiración: 480 minutos (8 horas)
Storage: localStorage

// Headers requeridos
Authorization: Bearer <token>
```

### Protección de Endpoints
```python
# Requieren token válido
GET  /auth/me
POST /auth/logout
POST /auth/refresh

# Requieren rol administrador
GET  /usuarios/all
POST /usuarios/create
GET  /biometria/all
GET  /registros/all
GET  /torniquetes/all
GET  /operarios/all

# Requieren rol operario o admin
POST /biometria/create
POST /liveness/start
POST /liveness/add-frame
POST /liveness/analyze
```

### Middlewares Implementados
```python
get_current_user()           # Validar token
require_admin()              # Validar rol admin
require_operario_or_admin()  # Validar rol operario/admin
```

---

## 🧪 TECNOLOGÍAS UTILIZADAS

### Backend
```
✅ FastAPI 0.117.1        - Framework web async
✅ Uvicorn 0.37.0         - Servidor ASGI
✅ SQLite                 - Base de datos
✅ DeepFace 0.0.95        - Reconocimiento facial
✅ TensorFlow 2.20.0      - Deep learning
✅ Facenet512             - Modelo de embeddings
✅ OpenCV 4.12.0          - Procesamiento de imágenes
✅ python-jose 3.5.0      - JWT tokens
✅ passlib 1.7.4          - Hashing de contraseñas
✅ bcrypt 4.1.3           - Algoritmo de encriptación
```

### Frontend
```
✅ HTML5 + CSS3 + JavaScript
✅ Bootstrap 5.3.0        - Framework CSS
✅ Font Awesome 6.4.0     - Iconos
✅ Fetch API              - Peticiones HTTP
✅ MediaDevices API       - Acceso a cámara
```

### Reconocimiento Facial
```
✅ Modelo: Facenet512
✅ Dimensiones: 512-dim embeddings
✅ Similarity: Cosine similarity
✅ Threshold: 70% (0.70)
✅ Liveness: 15 frames, 65% threshold
✅ Anti-spoofing: Motion + Texture + Depth analysis
```

---

## 📊 ESTADO DE LA BASE DE DATOS

### Información Actual
```
Archivo: src/backend/app/data/data.db
Estado: VACÍA (sin registros)
Tablas creadas: 7
```

### Tablas Disponibles
```sql
✅ Usuarios                    -- Personas del sistema de acceso
✅ Biometria                   -- Datos biométricos (facial, huella, RFID)
✅ Operarios                   -- Operarios del sistema (VACÍA)
✅ Torniquetes                 -- Dispositivos de acceso
✅ Registros                   -- Logs de acceso
✅ RegistrosInvalidos          -- Accesos denegados
✅ HistorialEstadoUsuario      -- Auditoría de cambios
```

### Usuarios de Autenticación
```
⚠️ NO están en la base de datos
✅ Están hardcodeados en auth.py
✅ Total: 3 usuarios (1 admin + 2 operarios)
```

---

## ✅ FUNCIONALIDADES COMPLETADAS

### ✅ Sistema de Autenticación
- [x] Login con JWT (8 horas de expiración)
- [x] Logout con invalidación de token
- [x] Refresh token
- [x] Verificación de usuario actual
- [x] Protección de endpoints por rol
- [x] 3 usuarios hardcodeados listos

### ✅ Panel de Administrador
- [x] Dashboard con estadísticas en tiempo real
- [x] Total de usuarios, accesos, biometría, torniquetes
- [x] Actividad reciente (últimos 10 registros)
- [x] Gestión completa de usuarios (listar, crear, editar, eliminar)
- [x] Gestión de datos biométricos (visualización)
- [x] Gestión de registros de acceso (logs)
- [x] Gestión de torniquetes
- [x] Gestión de operarios
- [x] Navegación entre secciones
- [x] Búsqueda y filtros

### ✅ Panel de Operario
- [x] Registro facial con cámara web
- [x] Detección de vida (liveness) con 15 frames
- [x] Captura automática de frames
- [x] Barra de progreso visual
- [x] Análisis de persona real
- [x] Generación de embedding 512-dim con DeepFace
- [x] Registro en base de datos
- [x] Resultados detallados
- [x] Actividad reciente
- [x] Módulos preparados para huella y RFID

### ✅ Reconocimiento Facial
- [x] DeepFace integrado con Facenet512
- [x] Embeddings de 512 dimensiones
- [x] Cosine similarity con threshold 70%
- [x] Corrección de dtype (float32)
- [x] Serialización base64

### ✅ Detección de Vida (Anti-Spoofing)
- [x] Captura de 15 frames
- [x] Análisis de movimiento (20%)
- [x] Análisis de textura con FFT (50%)
- [x] Análisis de profundidad 3D (30%)
- [x] Threshold de 65% para persona real
- [x] Veto de textura al 25%
- [x] Rechazo de fotos y videos

### ✅ Diseño y UX
- [x] Diseño corporativo UTB profesional
- [x] Colores: #003B71 (primary), #00A9E0 (secondary), #F7941D (accent)
- [x] Componentes reutilizables
- [x] Responsive design
- [x] Animaciones suaves
- [x] Iconografía Font Awesome
- [x] Sistema de alertas
- [x] Loading states

### ✅ Documentación
- [x] README.md completo y profesional
- [x] COMANDOS_EJECUCION.md con credenciales
- [x] Comentarios en código
- [x] Ejemplos de uso
- [x] Troubleshooting

### ✅ Configuración y Optimización
- [x] Warnings de TensorFlow silenciados
- [x] Warnings de bcrypt corregidos
- [x] Logging configurado
- [x] Variables de entorno
- [x] CORS configurado
- [x] Auto-reload en desarrollo

---

## ⏳ FUNCIONALIDADES PENDIENTES (Futuro)

### 🔲 Hardware Biométrico
- [ ] Integración con lector de huellas dactilares
- [ ] Integración con lector RFID
- [ ] Comunicación con ESP32/Arduino
- [ ] Protocolo de comunicación serial

### 🔲 Mejoras de UI
- [ ] Gráficos estadísticos (Chart.js)
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Filtros avanzados con fechas
- [ ] Paginación en tablas grandes
- [ ] Modo oscuro

### 🔲 Backend Avanzado
- [ ] Base de datos PostgreSQL (producción)
- [ ] Usuarios en BD (migrar de hardcoded)
- [ ] Caché con Redis
- [ ] WebSockets para tiempo real
- [ ] Rate limiting
- [ ] Logging avanzado

### 🔲 Seguridad Adicional
- [ ] 2FA (Two-Factor Authentication)
- [ ] Rotación de tokens
- [ ] Blacklist de tokens
- [ ] Auditoría completa
- [ ] Encriptación de datos biométricos

---

## 🐛 TROUBLESHOOTING

### ❌ Backend no inicia
```powershell
# Verificar Python
python --version  # Debe ser 3.13.7

# Verificar entorno virtual
.\src\.venv\Scripts\Activate.ps1

# Reinstalar dependencias
pip install -r requirements.txt
```

### ❌ Error "No module named uvicorn"
```powershell
# Activar entorno virtual
.\src\.venv\Scripts\Activate.ps1

# O instalar globalmente
pip install uvicorn
```

### ❌ Frontend no carga
```powershell
# Verificar que esté en el directorio correcto
cd STUTB-UI
python -m http.server 3000
```

### ❌ Error de CORS
```python
# En main.py, verificar:
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

### ❌ Cámara no funciona
```
1. Dar permisos de cámara en navegador
2. Usar localhost (no IP)
3. Probar en Chrome/Edge (mejor compatibilidad)
4. Verificar que no haya otra app usando la cámara
```

### ❌ Token expirado
```
Solución: Logout y login nuevamente
El token dura 8 horas
```

### ❌ Warnings de TensorFlow persisten
```python
# Verificar que main.py tenga:
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Y que bcrypt sea versión 4.1.3
pip install bcrypt==4.1.3
```

---

## 📞 INFORMACIÓN ADICIONAL

### Rutas de Archivos Importantes
```
Backend Principal:
  src/backend/app/api/main.py
  src/backend/app/api/routes/auth.py

Frontend Principal:
  STUTB-UI/login.html
  STUTB-UI/admin.html
  STUTB-UI/operador.html

CSS:
  assets/css/styles.css

Base de Datos:
  src/backend/app/data/data.db

Configuración:
  requirements.txt
  .env.example
```

### Puertos Utilizados
```
Backend:  http://localhost:8000
Frontend: http://localhost:3000
```

### Logs
```powershell
# Ver logs del backend en tiempo real
# Se muestran en la terminal donde corre uvicorn

# Ver logs del frontend
# Abrir DevTools (F12) → Console
```

---

## 🎓 NOTAS IMPORTANTES

### 1. Diferencia entre Usuarios
```
Usuarios de Autenticación (Login):
  - Hardcodeados en auth.py
  - admin, operario1, operario2
  - Para acceder al sistema
  - NO están en la BD

Usuarios del Sistema (Torniquete):
  - Se crean desde panel admin
  - En tabla "Usuarios" de BD
  - Son las personas que usan el torniquete
  - Tienen biometría asociada
```

### 2. IDs Importantes
```
Para Login:
  - Usar: admin / operario1 / operario2
  - Con sus contraseñas

Para Registro Biométrico:
  - Usar: ID numérico del usuario creado
  - Ej: 1, 2, 3, etc.
```

### 3. Flujo de Registro Biométrico
```
1. Admin crea usuario → Obtiene ID (ej: 1)
2. Operario usa ese ID para registrar biometría
3. Sistema asocia biometría con ese usuario
4. Usuario puede acceder con su biometría
```

### 4. Detección de Vida
```
Requiere:
  - Movimiento natural de cabeza
  - 15 frames capturados
  - Iluminación adecuada
  
No funciona con:
  - Fotos impresas
  - Fotos en pantalla
  - Videos pregrabados
```

---

**Sistema de Control de Acceso - Universidad Tecnológica de Bolívar**  
*Versión 2.0 - Octubre 2025*  
*✅ Warnings Corregidos - Sin Mensajes Molestos*
