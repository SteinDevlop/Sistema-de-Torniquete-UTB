import cv2
import time

class VerificadorCamaraMock:
    def verificar(self, data: dict) -> tuple[bool, int | None]:
        print("Simulando verificación de rostro...")
        embeddings_registrados = {
            "usuario1": {"id": 1},
            "usuario2": {"id": 2},
        }

        # Simulación de resultado
        if "usuario1" in embeddings_registrados:
            return True, embeddings_registrados["usuario1"]["id"]
        return False, None


def capturar_imagen():
    print("Activando cámara...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return None

    # Cargar el clasificador Haar Cascade para detección de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    print("Buscando rostro...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el frame.")
            break

        # Convertir el frame a escala de grises para la detección de rostros
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar rostros en el frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Dibujar rectángulos alrededor de los rostros detectados
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            print("Rostro detectado. Mostrando cuadro de seguimiento...")
            
            # Mostrar el cuadro de seguimiento durante 3 segundos antes de capturar la imagen
            cv2.imshow("Captura de rostro", frame)
            time.sleep(3)
            
            print("Capturando imagen...")
            cap.release()
            cv2.destroyAllWindows()
            return frame  # Retorna el frame con el rostro detectado

        cv2.imshow("Captura de rostro", frame)

        # Salir si no se detecta rostro después de un tiempo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def main():
    print("Iniciando prueba de VerificadorCamara...")
    verificador = VerificadorCamaraMock()

    # Capturar imagen desde la cámara
    frame = capturar_imagen()
    if frame is None:
        print("No se capturó ninguna imagen.")
        return

    # Simulación de datos de entrada
    data = {}

    # Ejecutar la verificación
    autorizado, usuario_id = verificador.verificar(data)

    # Mostrar el resultado
    if autorizado:
        print(f"Acceso autorizado para el usuario con ID: {usuario_id}")
    else:
        print("Acceso denegado. No se encontró coincidencia.")


if __name__ == "__main__":
    main()