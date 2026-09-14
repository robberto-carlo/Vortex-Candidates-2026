import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera
import lib.constants as constants

def main():
    cam = camera.open_camera() # Abrir la camara
    print("Cámara abierta correctamente")
    camera.camera_info(cam)

    while True:
        frame = camera.read_frame(cam)
        if frame is None:
            break

        # Detectar color
        mask = camera.hsv_mask(frame, constants.Color.BLUE)
        #mask = camera.threshold(frame, constants.Color.BLUE)

        mask = camera.filter_mask(mask) # Filtro máscara
        frame = camera.draw_color(frame, mask) # Dibujar contornos

        # Mostrar cámara
        cv2.imshow("Color Detection", frame)
        cv2.imshow("Mask", mask) 

        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.close_camera(cam)

if __name__ == "__main__":
    main()