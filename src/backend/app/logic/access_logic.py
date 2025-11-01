from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.logic.verification import VerificadorFactory, VerificadorCamara
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
        
        return AccesoResponse(
            status=status,
            medio=request.medio,
            usuario_id=usuario_id,
            mensaje="Acceso concedido" if autorizado else "Acceso denegado",
            score=detalles.get("mejor_score") if detalles else None,
            detalles_verificacion=detalles
        )