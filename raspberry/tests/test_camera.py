import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera

def main():
    # Abrir la camara
    cam = camera.open_camera(0) 
    print("Cámara abierta correctamente")
    camera.camera_info(cam)

    while True:
        frame = camera.read_frame(cam)

        if frame is None:
            break

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == 27: # Cerrar con ESC
            break

    # Cerrar la camara
    camera.close_camera(cam) 

if __name__ == "__main__":
    main()