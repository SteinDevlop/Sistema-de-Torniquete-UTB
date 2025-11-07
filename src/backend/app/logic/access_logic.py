from app.models.access import AccesoRequest, AccesoResponse
from app.logic.verification import VerificadorFactory, VerificadorCamara
from app.logic.universal_controller_instance import universal_controller as controller
from app.models.registros import RegistrosCreate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Servicio de acceso (DIP: depende de la abstracción VerificadorAcceso)
class AccessService:
    @staticmethod
    def solicitar_acceso(request: AccesoRequest) -> AccesoResponse:
        verificador = VerificadorFactory.obtener(request.medio)
        autorizado, usuario_id = verificador.verificar(request.data)

        status = True if autorizado else False
        
        # Si es verificación facial, incluir detalles de la comparación
        detalles = None
        if isinstance(verificador, VerificadorCamara):
            detalles = verificador.detalles_comparacion
        
        # ✅ GUARDAR REGISTRO EN LA BASE DE DATOS
        try:
            # Mapear nombres de medios
            medio_map = {
                "rfid": "RFID",
                "huella": "HUELLA",
                "camara": "FACIAL",
                "facial": "FACIAL"
            }
            tipo_acceso = medio_map.get(request.medio.lower(), request.medio.upper())
            
            # Crear registro usando el modelo
            registro = RegistrosCreate(
                id_usuario=usuario_id if usuario_id else None,
                id_torniquete=1,  # Torniquete por defecto
                id_operario=None,
                fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                tipo_acceso=tipo_acceso,
                imagen_capturada=None,
                resultado=status,
                observaciones=f"{'Acceso permitido' if status else 'Acceso denegado'} - Método: {tipo_acceso}"
            )
            
            # Guardar usando el universal controller
            controller.add(registro)
            logger.info(f"✅ Registro guardado: Usuario {usuario_id}, Medio {tipo_acceso}, Status {status}")
        except Exception as e:
            logger.error(f"❌ Error guardando registro: {e}")
        
        return AccesoResponse(
            status=status,
            medio=request.medio,
            usuario_id=usuario_id,
            mensaje="Acceso concedido" if autorizado else "Acceso denegado",
            score=detalles.get("mejor_score") if detalles else None,
            detalles_verificacion=detalles
        )
