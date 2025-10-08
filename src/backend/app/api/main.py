import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.middlewares import add_middlewares
from backend.app.logic.universal_controller_instance import universal_controller
from backend.app.api.routes import access_service
from backend.app.api.routes.biometria import biometria_cud, biometria_query
from backend.app.api.routes.historial_estado_usuario import historial_estado_usuario_cud, historial_estado_usuario_query
from backend.app.api.routes.usuarios import usuarios_cud, usuarios_query
from backend.app.api.routes.operarios import operarios_cud, operarios_query
from backend.app.api.routes.registros_invalidos import registros_invalidos_cud, registros_invalidos_query
from backend.app.api.routes.registros import registros_cud, registros_query
from backend.app.api.routes.torniquetes import torniquetes_cud, torniquetes_query
# Inicializar la aplicación FastAPI
# Placeholder for settings
app = FastAPI(title=settings.PROJECT_NAME)

# Añadir middlewares globales
add_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos

# Eventos de inicio y apagado
@app.on_event("startup")
async def startup_event():
    print("Conexión establecida con la base de datos")

@app.on_event("shutdown")
async def shutdown_event():
    if universal_controller.conn:
        universal_controller.conn.close()
        print("Conexión cerrada correctamente")

# Incluir rutas de los microservicios
app.include_router(access_service.app)
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