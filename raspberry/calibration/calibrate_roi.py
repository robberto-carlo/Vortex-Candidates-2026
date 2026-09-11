
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera

def select_roi(frame):
    print("\nSelecciona el ROI con el mouse.")
    print("ENTER -> confirmar")
    print("ESC -> cancelar")

    x, y, w, h = cv2.selectROI(
        "Seleccionar ROI",
        frame,
        fromCenter=False,
        showCrosshair=False
    )

    cv2.destroyWindow("Seleccionar ROI")
    if w == 0 or h == 0: # ROI cancelado
        return None

    return x, y, w, h

def print_roi(x, y, w, h):
    x1 = x
    y1 = y
    x2 = x + w
    y2 = y + h

    print("\nROI seleccionado:")
    print(f"x1 = {x1}")
    print(f"y1 = {y1}")
    print(f"x2 = {x2}")
    print(f"y2 = {y2}\n")

    return x1, y1, x2, y2

def main():
    cam = camera.open_camera(0)
    if cam is None:
        return

    print("Cámara abierta correctamente\n")
    print("Controles:")
    print("R -> seleccionar ROI")
    print("ESC -> salir")

    roi = None

    while True:
        frame = camera.read_frame(cam)

        if frame is None:
            print("No se pudo leer el frame.")
            break

        display = frame.copy() # Dibujar ROI 

        if roi is not None:
            x, y, w, h = roi

            cv2.rectangle(
                display,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                display,
                f"x1={x} y1={y} x2={x+w} y2={y+h}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        cv2.imshow("Calibracion ROI", display)
        key = cv2.waitKey(1) & 0xFF

        # ESC -> salir
        if key == 27:
            break

        # R -> seleccionar ROI
        elif key == ord("r"):
            selected_roi = select_roi(frame)

            if selected_roi is not None:
                roi = selected_roi
                x, y, w, h = roi
                x1, y1, x2, y2 = print_roi(x,y,w,h)

                selected_frame = camera.get_roi(frame,x1,y1,x2,y2)

                cv2.imshow("ROI seleccionado",selected_frame)

                print("Presiona R para seleccionar otro.")
                print("Presiona ESC para salir.")

    camera.close_camera(cam)

if __name__ == "__main__":
    main()
