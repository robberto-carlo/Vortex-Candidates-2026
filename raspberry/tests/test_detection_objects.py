import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera
import lib.constants as constants

def main():
    cam = camera.open_camera(0)
    print("Cámara abierta correctamente")
    camera.camera_info(cam)

    while True:
        frame = camera.read_frame(cam)
        if frame is None:
            break

        # Detectar color
        mask = camera.hsv_mask(frame, constants.Color.BLUE)
        # Limpiar máscara
        mask = camera.filter_mask(mask)
        # Detectar objeto
        obj = camera.detect_object(mask)
        # Dibujar objeto y coordenadas
        frame = camera.draw_object(frame, obj)

        # Mostrar imagen
        cv2.imshow("Object Detection", frame)
        # Mostrar máscara
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.close_camera(cam)

if __name__ == "__main__":
    main()