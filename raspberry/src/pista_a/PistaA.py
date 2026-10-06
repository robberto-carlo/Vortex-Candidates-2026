import sys
import time
import cv2
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib import constants
from lib.communication import Communication, ArduinoRestarted
from lib.camera import (
    open_camera,
    read_frame,
    get_roi,
    detect_dominant_color,
    detect_aruco,
    close_camera)

id_camera = 0
turnDegrees = 90
freeDistance = 20 * 10 #cm -> mm para considerar pared
cameraTime = 0.3 # 0.5
initialRightHand = True
debug = True
showCamera = True

last_aruco = None
aruco_backup_start = time.time()
aruco_backup_ids = []

# MOVIMIENTOS
def move_front(communication, camera=None, direccion=1):
    if not communication.send(f"MOVE|{direccion}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera, update_camera=update_aruco_backup)

def turn_right(communication, camera=None, degrees=turnDegrees):
    if not communication.send(f"TURN|R|{degrees}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera, update_camera=update_aruco_backup)

def turn_left(communication, camera=None, degrees=turnDegrees):
    if not communication.send(f"TURN|L|{degrees}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera, update_camera=update_aruco_backup)

def turn_back(communication, camera=None, direction="R"):
    if direction not in ("R", "L"):
        print("Dirección de giro inválida")
        return None

    if not communication.send(f"TURN|{direction}|180"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera, update_camera=update_aruco_backup)

def center_distance(communication, camera=None):
    if not communication.send("CENTER|1"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera,update_camera=update_aruco_backup)

def center_angle(communication, camera=None):
    if not communication.send("CENTER|2"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done(camera=camera,update_camera=update_aruco_backup)

def center(communication, camera=None):
    time.sleep(0.1)
    center_angle(communication)
    time.sleep(0.1)
    center_distance(communication, camera)
    time.sleep(0.1)

# SENSORES
def get_sensors(communication):
    sensors = communication.request_sensors()
    if sensors is None:
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return sensors

def front_is_free(sensors, distance=freeDistance):
    return sensors["front"] is not None and sensors["front"] > distance

def right_is_free(sensors, distance=freeDistance):
    return sensors["right"] is not None and sensors["right"] > distance

def left_is_free(sensors, distance=freeDistance):
    return sensors["left"] is not None and sensors["left"] > distance

def is_red_sensor(sensors):
    return sensors["color"] if sensors["color"] == "RED" else None

def is_green_sensor(sensors):
    return sensors["color"] if sensors["color"] == "GREEN" else None

# DECISIONES
def decide_direction(sensors, currentRightHand):
    if currentRightHand:
        if right_is_free(sensors):
            return "RIGHT"
        if front_is_free(sensors):
            return "FRONT"
        if left_is_free(sensors):
            return "LEFT"
        return "BACK"
    else: 
        if left_is_free(sensors):
            return "LEFT"
        if front_is_free(sensors):
            return "FRONT"
        if right_is_free(sensors):
            return "RIGHT"
        return "BACK"

# EJECUTAR DECISION
def execute_direction(communication, direction, camera):
    global last_aruco
    next_color = None
    next_aruco = None
    if direction == "FRONT":
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication, camera)
        center_distance(communication,camera)

    elif direction == "RIGHT":
        turn_right(communication, camera)
        center(communication, camera)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication, camera)
        center_distance(communication,camera)

    elif direction == "LEFT":
        turn_left(communication, camera)
        center(communication, camera)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication, camera)
        center_distance(communication,camera)

    elif direction == "BACK":
        turn_back(communication, camera)
        center(communication, camera)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication, camera)
        center_distance(communication,camera)

    if next_aruco is None:
        if last_aruco is not None:
            next_aruco = last_aruco
            last_aruco = None
        
    if debug:
        print("Color siguiente tile:", next_color.name if next_color else None)
        print("ArUco siguiente tile:", next_aruco)

    return next_color, next_aruco

# CAMARA
def get_next_tile_info(camera):
    start_time = time.time()
    colors = []
    arucos = []
    time.sleep(0.2)
    while time.time() - start_time < cameraTime:
        frame = read_frame(camera)
        if frame is None:
            continue
        roi = get_roi(frame, constants.ROI("nextTileMaze"))

        color = detect_dominant_color(roi)
        if color is not None and color != constants.Color.WHITE:
            colors.append(color)

        aruco = detect_aruco(frame)
        if aruco is not None:
            aruco_id, corners = aruco
            arucos.append(aruco_id)

            if showCamera:
                corners_int = corners.astype(int)
                cv2.polylines(
                    frame,
                    [corners_int],
                    True,
                    (0, 255, 0),
                    2)
                x, y = corners_int[0][0]
                cv2.putText(
                    frame,
                    f"ArUco: {aruco_id}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2)

        if showCamera:
            roi_coords = constants.ROI_COORDINATES[constants.ROI.NEXT_TILE_MAZE]
            x1 = roi_coords["x1"]
            y1 = roi_coords["y1"]
            x2 = roi_coords["x2"]
            y2 = roi_coords["y2"]

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2)
            cv2.imshow("Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if colors:
        dominant_color = max(set(colors), key=colors.count) # Color más detectado
    else:
        dominant_color = None

    if arucos:
        detected_aruco = max(set(arucos), key=arucos.count) # ArUco más detectado
    else:
        detected_aruco = None

    return dominant_color, detected_aruco

def update_aruco_backup(camera):
    global last_aruco
    global aruco_backup_start
    global aruco_backup_ids

    frame = read_frame(camera)
    if frame is not None:
        aruco = detect_aruco(frame)
        if aruco is not None:
            aruco_id, corners = aruco
            aruco_backup_ids.append(aruco_id)

            if showCamera:
                corners_int = corners.astype(int)
                cv2.polylines(
                    frame,
                    [corners_int],
                    True,
                    (0, 255, 0),
                    2)
                x, y = corners_int[0][0]
                cv2.putText(
                    frame,
                    f"ArUco: {aruco_id}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2)

        if showCamera:
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return last_aruco
        
    if time.time() - aruco_backup_start >= 3:
        if aruco_backup_ids:
            last_aruco = max(set(aruco_backup_ids),key=aruco_backup_ids.count)
            if debug:
                print("ID detectado:", last_aruco)
            aruco_backup_ids.clear()

        aruco_backup_start = time.time()
    return last_aruco

# MAZE
def solve_maze(communication):
    print("INICIANDO MAZE")

    camera = open_camera(id_camera)
    if camera is None:
            raise RuntimeError("No se pudo abrir la cámara")
    for _ in range(30): # Esperar los primeros 30 frames
        read_frame(camera)

    try:
        tile = 1
        currentRightHand = initialRightHand
        green_count = 0
        isFinalMode = False

        if debug:
            print("Tile:", tile)
            print("Dirección:", "FRONT")

        center(communication, camera)
        next_color,next_aruco = execute_direction(communication,"FRONT",camera)
        send_lcd(communication, next_color, next_aruco)
        tile += 1
        
        while True:
            if debug:
                print("Tile:", tile)

            sensors = get_sensors(communication)
            if debug:
                print("Sensores:", sensors)

            if next_color == constants.Color.RED:
                if debug:
                    print("Llegaste al final")
                    print("Regresando")

                turn_back(communication, camera)
                center(communication, camera)
                move_front(communication, camera)
                center_distance(communication,camera)
                sensors = get_sensors(communication)

                currentRightHand = not currentRightHand
                isFinalMode = True  

            elif next_color == constants.Color.GREEN: # Next color es Verde
                if(isFinalMode):
                    if(green_count>0):
                        green_count -= 1
                    else:
                        if debug:
                            print("Rregesaste al principio")
                        break # Terminar codigo
                else:
                    green_count += 1
                    if debug:
                        print("Cambio de regal de mano")
                currentRightHand = not currentRightHand

            direction = decide_direction(sensors, currentRightHand)
            if debug:
                print("Dirección:", direction)
            next_color, next_aruco = execute_direction(communication,direction,camera)
            send_lcd(communication, next_color, next_aruco)
            tile += 1

    finally:
        close_camera(camera)

def send_lcd(communication, color, aruco):
    color_text = color.name if color is not None else ""
    aruco_text = str(aruco) if aruco is not None else ""
    communication.send(f"LCD|{color_text}|{aruco_text}")

# MAIN
def main():
    while True:
        communication = Communication(port="/dev/ttyUSB0",baudrate=9600)

        try:
            print("Esperando Arduino...")
            communication.wait_ready()

            solve_maze(communication)
            break

        except ArduinoRestarted:
            print("\nArduino se reinició o se perdió la comunicación\n")
            communication.close()

        except KeyboardInterrupt:
            print("Programa detenido")
            communication.close()
            break

if __name__ == "__main__":
    main()
