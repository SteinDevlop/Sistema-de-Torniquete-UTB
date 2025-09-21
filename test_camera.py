import cv2

def test_camera():
    # Prueba con diferentes índices de cámara (0, 1, 2, ...)
    for i in range(1,2):
        print(f"Probando con la cámara índice {i}")
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print(f"No se pudo abrir la cámara con índice {i}")
            continue

        ret, frame = cap.read()
        if ret:
            print(f"Cámara {i} funciona correctamente")
            cv2.imshow(f"Cámara {i}", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            cap.release()
            return
        else:
            print(f"No se pudo leer un frame de la cámara {i}")
            cap.release()

    print("No se encontró ninguna cámara disponible.")

if __name__ == '__main__':
    test_camera()
