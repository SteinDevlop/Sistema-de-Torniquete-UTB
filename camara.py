import cv2
import serial
import time

def main():
    # Configura el puerto serie (reemplaza 'COM3' con el puerto correspondiente en tu sistema)
    ser = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Espera a que se establezca la conexión serie

    print("Esperando señal desde ESP32...")

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"Recibido: {line}")
                if line == 'capture':
                    capture_image()
        except serial.SerialException as e:
            print(f"Error de comunicación serie: {e}")
            break
        except UnicodeDecodeError:
            pass  # Ignora errores de decodificación
        time.sleep(0.1)

def capture_image():
    # Inicializa la cámara (0 es generalmente la cámara por defecto)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("No se puede acceder a la cámara")
        return
    
    # Configurar el ancho y alto si es necesario
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Ajustar brillo y exposición si es posible
    #cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)  # Valores entre 0 y 1
    #cap.set(cv2.CAP_PROP_EXPOSURE, -4)     # Dependiendo de la cámara, puede variar

    time.sleep(2)  # Espera 2 segundos

    # Lee algunos frames antes de capturar
    for i in range(5):
        ret, frame = cap.read()

    ret, frame = cap.read()
    if not ret:
        print("No se puede capturar el frame")
        cap.release()
        return

    # Guarda la imagen con un nombre único basado en la hora actual
    filename = f'imagen_{int(time.time())}.png'
    cv2.imwrite(filename, frame)
    print(f"Imagen guardada como {filename}")

    # Libera la cámara
    cap.release()

if __name__ == '__main__':
    main()
