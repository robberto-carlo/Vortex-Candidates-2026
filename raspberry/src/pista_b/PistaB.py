import sys
import time
import cv2
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib import constants
from lib.communication import Communication, ArduinoRestarted
from lib.camera import (
    color_percentage_hsv,
    color_percentage_hsv_pista_b,
    detect_object,
    filter_mask,
    get_color_percentages_hsv,
    hsv_mask,
    hsv_mask_custom,
    open_camera,
    read_frame,
    get_roi,
    close_camera)

id_cameraFront = 0
id_cameraBack = 2

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
def solve_niveles(communication, cameraFront, cameraBack):
    global seccion_actual

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
        mask = hsv_mask_custom(frame, constants.COLOR_RANGES_HSV_PISTA_B["ORANGE_BALL"])
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
        else:
            move_back(communication,5)
            time.sleep(0.5)
            stop_robot(communication)

    turn_left(communication)
    move_front(communication)
    center(communication)

    while(True):
        sensors = get_sensors(communication)

        if(right_is_free(sensors)):
            turn_right(communication)
            if(is_next_tile_red(camera)):
                center(communication)
                move_front(communication)
                return
            else:
                turn_left(communication)
        if(front_is_free(sensors)):
            if(is_next_tile_red(camera)):
                center(communication)
                move_front(communication)
                return
            else:
                move_back(communication,5)
                time.sleep(0.5)
                stop_robot(communication)

        turn_left(communication)
        center(communication)

        move_front(communication)
        center(communication)
        sensors = get_sensors(communication)
        if(right_is_free(sensors)):
            turn_right(communication)
            if(is_next_tile_red(camera)):
                center(communication)
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
        percentageRed = color_percentage_hsv_pista_b(roi, constants.Color.RED)

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
    WALLFRONT_DISTANCE_SECCION2 = 5.5*10 #6.5*10 # Distancia a la pared 
    WALL_DISTANCE_SECCION2 = 7.5*10 #6.5*10 # Distancia a la pared 
    move_front(communication)

    while True:
        frame = read_frame(camera)
        if frame is None:
            continue

        coordinates = constants.ROI_COORDINATES[constants.ROI.ADVANCE_SECTION_2]
        x1 = coordinates["x1"]
        y1 = coordinates["y1"]
        x2 = coordinates["x2"]
        y2 = coordinates["y2"]

        if debug:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        sensors = get_sensors(communication)
        paredFront = sensors["front"] is not None and sensors["front"] < WALLFRONT_DISTANCE_SECCION2
        paredRight = sensors["right"] is not None and sensors["right"] < WALL_DISTANCE_SECCION2
        paredLeft = sensors["left"] is not None and sensors["left"] < WALL_DISTANCE_SECCION2
        if paredLeft and paredRight:
            roiAdvance = frame[y1:y2, x1 + 55:x2 - 45] # recortar x1 a 245px y recortar x2 a 400px
        elif paredLeft:
            roiAdvance = frame[y1:y2, x1 + 55:x2] # recortar x1 a 245px
        elif paredRight:
            roiAdvance = frame[y1:y2, x1:x2 - 45] #recortar x2 a 400px
        else:
            roiAdvance = frame[y1:y2, x1:x2]

        percentages = get_color_percentages_hsv(roiAdvance,constants.Color.WHITE,constants.Color.RED)
        percentageWhite = percentages[constants.Color.WHITE]
        percentageRed = percentages[constants.Color.RED]

        if percentageRed>=30 or paredFront: # o si hay pared enfrentre
            stop_robot(communication)
            time.sleep(0.1)
            goto(communication, yaw_frontal)
            time.sleep(0.1)
            centrarCheckpoint(communication, paredFront)
            centerRedTile(communication)
            #move_front(communication)
            return True

        elif percentageWhite >= 5:
            stop_robot(communication)
            roiLine = get_roi(frame, constants.ROI.LINE_SECCION_2)
            _ , width = roiLine.shape[:2]
            middle_x = width // 2

            roiLeft = roiLine[:, :middle_x]
            roiRight = roiLine[:, middle_x:]
            roiLeft_verificacion = roiAdvance[:, :35]
            roiRight_verificacion = roiAdvance[:, -35:]

            percentageGreenLeft = color_percentage_hsv_pista_b(roiLeft, constants.Color.GREEN)
            percentageGreenRight = color_percentage_hsv_pista_b(roiRight, constants.Color.GREEN)
            percentageWhiteLeft = color_percentage_hsv_pista_b(roiLeft_verificacion, constants.Color.WHITE)
            percentageWhiteRight = color_percentage_hsv_pista_b(roiRight_verificacion, constants.Color.WHITE)

            if percentageWhiteLeft < 2 and percentageWhiteRight < 2:
                move_front(communication)
                continue

            lineWhite = 0
            if percentageWhiteLeft >= 10:
                lineWhite=0
            if percentageWhiteRight >= 10:
                lineWhite=0

            if percentageGreenLeft > percentageGreenRight:
                turn_left(communication)
                centrarLine(communication, lineWhite)
                turn_right(communication)
                goto(communication, yaw_frontal)
                center_angle(communication)
            else:
                turn_right(communication)
                centrarLine(communication, lineWhite)
                turn_left(communication)
                goto(communication, yaw_frontal)
                center_angle(communication)
        else:
            stop_robot(communication)
            time.sleep(0.1) 
            move_front(communication)

def centrarLine(communication, lineWhite):
    stop_robot(communication) 
    time.sleep(0.1) 
    if lineWhite == 2:
        move_front(communication)
    else:
        move_front(communication, 6) 

def centrarCheckpoint(communication, paredFront): 
    while True:
        sensors = get_sensors(communication)
        paredRight = sensors["right"] 
        paredLeft = sensors["left"]
        if paredRight is None or paredLeft is None:
            continue

        if paredFront:
            center(communication)
            if paredRight > paredLeft:
                turn_right(communication)
                center(communication)
                move_front(communication)
                center(communication)
                turn_left(communication)
                center(communication)
                sensors = get_sensors(communication)
                if (front_is_free(sensors)):
                    return
            else: # Pared izquierda es la mas lejana
                turn_left(communication)
                center(communication)
                move_front(communication)
                center(communication)
                turn_right(communication)
                center(communication)
                sensors = get_sensors(communication)
                if (front_is_free(sensors)):
                    return

        else: # Detecto el tile rojo
            center(communication)
            if paredRight < paredLeft:
                turn_right(communication)
                center(communication)
                turn_left(communication)
                center(communication)
                sensors = get_sensors(communication)
                if (front_is_free(sensors)):
                    return
                else:
                    paredFront = True
            else: # Pared izquierda es la mas lejana
                turn_left(communication)
                center(communication)
                turn_right(communication)
                center(communication)
                sensors = get_sensors(communication)
                if (front_is_free(sensors)):
                    return
                else:
                    paredFront = True


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
        elif nextColor == "LIME_GREEN":  # Verde --> terminar
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
        "LIME_GREEN"]

    while time.time() - start_time < cameraTime:
        frame = read_frame(camera)
        if frame is None:
            continue

        roi = get_roi(frame, constants.ROI.NEXT_TILE_NIVELES)
        percentages = get_color_percentages_hsv(roi, *colors)
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

    if not color_samples:
        return None

    average_percentages = {
        color: sum(sample[color] for sample in color_samples) / len(color_samples)
        for color in colors
    }

    sorted_colors = sorted(average_percentages.items(), key=lambda item: item[1], reverse=True)
    best_color, best_percentage = sorted_colors[0]
    second_percentage = sorted_colors[1][1]

    if best_percentage >= 15 and best_percentage - second_percentage >= 10:
        return best_color
    return None

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

def centerRedTile(communication): # PROBAR
    targetDistance = 970
    error = 10

    while True:
        sensors = get_sensors(communication)
        frontDistance = sensors["front"]

        if frontDistance is None:
            stop_robot(communication)
            continue

        if frontDistance > targetDistance + error:
            move_front(communication, 4)
        elif frontDistance < targetDistance - error:
            move_back(communication, 5)
        else:
            stop_robot(communication)
            break

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
    return communication.wait_done()

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
    cameraFront = None
    cameraBack = None
    communication = None
    try:
        cameraFront = open_camera(id_cameraFront)
        if cameraFront is None:
            raise RuntimeError("No se pudo abrir la cámara frontal")
        cameraBack = open_camera(id_cameraBack)
        if cameraBack is None:
            raise RuntimeError("No se pudo abrir la cámara trasera")
        for _ in range(30): # Leer los primeros 30 frames
            read_frame(cameraFront)
            read_frame(cameraBack)

        while True:
            communication = Communication(port="/dev/ttyUSB0",baudrate=9600)
            try:
                print("\nEsperando Arduino...")
                communication.wait_ready()
                solve_niveles(communication, cameraFront, cameraBack)
                break
            except ArduinoRestarted:
                print("\nArduino se reinició o se perdió la comunicación\n")
                communication.close()
            except KeyboardInterrupt:
                print("Programa detenido")
                communication.close()
                break
    finally:
        if communication is not None:
            communication.close()
        if cameraFront is not None:
            close_camera(cameraFront)
        if cameraBack is not None:
            close_camera(cameraBack)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
