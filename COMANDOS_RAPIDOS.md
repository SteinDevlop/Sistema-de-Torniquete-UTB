# ⚡ COMANDOS RÁPIDOS - COPIAR Y PEGAR# 🚀 Comandos Rápidos - Arrancar Sistema



## 🚀 EJECUTAR EL SISTEMA (2 Terminales)## ▶️ Opción 1: Usar Scripts (Recomendado)



### Terminal 1 - Backend### Backend

```powershell```powershell

cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB"# Desde la raíz del repositorio

.\src\.venv\Scripts\Activate.ps1.\start-backend.ps1

python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src```

```- ✅ Crea/activa ambiente virtual automáticamente

- ✅ Instala dependencias si faltan

### Terminal 2 - Frontend- ✅ Arranca en http://localhost:8000

```powershell

cd "C:\Users\William\Documents\Codigos\REPOSITORIOS\TorniqueteFrontend\Sistema-de-Torniquete-UTB\STUTB-UI"### Frontend

python -m http.server 3000```powershell

```# Desde la raíz del repositorio (en otra terminal)

.\start-frontend.ps1

---```

- ✅ Sirve archivos estáticos desde `STUTB-UI`

## 🔐 CREDENCIALES- ✅ Arranca en http://localhost:3000



### Admin---

```

Usuario: admin## ▶️ Opción 2: Comandos Manuales

Contraseña: admin123

```### Backend (Paso a Paso)

```powershell

### Operario# 1. Activar ambiente virtual

```.\.venv\Scripts\Activate.ps1

Usuario: operario1

Contraseña: operario123# 2. Instalar dependencias (primera vez o si hay cambios)

```pip install -r requirements.txt



---# 3. Arrancar servidor

python -m uvicorn backend.app.api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src

## 🌐 URLs```



```### Frontend (Servidor Estático)

Login:      http://localhost:3000/login.html```powershell

API Docs:   http://localhost:8000/docs# En otra terminal PowerShell

```cd STUTB-UI

python -m http.server 3000

---```



## 🔧 SI HAY PROBLEMAS---



### Reinstalar bcrypt## 🌐 URLs Disponibles

```powershell

pip uninstall bcrypt passlib -y### Backend (http://localhost:8000)

pip install "passlib[bcrypt]==1.7.4" "bcrypt==4.1.3"- **API Docs**: http://localhost:8000/docs

```- **Reconocimiento Facial**: http://localhost:8000/facial-recognition.html



### Reinstalar todas las dependencias### Frontend (http://localhost:3000)

```powershell- **Reconocimiento Facial**: http://localhost:3000/facial-recognition.html

pip install -r requirements.txt- **Admin**: http://localhost:3000/admin.html

```- **Operador**: http://localhost:3000/operador.html

- **Login**: http://localhost:3000/login.html

---

---

## 📋 FLUJO DE PRUEBA RÁPIDO

## 📋 Notas Importantes

1. **Ejecutar backend y frontend** (comandos arriba)

2. **Ir a:** http://localhost:3000/login.html### Primera Ejecución

3. **Login:** admin / admin123- ⏱️ La instalación de dependencias (DeepFace + TensorFlow) tarda ~5-10 minutos

4. **Crear usuario** en sección Usuarios (obtener ID)- 💾 Requiere ~2GB de espacio en disco

5. **Logout** y login como operario1 / operario123- 🌐 DeepFace descarga modelos pre-entrenados (~100MB) al primer uso

6. **Registro facial** con el ID del usuario creado

7. **Capturar 15 frames** con cámara### Carpeta `prueba2`

8. **Verificar** en panel admin → sección Biometría- ❌ **No se usa** en el sistema actual

- 📁 Solo es demostrativa para referencia

---- 🚫 Excluida del control de versiones (.gitignore)



✅ **LISTO PARA USAR**### Dependencias del Sistema

Asegúrate de tener instalado:
- ✅ Python 3.10+ (`python --version`)
- ✅ pip actualizado (`python -m pip install --upgrade pip`)

---

## 🔧 Solución de Problemas

### Error: "No se puede cargar el archivo .venv\Scripts\Activate.ps1"
**Solución**: Habilitar ejecución de scripts en PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "ModuleNotFoundError: No module named 'backend'"
**Solución**: Asegúrate de usar `--app-dir src` en uvicorn o ejecuta desde la carpeta correcta.

### Error: "No module named 'deepface'"
**Solución**: Instalar dependencias
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🎯 Flujo de Trabajo Típico

1. **Arrancar Backend**: `.\start-backend.ps1` (Terminal 1)
2. **Arrancar Frontend**: `.\start-frontend.ps1` (Terminal 2)
3. **Abrir navegador**: http://localhost:3000/facial-recognition.html
4. **Probar**: Registrar usuario con foto → Verificar acceso

---

## 📦 Actualizar Dependencias

Si hay cambios en `requirements.txt`:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade
```

---

## 🛑 Detener Servidores

- Presiona **Ctrl + C** en cada terminal donde esté corriendo un servidor
