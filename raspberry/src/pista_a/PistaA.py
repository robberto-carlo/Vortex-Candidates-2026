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

cmTile = 30
turnDegrees = 90
freeDistance = 20
cameraTime = 0.3
initialRightHand = True
debug = True

# MOVIMIENTOS
def move_front(communication, cm=cmTile):
    if not communication.send(f"MOVE|{cm}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()

def turn_right(communication, degrees=turnDegrees):
    if not communication.send(f"TURN|R|{degrees}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()

def turn_left(communication, degrees=turnDegrees):
    if not communication.send(f"TURN|L|{degrees}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()

def turn_back(communication, direction="R"):
    if direction not in ("R", "L"):
        print("Dirección de giro inválida")
        return None

    if not communication.send(f"TURN|{direction}|180"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()


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

def invert_direction(direction):
    if direction == "RIGHT":
        return "LEFT"
    if direction == "LEFT":
        return "RIGHT"
    return direction


# EJECUTAR DECISION
def execute_direction(communication, direction, camera):
    if direction == "FRONT":
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication)

    elif direction == "RIGHT":
        turn_right(communication)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication)

    elif direction == "LEFT":
        turn_left(communication)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication)

    elif direction == "BACK":
        turn_back(communication)
        next_color,next_aruco = get_next_tile_info(camera)
        move_front(communication)

    if debug:
        print("Color siguiente tile:", next_color.name if next_color else None)
        print("ArUco siguiente tile:", next_aruco)

    return next_color, next_aruco

# CAMARA
def get_next_tile_info(camera):
    start_time = time.time()
    colors = []
    arucos = []

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
            arucos.append(aruco)

        if debug:
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

# MAZE
def solve_maze(communication):
    print("INICIANDO MAZE")

    camera = open_camera(0)
    if camera is None:
            raise RuntimeError("No se pudo abrir la cámara")

    try:
        tile = 1
        currentRightHand = initialRightHand
        route = []

        if debug:
            print("Tile:", tile)
            print("Dirección:", "FRONT")
        
        next_color,next_aruco = execute_direction(communication,"FRONT",camera)
        communication.send(f"LCD|{next_color}|{next_aruco}")
        tile += 1
        
        while True:
            if debug:
                print("Tile:", tile)

            sensors = get_sensors(communication)
            if debug:
                print("Sensores:", sensors)

            if next_color == constants.Color.RED:
                if debug:
                    print("Final:", route)

                turn_back(communication)
                move_front(communication)

                for direction in reversed(route): # Hacer los movimientos pero inversos
                    if debug:
                        print("Regresando:", direction)
                    execute_direction(communication,direction,camera)
                break

            if next_color == constants.Color.GREEN: # Next color es Verde
                if debug:
                    print("Cambio de regal de mano")
                currentRightHand = not currentRightHand

            direction = decide_direction(sensors, currentRightHand)
            route.append(invert_direction(direction))
            if debug:
                print("Dirección:", direction)
            next_color, next_aruco = execute_direction(communication,direction,camera)
            communication.send(f"LCD|{next_color}|{next_aruco}")
            tile += 1

    finally:
        close_camera(camera)


# MAIN
def main():
    while True:
        communication = Communication(port="COM6",baudrate=9600)

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