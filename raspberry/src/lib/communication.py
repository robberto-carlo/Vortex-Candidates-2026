import serial
import threading
from lib import constants

class ArduinoRestarted(Exception):
    pass

class Communication:
    def __init__(self, port=constants.SERIAL_PORT, baudrate=constants.BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.serial = None

        # Valor de Sensores
        self.S = {
            "front": None,
            "right": None,
            "left": None,
            "back": None,
            "color": None,
            "yaw": None,
            "pitch": None
        }

        self.ready = False
        self.status = "ESPERANDO"
        self.initialized = False
        self.last_done = None # Cambiar a una lista
        self.last_done_id = None
        self.command_id = 0
        self.waiting_id = None

        # Eventos
        self.done_event = threading.Event()
        self.sensor_event = threading.Event()
        self.ready_event = threading.Event()
        self.restart_event = threading.Event()

        self.running = True
        # Hilo
        self.thread = threading.Thread(
            target=self._read_serial,
            daemon=True
            )

        # Conectar
        self._connect()
        self.thread.start()

    def _connect(self): # Conectar la comunicacion Serial
        while self.running:
            try:
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=0.1
                )
                print(f"Conectado a {self.port}")
                return

            except serial.SerialException:
                self.ready = False
                self.status = "ESPERANDO"
                print(f"No se pudo conectar a {self.port}")
                threading.Event().wait(0.5) # Esperar 0.5 segundos para volver a intentarlo

    def _next_id(self):
        self.command_id += 1
        return self.command_id

    # Hilo para leer comunicacion Serial
    def _read_serial(self):
        while self.running:
            try:
                line = self.serial.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()
                if not line: # Line esta vacio
                    continue
                print(f"Arduino: {line}") # Ver que mando el arduino - logging

                # INIT - Inicio/Reincio de Arduino
                if line == "INIT":
                    self._reset_state()

                    self.ready = True
                    self.status = "LISTO"

                    if not self.initialized: # Primer INIT = Arduino arrancó normalmente
                        self.initialized = True
                        print("Arduino listo") # logging
                    else: # Despues del primer INIT = Arduino se reinició
                        self.restart_event.set()
                        print("Arduino se reinició") # logging

                    self.ready_event.set()

                # DONE - El Arduino termino la accion que se pidio
                elif line.startswith("DONE|"):
                    parts = line.split("|")

                    if len(parts) != 3:
                        print("DONE inválido")
                        continue

                    try:
                        self.last_done_id = int(parts[2])
                    except ValueError:
                        print("ID de DONE inválido")
                        continue

                    if self.waiting_id == self.last_done_id:
                        self.last_done = parts[1] # Ultima accion que realizo
                        self.done_event.set()

                # SENSORES
                elif line.startswith("SENSOR|"):
                    self._read_sensor_data(line)

                # ERROR
                elif line.startswith("ERROR|"):
                    print(f"Error Arduino: {line}")  # logging

            except serial.SerialException:
                print("Arduino desconectado") # logging
                self.ready = False
                self.status = "ESPERANDO"

                try:
                    if self.serial is not None: # Borrar comunicacion Serial perdida 
                        self.serial.close()

                except Exception:
                    pass

                self.serial = None
                self._connect() # Intentar conectar nuevamente al Arduino

    # REINICIAR ESTADO
    def _reset_state(self):
        self.S = {
            "front": None,
            "right": None,
            "left": None,
            "back": None,
            "color": None,
            "yaw": None,
            "pitch": None
        }
        self.last_done = None
        self.last_done_id = None
        self.waiting_id = None
        self.done_event.clear()
        self.sensor_event.clear()
        self.ready = False

    # LEER SENSORES
    def _read_sensor_data(self, line):
        parts = line.split("|")
        if len(parts) != 8: # Verificar que llego todos los datos
            return

        try: # Guardar valores de los sensores
            self.S["front"] = float(parts[1])
            self.S["right"] = float(parts[2])
            self.S["left"] = float(parts[3])
            self.S["back"] = float(parts[4])
            self.S["color"] = parts[5]
            self.S["yaw"] = float(parts[6])
            self.S["pitch"] = float(parts[7])
            self.sensor_event.set()

        except ValueError:
            print("Datos de sensores inválidos") # logging

    # ENVIAR COMANDOS
    def send(self, command):
        if not self.ready or self.serial is None:
            print("No se puede mandar comando - Arduino Desconectado") # logging
            return False

        try:
            command_id = self._next_id()
            self.waiting_id = command_id
            command_with_id = f"{command}|{command_id}"
            self.serial.write((command_with_id + "\n").encode("utf-8"))
            self.serial.flush()
            return True

        except serial.SerialException:
            self.ready = False
            self.status = "ESPERANDO"
            print("Arduino se desconectó al enviar comando") # logging
            return False

    # ESPERAR DONE
    def wait_done(self):
        while True:
            if self.restart_event.is_set(): # Arduino se reinició a media accion
                self.restart_event.clear()
                raise ArduinoRestarted("Arduino se reinició mientras se esperaba DONE")

            if self.done_event.wait(0.1): # Arduino termino la accion
                self.done_event.clear()

                return self.last_done

    # PEDIR SENSORES
    def request_sensors(self):
        self.sensor_event.clear()

        if not self.send("GET_SENSOR"):
            return None

        while True:
            if self.restart_event.is_set(): # Arduino se reinició mientras esperaba sensores
                self.restart_event.clear()
                raise ArduinoRestarted("Arduino se reinició mientras se esperaban sensores")

            if self.sensor_event.wait(0.1): # Llegaron los valores de los sensores
                self.sensor_event.clear()
                return self.S.copy()

    # ESPERAR INIT - Inicio del Arduino
    def wait_ready(self):
        self.ready_event.wait()
        self.ready_event.clear()

    # CERRAR
    def close(self):
        self.running = False

        if self.serial is not None:
            try:
                self.serial.close()
            except Exception:
                pass