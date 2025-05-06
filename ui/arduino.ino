/*
 * Selector de Juegos para Arduino Uno
 * Recibe comandos desde la interfaz Tkinter y carga el juego correspondiente
 */

// Variables globales
int currentGame = 0;  // 0: ningún juego, 1-3: juegos
String inputBuffer = "";
boolean newCommand = false;

// Configuración de pines para cada juego (ejemplo)
// Juego 1: LEDs secuenciales
const int game1Pins[] = {2, 3, 4, 5};  // Pines LED para juego 1

// Juego 2: Botón y LED
const int game2ButtonPin = 6;  // Pin para botón del juego 2
const int game2LedPin = 7;     // Pin LED para juego 2

// Juego 3: Sensor y LED
const int game3SensorPin = A0;  // Pin para sensor del juego 3
const int game3LedPin = 8;      // Pin LED para juego 3

void setup() {
  // Iniciar comunicación serial
  Serial.begin(9600);
  Serial.println("Arduino listo para recibir comandos");

  // Configurar pines para todos los juegos posibles
  for (int i = 0; i < 4; i++) {
    pinMode(game1Pins[i], OUTPUT);
    digitalWrite(game1Pins[i], LOW);
  }

  pinMode(game2ButtonPin, INPUT_PULLUP);
  pinMode(game2LedPin, OUTPUT);

  pinMode(game3LedPin, OUTPUT);

  // Indicar que está listo
  for (int i = 0; i < 3; i++) {
    digitalWrite(game1Pins[0], HIGH);
    delay(100);
    digitalWrite(game1Pins[0], LOW);
    delay(100);
  }
}

void loop() {
  // Revisar si hay comandos nuevos
  checkSerialCommand();

  // Ejecutar el juego seleccionado
  switch (currentGame) {
    case 0:
      // Ningún juego seleccionado - modo standby
      standbyMode();
      break;
    case 1:
      // Juego 1: LEDs secuenciales
      runGame1();
      break;
    case 2:
      // Juego 2: Interacción con botón
      runGame2();
      break;
    case 3:
      // Juego 3: Juego con sensor
      runGame3();
      break;
  }
}

// Función para verificar comandos seriales
void checkSerialCommand() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    // Procesar solo cuando se recibe un salto de línea
    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}

// Función para procesar comandos
void processCommand(String command) {
  command.trim();  // Eliminar espacios en blanco

  if (command.startsWith("G")) {
    // Comando de selección de juego (G1, G2, G3)
    int gameNumber = command.substring(1).toInt();

    if (gameNumber >= 1 && gameNumber <= 3) {
      // Cambiar al juego seleccionado
      currentGame = gameNumber;
      Serial.print("Juego ");
      Serial.print(currentGame);
      Serial.println(" activado");

      // Reiniciar todos los pines antes de cambiar de juego
      resetAllPins();
    } else {
      Serial.println("Error: Número de juego no válido");
    }
  } else {
    Serial.println("Comando no reconocido");
  }
}

// Función para reiniciar todos los pines
void resetAllPins() {
  // Apagar todos los LEDs
  for (int i = 0; i < 4; i++) {
    digitalWrite(game1Pins[i], LOW);
  }
  digitalWrite(game2LedPin, LOW);
  digitalWrite(game3LedPin, LOW);
}

// Modo standby - ningún juego seleccionado
void standbyMode() {
  // Parpadeo lento en el primer LED para indicar standby
  digitalWrite(game1Pins[0], HIGH);
  delay(500);
  digitalWrite(game1Pins[0], LOW);
  delay(500);
}

// Juego 1: LEDs secuenciales
void runGame1() {
  // Secuencia de luces simple
  for (int i = 0; i < 4; i++) {
    digitalWrite(game1Pins[i], HIGH);
    delay(100);
    digitalWrite(game1Pins[i], LOW);
  }

  // Secuencia inversa
  for (int i = 3; i >= 0; i--) {
    digitalWrite(game1Pins[i], HIGH);
    delay(100);
    digitalWrite(game1Pins[i], LOW);
  }

  delay(200);  // Pequeña pausa entre ciclos
}

// Juego 2: Interacción con botón
void runGame2() {
  // Si el botón está presionado, enciende el LED
  if (digitalRead(game2ButtonPin) == LOW) {  // Activo en bajo por el PULLUP
    digitalWrite(game2LedPin, HIGH);

    // También enviar datos al PC
    if (!digitalRead(game2ButtonPin)) {  // Si el botón sigue presionado
      Serial.println("Botón presionado en Juego 2");
      delay(200);  // Evitar múltiples mensajes
    }
  } else {
    digitalWrite(game2LedPin, LOW);
  }
  delay(50);  // Pequeño retardo para estabilidad
}

// Juego 3: Juego con sensor
void runGame3() {
  // Leer valor del sensor (ejemplo con fotorresistor)
  int sensorValue = analogRead(game3SensorPin);

  // Mapear el valor a un rango visible (parpadeo más rápido o más lento)
  int delayTime = map(sensorValue, 0, 1023, 50, 500);

  // Parpadear el LED según el valor del sensor
  digitalWrite(game3LedPin, HIGH);
  delay(delayTime);
  digitalWrite(game3LedPin, LOW);
  delay(delayTime);

  // Enviar datos cada segundo aproximadamente
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 1000) {
    Serial.print("Sensor Juego 3: ");
    Serial.println(sensorValue);
    lastSendTime = millis();
  }
}
