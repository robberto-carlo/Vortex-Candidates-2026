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

    # Threshold máscara normal
    cv2.createTrackbar(
        "Thresh Min",
        "Trackbars",
        0,
        255,
        nothing
    )

    cv2.createTrackbar(
        "Thresh Max",
        "Trackbars",
        255,
        255,
        nothing
    )

    # Threshold máscara invertida
    cv2.createTrackbar(
        "Invert Min",
        "Trackbars",
        0,
        255,
        nothing
    )

    cv2.createTrackbar(
        "Invert Max",
        "Trackbars",
        255,
        255,
        nothing
    )


def get_threshold_values():
    t_min = cv2.getTrackbarPos("Thresh Min", "Trackbars")
    t_max = cv2.getTrackbarPos("Thresh Max", "Trackbars")

    invert_min = cv2.getTrackbarPos("Invert Min", "Trackbars")
    invert_max = cv2.getTrackbarPos("Invert Max", "Trackbars")

    return t_min, t_max, invert_min, invert_max


def main():
    cam = camera.open_camera(0)

    if cam is None:
        return

    print("Cámara abierta correctamente\n")
    print("P   -> mostrar rangos de threshold")
    print("ESC -> salir\n")

    create_trackbars()

    while True:
        frame = camera.read_frame(cam)

        if frame is None:
            print("No se pudo leer el frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        t_min, t_max, invert_min, invert_max = get_threshold_values()

        # Máscara normal
        mask_normal = cv2.inRange(gray, t_min, t_max)

        # Máscara invertida con thresholds independientes
        mask_invertida = cv2.inRange(
            gray,
            invert_min,
            invert_max
        )
        mask_invertida = cv2.bitwise_not(mask_invertida)

        # Combinación de ambas máscaras
        mask_combinada = cv2.bitwise_and(
            mask_normal,
            mask_invertida
        )

        # Mostrar cámara original
        cv2.imshow("Camera", frame)

        # Mostrar máscara normal
        normal_display = cv2.cvtColor(
            mask_normal,
            cv2.COLOR_GRAY2BGR
        )
        cv2.putText(
            normal_display,
            f"Normal: {t_min} - {t_max}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        cv2.imshow("Mask Normal", normal_display)

        # Mostrar máscara invertida
        invert_display = cv2.cvtColor(
            mask_invertida,
            cv2.COLOR_GRAY2BGR
        )
        cv2.putText(
            invert_display,
            f"Invertida: {invert_min} - {invert_max}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        cv2.imshow("Mask Invertida", invert_display)

        # Mostrar combinación
        combined_display = cv2.cvtColor(
            mask_combinada,
            cv2.COLOR_GRAY2BGR
        )
        cv2.imshow("Combinacion", combined_display)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break

        elif key == ord("p"):
            print("\nThreshold normal:")
            print(f"({t_min}, {t_max})")

            print("Threshold invertido:")
            print(f"({invert_min}, {invert_max})")

    camera.close_camera(cam)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()