#include <Wire.h>
#include <VL53L0X.h>

// true = 7 sensores
// false = 6 sensores
const bool USE_7_SENSORS = true;

// Pines XSHUT
const uint8_t xshutPins[7] = {
  34, 36, 38, 40, 42, 44, 46
};

// Direcciones I2C
const uint8_t sensorAddresses[7] = {
  0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36
};

// Número de sensores según la variable
const uint8_t NUM_SENSORS = USE_7_SENSORS ? 7 : 6;

// Creación de sensores
VL53L0X sensors[7];

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Configurar todos los pines XSHUT
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(xshutPins[i], OUTPUT);
    digitalWrite(xshutPins[i], LOW);
  }

  delay(10);

  // Inicializar sensores uno por uno
  for (int i = 0; i < NUM_SENSORS; i++) {
    digitalWrite(xshutPins[i], HIGH);
    delay(10);

    if (!sensors[i].init()) {
      Serial.print("Error al detectar el Sensor ");
      Serial.println(i + 1);
      while (1);
    }

    sensors[i].setAddress(sensorAddresses[i]);
    sensors[i].startContinuous();
  }

  Serial.print("¡");
  Serial.print(NUM_SENSORS);
  Serial.println(" sensores VL53L0X inicializados correctamente!");
}

void loop() {

  // Leer sensores
  for (int i = 0; i < NUM_SENSORS; i++) {

    int distancia = sensors[i].readRangeContinuousMillimeters();

    Serial.print("S");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(distancia);

    if (sensors[i].timeoutOccurred()) {
      Serial.print(" (TIMEOUT)");
    }

    Serial.print(" mm  |  ");
  }

  Serial.println();
  delay(100);
}