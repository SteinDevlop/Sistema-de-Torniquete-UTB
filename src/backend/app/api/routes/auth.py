"""
Sistema de Autenticación JWT para el Sistema de Torniquete UTB

Endpoints:
- POST /auth/login: Autenticación de usuarios
- POST /auth/logout: Cerrar sesión
- GET /auth/me: Obtener usuario actual
- POST /auth/refresh: Renovar token
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

app = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración JWT
SECRET_KEY = "utb-torniquete-secret-key-2025-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Usuarios hardcodeados (en producción usar base de datos)
USERS_DB = {
    "admin": {
        "id_usuario": 1,
        "username": "admin",
        "password_hash": pwd_context.hash("admin123"),
        "nombre": "Administrador",
        "apellido": "Sistema",
        "rol": "administrador",
        "email": "admin@utb.edu.co"
    },
    "operario1": {
        "id_usuario": 2,
        "username": "operario1",
        "password_hash": pwd_context.hash("operario123"),
        "nombre": "Juan",
        "apellido": "Pérez",
        "rol": "operario",
        "email": "operario1@utb.edu.co"
    },
    "operario2": {
        "id_usuario": 3,
        "username": "operario2",
        "password_hash": pwd_context.hash("operario123"),
        "nombre": "María",
        "apellido": "González",
        "rol": "operario",
        "email": "operario2@utb.edu.co"
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserInfo(BaseModel):
    id_usuario: int
    username: str
    nombre: str
    apellido: str
    rol: str
    email: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica y valida un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Obtiene el usuario actual desde el token JWT"""
    token = credentials.credentials
    payload = decode_token(token)
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    return user


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Middleware que requiere rol de administrador"""
    if current_user["rol"] != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de administrador"
        )
    return current_user


async def require_operario_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Middleware que requiere rol de operario o administrador"""
    if current_user["rol"] not in ["operario", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: se requiere rol de operario o administrador"
        )
    return current_user


@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Endpoint de inicio de sesión
    
    Retorna un token JWT válido por 8 horas
    """
    # Buscar usuario
    user = USERS_DB.get(request.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "rol": user["rol"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Usuario {user['username']} ({user['rol']}) inició sesión exitosamente")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # En segundos
        "user": {
            "id_usuario": user["id_usuario"],
            "username": user["username"],
            "nombre": user["nombre"],
            "apellido": user["apellido"],
            "rol": user["rol"],
            "email": user["email"]
        }
    }


@app.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado
    """
    return {
        "id_usuario": current_user["id_usuario"],
        "username": current_user["username"],
        "nombre": current_user["nombre"],
        "apellido": current_user["apellido"],
        "rol": current_user["rol"],
        "email": current_user["email"]
    }


@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Cierra la sesión del usuario (cliente debe eliminar el token)
    """
    logger.info(f"Usuario {current_user['username']} cerró sesión")
    return {
        "success": True,
        "message": "Sesión cerrada exitosamente"
    }


@app.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Renueva el token de acceso
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_token = create_access_token(
        data={"sub": current_user["username"], "rol": current_user["rol"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
