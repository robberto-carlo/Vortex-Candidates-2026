import cv2
import numpy as np
import lib.constants as constants

# Camera
def open_camera(camera_id=0):
    camera = cv2.VideoCapture(camera_id)
    if not camera.isOpened():
        print("No se pudo abrir la cámara.")
        return None
    return camera

def read_frame(camera):
    ret, frame = camera.read()
    return frame if ret else None

def close_camera(camera):
    camera.release()
    cv2.destroyAllWindows()

def get_roi(frame, roi):
    coordinates = constants.ROI_COORDINATES[roi]
    x1 = coordinates["x1"]
    y1 = coordinates["y1"]
    x2 = coordinates["x2"]
    y2 = coordinates["y2"]

    return frame[y1:y2, x1:x2]

def color_percentage(frame, color):
    mask = hsv_mask(frame, color)

    color_pixels = cv2.countNonZero(mask)
    total_pixels = mask.size
    percentage = (color_pixels / total_pixels) * 100

    return percentage

def camera_info(camera):
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = camera.get(cv2.CAP_PROP_FPS)

    print("Camera information:")
    print(f"Resolution: {width} x {height}")
    print(f"FPS: {fps}")

# Detection
def hsv_mask(frame, color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

    for lower, upper in constants.COLOR_RANGES_HSV[color]:
        mask |= cv2.inRange(hsv, lower, upper)

    return mask

def threshold(frame, color, inverse=False):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lower, upper = constants.THRESHOLD_RANGES[color]
    mask = cv2.inRange(gray, lower, upper)

    if inverse:
        mask = cv2.bitwise_not(mask)
    return mask

def filter_mask(mask, kernel_size=5):
    if mask is None or mask.size == 0:
        return mask

    # Filtros
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # Area minima
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_mask = np.zeros_like(mask)
    for cnt in contours:
        if cv2.contourArea(cnt) >= constants.MIN_COLOR_AREA:
            cv2.drawContours(filtered_mask, [cnt], -1, 255, thickness=cv2.FILLED)

    return filtered_mask

def detect_object(mask):
    contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)

    if area < constants.MIN_OBJECT_AREA:
        return None

    x, y, w, h = cv2.boundingRect(contour)

    return {
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "center_x": x + w // 2,
        "center_y": y + h // 2,
        "area": area
    }

def detect_dominant_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    best_color = None
    best_area = 0

    for color in constants.COLOR_RANGES_HSV:
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in constants.COLOR_RANGES_HSV[color]:
            mask |= cv2.inRange(hsv, lower, upper)
        area = cv2.countNonZero(mask)

        if area > best_area:
            best_area = area
            best_color = color

    return best_color

# Detectar ArUco
def detect_aruco(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary,parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is None:
        return None
    return int(ids[0])

# Display
def draw_object(frame, obj):
    if obj is None:
        return frame

    x = obj["x"]
    y = obj["y"]
    w = obj["width"]
    h = obj["height"]
    u = obj["center_x"]
    v = obj["center_y"]

    cv2.rectangle(
        frame,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        2
    )

    cv2.circle(
        frame,
        (u, v),
        5,
        (0, 0, 255),
        -1
    )

    cv2.putText(
        frame,
        f"U: {u}  V: {v}",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    return frame

def draw_color(frame, mask):
    contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        cv2.drawContours(
            frame,
            [contour],
            -1,
            (0, 255, 0),
            2
        )

    return frame