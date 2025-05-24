/**
 * Simon Game - 6 botones usando columnas 0 y 2 del keypad
 * Botones utilizados: 1,4,7 (columna 0) y 3,6,9 (columna 2)
 *
 * Conexiones requeridas:
 * - ROW0 del keypad → Pin 7 Arduino (botones 1, 3)
 * - ROW1 del keypad → Pin 6 Arduino (botones 4, 6)
 * - ROW2 del keypad → Pin 5 Arduino (botones 7, 9)
 * - ROW3 → SIN CONECTAR
 * - COL0 del keypad → Pin 4 Arduino (botones 1,4,7)
 * - COL1 → SIN CONECTAR
 * - COL2 del keypad → Pin 3 Arduino (botones 3,6,9)
 * - COL3 → SIN CONECTAR
 */

// Keypad optimizado - 3 filas × 2 columnas
const byte ROW_COUNT = 3;  // 3 filas superiores
const byte COL_COUNT = 2;  // Solo 2 columnas (0 y 2)

byte rowPins[ROW_COUNT] = {7, 6, 5};    // ROW0, ROW1, ROW2 del keypad
byte colPins[COL_COUNT] = {4, 3};       // COL0, COL2 del keypad

// Layout optimizado - solo botones útiles
char keys[ROW_COUNT][COL_COUNT] = {
  {'1', '3'},  // Fila 0: 1=COL0, 3=COL2
  {'4', '6'},  // Fila 1: 4=COL0, 6=COL2
  {'7', '9'}   // Fila 2: 7=COL0, 9=COL2
};

// Mapeo de teclas a números de LED (1-6)
// Botón del keypad → LED número
int keyToLed(char key) {
  switch(key) {
    case '1': return 1;  // LED 1
    case '4': return 2;  // LED 2
    case '7': return 3;  // LED 3
    case '3': return 4;  // LED 4
    case '6': return 5;  // LED 5
    case '9': return 6;  // LED 6
    default: return 0;   // No válido
  }
}

// LED pins - 6 LEDs para el juego Simon
const byte LED_1 = 8;   // Botón 1
const byte LED_2 = 9;   // Botón 4
const byte LED_3 = 10;  // Botón 7
const byte LED_4 = 11;  // Botón 3
const byte LED_5 = 12;  // Botón 6
const byte LED_6 = 13;  // Botón 9

// Buzzer opcional
const byte BUZZER_PIN = A2;

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

// LED array para fácil acceso
byte ledPins[] = {LED_1, LED_2, LED_3, LED_4, LED_5, LED_6};

// Game state
enum GameState {WAITING_TO_START, SHOWING_SEQUENCE, PLAYER_INPUT, GAME_OVER, GAME_WON};
GameState gameState = WAITING_TO_START;

// Tonos para cada LED
int tones[] = {262, 294, 330, 349, 392, 440}; // C4, D4, E4, F4, G4, A4

void setup() {
  // Configurar LEDs
  for (int i = 0; i < 6; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  // Configurar buzzer
  pinMode(BUZZER_PIN, OUTPUT);

  // Configurar keypad - 3 FILAS × 2 COLUMNAS
  for (byte row = 0; row < ROW_COUNT; row++) {
    pinMode(rowPins[row], INPUT_PULLUP);
  }

  for (byte col = 0; col < COL_COUNT; col++) {
    pinMode(colPins[col], OUTPUT);
    digitalWrite(colPins[col], HIGH);
  }

  Serial.begin(9600);
  Serial.println("=== SIMON GAME - 6 BOTONES ===");
  Serial.println("Configuración optimizada:");
  Serial.println("ROW0→Pin7, ROW1→Pin6, ROW2→Pin5");
  Serial.println("COL0→Pin4, COL2→Pin3");
  Serial.println();
  Serial.println("Layout del keypad:");
  Serial.println("  COL0  COL2");
  Serial.println("   [1]   [3]  ← ROW0");
  Serial.println("   [4]   [6]  ← ROW1");
  Serial.println("   [7]   [9]  ← ROW2");
  Serial.println();
  Serial.println("Mapeo a LEDs:");
  Serial.println("1→LED1, 4→LED2, 7→LED3");
  Serial.println("3→LED4, 6→LED5, 9→LED6");

  randomSeed(analogRead(A1));
  showStartupAnimation();
  resetGame();
}

void loop() {
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
}

char getKey() {
  char key = 0;

  // Escanear las 3 filas × 2 columnas
  for (byte col = 0; col < COL_COUNT; col++) {
    digitalWrite(colPins[col], LOW);

    // Revisar las 3 filas
    for (byte row = 0; row < ROW_COUNT; row++) {
      if (digitalRead(rowPins[row]) == LOW) {
        delay(DEBOUNCE_DELAY);

        if (digitalRead(rowPins[row]) == LOW) {
          key = keys[row][col];

          // Debug: mostrar qué tecla se presionó
          Serial.print("Tecla: ");
          Serial.print(key);
          Serial.print(" → LED");
          Serial.println(keyToLed(key));

          // Esperar release
          while (digitalRead(rowPins[row]) == LOW) {
            ; // Esperar
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

  // Acepta cualquier tecla válida para empezar
  if (keyToLed(key) > 0) {
    Serial.println("\n¡🎮 JUEGO INICIANDO! 🎮");
    delay(500);
    gameState = SHOWING_SEQUENCE;
  }
}

void showSequence() {
  Serial.print("\n🎯 NIVEL ");
  Serial.print(playerLevel);
  Serial.print(" - Secuencia: ");

  delay(START_DELAY);

  // Velocidad aumenta con el nivel
  int delayTime = max(MIN_DELAY, INITIAL_DELAY - (playerLevel * 15));

  // Mostrar secuencia
  for (int i = 0; i < playerLevel; i++) {
    int ledIndex = gameSequence[i] - 1; // 1-6 → 0-5

    // Validar índice por seguridad
    if (ledIndex >= 0 && ledIndex < 6) {
      digitalWrite(ledPins[ledIndex], HIGH);

      // Sonido opcional
      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[ledIndex], delayTime);
      }

      Serial.print("LED");
      Serial.print(gameSequence[i]);
      Serial.print(" ");

      delay(delayTime);
      digitalWrite(ledPins[ledIndex], LOW);
      delay(PAUSE_BETWEEN);
    }
  }

  Serial.println();
  Serial.println("🎯 Tu turno! Presiona los botones en el mismo orden:");
  Serial.println("   Usa: 1,4,7 (izquierda) y 3,6,9 (derecha)");
  inputCount = 0;
}

void readPlayerInput() {
  char key = getKey();

  if (key != 0) {
    int ledNumber = keyToLed(key);

    // Solo procesar teclas válidas
    if (ledNumber > 0) {
      int ledIndex = ledNumber - 1;

      // Feedback visual inmediato
      digitalWrite(ledPins[ledIndex], HIGH);

      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[ledIndex], 200);
      }

      delay(200);
      digitalWrite(ledPins[ledIndex], LOW);

      // Verificar si es correcto
      if (ledNumber == gameSequence[inputCount]) {
        inputCount++;
        Serial.print("✅ Correcto! ");

        // ¿Completó la secuencia?
        if (inputCount >= playerLevel) {
          Serial.println("\n🎉 ¡NIVEL COMPLETADO! 🎉");
          delay(500);

          if (playerLevel >= MAX_LEVEL) {
            gameState = GAME_WON;
          } else {
            playerLevel++;
            gameState = SHOWING_SEQUENCE;
          }
        } else {
          Serial.print("Siguiente... ");
        }
      } else {
        // Error - game over
        Serial.print("\n❌ ¡ERROR! Esperaba LED");
        Serial.print(gameSequence[inputCount]);
        Serial.print(", presionaste botón ");
        Serial.print(key);
        Serial.print(" (LED");
        Serial.print(ledNumber);
        Serial.println(")");
        gameState = GAME_OVER;
      }
    } else {
      // Tecla no válida
      Serial.print("⚠️ Botón no válido: ");
      Serial.print(key);
      Serial.println(" (Usa solo: 1,4,7,3,6,9)");
    }
  }
}

void resetGame() {
  playerLevel = 1;
  inputCount = 0;

  // Generar nueva secuencia aleatoria
  for (int i = 0; i < MAX_LEVEL; i++) {
    gameSequence[i] = random(1, 7); // 1-6 (LEDs)
  }

  gameState = WAITING_TO_START;
  Serial.println("\n" + String("=").substring(0,40));
  Serial.println("🔄 JUEGO REINICIADO");
  Serial.println("Presiona cualquier botón para empezar");
  Serial.println("Botones disponibles: 1, 4, 7, 3, 6, 9");
  Serial.println(String("=").substring(0,40));
}

void showStartupAnimation() {
  Serial.println("\n🚀 Iniciando Simon Game...");
  Serial.println("🔍 Probando LEDs...");

  // Encender LEDs en secuencia con nombres
  String ledNames[] = {"1", "4", "7", "3", "6", "9"};
  for (int i = 0; i < 6; i++) {
    digitalWrite(ledPins[i], HIGH);
    Serial.print("🔴 LED");
    Serial.print(i+1);
    Serial.print(" (botón ");
    Serial.print(ledNames[i]);
    Serial.println(") ON");
    delay(300);
  }

  delay(500);

  // Apagar en secuencia
  for (int i = 0; i < 6; i++) {
    digitalWrite(ledPins[i], LOW);
    Serial.print("⚫ LED");
    Serial.print(i+1);
    Serial.println(" OFF");
    delay(200);
  }

  // Flash general 3 veces
  Serial.println("✨ Test de sincronización...");
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

  Serial.println("✅ ¡Sistema listo!");
}

void gameOverSequence() {
  Serial.println("\n💀 ¡GAME OVER! 💀");
  Serial.print("📊 Nivel alcanzado: ");
  Serial.println(playerLevel);

  if (playerLevel >= 10) {
    Serial.println("🏆 ¡Excelente puntuación!");
  } else if (playerLevel >= 5) {
    Serial.println("👍 ¡Buen intento!");
  } else {
    Serial.println("💪 ¡Sigue practicando!");
  }

  // Secuencia de error dramática
  for (int i = 0; i < 4; i++) {
    // Flash rápido
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 100, 200); // Tono grave de error
    }

    delay(200);

    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(200);
  }

  delay(1000);
}

void victorySequence() {
  Serial.println("\n🎉🎉🎉 ¡FELICITACIONES! 🎉🎉🎉");
  Serial.println("👑 ¡COMPLETASTE TODOS LOS 20 NIVELES! 👑");
  Serial.println("🏆 ¡ERES UN MAESTRO DE SIMON! 🏆");

  // Animación de victoria espectacular
  // Fase 1: Ondas de luz
  for (int wave = 0; wave < 3; wave++) {
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], HIGH);

      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[i] + 200, 120); // Tonos más agudos
      }

      delay(120);
      digitalWrite(ledPins[i], LOW);
      delay(80);
    }
  }

  // Fase 2: Flash sincronizado con música
  for (int i = 0; i < 6; i++) {
    // Todos encendidos
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 440 + (i * 50), 250); // Escalas ascendentes
    }

    delay(250);

    // Todos apagados
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(150);
  }

  // Fase 3: Final explosivo
  for (int i = 0; i < 5; i++) {
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 880, 100); // Nota aguda de victoria
    }

    delay(100);

    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(100);
  }

  delay(1000);
}

/*
=== DIAGRAMA DE CONEXIONES OPTIMIZADO ===

Keypad 4x4:    Arduino:
ROW0    -----> Pin 7    (Fila 1: botones 1, 3)
ROW1    -----> Pin 6    (Fila 2: botones 4, 6)
ROW2    -----> Pin 5    (Fila 3: botones 7, 9)
ROW3    -----> SIN CONECTAR

COL0    -----> Pin 4    (Columna izquierda: 1,4,7)
COL1    -----> SIN CONECTAR
COL2    -----> Pin 3    (Columna derecha: 3,6,9)
COL3    -----> SIN CONECTAR

LEDs:
LED1 (botón 1) -----> Pin 8  (+ resistor 220Ω)
LED2 (botón 4) -----> Pin 9  (+ resistor 220Ω)
LED3 (botón 7) -----> Pin 10 (+ resistor 220Ω)
LED4 (botón 3) -----> Pin 11 (+ resistor 220Ω)
LED5 (botón 6) -----> Pin 12 (+ resistor 220Ω)
LED6 (botón 9) -----> Pin 13 (+ resistor 220Ω)

Buzzer: -----> Pin A2 (opcional)

=== LAYOUT VISUAL DEL KEYPAD ===

Keypad completo 4x4:
[1] [2] [3] [A]
[4] [5] [6] [B]
[7] [8] [9] [C]
[*] [0] [#] [D]

Botones CONECTADOS (marcados con ●):
[●] [ ] [●] [ ]  ← ROW0 conectada
[●] [ ] [●] [ ]  ← ROW1 conectada
[●] [ ] [●] [ ]  ← ROW2 conectada
[ ] [ ] [ ] [ ]  ← ROW3 SIN conectar
 ↑       ↑
COL0    COL2
conectadas

=== VENTAJAS DE ESTA CONFIGURACIÓN ===
✅ Solo 5 cables del keypad (3 filas + 2 columnas)
✅ 6 botones perfectamente distribuidos
✅ Patrón simétrico fácil de memorizar
✅ Menos conexiones = menos errores
✅ Layout intuitivo (izquierda: 1,4,7 / derecha: 3,6,9)
*/
