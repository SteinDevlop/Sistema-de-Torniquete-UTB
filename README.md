# Sistema-de-Torniquete-UTB
## Descripción del sistema

Sistema de control de acceso para la UTB basado en torniquetes con módulos de verificación: RFID, huella dactilar y verificación facial.

- Backend (FastAPI)
  - API REST/ASGI que gestiona usuarios, biometría (CRUD), reglas de acceso y registros (AccessLog).
  - Lógica de verificación modular: VerificadorRFID, VerificadorHuella y VerificadorCamara/Facial.
  - **✅ Reconocimiento facial implementado**: Recibe embeddings de 128 dimensiones desde ESP32.
  - Capa de persistencia abstracta (UniversalController) para operaciones add/get/update/delete.
  - Auditoría y logs estratégicos para trazabilidad de intentos y depuración.
  - **Hash-indexing** para búsqueda rápida de candidatos (RFID, huella y facial).

- Frontend / Dispositivos
  - Panel web o móvil para administración y visualización en tiempo real.
  - Servicio en el dispositivo torniquete que captura RFID/huella/imagen y consulta la API.
  - Comunicación síncrona (HTTP) o en tiempo real (WebSocket/MQTT) según despliegue.

- Flujo básico de acceso
  1. Dispositivo captura medio (rfid / huella / cámara).
  2. Envía request al endpoint de verificación con el payload correspondiente.
  3. Backend selecciona verificador, filtra candidatos, compara templates/vectores y responde { allowed, user_id, score }.
  4. Dispositivo actúa sobre el torniquete y registra el intento en AccessLog.

- Seguridad y buenas prácticas
  - Usar TLS, autenticación (API keys / JWT) entre dispositivos y backend.
  - Cifrado en reposo para plantillas biométricas; logs sin exponer templates completos.
  - Umbrales configurables para coincidencia y retención explícita de datos biométricos.
  - Tests aislados (DB in-memory o archivos temporales) para evitar bloqueos en SQLite.

- Extensiones posibles
  - Mostrar imágenes/vectores en dashboard, modo aprendizaje para modelos faciales, fallback por PIN.
  - Integración con sistemas institucionales (LDAP/AD) y balanceo de carga en producción.

---

## ✅ Estado de Implementación

### Módulos Completados:
- ✅ **RFID**: Búsqueda directa por tag
- ✅ **Huella Dactilar**: Comparación de templates con hash-indexing y similitud coseno
- ✅ **Reconocimiento Facial**: Comparación de embeddings de 128 dimensiones
  - Soporta formato JSON y Base64
  - Hash-indexing (SHA256) para búsqueda optimizada
  - Similitud coseno normalizada
  - Umbral configurable (default: 0.70)

### Guías de Integración:
- 📘 **[ESP32_INTEGRATION.md](./ESP32_INTEGRATION.md)** - Guía completa para enviar embeddings desde ESP32
- 🧪 **Tests**: `src/backend/app/tests/test_reconocimiento_facial.py`
- 📝 **Ejemplo**: `src/backend/app/examples/ejemplo_registro_facial.py`

---

### Instrucciones para ejecutar el backend (Windows)

Requisitos
- Python 3.8+
- Git (opcional)
- Tener el archivo `.env` con las variables necesarias en la carpeta `src`.

Pasos (PowerShell)
1. Abrir PowerShell y colocarse en la carpeta `src`:
   ```powershell
   cd c:\Users\XXX\XXX\Sistema-de-Torniquete-UTB\src
   ```

2. Crear y activar un entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Cargar el archivo `.env` en la sesión (temporal) y configurar PYTHONPATH:
   ```powershell
   # Establecer PYTHONPATH para que el paquete se resuelva desde src
   $env:PYTHONPATH = '.'
   ```

5. Levantar el servidor FastAPI (modo desarrollo):
   ```powershell
   python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000
   ```



Notas
- Asegúrate de que el archivo `backend/app/api/main.py` exporte la aplicación FastAPI con el nombre `app` (por ejemplo `app = FastAPI()`).
- Si usas WSL/Git Bash las mismas instrucciones son válidas (usar `source .venv/Scripts/activate` si aplica).
- Si la instalación usa otro `requirements.txt` en otra carpeta, ajusta la ruta en el comando `pip install -r`.
- Para producción usa un servidor ASGI (uvicorn/gunicorn) sin `--reload` y configura correctamente las variables de entorno y permisos.

