import sys

from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent / "src")
)

import cv2

from lib.camera import (
    open_camera,
    read_frame,
    detect_aruco,
    close_camera
)


camera = open_camera(0)
if camera is None:
    exit()

while True:
    frame = read_frame(camera)
    if frame is None:
        continue

    # Detectar ArUco
    aruco = detect_aruco(frame)
    if aruco is not None:
        marker_id, corners = aruco
        print("ArUco ID:", marker_id)

        # Convertir las esquinas
        corners = corners.reshape(4, 2).astype(int)

        # Dibujar el recuadro
        cv2.line(
            frame,
            tuple(corners[0]),
            tuple(corners[1]),
            (0, 255, 0),
            2
        )

        cv2.line(
            frame,
            tuple(corners[1]),
            tuple(corners[2]),
            (0, 255, 0),
            2
        )

        cv2.line(
            frame,
            tuple(corners[2]),
            tuple(corners[3]),
            (0, 255, 0),
            2
        )

        cv2.line(
            frame,
            tuple(corners[3]),
            tuple(corners[0]),
            (0, 255, 0),
            2
        )

        # Posición del ID
        x, y = corners[0]
        cv2.putText(
            frame,
            f"ID: {marker_id}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"): # Presionar Q para salir
        break

close_camera(camera)
cv2.destroyAllWindows()