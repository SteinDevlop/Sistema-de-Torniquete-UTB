from backend.app.models.access import MedioAcceso, AccesoRequest
from backend.app.models.verificador_acceso import VerificadorAcceso
from backend.app.logic.universal_controller_instance import universal_controller

class VerificadorRFID:
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        """
        Verifica si el RFID proporcionado pertenece a un usuario registrado en la tabla Biometria.
        Args:
            data (dict): Diccionario que contiene el valor del RFID bajo la clave 'rfid_tag'.
        Returns:
            tuple[bool, int | None]: (True, id_usuario) si se encuentra el RFID;
            (False, None) en caso contrario.
        """
        rfid_tag = data.get("rfid_tag")
        if not rfid_tag:
            return False, None
        biometria = universal_controller.get_by_field("Biometria", "rfid_tag", rfid_tag)
        if biometria:
            return True, biometria["id_usuario"]
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