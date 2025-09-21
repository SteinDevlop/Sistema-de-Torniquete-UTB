import cv2
import time

import cv2
import time

def capture_image():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Puedes probar CAP_MSMF también

    if not cap.isOpened():
        print("No se puede acceder a la cámara")
        return

    time.sleep(2)  # Espera a que la cámara se inicie

    # Leer y descartar algunos frames iniciales
    for i in range(5):
        ret, frame = cap.read()

    ret, frame = cap.read()
    if not ret:
        print("No se puede capturar el frame")
        cap.release()
        return

    # Verifica el tamaño y el tipo de datos del frame
    print("Dimensiones del frame:", frame.shape if frame is not None else "Frame vacío")
    print("Tipo de datos:", frame.dtype if frame is not None else "No hay datos")

    # Si el frame no está completamente negro, debería haber valores de píxeles mayores que cero
    if frame is not None and frame.any():
        print("El frame contiene datos.")
        cv2.imshow('Imagen Capturada', frame)
        cv2.waitKey(500)  # Espera 500 ms para ver la imagen
        cv2.destroyAllWindows()

        # Guarda la imagen
        filename = f'imagen_{int(time.time())}.jpg'
        cv2.imwrite(filename, frame)
        print(f"Imagen guardada como {filename}")
    else:
        print("El frame está completamente negro o vacío.")

    cap.release()

capture_image()
