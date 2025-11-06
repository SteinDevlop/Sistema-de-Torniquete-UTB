# 🚀 COMANDOS DE EJECUCIÓN - SISTEMA DE TORNIQUETE UTB

## ⚠️ CORRECCIONES DE WARNINGS APLICADAS

### ✅ Problemas Solucionados:
1. **TensorFlow oneDNN warnings** → Silenciados con variables de entorno
2. **TensorFlow deprecation warnings** → Filtrados con logging
3. **Bcrypt version error** → Actualizado a versión 4.1.3 compatible
4. **Passlib warnings** → Nivel de logging configurado a ERROR

### 🔧 Cambios Realizados:
- ✅ `main.py` actualizado con configuración completa de warnings
- ✅ `requirements.txt` actualizado: `bcrypt==4.1.3` y `passlib[bcrypt]==1.7.4`
- ✅ Variables de entorno configuradas para silenciar TensorFlow
- ✅ Logging configurado para ocultar mensajes innecesarios

---

## 📋 INFORMACIÓN DE USUARIOS DE PRUEBA

### Usuarios Hardcodeados en el Sistema (auth.py)

#### 1. **Administrador**
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Rol**: `administrador`
- **ID**: 1
- **Email**: admin@utb.edu.co
- **Acceso**: Panel completo de administración

#### 2. **Operario 1**
- **Usuario**: `operario1`
- **Contraseña**: `operario123`
- **Rol**: `operario`
- **ID**: 2
- **Email**: operario1@utb.edu.co
- **Acceso**: Panel de registro biométrico

#### 3. **Operario 2**
- **Usuario**: `operario2`
- **Contraseña**: `operario123`
- **Rol**: `operario`
- **ID**: 3
- **Email**: operario2@utb.edu.co
- **Acceso**: Panel de registro biométrico

---

## 🔧 COMANDOS PARA EJECUTAR EL SISTEMA

### 1️⃣ Activar Backend (Terminal 1)

```powershell
# Navegar al directorio del proyecto
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB"

# Ejecutar el backend con Uvicorn
python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

**Verificación**: El backend estará corriendo en `http://localhost:8000`
- Docs interactivas: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

---

### 2️⃣ Activar Frontend (Terminal 2)

```powershell
# Navegar al directorio del frontend
cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB\STUTB-UI"

# Iniciar servidor HTTP simple
python -m http.server 3000
```

**Verificación**: El frontend estará corriendo en `http://localhost:3000`

---

## 🌐 ACCESO AL SISTEMA

1. **Abrir navegador** y ir a: `http://localhost:3000/login.html`

2. **Iniciar sesión** con cualquiera de las credenciales:
   - Admin: `admin` / `admin123`
   - Operario: `operario1` / `operario123`

3. **Serás redirigido automáticamente** según tu rol:
   - **Administrador** → `admin.html` (Panel de administración completo)
   - **Operario** → `operador.html` (Panel de registro biométrico)

---

## 🎯 FLUJO DE PRUEBA COMPLETO

### Paso 1: Login como Administrador
```
URL: http://localhost:3000/login.html
Usuario: admin
Contraseña: admin123
```

### Paso 2: Crear Usuario en el Sistema
1. En el panel de administrador, ir a sección **Usuarios**
2. Click en "Nuevo Usuario"
3. Llenar formulario:
   - Nombre Completo: "Juan Pérez"
   - Cargo: "Estudiante"
   - Estado: Activo
4. Guardar usuario (obtendrás un ID, ej: 1)

### Paso 3: Registrar Biometría Facial
1. **Cerrar sesión** y hacer login como operario:
   ```
   Usuario: operario1
   Contraseña: operario123
   ```

2. En el panel de operario, click en **"Registro Facial"**

3. Ingresar el **ID del usuario** creado (ej: 1)

4. Click en **"Iniciar Captura"**
   - Se abrirá la cámara
   - Capturar 15 frames moviendo ligeramente la cabeza
   - El sistema detectará si es una persona real (liveness)

5. Si pasa liveness, se generará el embedding facial 512-dim

### Paso 4: Verificar Registro
1. Volver al panel de administrador
2. Ir a sección **Biometría**
3. Verificar que aparece el registro del usuario con:
   - ✓ Facial registrado
   - Vector de 512 dimensiones
   - Fecha de actualización

---

## 📊 ESTADO DE LA BASE DE DATOS

### Base de Datos Actual
- **Archivo**: `src/backend/app/data/data.db`
- **Estado**: VACÍA (sin usuarios ni operarios en BD)
- **Usuarios de Auth**: Hardcodeados en `src/backend/app/api/routes/auth.py`

### Tablas Disponibles
- ✅ `Usuarios` - Para usuarios del sistema de acceso
- ✅ `Biometria` - Para datos biométricos (facial, huella, RFID)
- ✅ `Operarios` - Para operarios del sistema (vacía)
- ✅ `Torniquetes` - Para dispositivos de acceso
- ✅ `Registros` - Para logs de acceso
- ✅ `RegistrosInvalidos` - Para accesos denegados
- ✅ `HistorialEstadoUsuario` - Para auditoría

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### ✅ Backend
- [x] Sistema de autenticación JWT completo
- [x] Endpoints protegidos con roles (admin, operario)
- [x] CRUD completo para todas las entidades
- [x] Reconocimiento facial con DeepFace + Facenet512
- [x] Detección de vida (liveness) con 15 frames
- [x] Embeddings faciales de 512 dimensiones
- [x] Validación de tokens y refresh

### ✅ Frontend
- [x] Login profesional con JWT
- [x] Panel de administrador completo
  - Dashboard con estadísticas
  - Gestión de usuarios
  - Gestión de biometría
  - Gestión de registros
  - Gestión de torniquetes
  - Gestión de operarios
- [x] Panel de operario con registro biométrico
  - Registro facial con cámara
  - Detección de vida (liveness)
  - Captura de 15 frames
  - Visualización de progreso
  - Actividad reciente
- [x] Diseño corporativo UTB responsive
- [x] Sistema de alertas y notificaciones

### ⏳ Pendiente (Desarrollo Futuro)
- [ ] Integración con lector de huellas dactilares
- [ ] Integración con lector RFID
- [ ] Exportación de reportes
- [ ] Gráficos y estadísticas avanzadas
- [ ] Filtros avanzados en tablas
- [ ] Paginación en listados

---

## 🔐 SEGURIDAD

### Tokens JWT
- **Algoritmo**: HS256
- **Expiración**: 480 minutos (8 horas)
- **Secret Key**: Configurado en `auth.py`
- **Storage**: LocalStorage del navegador

### Protección de Endpoints
- `GET /auth/me` - Requiere token válido
- `POST /auth/logout` - Requiere token válido
- `POST /auth/refresh` - Requiere token válido
- Todos los endpoints de CRUD requieren autenticación
- Endpoints de admin requieren rol `administrador`
- Endpoints de operario requieren rol `operario` o `administrador`

---

## 🐛 TROUBLESHOOTING

### Backend no inicia
```powershell
# Verificar Python
python --version  # Debe ser 3.13.7

# Verificar dependencias
pip list | Select-String "fastapi|uvicorn|deepface"

# Reinstalar si falta algo
pip install -r requirements.txt
```

### Frontend no carga
```powershell
# Verificar que el servidor HTTP esté corriendo
# Debe mostrar: Serving HTTP on :: port 3000...
```

### Error de CORS
- El backend tiene CORS habilitado para `http://localhost:3000`
- Si usas otro puerto, actualizar en `src/backend/app/api/main.py`

### Cámara no funciona
- Dar permisos de cámara al navegador
- Usar HTTPS o localhost (HTTP no funciona en Chrome para getUserMedia)

### Token expirado
- Hacer logout y login nuevamente
- El token dura 8 horas

---

## 📝 NOTAS IMPORTANTES

1. **Los usuarios de autenticación están hardcodeados** en `src/backend/app/api/routes/auth.py`
   - NO están en la base de datos
   - Son para login en el sistema

2. **Los usuarios del sistema de acceso** se crean desde el panel de administrador
   - Estos SÍ están en la BD (tabla `Usuarios`)
   - Son las personas que usarán el torniquete

3. **La biometría se registra** usando el ID del usuario del sistema de acceso
   - No el usuario de login
   - Usar el ID que devuelve al crear un usuario

4. **La detección de vida requiere movimiento**
   - No funciona con fotos estáticas
   - Mover ligeramente la cabeza al capturar frames
   - Umbral: 65% de confianza

---

## 📞 SOPORTE

Para cualquier problema o duda:
- Revisar logs del backend en la terminal
- Revisar consola del navegador (F12)
- Verificar que ambos servidores estén corriendo
- Verificar credenciales de usuario

---

**Sistema de Control de Acceso - Universidad Tecnológica de Bolívar**  
*Versión 2.0 - Octubre 2025*
