import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import numpy as np
import lib.camera as camera

def nothing(value):
    pass

def create_trackbars():
    cv2.namedWindow("Trackbars")

    # Threshold Min
    cv2.createTrackbar(
        "Thresh Min",
        "Trackbars",
        0,
        255,
        nothing
    )

    # Threshold Max
    cv2.createTrackbar(
        "Thresh Max",
        "Trackbars",
        255,
        255,
        nothing
    )

def get_threshold_values():
    t_min = cv2.getTrackbarPos("Thresh Min", "Trackbars")
    t_max = cv2.getTrackbarPos("Thresh Max", "Trackbars")
    return t_min, t_max

def print_threshold_range(t_min, t_max):
    print("\nRango de Threshold actual:")
    print(f"({t_min}, {t_max})")

def main():
    cam = camera.open_camera(0)
    if cam is None:
        return

    print("Cámara abierta correctamente\n")
    print("Controles:")
    print("P   -> mostrar rango de threshold")
    print("ESC -> salir\n")

    create_trackbars()

    while True:
        frame = camera.read_frame(cam)
        if frame is None:
            print("No se pudo leer el frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)        
        t_min, t_max = get_threshold_values()

        mask = cv2.inRange(gray, t_min, t_max)
        cv2.imshow("Camera", frame)
        mask_display = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # Mostrar valores de Threshold
        cv2.putText(
            mask_display,
            f"Thresh: {t_min} - {t_max}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Mask", mask_display)

        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC -> salir
            break
        elif key == ord("p"): # P -> imprimir rango
            print_threshold_range(t_min, t_max)

    camera.close_camera(cam)

if __name__ == "__main__":
    main()