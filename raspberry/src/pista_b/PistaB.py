import sys
import time
import cv2
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib import constants
from lib.communication import Communication, ArduinoRestarted
from lib.camera import (
    color_percentage,
    detect_object,
    filter_mask,
    hsv_mask,
    hsv_mask_custom,
    open_camera,
    read_frame,
    get_roi,
    detect_dominant_color,
    close_camera)

id_cameraFront = 2
id_cameraBack = 0

debug = True

cameraTime = 0.3 # 0.5
LINE_SECTION_2_X1 = 200
LINE_SECTION_2_X2 = 440

CENTER_X = 300 #272
CENTER_TOLERANCE = 20
# CONSTANTES
turnDegrees = 90
freeDistance = 20 * 10 #cm para considerar pared * 10 (mm a cm)

# CONFIGURACIÓN
SECCION_1 = 1
SECCION_2 = 2
SECCION_3 = 3
seccion_actual = SECCION_1

# ESTADO DE LA PELOTA
tiene_pelota = False

# ORIENTACIÓN 
NORTH = 0
EAST = 90
SOUTH = 180
WEST = 270

# RESOLVER PISTA B
def solve_niveles(communication):
    global seccion_actual

    cameraFront = open_camera(id_cameraFront)
    cameraBack = open_camera(id_cameraBack)
    if cameraFront is None:
        raise RuntimeError("No se pudo abrir la cámara frontal")
    if cameraBack is None:
        raise RuntimeError("No se pudo abrir la cámara trasera")
    for _ in range(30): # Leer los primeros 30 frames
        read_frame(cameraFront)
        read_frame(cameraBack)

    try:
        while True:
            # SECCIÓN 1
            if seccion_actual == SECCION_1:
                print("\nRESOLVIENDO SECCIÓN 1")
                resolver_seccion_1(communication, cameraBack)
                exit_seccion_1(communication, cameraFront)
                seccion_actual = SECCION_2
                print("Sección 1 completada")
                continue

            # SECCIÓN 2
            elif seccion_actual == SECCION_2:
                print("\nRESOLVIENDO SECCIÓN 2")
                resolver_seccion_2(communication,cameraFront)
                seccion_actual = SECCION_3
                print("Sección 2 completada")
                continue

            # SECCIÓN 3
            elif seccion_actual == SECCION_3:
                print("\nRESOLVIENDO SECCIÓN 3")
                resolver_seccion_3(communication,cameraFront)
                print("Sección 3 completada\nPISTA B TERMINADA")
                return True

    finally:
        close_camera(cameraFront)
        close_camera(cameraBack)


# SECCIÓN 1
def resolver_seccion_1(communication, camera):
    move_front(communication)
    center(communication)
    sensors = get_sensors(communication)
    if debug:
        print("Sensores:", sensors)

    if right_is_free(sensors) and left_is_free(sensors):
        if front_is_free(sensors):
            if debug:
                print("Pelota encontrada")
            turn_back(communication)
            take_ball(communication,camera)
            return
        else:
            turn_right(communication)
            center(communication)
            move_front(communication)
            center(communication)
            turn_left(communication)
            center(communication)
    elif right_is_free(sensors):
        turn_right(communication)
        center(communication)

    while True:
        move_front(communication)
        center(communication)
        sensors = get_sensors(communication)
        if left_is_free(sensors):
            turn_right(communication)
            if debug:
                print("Pelota encontrada")
            take_ball(communication,camera)
            return
        move_front(communication)
        center(communication)
        turn_left(communication)
        center(communication)


# PELOTA
def take_ball(communication, camera):
    global tiene_pelota

    sensors = get_sensors(communication)
    yaw_exit = sensors["yaw"]
    centrar_pelota(communication, camera)
    intake_in(communication) # Activar intake
    move_back(communication, 5)

    while(True): # Mientras no tenga pelota
        sensors = get_sensors(communication)
        if not down_is_free(sensors): # Tiene pelota el intake 
            tiene_pelota = True
            break

    stop_robot(communication)
    time.sleep(0.2) # Tiempo para asegurar que entre la pelota
    intake_off(communication)
    goto(communication, yaw_exit)

def centrar_pelota(communication, camera):
    while True:
        frame = read_frame(camera)
        if frame is None:
            if debug:
                print("No se pudo leer la cámara")
            continue

        # Detectar color naranja
        mask = hsv_mask_custom(frame, constants.ORANGE_BALL)
        mask = filter_mask(mask)

        obj = detect_object(mask) # Detectar objeto
        if obj is None:
            if debug:
                print("No se encontró la pelota")
            continue
        center_x = obj["center_x"]
        error_x = center_x - CENTER_X # Error en X

        if debug:
            print("Error x:", error_x)
            cv2.rectangle(
                frame,
                (CENTER_X - CENTER_TOLERANCE, 0),
                (CENTER_X + CENTER_TOLERANCE, frame.shape[0]),
                (0, 255, 0),
                2)
            cv2.imshow("Camera", frame) # Mostrar cámara
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Pelota centrada
        if abs(error_x) <= CENTER_TOLERANCE: 
            stop_robot(communication)
            time.sleep(0.2)
            if debug:
                print("Pelota centrada")
            return

        if error_x < 0: # Pelota a la izquierda
            spin_left(communication)
            #swipe_right(communication) # Gira a la derecha porque esta hacia atras el robot
        else: # Pelota a la derecha
            spin_right(communication)
            #swipe_left(communication) # Gira a la izquierda porque esta hacia atras el robot

def exit_seccion_1(communication, camera):
    center_distance(communication)
    time.sleep(0.1)
    center_angle(communication)
    time.sleep(0.1)
    move_front(communication)

    sensors = get_sensors(communication)
    if front_is_free(sensors):
        if(is_next_tile_red(camera)):
            move_front(communication)
            return

    turn_left(communication)
    move_front(communication)
    center(communication)

    while(True):
        sensors = get_sensors(communication)

        if(right_is_free(sensors)):
            turn_right(communication)
            if(is_next_tile_red(camera)):
                move_front(communication)
                return
            else:
                turn_left(communication)
        if(front_is_free(sensors)):
            if(is_next_tile_red(camera)):
                move_front(communication)
                return

        turn_left(communication)
        center(communication)

        move_front(communication)
        center(communication)
        sensors = get_sensors(communication)
        if(right_is_free(sensors)):
            turn_right(communication)
            if(is_next_tile_red(camera)):
                move_front(communication)
                return
            else:
                turn_left(communication)

        move_front(communication)
        center(communication)

def is_next_tile_red(camera):
    start_time = time.time()

    while time.time() - start_time < cameraTime:
        frame = read_frame(camera)
        if frame is None:
            continue

        roi = get_roi(frame, constants.ROI.NEXT_TILE_NIVELES)
        percentageRed = color_percentage(roi, constants.Color.RED)

        if debug:
            roi_coords = constants.ROI_COORDINATES[constants.ROI.NEXT_TILE_NIVELES]
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

        if percentageRed >= 40: # Mas de 40% es rojo
            return True

    return False


# SECCIÓN 2
def resolver_seccion_2(communication, camera):
    sensors = get_sensors(communication)
    yaw_frontal = sensors["yaw"]

    going_right = False
    going_left = False
    WALL_DISTANCE_SECCION2 = 15*10 # Distancia a la pared
    while True:
        frame = read_frame(camera)
        if frame is None:
            continue
        
        roiAdvance = get_roi(frame, constants.ROI.LINE_SECCION_2) 
        if debug:
            coordinates = constants.ROI_COORDINATES[constants.ROI.ADVANCE_SECTION_2]
            x1 = coordinates["x1"]
            y1 = coordinates["y1"]
            x2 = coordinates["x2"]
            y2 = coordinates["y2"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        percentageWhite = color_percentage(roiAdvance, constants.Color.WHITE)
        percentageRed = color_percentage(roiAdvance, constants.Color.RED)

        if percentageRed>30:
            stop_robot(communication)
            goto(communication, yaw_frontal)
            # Mover hasta centra rne las 2 paredes
            # VERRRR
            return True

        if going_right:
            sensors = get_sensors(communication)
            right = sensors["right"]

            if percentageWhite < 15:
                stop_robot(communication)
                going_right = False
                move_front(communication, 4)
                continue

            if right > WALL_DISTANCE_SECCION2:
                swipe_right(communication)
            else:
                stop_robot(communication)
                going_right = False
                goto(communication, yaw_frontal)
            continue

        if going_left:
            sensors = get_sensors(communication)
            left = sensors["left"]

            if percentageWhite < 15:
                stop_robot(communication)
                going_left = False
                move_front(communication, 4)
                continue

            if left > WALL_DISTANCE_SECCION2:
                swipe_left(communication)
            else:
                stop_robot(communication)
                going_left = False
                goto(communication, yaw_frontal)
            continue

        if percentageWhite > 15:
            stop_robot(communication)
            sensors = get_sensors(communication)
            left = sensors["left"]
            right = sensors["right"]

            if right > left + 20:
                going_right = True
            elif left > right + 20:
                going_left = True
            else:
                going_left = True
        
        else:
            move_front(communication,4)

def centrarCheckpoint(communication, camera):
    while True:
        frame = read_frame(camera)
        if frame is None:
            continue

        roi = get_roi(frame,constants.ROI.ADVANCE_SECTION_2)
        mask = hsv_mask(roi,constants.Color.RED)
        obj = detect_object(mask)
        if obj is None:
            stop_robot(communication)
            continue

        center_x = roi.shape[1] // 2
        object_x = obj["center_x"]
        error = object_x - center_x

        if abs(error) < 30: # px de tolerancia para considera centrado el tile
            stop_robot(communication)
            print("Checkpoint centrado")
            return
        elif error < 0:
            swipe_left(communication)
        else:
            swipe_right(communication)


# SECCIÓN 3
def resolver_seccion_3(communication, camera):
    reset_mpu(communication)
    nextColor = None

    while True:
        while nextColor is None:
            nextColor = get_next_tile_info(camera)
            if debug:
                print(nextColor)

        move_front(communication)
        center(communication)

        if nextColor == constants.Color.ORANGE:
            goto(communication, NORTH)  # Arriba
            center_angle(communication)
        elif nextColor == constants.Color.BLUE:
            goto(communication, EAST)  # Derecha
            center_angle(communication)
        elif nextColor == constants.Color.YELLOW:
            goto(communication, WEST)  # Izquierda
            center_angle(communication)
        elif nextColor == constants.Color.PINK:
            goto(communication, SOUTH)  # Abajo
            center_angle(communication)
        elif nextColor == constants.Color.GREEN:  # Verde --> terminar
            return

        nextColor = None


def get_next_tile_info(camera):
    start_time = time.time()
    color_samples = []

    colors = [
        constants.Color.ORANGE,
        constants.Color.BLUE,
        constants.Color.YELLOW,
        constants.Color.PINK,
        constants.Color.GREEN]

    while time.time() - start_time < cameraTime:
        frame = read_frame(camera)
        if frame is None:
            continue

        roi = get_roi(frame, constants.ROI.NEXT_TILE_NIVELES)
        percentages = {
            color: color_percentage(roi, color)
            for color in colors}
        color_samples.append(percentages)

        if debug:
            roi_coords = constants.ROI_COORDINATES[constants.ROI.NEXT_TILE_NIVELES]
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

    if color_samples:
        average_percentages = {
            color: sum(sample[color] for sample in color_samples) / len(color_samples)
            for color in colors
        }

        sorted_colors = sorted(
            average_percentages.items(),
            key=lambda item: item[1],
            reverse=True)

        best_color, best_percentage = sorted_colors[0]
        second_percentage = sorted_colors[1][1]

        if best_percentage >= 25 and best_percentage - second_percentage >= 10:
            dominant_color = best_color
        else:
            dominant_color = None
    else:
        dominant_color = None

    return dominant_color

# MOVIMIENTOS
def move_front(communication, direccion=1):
    if not communication.send(f"MOVE_OMNI|{direccion}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()

def move_back(communication, direccion=-1):
    if not communication.send(f"MOVE_OMNI|{direccion}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

    return communication.wait_done()

def swipe_right(communication, direccion=2):
    if not communication.send(f"MOVE_OMNI|{direccion}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def swipe_left(communication, direccion=3):
    if not communication.send(f"MOVE_OMNI|{direccion}"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def stop_robot(communication):
    if not communication.send("STOP"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def center_distance(communication):
    if not communication.send("CENTER|1"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def center_angle(communication):
    if not communication.send("CENTER|2"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def center(communication):
    time.sleep(0.1)
    center_angle(communication)
    time.sleep(0.1)
    center_distance(communication)
    time.sleep(0.1)

# GIROS
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

def spin_right(communication):
    if not communication.send(f"SPIN|R"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def spin_left(communication):
    if not communication.send(f"SPIN|L"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def goto(communication, angulo):
    if not communication.send(f"GOTO|{angulo}"):
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

def back_is_free(sensors, distance=freeDistance):
    return sensors["back"] is not None and sensors["back"] > distance

def down_is_free(sensors, distance=40):
    return sensors["down"] is not None and sensors["down"] > distance

def reset_mpu(communication):
    if not communication.send("RESET_MPU"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")

# INTAKE
def intake_in(communication):
    if not communication.send("INTAKE|IN"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def intake_out(communication):
    if not communication.send("INTAKE|OUT"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

def intake_off(communication):
    if not communication.send("INTAKE|OFF"):
        raise ArduinoRestarted("Se perdió la comunicación con Arduino")
    return communication.wait_done()

# MAIN
def main():
    while True:
        communication = Communication(port="/dev/ttyUSB0",baudrate=9600)

        try:
            print("\nEsperando Arduino...")
            communication.wait_ready()
            solve_niveles(communication)
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