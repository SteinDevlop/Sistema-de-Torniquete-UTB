from backend.app.models.access import AccesoRequest, AccesoResponse
from backend.app.logic.verification import VerificadorFactory
# Servicio de acceso (DIP: depende de la abstracción VerificadorAcceso)
class AccessService:
    @staticmethod
    def solicitar_acceso(request: AccesoRequest) -> AccesoResponse:
        verificador = VerificadorFactory.obtener(request.medio)
        autorizado, usuario_id = verificador.verificar(request.data)

        status = "autorizado" if autorizado else "denegado"
        return AccesoResponse(
            status=status,
            medio=request.medio,
            usuario_id=usuario_id,
            mensaje="Acceso concedido" if autorizado else "Acceso denegado"
        )