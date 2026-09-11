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

    # Hue
    cv2.createTrackbar(
        "H Min",
        "Trackbars",
        0,
        179,
        nothing
    )

    cv2.createTrackbar(
        "H Max",
        "Trackbars",
        179,
        179,
        nothing
    )

    # Saturation
    cv2.createTrackbar(
        "S Min",
        "Trackbars",
        0,
        255,
        nothing
    )

    cv2.createTrackbar(
        "S Max",
        "Trackbars",
        255,
        255,
        nothing
    )

    # Value
    cv2.createTrackbar(
        "V Min",
        "Trackbars",
        0,
        255,
        nothing
    )

    cv2.createTrackbar(
        "V Max",
        "Trackbars",
        255,
        255,
        nothing
    )


def get_hsv_values():
    h_min = cv2.getTrackbarPos(
        "H Min",
        "Trackbars"
    )

    h_max = cv2.getTrackbarPos(
        "H Max",
        "Trackbars"
    )

    s_min = cv2.getTrackbarPos(
        "S Min",
        "Trackbars"
    )

    s_max = cv2.getTrackbarPos(
        "S Max",
        "Trackbars"
    )

    v_min = cv2.getTrackbarPos(
        "V Min",
        "Trackbars"
    )

    v_max = cv2.getTrackbarPos(
        "V Max",
        "Trackbars"
    )

    return (h_min,h_max,s_min,s_max,v_min,v_max)


def print_hsv_range(h_min,h_max,s_min,s_max,v_min,v_max):
    print("\nRango HSV actual:\n")
    print(f"(np.array([{h_min}, {s_min}, {v_min}]), "f"np.array([{h_max}, {s_max}, {v_max}]))\n")


def main():
    cam = camera.open_camera(0)
    if cam is None:
        return

    print("Cámara abierta correctamente\n")
    print("Controles:")
    print("S   -> mostrar rango HSV")
    print("ESC -> salir\n")

    create_trackbars()

    while True:
        frame = camera.read_frame(cam)
        if frame is None:
            print("No se pudo leer el frame.")
            break

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        (h_min,h_max,s_min,s_max,v_min,v_max) = get_hsv_values()

        lower = np.array([
            h_min,
            s_min,
            v_min
        ])

        upper = np.array([
            h_max,
            s_max,
            v_max
        ])

        mask = cv2.inRange(hsv,lower,upper)

        cv2.imshow("Camera",frame)

        mask_display = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)

        # Mostrar H
        cv2.putText(
            mask_display,
            f"H: {h_min} - {h_max}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Mostrar S
        cv2.putText(
            mask_display,
            f"S: {s_min} - {s_max}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Mostrar V
        cv2.putText(
            mask_display,
            f"V: {v_min} - {v_max}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow("Mask",mask_display)

        key = cv2.waitKey(1) & 0xFF
        # ESC -> salir
        if key == 27:
            break
        # S -> imprimir rango HSV
        elif key == ord("s"):

            print_hsv_range(h_min,h_max,s_min,s_max,v_min,v_max)

    camera.close_camera(cam)

if __name__ == "__main__":
    main()