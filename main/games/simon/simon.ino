/**
 * Simon Game with 4x4 Keypad and 6 LEDs
 * (No Keypad library required)
 *
 * The game will show a sequence of LEDs lighting up.
 * Player must repeat that sequence by pressing the corresponding
 * number keys (1-6) on the 4x4 keypad.
 */

// Keypad pins without library
const byte ROW_COUNT = 4;
const byte COL_COUNT = 4;

byte rowPins[ROW_COUNT] = {9, 8, 7, 6}; // Connect keypad ROW0, ROW1, ROW2, ROW3 to these pins
byte colPins[COL_COUNT] = {5, 4, 3, 2}; // Connect keypad COL0, COL1, COL2, COL3 to these pins

// Keypad layout
char keys[ROW_COUNT][COL_COUNT] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

// LED pins - connect LEDs to these Arduino pins with appropriate resistors
const byte LED_1 = 10;
const byte LED_2 = 11;
const byte LED_3 = 12;
const byte LED_4 = 13;
const byte LED_5 = A0;
const byte LED_6 = A1;

// Optional buzzer pin
const byte BUZZER_PIN = A2;

// Game constants
const int MAX_LEVEL = 20;      // Maximum game level
const int INITIAL_DELAY = 500; // Initial time each LED is lit (ms)
const int MIN_DELAY = 200;     // Minimum time each LED is lit at higher levels (ms)
const int PAUSE_BETWEEN = 200; // Pause between LED activations (ms)
const int START_DELAY = 1500;  // Delay before starting a sequence (ms)
const int DEBOUNCE_DELAY = 50; // Debounce delay for keypad (ms)

// Game variables
int gameSequence[MAX_LEVEL];   // Stores the generated sequence
int playerLevel = 1;           // Current level (length of sequence)
int inputCount = 0;            // Count of player inputs in current sequence

// Button to LED mapping (button -> LED pin)
byte ledPins[] = {LED_1, LED_2, LED_3, LED_4, LED_5, LED_6};

// Game state
enum GameState {WAITING_TO_START, SHOWING_SEQUENCE, PLAYER_INPUT, GAME_OVER, GAME_WON};
GameState gameState = WAITING_TO_START;

// Tone frequencies for each button (optional, if buzzer is connected)
int tones[] = {262, 294, 330, 349, 392, 440}; // C4, D4, E4, F4, G4, A4

// Variables for manual keypad reading
char lastKey = 0;
unsigned long lastKeyTime = 0;

void setup() {
  // Initialize LED pins as outputs
  for (int i = 0; i < 6; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  // Initialize buzzer pin (if used)
  pinMode(BUZZER_PIN, OUTPUT);

  // Setup keypad pins
  for (byte row = 0; row < ROW_COUNT; row++) {
    pinMode(rowPins[row], INPUT_PULLUP); // Set row pins as INPUT_PULLUP
  }

  for (byte col = 0; col < COL_COUNT; col++) {
    pinMode(colPins[col], OUTPUT);     // Set column pins as OUTPUT
    digitalWrite(colPins[col], HIGH);  // Set column pins HIGH initially
  }

  // Initialize serial monitor for debugging
  Serial.begin(9600);
  Serial.println("Simon Game Started");

  // Seed random number generator with an unconnected analog pin
  randomSeed(analogRead(A5));

  // Signal that the game is ready with a light sequence
  showStartupAnimation();

  // Start game
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

  // Scan the keypad
  for (byte col = 0; col < COL_COUNT; col++) {
    digitalWrite(colPins[col], LOW);  // Set current column LOW

    // Check each row
    for (byte row = 0; row < ROW_COUNT; row++) {
      if (digitalRead(rowPins[row]) == LOW) {
        delay(DEBOUNCE_DELAY);  // Debounce

        // Check if still pressed
        if (digitalRead(rowPins[row]) == LOW) {
          key = keys[row][col];

          // Wait for key release to avoid multiple reads
          while (digitalRead(rowPins[row]) == LOW) {
            ; // Wait for release
          }
        }
      }
    }

    digitalWrite(colPins[col], HIGH);  // Set column back to HIGH
  }

  return key;
}

void waitForStart() {
  char key = getKey();

  if (key != 0) {
    Serial.println("Game starting!");
    delay(500);
    gameState = SHOWING_SEQUENCE;
  }
}

void showSequence() {
  Serial.print("Level ");
  Serial.print(playerLevel);
  Serial.println(" sequence:");

  // Wait before starting the sequence
  delay(START_DELAY);

  // Calculate LED display time based on level (gets faster as level increases)
  int delayTime = max(MIN_DELAY, INITIAL_DELAY - (playerLevel * 20));

  // Display the sequence
  for (int i = 0; i < playerLevel; i++) {
    // Turn on the LED for this step in the sequence
    int ledIndex = gameSequence[i] - 1; // Convert 1-6 to 0-5 for array index

    digitalWrite(ledPins[ledIndex], HIGH);

    // Play tone if buzzer is connected
    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, tones[ledIndex], delayTime);
    }

    Serial.print(gameSequence[i]);
    Serial.print(" ");

    delay(delayTime);

    // Turn off the LED
    digitalWrite(ledPins[ledIndex], LOW);

    // Pause between LED activations
    delay(PAUSE_BETWEEN);
  }

  Serial.println();
  inputCount = 0; // Reset input counter for player's turn
}

void readPlayerInput() {
  char key = getKey();

  if (key != 0) {
    // Only process keys 1-6
    if (key >= '1' && key <= '6') {
      int number = key - '0'; // Convert char to int (ASCII '1' -> 1)
      int ledIndex = number - 1; // Convert 1-6 to 0-5 for array index

      // Light up the corresponding LED
      digitalWrite(ledPins[ledIndex], HIGH);

      // Play tone if buzzer is connected
      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[ledIndex], 200);
      }

      delay(200);
      digitalWrite(ledPins[ledIndex], LOW);

      // Check if this input matches the expected sequence
      if (number == gameSequence[inputCount]) {
        // Correct input
        inputCount++;

        // Check if the player completed the current sequence
        if (inputCount >= playerLevel) {
          // Player completed this level
          delay(500);

          if (playerLevel >= MAX_LEVEL) {
            // Player won the game by completing all levels
            gameState = GAME_WON;
          } else {
            // Move to the next level
            playerLevel++;
            gameState = SHOWING_SEQUENCE;
          }
        }
      } else {
        // Incorrect input - game over
        gameState = GAME_OVER;
      }
    }
  }
}

void resetGame() {
  playerLevel = 1;
  inputCount = 0;

  // Generate a new random sequence
  for (int i = 0; i < MAX_LEVEL; i++) {
    gameSequence[i] = random(1, 7); // Random number between 1-6
  }

  gameState = WAITING_TO_START;
  Serial.println("Game reset. Press any key to start.");
}

void showStartupAnimation() {
  // Light each LED in sequence
  for (int i = 0; i < 6; i++) {
    digitalWrite(ledPins[i], HIGH);
    delay(100);
  }

  // And turn them off in sequence
  for (int i = 0; i < 6; i++) {
    digitalWrite(ledPins[i], LOW);
    delay(100);
  }

  // Flash all LEDs twice
  for (int j = 0; j < 2; j++) {
    // All on
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], HIGH);
    }
    delay(250);

    // All off
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    delay(250);
  }
}

void gameOverSequence() {
  Serial.println("Game Over!");

  // Flash all LEDs together 3 times
  for (int i = 0; i < 3; i++) {
    // All on
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    // Play error tone if buzzer is connected
    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 150, 300);
    }

    delay(300);

    // All off
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(300);
  }

  // Brief pause before resetting
  delay(1000);
}

void victorySequence() {
  Serial.println("Congratulations! You won!");

  // Victory animation: light LEDs in various patterns
  // Pattern 1: Sweep right to left and back
  for (int j = 0; j < 2; j++) {
    for (int i = 0; i < 6; i++) {
      digitalWrite(ledPins[i], HIGH);

      // Play ascending tone if buzzer is connected
      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[i], 150);
      }

      delay(150);
      digitalWrite(ledPins[i], LOW);
    }

    for (int i = 4; i >= 0; i--) {
      digitalWrite(ledPins[i], HIGH);

      // Play descending tone if buzzer is connected
      if (BUZZER_PIN != 0) {
        tone(BUZZER_PIN, tones[i], 150);
      }

      delay(150);
      digitalWrite(ledPins[i], LOW);
    }
  }

  // Pattern 2: All LEDs flashing
  for (int i = 0; i < 3; i++) {
    // All on
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], HIGH);
    }

    // Victory chord if buzzer is connected
    if (BUZZER_PIN != 0) {
      tone(BUZZER_PIN, 440, 300); // A4 note
    }

    delay(300);

    // All off
    for (int j = 0; j < 6; j++) {
      digitalWrite(ledPins[j], LOW);
    }

    delay(300);
  }

  // Brief pause before resetting
  delay(1000);
}
