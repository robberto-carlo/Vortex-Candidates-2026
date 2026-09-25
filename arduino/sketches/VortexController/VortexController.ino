// VORTEX - Arduino Controller
#include <Wire.h>
#include <MPU6050.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_TCS34725.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
MPU6050 mpu;
Adafruit_TCS34725 tcs = Adafruit_TCS34725(
  TCS34725_INTEGRATIONTIME_50MS,
  TCS34725_GAIN_4X
);
// Motores Intake
const int intakePin1 = 10;
const int intakePin2 = 11;

// Motores movimiento
const int motFR1 = 39; // Naranja
const int motFR2 = 41;
const int motFL1 = 37; // Amarillo
const int motFL2 = 35;
const int motBR1 = 31; // Morado
const int motBR2 = 29;
const int motBL1 = 27; // Azul
const int motBL2 = 25;

// Pines PWM de velocidad
const int potmotFR = 7; 
const int potmotFL = 6; 
const int potmotBR = 5; 
const int potmotBL = 4; 

// PINES DE ENCODERS
const int encoderIzqPin = 2; // Izquierdo en Pin 2
const int encoderDerPin = 3; // Derecho en Pin 3

// Variables para el conteo de pulsos
volatile long encoderIzqCount = 0;
volatile long encoderDerCount = 0;

// Variables de control del MPU6050
float targetYaw = 0;    
float currentYaw = 0;    
unsigned long lastTime = 0;
float gyroZoffset = 0;

float Kp = 25.0; // Fuerza de corrección
float KpSwipe = 8.0;

// Velocidades base
int baseFR = 180;
int baseFL = 180;
int baseBR = 180;
int baseBL = 180;

// Temporizadores
unsigned long lastDisplayTime = 0;
const int displayInterval = 250; 
unsigned long lastSerialTime = 0;
const int serialInterval = 100; 

int lastDirection = 0; 

void setup() {
  Serial.begin(9600);
  Wire.begin();
  
  // Inicializar LCD
  lcd.init();                     
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Iniciando MPU...");
  
  // Inicializar MPU6050
  mpu.initialize();
  if (!mpu.testConnection()) {
    lcd.clear();
    lcd.print("Error MPU6050");
    Serial.println("Error: MPU6050 no conectado."); // ERROR
    while (1);
  }

  if (!tcs.begin()) {
    lcd.clear();
    lcd.print("Error TCS34725");
    Serial.println("ERROR|TCS34725");
    while (1);
  }

  // Configurar pines de motores
  pinMode(motFR1, OUTPUT); pinMode(motFR2, OUTPUT);
  pinMode(motFL1, OUTPUT); pinMode(motFL2, OUTPUT);
  pinMode(motBR1, OUTPUT); pinMode(motBR2, OUTPUT);
  pinMode(motBL1, OUTPUT); pinMode(motBL2, OUTPUT);

  pinMode(potmotFR, OUTPUT);
  pinMode(potmotFL, OUTPUT);
  pinMode(potmotBR, OUTPUT);
  pinMode(potmotBL, OUTPUT);

  // Configurar pines del Intake
  pinMode(intakePin1, OUTPUT);
  pinMode(intakePin2, OUTPUT);

  digitalWrite(intakePin1, HIGH);
  digitalWrite(intakePin2, HIGH);

  // CONFIGURAR ENCODERS
  pinMode(encoderIzqPin, INPUT_PULLUP);
  pinMode(encoderDerPin, INPUT_PULLUP);
  // Asociamos las interrupciones por flanco de subida (RISING)
  attachInterrupt(digitalPinToInterrupt(encoderIzqPin), contarEncoderIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(encoderDerPin), contarEncoderDer, RISING);

  // Calibrar el giroscopio
  calibrarGyro();

  // Establecer la posición actual como el CERO absoluto
  lcd.clear();
  lcd.print("Seteando Cero...");
  delay(1000); 
  
  currentYaw = 0;    
  targetYaw = 0;       
  lastTime = millis();
  
  lcd.clear();
  Serial.println("INIT");
}

// RUTINAS DE INTERRUPCIÓN (ISR) PARA ENCODERS
void contarEncoderIzq() {
  encoderIzqCount++;
}

void contarEncoderDer() {
  encoderDerCount++;
}

// Resetea los contadores a cero antes de iniciar un desplazamiento
void reiniciarEncoders() {
  noInterrupts(); // Desactivar interrupciones temporalmente al modificar variables
  encoderIzqCount = 0;
  encoderDerCount = 0;
  interrupts();
}


// LOOP PRINCIPAL
void loop() {
  actualizarYaw();
  if (!Serial.available()) {
    return;
  }

  String comando = Serial.readStringUntil('\n');
  comando.trim();
  if (comando.length() == 0) {
    return;
  }

  Serial.print("RECIBIDO|");
  Serial.println(comando);

  // MOVE|DIRECCION|ID
  if (comando.startsWith("MOVE|")) {
    int p1 = comando.indexOf('|');
    int p2 = comando.indexOf('|', p1 + 1);
    if (p2 == -1) {
      Serial.println("ERROR|MOVE_FORMAT");
      return;
    }

    int direccion = comando.substring(p1 + 1, p2).toInt();
    int id = comando.substring(p2 + 1).toInt();

    if (direccion == 1) {
      Serial.println("MOVIENDO ADELANTE");
      avanzarPulsos(971, 1);

      Serial.print("DONE|MOVE|");
      Serial.println(id);
    }
    else if (direccion == -1) {
      Serial.println("MOVIENDO ATRAS");
      avanzarPulsos(971, -1);

      Serial.print("DONE|MOVE|");
      Serial.println(id);
    }
    else{
      Serial.println("ERROR|MOVE_DIRECTION");
    }
  }

  // TURN|R/L|GRADOS|ID
  else if (comando.startsWith("TURN|")) {
    int primerSeparador = comando.indexOf('|');
    int segundoSeparador = comando.indexOf('|', primerSeparador + 1);
    int tercerSeparador = comando.indexOf('|', segundoSeparador + 1);

    char direccion = comando.charAt(primerSeparador + 1);
    int grados = comando.substring(segundoSeparador + 1,tercerSeparador).toInt();
    int id = comando.substring(tercerSeparador + 1).toInt();

    if (direccion == 'R') {
        girarGrados(grados);
    }
    else if (direccion == 'L') {
        girarGrados(-grados);
    }
    else {
        Serial.println("ERROR|DIRECCION");
        return;
    }

    Serial.println("DONE|TURN|" + String(id));
  }

  // GOTO|ANGULO|ID
  else if (comando.startsWith("GOTO|")) {
    int p1 = comando.indexOf('|');
    int p2 = comando.indexOf('|', p1 + 1);
    if (p2 == -1) {
      Serial.println("ERROR|GOTO_FORMAT");
      return;
    }

    float angulo = comando.substring(p1 + 1, p2).toFloat();
    int id = comando.substring(p2 + 1).toInt();
    Serial.print("GOTO YAW: ");
    Serial.println(angulo);

    girar2(angulo);
    Serial.print("DONE|GOTO|");
    Serial.println(id);
  }

  // INTAKE|IN/OUT/OFF|ID
  else if (comando.startsWith("INTAKE|")) {
    int separador1 = comando.indexOf('|');
    int separador2 = comando.indexOf('|', separador1 + 1);

    String estado = comando.substring(separador1 + 1, separador2);
    int id = comando.substring(separador2 + 1).toInt();

    if (estado == "IN") {
        intakeOn(1); // Encender IN intake
        Serial.println("DONE|INTAKE|" + String(id));
    }
    else if (estado == "OUT") {
        intakeOn(-1); // Encender OUT intake
        Serial.println("DONE|INTAKE|" + String(id));
    }
    else if (estado == "OFF") {
        intakeOff(); // Apagar intake
        Serial.println("DONE|INTAKE|" + String(id));
    }
  }

  // RESET_MPU|ID
  else if (comando.startsWith("RESET_MPU|")) {
    int id = comando.substring(10).toInt();
    establecerCeroYaw();
    Serial.println("DONE|RESET_MPU|" + String(id));
  }

  // STOP|ID
  else if (comando.startsWith("STOP|")) {
    int id = comando.substring(5).toInt();
    parar();
    Serial.print("DONE|STOP|");
    Serial.println(id);
  }

  // GET_SENSOR|ID
  else if (comando.startsWith("GET_SENSOR|")) {
    int id = comando.substring(11).toInt();

    enviarSensores();
  }

  // LCD|COLOR|ARUCO
  else if (comando.startsWith("LCD|")) {
    int p1 = comando.indexOf('|');
    int p2 = comando.indexOf('|', p1 + 1);
    if (p2 == -1) {
      Serial.println("ERROR|LCD_FORMAT");
      return;
    }

    String color = comando.substring(p1 + 1, p2);
    String aruco = comando.substring(p2 + 1);

    lcd.clear();
    if (color.length() > 0) { // Primera línea
      lcd.setCursor(0, 0);
      lcd.print("Color: ");
      lcd.print(color);
    }

    if (aruco.length() > 0) { // Segunda línea
      lcd.setCursor(0, 1);
      lcd.print("ArUco: ");
      lcd.print(aruco);
    }
  }
  else{
    Serial.println("ERROR|COMANDO");
  }
}

// Avanzar por cantidad de pulsos
void avanzarPulsos(long pulsosObjetivo, int direccion) {
  reiniciarEncoders();

  if (direccion == 1) {
    lastDirection = 1;
  } else {
    lastDirection = -1;
  }

  while (true) { // Hasta que alcance el objetivo
    long pulsosActuales = (encoderIzqCount + encoderDerCount) / 2; // Obtener promedio de pulsos recorridos
    
    if (pulsosActuales >= pulsosObjetivo) {
      break; // Llegaste a la distancia objectivo 
    }

    actualizarYaw(); // Mantener la corrección con MPU6050
    float error = targetYaw - currentYaw;
    int ajuste = Kp * error;

    int speedFR, speedBR, speedFL, speedBL;
    if (direccion == 1) {
      speedFR = constrain(baseFR - ajuste, 0, 255);
      speedBR = constrain(baseBR - ajuste, 0, 255);
      speedFL = constrain(baseFL + ajuste, 0, 255);
      speedBL = constrain(baseBL + ajuste, 0, 255);
      moverAdelante(speedFR, speedFL, speedBR, speedBL);
    } else {
      speedFR = constrain(baseFR + ajuste, 0, 255);
      speedBR = constrain(baseBR + ajuste, 0, 255);
      speedFL = constrain(baseFL - ajuste, 0, 255);
      speedBL = constrain(baseBL - ajuste, 0, 255);
      moverAtras(speedFR, speedFL, speedBR, speedBL);
    }

    if (millis() - lastSerialTime >= serialInterval) {
      lastSerialTime = millis();
      Serial.print("[AVANCE PULSOS] Actuales: "); Serial.print(pulsosActuales);
      Serial.print(" / Target: "); Serial.print(pulsosObjetivo);
      Serial.print(" | ErrorYaw: "); Serial.println(error);
    }
  }

  parar();
}

// Función de tiempo detenido
void ejecutarAccionParar(unsigned long tiempo) {
  unsigned long inicio = millis();
  while (millis() - inicio < tiempo) {
    parar();
  }
}

// Funcion de giro
void girarGrados(float gradosDeseados) {
  if (gradosDeseados > 0) {
    lastDirection = 2;  // Giro derecha
  } else {
    lastDirection = 3;  // Giro izquierda
  }

  float anguloInicial = currentYaw;
  float anguloObjetivo = anguloInicial + gradosDeseados; 
  float KpGiro = 2.5; 

  unsigned long tiempoGiroPrevio = millis();
  while (true) {
    unsigned long currentTime = millis();
    float dt = (currentTime - tiempoGiroPrevio) / 1000.0;
    if (dt > 0.1) dt = 0.01;
    tiempoGiroPrevio = currentTime;
    lastTime = currentTime; 

    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    float gz_f = (gz - gyroZoffset) / 131.0;
    if (abs(gz_f) < 0.8) gz_f = 0;
    currentYaw += gz_f * dt;
    float errorGiro = anguloObjetivo - currentYaw;

    if (millis() - lastSerialTime >= serialInterval) {
      lastSerialTime = millis();
      Serial.print("[GIRAR] TargetYaw: "); Serial.print(targetYaw);
      Serial.print(" | CurrentYaw: "); Serial.print(currentYaw);
      Serial.print(" | Error: "); Serial.println(errorGiro);
    }

    if (abs(errorGiro) <= 1.5) {
      break;
    }

    int velocidadGiro = constrain(abs(errorGiro) * KpGiro, 90, 200);

    if (errorGiro > 0) {
      digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);  
      digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
      digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW); 
      digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);
    } else {
      digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);  
      digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
      digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH); 
      digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);
    }

    analogWrite(potmotFR, velocidadGiro);
    analogWrite(potmotBR, velocidadGiro);
    analogWrite(potmotFL, velocidadGiro);
    analogWrite(potmotBL, velocidadGiro);
  }

  parar();
  targetYaw = currentYaw; 
}

float normalizarAngulo(float angulo) {
  while (angulo > 180) {
    angulo -= 360;
  }
  while (angulo < -180) {
    angulo += 360;
  }
  return angulo;
}

void girar2(float anguloObjetivo) {
  float KpGiro = 2.5;
  anguloObjetivo = normalizarAngulo(anguloObjetivo);

  while (true) {
    actualizarYaw();
    float errorGiro = anguloObjetivo - normalizarAngulo(currentYaw);
    errorGiro = normalizarAngulo(errorGiro);

    if (millis() - lastSerialTime >= serialInterval) {
      lastSerialTime = millis();

      Serial.print("[GIRAR2] Target: ");
      Serial.print(anguloObjetivo);
      Serial.print(" | Current: ");
      Serial.print(currentYaw);
      Serial.print(" | Error: ");
      Serial.println(errorGiro);
    }

    if (abs(errorGiro) <= 1.5) { // Llegamos al objetivo
      break;
    }

    int velocidadGiro = constrain(abs(errorGiro) * KpGiro,80,200);
    if (errorGiro > 0) { // GIRO DERECHA
      digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);
      digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
      digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW);
      digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);

      lastDirection = 2;
    } else { // GIRO IZQUIERDA
      digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);
      digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
      digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH);
      digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);

      lastDirection = 3;
    }

    analogWrite(potmotFR, velocidadGiro);
    analogWrite(potmotFL, velocidadGiro);
    analogWrite(potmotBR, velocidadGiro);
    analogWrite(potmotBL, velocidadGiro);
  }

  parar();
  targetYaw = currentYaw;
}

// Funcion Parar
void parar() {
  actualizarYaw();

  if (lastDirection == 1) {
    digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);
    digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH);
    digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
    digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);
  } 
  else if (lastDirection == -1) {
    digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);
    digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW);
    digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
    digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);
  }
  else if (lastDirection == 2) {
    digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);
    digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
    digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW);
    digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);
  }
  else if (lastDirection == 3) {
    digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);
    digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
    digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH);
    digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);
  }

  if (lastDirection != 0) {
    analogWrite(potmotFR, 200);
    analogWrite(potmotFL, 200);
    analogWrite(potmotBR, 200);
    analogWrite(potmotBL, 200);
    delay(40); 
  }

  digitalWrite(motFR1, LOW); digitalWrite(motFR2, LOW);
  digitalWrite(motFL1, LOW); digitalWrite(motFL2, LOW);
  digitalWrite(motBR1, LOW); digitalWrite(motBR2, LOW);
  digitalWrite(motBL1, LOW); digitalWrite(motBL2, LOW);

  analogWrite(potmotFR, 0);
  analogWrite(potmotFL, 0);
  analogWrite(potmotBR, 0);
  analogWrite(potmotBL, 0);

  lastDirection = 0; 
}

// Funciones de Movimientos con ruedas normales
void moverAdelante(int fr, int fl, int br, int bl) {
  digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);
  digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW);
  digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
  digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);

  analogWrite(potmotFR, fr);
  analogWrite(potmotFL, fl);
  analogWrite(potmotBR, br);
  analogWrite(potmotBL, bl);
}

void moverAtras(int fr, int fl, int br, int bl) {
  digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);
  digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH);
  digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
  digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);

  analogWrite(potmotFR, fr);
  analogWrite(potmotFL, fl);
  analogWrite(potmotBR, br);
  analogWrite(potmotBL, bl);
}

// Funciones de Movimientos con ruedas mecanum
void swipeLeft(int velocidad) {
  actualizarYaw();
  float error = targetYaw - currentYaw;
  int ajuste = KpSwipe * error;

  int speedFR = constrain(velocidad - ajuste, 0, 255);
  int speedFL = constrain(velocidad + ajuste, 0, 255);
  int speedBR = constrain(velocidad - ajuste, 0, 255);
  int speedBL = constrain(velocidad + ajuste, 0, 255);

  // Movimiento lateral izquierda
  digitalWrite(motFR1, HIGH); digitalWrite(motFR2, LOW);
  digitalWrite(motFL1, LOW);  digitalWrite(motFL2, HIGH);
  digitalWrite(motBR1, LOW);  digitalWrite(motBR2, HIGH);
  digitalWrite(motBL1, HIGH); digitalWrite(motBL2, LOW);

  analogWrite(potmotFR, speedFR);
  analogWrite(potmotFL, speedFL);
  analogWrite(potmotBR, speedBR);
  analogWrite(potmotBL, speedBL);
}

void swipeRight(int velocidad) {
  actualizarYaw();
  float error = targetYaw - currentYaw;
  int ajuste = KpSwipe * error;

  int speedFR = constrain(velocidad + ajuste, 0, 255);
  int speedFL = constrain(velocidad - ajuste, 0, 255);
  int speedBR = constrain(velocidad + ajuste, 0, 255);
  int speedBL = constrain(velocidad - ajuste, 0, 255);

  // Movimiento lateral derecha
  digitalWrite(motFR1, LOW);  digitalWrite(motFR2, HIGH);
  digitalWrite(motFL1, HIGH); digitalWrite(motFL2, LOW);
  digitalWrite(motBR1, HIGH); digitalWrite(motBR2, LOW);
  digitalWrite(motBL1, LOW);  digitalWrite(motBL2, HIGH);

  analogWrite(potmotFR, speedFR);
  analogWrite(potmotFL, speedFL);
  analogWrite(potmotBR, speedBR);
  analogWrite(potmotBL, speedBL);
}

// Funciones del MPU
void calibrarGyro() {
  long sum = 0;
  int muestras = 200;
  int16_t ax, ay, az, gx, gy, gz;
  for (int i = 0; i < muestras; i++) {
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    sum += gz;
    delay(3);
  }
  gyroZoffset = (float)sum / muestras;
}

void actualizarYaw() {
  unsigned long currentTime = millis();
  float dt = (currentTime - lastTime) / 1000.0;
  if (dt > 0.1) dt = 0.01; 
  lastTime = currentTime;

  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  float gz_f = (gz - gyroZoffset) / 131.0; 
  if (abs(gz_f) < 0.8) gz_f = 0; 

  currentYaw += gz_f * dt;
}

void establecerCeroYaw() {
  actualizarYaw();
  currentYaw = 0;
  targetYaw = 0;
}

// Funcion detectar colores
String detectarColor() {
  uint16_t r, g, b, c;
  tcs.getRawData(&r, &g, &b, &c);
  if (c == 0) {
    return "UNKNOWN";
  }

  float R = (float)r / c;
  float G = (float)g / c;
  float B = (float)b / c;

  if (R > 0.45 && R > G * 1.3 && R > B * 1.3) {
    return "RED";
  }
  if (G > 0.40 && G > R * 1.2 && G > B * 1.2) {
    return "GREEN";
  }
  return "UNKNOWN";
}

void enviarSensores() {
  actualizarYaw();
  String color = detectarColor();
  // Por ahora los sensores de distancia están en 0

  Serial.print("SENSOR|");

  Serial.print(0);           // front
  Serial.print("|");
  Serial.print(0);           // right
  Serial.print("|");
  Serial.print(0);           // left
  Serial.print("|");
  Serial.print(0);           // back
  Serial.print("|");
  Serial.print(0);           // down
  Serial.print("|");
  Serial.print(color);       // color
  Serial.print("|");
  Serial.print(currentYaw);  // yaw
  Serial.print("|");
  Serial.println(0);         // pitch
}

// Funciones del Intake
void intakeOn(int direccion){
  if(direccion == 1){
    digitalWrite(intakePin1, HIGH);
    digitalWrite(intakePin2, LOW);
  }
  else if(direccion == -1){
    digitalWrite(intakePin1, LOW);
    digitalWrite(intakePin2, HIGH);
  }else{
    digitalWrite(intakePin1, HIGH);
    digitalWrite(intakePin2, HIGH);
  }
}

void intakeOff(){
  digitalWrite(intakePin1, HIGH);
  digitalWrite(intakePin2, HIGH);
}