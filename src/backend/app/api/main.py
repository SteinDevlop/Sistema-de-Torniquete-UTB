import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from backend.app.core.config import settings
from backend.app.core.middlewares import add_middlewares
from backend.app.logic.universal_controller_instance import universal_controller
from backend.app.api.routes import (access_service)
# Inicializar la aplicación FastAPI
settings = type('Settings', (), {'PROJECT_NAME': 'Sistema de Torniquete UTB'})()  # Placeholder for settings
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
#@app.on_event("startup")
#async def startup_event():
#    print("Conexión establecida con la base de datos")

#@app.on_event("shutdown")
#async def shutdown_event():
#    if universal_controller.conn:
#        universal_controller.conn.close()
#        print("Conexión cerrada correctamente")

# Incluir rutas de los microservicios
app.include_router(access_service.app)