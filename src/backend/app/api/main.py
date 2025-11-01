import os
import warnings
import logging

# ==========================================
# CONFIGURACIÓN DE WARNINGS Y LOGS
# Debe estar ANTES de cualquier import de TensorFlow
# ==========================================
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Silenciar todos los logs de TensorFlow
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Desactivar oneDNN warnings
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Desactivar GPU si no se usa

# Silenciar todos los warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configurar logging para TensorFlow
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('passlib').setLevel(logging.ERROR)
logging.getLogger('bcrypt').setLevel(logging.ERROR)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.app.core.config import settings
from backend.app.core.middlewares import add_middlewares
from backend.app.logic.universal_controller_instance import universal_controller
from backend.app.api.routes import access_service
from backend.app.api.routes import liveness_service
from backend.app.api.routes import auth
from backend.app.api.routes.biometria import biometria_cud, biometria_query
from backend.app.api.routes.historial_estado_usuario import historial_estado_usuario_cud, historial_estado_usuario_query
from backend.app.api.routes.usuarios import usuarios_cud, usuarios_query
from backend.app.api.routes.operarios import operarios_cud, operarios_query
from backend.app.api.routes.registros_invalidos import registros_invalidos_cud, registros_invalidos_query
from backend.app.api.routes.registros import registros_cud, registros_query
from backend.app.api.routes.torniquetes import torniquetes_cud, torniquetes_query

# Montar archivos estáticos (se monta más abajo, después de crear `app`)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP =====
    print("Conexión establecida con la base de datos")

    try:
        yield  # 👈 Aquí se ejecuta la app mientras está viva
    finally:
        # ===== SHUTDOWN =====
        if hasattr(universal_controller, "conn") and universal_controller.conn:
            universal_controller.conn.close()
            print("Conexión cerrada correctamente")

# Inicializar la aplicación FastAPI
# Placeholder for settings
app = FastAPI(title=settings.PROJECT_NAME,lifespan=lifespan)

# Añadir middlewares globales
add_middlewares(app)

# Montar carpeta STUTB-UI (raíz del repositorio) para servir el frontend estático
try:
    # __file__ -> src/backend/app/api/main.py
    # parents[0]=api,1=app,2=backend,3=src,4=<repo root>
    repo_root = Path(__file__).resolve().parents[4]
    static_dir = repo_root / 'STUTB-UI'
    if static_dir.exists():
        # Montar archivos estáticos bajo /ui para no interferir con las rutas de la API
        app.mount('/ui', StaticFiles(directory=str(static_dir), html=True), name='frontend')

        # Servir directamente /facialtest.html desde el backend para compatibilidad con tests
        from fastapi.responses import FileResponse

        @app.get('/facialtest.html')
        async def _facialtest():
            target = static_dir / 'facialtest.html'
            if target.exists():
                return FileResponse(str(target))
            return {"detail": "facialtest.html not found"}
    else:
        print(f"Static UI folder not found: {static_dir}")
except Exception as e:
    print(f"Error mounting static files: {e}")

app.add_middleware(
    CORSMiddleware,
    # Permitir orígenes para desarrollo; en producción restringir a los dominios necesarios
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de los microservicios
app.include_router(auth.app)
app.include_router(access_service.app)
app.include_router(liveness_service.app)
app.include_router(biometria_cud.app)
app.include_router(biometria_query.app)
app.include_router(historial_estado_usuario_cud.app)
app.include_router(historial_estado_usuario_query.app)
app.include_router(usuarios_cud.app)
app.include_router(usuarios_query.app)
app.include_router(operarios_cud.app)
app.include_router(operarios_query.app)
app.include_router(registros_invalidos_cud.app)
app.include_router(registros_invalidos_query.app)
app.include_router(registros_cud.app)
app.include_router(registros_query.app)
app.include_router(torniquetes_cud.app)
app.include_router(torniquetes_query.app)