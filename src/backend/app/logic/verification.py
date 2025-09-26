from backend.app.models.access import MedioAcceso, AccesoRequest
from backend.app.models.verificador_acceso import VerificadorAcceso
from backend.app.logic.universal_controller_instance import universal_controller

class VerificadorRFID(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        codigo = data.get("Codigo")
        #usuario=universal_controller.get_by_code(self, "tarjeta", codigo)
        #Codigo de prueba
        usuario={"id": 1, "nombre": "Usuario de prueba"}
        if usuario:
            return True, usuario["id"]
        return False, None

class VerificadorHuella(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        pass

class VerificadorCamara(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        pass

class VerificadorFactory:
    @staticmethod
    def obtener(medio: MedioAcceso) -> VerificadorAcceso:
        if medio == MedioAcceso.rfid:
            return VerificadorRFID()
        elif medio == MedioAcceso.huella:
            return VerificadorHuella()
        elif medio == MedioAcceso.camara:
            return VerificadorCamara()
        raise ValueError("Medio no soportado")