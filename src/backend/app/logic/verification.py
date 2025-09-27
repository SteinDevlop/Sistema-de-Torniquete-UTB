import cv2
import face_recognition
import numpy as np
from backend.app.models.access import MedioAcceso, AccesoRequest
from backend.app.models.verificador_acceso import VerificadorAcceso
from backend.app.logic.universal_controller_instance import universal_controller

class VerificadorRFID(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        codigo = data.get("Codigo")
        usuario = {"id": 1, "nombre": "Usuario de prueba"}  # Código de prueba
        if usuario:
            return True, usuario["id"]
        return False, None

class VerificadorHuella(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        # Implementación pendiente
        pass

class VerificadorCamara(VerificadorAcceso):
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        # Capturar imagen de la cámara
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: No se pudo acceder a la cámara.")
            return False, None

        print("Presiona 'q' para capturar la imagen.")
        frame = None
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo leer el frame de la cámara.")
                break

            cv2.imshow("Captura de rostro", frame)

            # Presionar 'q' para capturar la imagen
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if frame is None:
            return False, None

        # Detectar rostros y generar embeddings
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            print("No se detectó ningún rostro.")
            return False, None

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if not face_encodings:
            print("No se pudieron generar embeddings para el rostro.")
            return False, None

        # Simulación de embeddings registrados
        embeddings_registrados = {
            "usuario1": {
                "id": 1,
                "embedding": np.random.rand(128),  # Reemplazar con embeddings reales
            },
            "usuario2": {
                "id": 2,
                "embedding": np.random.rand(128),  # Reemplazar con embeddings reales
            },
        }

        # Comparar el embedding capturado con los registrados
        rostro_capturado = face_encodings[0]
        for usuario, datos in embeddings_registrados.items():
            distancia = np.linalg.norm(datos["embedding"] - rostro_capturado)
            if distancia < 0.6:  # Umbral de similitud
                print(f"Usuario reconocido: {usuario}")
                return True, datos["id"]

        print("No se encontró coincidencia para el rostro capturado.")
        return False, None

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