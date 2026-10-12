import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera
import lib.constants as constants

cap = camera.open_camera(0)
if cap is None:
    exit()

try:
    while True:
        frame = camera.read_frame(cap)
        if frame is None:
            continue

        # Seleccionar ROI
        roi_name = constants.ROI.NEXT_TILE_NIVELES
        # roi_name = constants.ROI.NEXT_TILE_MAZE

        coordinates = constants.ROI_COORDINATES[roi_name]
        x1 = coordinates["x1"]
        y1 = coordinates["y1"]
        x2 = coordinates["x2"]
        y2 = coordinates["y2"]
        roi = camera.get_roi(frame, roi_name)

        # Mostrar porcentajes de colores dentro del ROI
        print("\033[2J\033[H", end="")
        for color in constants.COLOR_RANGES_HSV:
            percentage = camera.color_percentage(roi, color)
            color_name = color.name if hasattr(color, "name") else str(color)
            print(f"{color_name}: {percentage:.2f}%")

        # Dibujar ROI
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2)

        # Nombre del ROI en la esquina superior izquierda
        roi_label = roi_name.name if hasattr(roi_name, "name") else str(roi_name)
        cv2.putText(
            frame,
            roi_label,
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.close_camera(cap)