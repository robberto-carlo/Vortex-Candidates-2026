import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
import cv2
from lib.camera import (
    open_camera,
    read_frame,
    detect_aruco,
    close_camera)

camera = open_camera(0)

if camera is None:
    exit()

while True:
    frame = read_frame(camera)
    if frame is None:
        continue

    aruco = detect_aruco(frame)
    print("ArUco ID:", aruco)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

close_camera(camera)