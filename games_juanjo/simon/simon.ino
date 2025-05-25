// CÓDIGO ARDUINO - Subir al Arduino
// Simon Game con comunicación serial - 6 botones (1,4,7,3,6,9)

// Keypad optimizado - 3 filas × 2 columnas
const byte ROW_COUNT = 3;
const byte COL_COUNT = 2;

byte rowPins[ROW_COUNT] = {7, 6, 5};    // ROW0, ROW1, ROW2
byte colPins[COL_COUNT] = {4, 3};       // COL0, COL2

// Layout optimizado
char keys[ROW_COUNT][COL_COUNT] = {
  {'1', '3'},  // Fila 0
  {'4', '6'},  // Fila 1
  {'7', '9'}   // Fila 2
};

// Mapeo de teclas a números de LED
int keyToLed(char key) {
  switch(key) {
    case '1': return 1;
    case '4': return 2;
    case '7': return 3;
    case '3': return 4;
    case '6': return 5;
    case '9': return 6;
    default: return 0;
  }
}

// LED pins
const byte LED_1 = 8;
const byte LED_4 = 9;
const byte LED_7 = 10;
const byte LED_3 = 11;
const byte LED_6 = 12;
const byte LED_9 = 13;
const byte BUZZER_PIN = 2;

// Game constants
const int MAX_LEVEL = 20;
const int INITIAL_DELAY = 500;
const int MIN_DELAY = 200;
const int PAUSE_BETWEEN = 200;
const int START_DELAY = 1500;
const int DEBOUNCE_DELAY = 50;

// Game variables
int gameSequence[MAX_LEVEL];
int playerLevel = 1;
int inputCount = 0;

byte ledPins[] = {LED_1, LED_4, LED_7, LED_3, LED_6, LED_9};

enum GameState {WAITING_TO_START, SHOWING_SEQUENCE, PLAYER_INPUT, GAME_OVER, GAME_WON};
GameState gameState = WAITING_TO_START;

int tones[] = {262, 294, 330, 349, 392, 440};

// Variables para comunicación serial
unsigned long lastSerialSend = 0;
const unsigned long SERIAL_INTERVAL = 100;

void setup() {
  // Configurar LEDs
  for (int i = 0; i < 6; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  pinMode(BUZZER_PIN, OUTPUT);

  // Configurar keypad
  for (byte row = 0; row < ROW_COUNT; row++) {
    pinMode(rowPins[row], INPUT_PULLUP);
  }

  for (byte col = 0; col < COL_COUNT; col++) {
    pinMode(colPins[col], OUTPUT);
    digitalWrite(colPins[col], HIGH);
  }

  Serial.begin(9600);
  Serial.println("SIMON_READY");

  randomSeed(analogRead(A1));
  showStartupAnimation();
  resetGame();
}

void loop() {
  // Manejar comandos serial
  handleSerialInput();

  switch (gameState) {
    case WAITING_TO_START:
      waitForStart();
      break;

    case SHOWING_SEQUENCE:
      showSequence();
      gameState = PLAYER_INPUT;
      break;

    case PLAYER_INPUT:
      readPlayerInput();
      break;

    case GAME_OVER:
      gameOverSequence();
      resetGame();
      break;

    case GAME_WON:
      victorySequence();
      resetGame();
      break;
  }

  // Enviar actualizaciones periódicas
  unsigned long currentTime = millis();
  if (currentTime - lastSerialSend >= SERIAL_INTERVAL) {
    lastSerialSend = currentTime;
    sendGameState();
  }
}

void handleSerialInput() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "GET_STATE") {
      sendGameState();
    } else if (command == "RESTART") {
      resetGame();
      Serial.println("GAME_RESTART");
    } else if (command == "PAUSE") {
      if (gameState == PLAYER_INPUT || gameState == SHOWING_SEQUENCE) {
        gameState = WAITING_TO_START;
        Serial.println("GAME_PAUSE");
      }
    }
  }
}

void sendGameState() {
  Serial.print("STATE:");
  Serial.print(playerLevel); Serial.print(",");
  Serial.print(inputCount); Serial.print(",");
  Serial.print(gameState); Serial.print(",");

  // Enviar secuencia actual
  Serial.print("SEQ:");
  for (int i = 0; i < playerLevel && i < MAX_LEVEL; i++) {
    Serial.print(gameSequence[i]);
    if (i < playerLevel - 1) Serial.print("-");
  }
  Serial.println();
}

char getKey() {
  char key = 0;

  for (byte col = 0; col < COL_COUNT; col++) {
    digitalWrite(colPins[col], LOW);

    for (byte row = 0; row < ROW_COUNT; row++) {
      if (digitalRead(rowPins[row]) == LOW) {
        delay(DEBOUNCE_DELAY);

        if (digitalRead(rowPins[row]) == LOW) {
          key = keys[row][col];

          // Enviar tecla presionada por serial
          Serial.print("KEY_PRESS:");
          Serial.print(key);
          Serial.print(",");
          Serial.println(keyToLed(key));

          while (digitalRead(rowPins[row]) == LOW) {
            delay(10);
          }
        }
      }
    }

    digitalWrite(colPins[col], HIGH);
  }

  return key;
}

void waitForStart() {
  char key = getKey();

  if (keyToLed(key) > 0) {
    Serial.println("GAME_START");
    delay(500);
    gameState = SHOWING_SEQUENCE;
  }
}

void showSequence() {
  Serial.print("SEQUENCE_START:");
  Serial.println(playerLevel);

  delay(START_DELAY);

  int delayTime = max(MIN_DELAY, INITIAL_DELAY - (playerLevel * 15));

  for (int i = 0; i < playerLevel; i++) {
    int ledIndex = gameSequence[i] - 1;

    if (ledIndex >= 0 && ledIndex < 6) {
      digitalWrite(ledPins[ledIndex], HIGH);

      // Enviar LED activado
      Serial.print("LED_ON:");
      Serial.println(gameSequence[i]);

      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[ledIndex], delayTime);
      }

      delay(delayTime);
      digitalWrite(ledPins[ledIndex], LOW);

      Serial.print("LED_OFF:");
      Serial.println(gameSequence[i]);

      delay(PAUSE_BETWEEN);
    }
  }

  Serial.println("SEQUENCE_END");
  inputCount = 0;
}

void readPlayerInput() {
  char key = getKey();

  if (key != 0) {
    int ledNumber = keyToLed(key);

    if (ledNumber > 0) {
      int ledIndex = ledNumber - 1;

      // Feedback visual
      digitalWrite(ledPins[ledIndex], HIGH);

      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[ledIndex], 200);
      }

      delay(200);
      digitalWrite(ledPins[ledIndex], LOW);

      // Verificar respuesta
      if (ledNumber == gameSequence[inputCount]) {
        inputCount++;
        Serial.print("CORRECT:");
        Serial.print(inputCount);
        Serial.print("/");
        Serial.println(playerLevel);

        if (inputCount >= playerLevel) {
          Serial.println("LEVEL_COMPLETE");
          delay(500);

          if (playerLevel >= MAX_LEVEL) {
            gameState = GAME_WON;
            Serial.println("GAME_WON");
          } else {
            playerLevel++;
            gameState = SHOWING_SEQUENCE;
            Serial.print("NEXT_LEVEL:");
            Serial.println(playerLevel);
          }
        }
      } else {
        Serial.print("WRONG:");
        Serial.print(gameSequence[inputCount]);
        Serial.print(",");
        Serial.println(ledNumber);
        gameState = GAME_OVER;
        Serial.println("GAME_OVER");
      }
    }
  }
}

void resetGame() {
  playerLevel = 1;
  inputCount = 0;

  for (int i = 0; i < MAX_LEVEL; i++) {
    gameSequence[i] = random(1, 7);
  }

  gameState = WAITING_TO_START;
  Serial.println("GAME_RESET");
}

void showStartupAnimation() {
  Serial.println("STARTUP_ANIMATION");

  for (int i = 0; i < 6; i++) {
    digitalWrite(ledPins[i], HIGH);
    Serial.print("STARTUP_LED:");
    Serial.println(i + 1);
    delay(300);
    digitalWrite(ledPins[i], LOW);
    delay(200);
  }

  for (int j = 0; j < 3; j++) {
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 440, 150);
    }

    delay(200);

    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    delay(200);
  }

  Serial.println("STARTUP_COMPLETE");
}

void gameOverSequence() {
  Serial.print("GAME_OVER_LEVEL:");
  Serial.println(playerLevel);

  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 100, 200);
    }

    delay(200);

    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(200);
  }

  Serial.println("GAME_OVER_COMPLETE");
  delay(1000);
}

void victorySequence() {
  Serial.println("VICTORY_START");

  for (int wave = 0; wave < 3; wave++) {
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], HIGH);

      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[i] + 200, 120);
      }

      delay(120);
      digitalWrite(ledPins[i], LOW);
      delay(80);
    }
  }

  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 880, 100);
    }

    delay(100);

    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(100);
  }

  Serial.println("VICTORY_COMPLETE");
  delay(1000);
}

/*
PROTOCOLO SERIAL:
Arduino -> Python:
- "SIMON_READY" -> Arduino inicializado
- "STATE:level,input,gameState,SEQ:1-2-3..." -> Estado del juego
- "KEY_PRESS:key,ledNumber" -> Tecla presionada
- "LED_ON/OFF:number" -> LED encendido/apagado
- "GAME_START/OVER/WON/RESTART" -> Eventos del juego
- "CORRECT:x/y" -> Respuesta correcta
- "WRONG:expected,received" -> Respuesta incorrecta

Python -> Arduino:
- "GET_STATE" -> Solicitar estado
- "RESTART" -> Reiniciar juego
- "PAUSE" -> Pausar juego
*/
