import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
import lib.camera as camera

def main():
    cam = camera.open_camera(0)
    print("Cámara abierta correctamente.")
    camera.camera_info(cam)

    while True:
        frame = camera.read_frame(cam)
        if frame is None:
            break

        color = camera.detect_dominant_color(frame)
        if color is not None:
            cv2.putText(
                frame,
                f"Color: {color.value}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
        cv2.imshow("Dominant Color", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.close_camera(cam)

if __name__ == "__main__":
    main()