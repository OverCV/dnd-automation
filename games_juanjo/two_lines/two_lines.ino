// CÓDIGO ARDUINO - Subir al Arduino
// Two-Lane Runner Game con comunicación serial

#include <LiquidCrystal.h>

// Define LCD pins for the LCD Keypad Shield
const int RS = 8, EN = 9, D4 = 4, D5 = 5, D6 = 6, D7 = 7;
LiquidCrystal lcd(RS, EN, D4, D5, D6, D7);

// Custom characters
byte playerChar[8] = {
  B01110,
  B01110,
  B00100,
  B01110,
  B10101,
  B00100,
  B01010,
  B10001
};

byte obstacleChar[8] = {
  B00000,
  B01110,
  B11111,
  B11111,
  B11111,
  B01110,
  B00000,
  B00000
};

// Button read analog pin
const int BUTTONS_PIN = A0;

// Button values
const int BTN_RIGHT_VAL = 0;
const int BTN_UP_VAL = 100;
const int BTN_DOWN_VAL = 255;
const int BTN_LEFT_VAL = 400;
const int BTN_SELECT_VAL = 640;
const int BTN_NONE_VAL = 1023;

// Game constants
const int LCD_WIDTH = 16;
const int LCD_HEIGHT = 2;
const int MAX_OBSTACLES = 8;
const unsigned long INITIAL_SPEED = 500;
const unsigned long MIN_SPEED = 150;
const int PLAYER_X = 1;

// Game variables
int playerY = 0;
unsigned long lastMoveTime = 0;
unsigned long moveDelay;
int score = 0;
bool gameOver = false;
bool gamePaused = false;
int obstacleX[MAX_OBSTACLES];
int obstacleY[MAX_OBSTACLES];
int numObstacles = 0;
int scrollCounter = 0;

// Variables para comunicación serial
unsigned long lastSerialSend = 0;
const unsigned long SERIAL_INTERVAL = 50;

void setup() {
  // Initialize LCD
  lcd.begin(LCD_WIDTH, LCD_HEIGHT);

  // Create custom characters
  lcd.createChar(0, playerChar);
  lcd.createChar(1, obstacleChar);

  // Initialize analog input for buttons
  pinMode(BUTTONS_PIN, INPUT);

  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("RUNNER_READY");

  // Seed random number generator
  randomSeed(analogRead(A1));

  // Show welcome screen
  showWelcomeScreen();
  waitForButtonPress();

  // Initialize game
  initializeGame();
}

void loop() {
  // Handle serial commands
  handleSerialInput();

  if (!gameOver && !gamePaused) {
    // Read button input
    readButtons();

    // Update game at specified intervals
    unsigned long currentTime = millis();
    if (currentTime - lastMoveTime >= moveDelay) {
      lastMoveTime = currentTime;
      updateGame();
      drawGame();
    }
  } else if (gameOver) {
    // Wait for button press to restart
    if (readAnyButton()) {
      initializeGame();
      Serial.println("GAME_RESTART");
    }
  } else if (gamePaused) {
    // Check for unpause (SELECT button)
    int button = getButton();
    if (button == BTN_SELECT_VAL) {
      gamePaused = false;
      delay(300);
      drawGame();
      Serial.println("GAME_RESUME");
    }
  }

  // Send periodic updates to Python
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
      initializeGame();
      Serial.println("GAME_RESTART");
    } else if (command == "PAUSE") {
      if (!gameOver) {
        gamePaused = !gamePaused;
        if (gamePaused) {
          showPauseScreen();
          Serial.println("GAME_PAUSE");
        } else {
          drawGame();
          Serial.println("GAME_RESUME");
        }
      }
    } else if (command == "MOVE_UP") {
      if (!gameOver && !gamePaused) {
        playerY = 0;
        Serial.println("PLAYER_MOVE:0");
      }
    } else if (command == "MOVE_DOWN") {
      if (!gameOver && !gamePaused) {
        playerY = 1;
        Serial.println("PLAYER_MOVE:1");
      }
    }
  }
}

void sendGameState() {
  // Enviar estado completo del juego
  Serial.print("STATE:");
  Serial.print(playerY); Serial.print(",");
  Serial.print(score); Serial.print(",");
  Serial.print(moveDelay); Serial.print(",");
  Serial.print(gameOver ? 1 : 0); Serial.print(",");
  Serial.print(gamePaused ? 1 : 0); Serial.print(",");
  Serial.print(numObstacles);
  Serial.println();

  // Enviar posiciones de obstáculos
  if (numObstacles > 0) {
    Serial.print("OBSTACLES:");
    for (int i = 0; i < numObstacles; i++) {
      Serial.print(obstacleX[i]);
      Serial.print(",");
      Serial.print(obstacleY[i]);
      if (i < numObstacles - 1) Serial.print(";");
    }
    Serial.println();
  }
}

void readButtons() {
  int button = getButton();

  // Handle direction buttons
  if (button == BTN_UP_VAL) {
    playerY = 0;
    Serial.println("PLAYER_MOVE:0");
    delay(100);
  } else if (button == BTN_DOWN_VAL) {
    playerY = 1;
    Serial.println("PLAYER_MOVE:1");
    delay(100);
  } else if (button == BTN_SELECT_VAL) {
    gamePaused = true;
    showPauseScreen();
    Serial.println("GAME_PAUSE");
    delay(300);
  }
}

int getButton() {
  int buttonValue = analogRead(BUTTONS_PIN);

  if (buttonValue < 50) return BTN_RIGHT_VAL;
  if (buttonValue < 150) return BTN_UP_VAL;
  if (buttonValue < 350) return BTN_DOWN_VAL;
  if (buttonValue < 500) return BTN_LEFT_VAL;
  if (buttonValue < 850) return BTN_SELECT_VAL;

  return BTN_NONE_VAL;
}

bool readAnyButton() {
  return getButton() != BTN_NONE_VAL;
}

void waitForButtonPress() {
  while (!readAnyButton()) {
    delay(100);
  }
  delay(300);
}

void showWelcomeScreen() {
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("TWO LANES");
  lcd.setCursor(0, 1);
  lcd.print("Press any button");
  Serial.println("WELCOME_SCREEN");
}

void showPauseScreen() {
  lcd.clear();
  lcd.setCursor(4, 0);
  lcd.print("PAUSED");
  lcd.setCursor(2, 1);
  lcd.print("Score: ");
  lcd.print(score);
}

void initializeGame() {
  // Reset game variables
  playerY = 0;
  score = 0;
  gameOver = false;
  gamePaused = false;
  moveDelay = INITIAL_SPEED;
  numObstacles = 0;
  scrollCounter = 0;

  // Clear obstacles
  for (int i = 0; i < MAX_OBSTACLES; i++) {
    obstacleX[i] = -1;
  }

  // Draw initial state
  lcd.clear();
  drawGame();

  Serial.println("GAME_START");
  sendGameState();
}

void updateGame() {
  // Move all obstacles left
  for (int i = 0; i < numObstacles; i++) {
    obstacleX[i]--;

    // Check collision with player
    if (obstacleX[i] == PLAYER_X && obstacleY[i] == playerY) {
      gameOver = true;
      showGameOver();
      Serial.print("COLLISION:");
      Serial.print(obstacleX[i]);
      Serial.print(",");
      Serial.println(obstacleY[i]);
      Serial.print("GAME_OVER:");
      Serial.println(score);
      return;
    }

    // Remove obstacles that move off-screen
    if (obstacleX[i] < 0) {
      // Shift all obstacles down in the array
      for (int j = i; j < numObstacles - 1; j++) {
        obstacleX[j] = obstacleX[j + 1];
        obstacleY[j] = obstacleY[j + 1];
      }
      numObstacles--;
      i--;

      // Increase score
      score++;
      Serial.print("SCORE_UPDATE:");
      Serial.println(score);

      // Increase speed every 10 points
      if (score % 10 == 0) {
        moveDelay = max(MIN_SPEED, moveDelay - 30);
        Serial.print("SPEED_INCREASE:");
        Serial.println(moveDelay);
      }
    }
  }

  // Generate new obstacles
  scrollCounter++;
  if (scrollCounter >= 3 && numObstacles < MAX_OBSTACLES) {
    scrollCounter = 0;

    // Determine which lane will have the new obstacle
    int newObstacleY;

    // Check the rightmost obstacle to ensure we don't block both lanes
    bool topLaneBlocked = false;
    bool bottomLaneBlocked = false;

    for (int i = 0; i < numObstacles; i++) {
      if (obstacleX[i] == LCD_WIDTH - 1) {
        if (obstacleY[i] == 0) topLaneBlocked = true;
        if (obstacleY[i] == 1) bottomLaneBlocked = true;
      }
    }

    // Make sure there's always a path
    if (topLaneBlocked) {
      newObstacleY = 0;
    } else if (bottomLaneBlocked) {
      newObstacleY = 1;
    } else {
      newObstacleY = random(2);
    }

    // Add the new obstacle
    obstacleX[numObstacles] = LCD_WIDTH - 1;
    obstacleY[numObstacles] = newObstacleY;
    numObstacles++;

    Serial.print("NEW_OBSTACLE:");
    Serial.print(LCD_WIDTH - 1);
    Serial.print(",");
    Serial.println(newObstacleY);
  }
}

void drawGame() {
  lcd.clear();

  // Draw player
  lcd.setCursor(PLAYER_X, playerY);
  lcd.write(byte(0));

  // Draw obstacles
  for (int i = 0; i < numObstacles; i++) {
    if (obstacleX[i] >= 0 && obstacleX[i] < LCD_WIDTH) {
      lcd.setCursor(obstacleX[i], obstacleY[i]);
      lcd.write(byte(1));
    }
  }

  // Display score
  if (LCD_WIDTH >= 14) {
    lcd.setCursor(LCD_WIDTH - 3, 0);
    lcd.print(score);
  }
}

void showGameOver() {
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("GAME OVER");
  lcd.setCursor(0, 1);
  lcd.print("Score: ");
  lcd.print(score);
}

/*
PROTOCOLO SERIAL:
Arduino -> Python:
- "RUNNER_READY" -> Arduino inicializado
- "STATE:playerY,score,speed,gameOver,gamePaused,numObstacles" -> Estado del juego
- "OBSTACLES:x1,y1;x2,y2;..." -> Posiciones de obstáculos
- "PLAYER_MOVE:lane" -> Jugador cambió de carril
- "COLLISION:x,y" -> Colisión detectada
- "SCORE_UPDATE:score" -> Puntuación actualizada
- "SPEED_INCREASE:newSpeed" -> Velocidad aumentada
- "NEW_OBSTACLE:x,y" -> Nuevo obstáculo creado
- "GAME_START/PAUSE/RESUME/RESTART/OVER" -> Eventos del juego

Python -> Arduino:
- "GET_STATE" -> Solicitar estado
- "RESTART" -> Reiniciar juego
- "PAUSE" -> Pausar/reanudar
- "MOVE_UP/MOVE_DOWN" -> Mover jugador (control desde PC)
*/
