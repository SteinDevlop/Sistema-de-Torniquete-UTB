import os
import warnings
import logging
import asyncio

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
from backend.app.api.routes import dep_access 
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
        yield  # 👈 Aquí se ejecaccess la app mientras está viva
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

app.add_middleware(
    CORSMiddleware,
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

# Incluir el router que maneja la UTA/torniquete por cara
app.include_router(dep_access.app)