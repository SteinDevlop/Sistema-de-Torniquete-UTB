from fastapi import APIRouter
import asyncio

# Router exportado como `app` para mantener la misma convención usada en main.py
app = APIRouter(tags=["Acceso dependencia"],prefix="/dependencia")

# Estado en memoria
access_dp_state: bool = False
access_dp_version: int = 0
_access_dp_lock = asyncio.Lock()


async def _access_dp_worker(version: int, duration: float = 4.0):
	"""Tarea que apaga la access_dp solo si la versión no cambió."""
	try:
		await asyncio.sleep(duration)
		async with _access_dp_lock:
			global access_dp_state, access_dp_version
			if version == access_dp_version:
				access_dp_state = False
	except asyncio.CancelledError:
		return


@app.post("/permitir")
async def permitir_cara():
	"""
	Activa la access_dp (True) durante 4 segundos. Si se llama de nuevo antes de
	que pasen los 4s, se reinicia el temporizador.
	"""
	global access_dp_state, access_dp_version
	async with _access_dp_lock:
		access_dp_version += 1
		current_version = access_dp_version
		access_dp_state = True

	# lanzar tarea en background; el versioning evita carreras
	asyncio.create_task(_access_dp_worker(current_version, duration=4.0))
	return {"access_dp": access_dp_state, "duration": 4}


@app.get("/permiso")
async def obtener_estado_access_dp():
	"""Devuelve el estado actual de la access_dp."""
	async with _access_dp_lock:
		return {"access_dp": access_dp_state}
