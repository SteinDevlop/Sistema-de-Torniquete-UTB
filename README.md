# 🎓 Sistema de Control de Acceso - Universidad Tecnológica de Bolívar# Sistema-de-Torniquete-UTB

## Descripción del sistema

Sistema integral de control de acceso con reconocimiento biométrico múltiple (facial, huella dactilar y RFID) para la gestión de torniquetes universitarios.

Sistema de control de acceso para la UTB basado en torniquetes con módulos de verificación: RFID, huella dactilar y verificación facial.

---

- Backend (FastAPI)

## 📋 **Características Principales**  - API REST/ASGI que gestiona usuarios, biometría (CRUD), reglas de acceso y registros (AccessLog).

  - Lógica de verificación modular: VerificadorRFID, VerificadorHuella y VerificadorCamara/Facial.

### **Sistema Biométrico Triple**  - **✅ Reconocimiento facial implementado**: Recibe embeddings de 128 dimensiones desde ESP32.

- ✅ **Reconocimiento Facial** con DeepFace + Facenet512 (512 dimensiones)  - Capa de persistencia abstracta (UniversalController) para operaciones add/get/update/delete.

- ✅ **Detección de Liveness** anti-spoofing (previene fotos/videos)  - Auditoría y logs estratégicos para trazabilidad de intentos y depuración.

- ✅ **Huella Dactilar** con templates encriptados  - **Hash-indexing** para búsqueda rápida de candidatos (RFID, huella y facial).

- ✅ **RFID** para tarjetas de acceso

- Frontend / Dispositivos

### **Roles de Usuario**  - Panel web o móvil para administración y visualización en tiempo real.

- 👨‍💼 **Administrador**: Gestión completa del sistema  - Servicio en el dispositivo torniquete que captura RFID/huella/imagen y consulta la API.

- 👷 **Operario**: Registro biométrico y monitoreo de accesos  - Comunicación síncrona (HTTP) o en tiempo real (WebSocket/MQTT) según despliegue.

- 👤 **Usuario**: Acceso mediante biometría

- Flujo básico de acceso

### **Funcionalidades**  1. Dispositivo captura medio (rfid / huella / cámara).

- 📊 Dashboard en tiempo real  2. Envía request al endpoint de verificación con el payload correspondiente.

- 📈 Reportes y estadísticas de acceso  3. Backend selecciona verificador, filtra candidatos, compara templates/vectores y responde { allowed, user_id, score }.

- 🔐 Autenticación segura con JWT  4. Dispositivo actúa sobre el torniquete y registra el intento en AccessLog.

- 🎭 Anti-spoofing con detección de liveness

- 📱 Interfaz responsive y profesional- Seguridad y buenas prácticas

  - Usar TLS, autenticación (API keys / JWT) entre dispositivos y backend.

---  - Cifrado en reposo para plantillas biométricas; logs sin exponer templates completos.

  - Umbrales configurables para coincidencia y retención explícita de datos biométricos.

## ▶️ **Inicio Rápido**  - Tests aislados (DB in-memory o archivos temporales) para evitar bloqueos en SQLite.



### **1. Iniciar Backend**- Extensiones posibles

```powershell  - Mostrar imágenes/vectores en dashboard, modo aprendizaje para modelos faciales, fallback por PIN.

python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src  - Integración con sistemas institucionales (LDAP/AD) y balanceo de carga en producción.

```

---

### **2. Iniciar Frontend**

```powershell## ✅ Estado de Implementación

cd STUTB-UI

python -m http.server 3000### Módulos Completados:

```- ✅ **RFID**: Búsqueda directa por tag

- ✅ **Huella Dactilar**: Comparación de templates con hash-indexing y similitud coseno

### **3. Acceder al Sistema**- ✅ **Reconocimiento Facial**: Comparación de embeddings de 128 dimensiones

- **Frontend:** http://localhost:3000  - Soporta formato JSON y Base64

- **API Docs:** http://localhost:8000/docs  - Hash-indexing (SHA256) para búsqueda optimizada

  - Similitud coseno normalizada

### **Credenciales**  - Umbral configurable (default: 0.70)

- **Admin:** admin / admin123

- **Operario:** operario1 / operario123### Guías de Integración:

- 📘 **[ESP32_INTEGRATION.md](./ESP32_INTEGRATION.md)** - Guía completa para enviar embeddings desde ESP32

---- 🧪 **Tests**: `src/backend/app/tests/test_reconocimiento_facial.py`

- 📝 **Ejemplo**: `src/backend/app/examples/ejemplo_registro_facial.py`

## 🏗️ **Arquitectura**

---

```

Sistema-de-Torniquete-UTB/### Instrucciones para ejecutar el backend (Windows)

├── src/backend/app/          # Backend FastAPI

│   ├── api/routes/           # Endpoints RESTRequisitos

│   ├── logic/                # Lógica de negocio- Python 3.8+

│   └── models/               # Modelos Pydantic- Git (opcional)

├── STUTB-UI/                 # Frontend- Tener el archivo `.env` con las variables necesarias en la carpeta `src`.

│   ├── login.html            # Autenticación

│   ├── admin.html            # Panel administradorPasos (PowerShell)

│   └── operador.html         # Panel operario1. Abrir PowerShell y colocarse en la carpeta `src`:

└── requirements.txt   ```powershell

```   cd c:\Users\XXX\XXX\Sistema-de-Torniquete-UTB\src

   ```

---

2. Crear y activar un entorno virtual:

## 🔐 **Seguridad**   ```powershell

   python -m venv .venv

- **JWT** para autenticación   .\.venv\Scripts\Activate.ps1

- **SHA-256** para hashing biométrico   ```

- **Liveness Detection** anti-spoofing (65% umbral)

- **Cosine Similarity** para reconocimiento facial (70% umbral)3. Instalar dependencias:

   ```powershell

---   pip install -r requirements.txt

   ```

## 🛠️ **Tecnologías**

4. Cargar el archivo `.env` en la sesión (temporal) y configurar PYTHONPATH:

- FastAPI + Python 3.11   ```powershell

- DeepFace + TensorFlow   # Establecer PYTHONPATH para que el paquete se resuelva desde src

- OpenCV + Scikit-learn   $env:PYTHONPATH = '.'

- SQLite   ```

- Bootstrap 5

5. Levantar el servidor FastAPI (modo desarrollo):

---   ```powershell

   python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000

## 📞 **Soporte**   ```



**Issues:** https://github.com/SteinDevlop/Sistema-de-Torniquete-UTB/issues



---Notas

- Asegúrate de que el archivo `backend/app/api/main.py` exporte la aplicación FastAPI con el nombre `app` (por ejemplo `app = FastAPI()`).

**Versión:** 2.0.0 | **Fecha:** 30 Oct 2025- Si usas WSL/Git Bash las mismas instrucciones son válidas (usar `source .venv/Scripts/activate` si aplica).

- Si la instalación usa otro `requirements.txt` en otra carpeta, ajusta la ruta en el comando `pip install -r`.
- Para producción usa un servidor ASGI (uvicorn/gunicorn) sin `--reload` y configura correctamente las variables de entorno y permisos.

