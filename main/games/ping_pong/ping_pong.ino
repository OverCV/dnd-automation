// CÓDIGO ARDUINO - Subir al Arduino
// Ping Pong Game con comunicación serial

#include <LiquidCrystal.h>

// Define LCD pins for the LCD Keypad Shield
const int RS = 8, EN = 9, D4 = 4, D5 = 5, D6 = 6, D7 = 7;
LiquidCrystal lcd(RS, EN, D4, D5, D6, D7);

// Custom characters
byte ballChar[8] = {
  B00000,
  B00000,
  B00100,
  B01110,
  B01110,
  B00100,
  B00000,
  B00000
};

byte leftPaddleChar[8] = {
  B10000,
  B10000,
  B10000,
  B10000,
  B10000,
  B10000,
  B10000,
  B10000
};

byte rightPaddleChar[8] = {
  B00001,
  B00001,
  B00001,
  B00001,
  B00001,
  B00001,
  B00001,
  B00001
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
const unsigned long GAME_SPEED = 300;

// Game variables
int ballX = LCD_WIDTH / 2;
int ballY = 0;
int ballDX = 1;
int ballDY = 1;
bool leftPaddleActive = false;
bool rightPaddleActive = false;
unsigned long lastMoveTime = 0;
int score = 0;
bool gameOver = false;
bool gamePaused = false;

// Variables para comunicación serial
unsigned long lastSerialSend = 0;
const unsigned long SERIAL_INTERVAL = 50; // Enviar datos cada 50ms

void setup() {
  // Initialize LCD
  lcd.begin(LCD_WIDTH, LCD_HEIGHT);

  // Create custom characters
  lcd.createChar(0, ballChar);
  lcd.createChar(1, leftPaddleChar);
  lcd.createChar(2, rightPaddleChar);

  // Initialize analog input for buttons
  pinMode(BUTTONS_PIN, INPUT);

  // Initialize serial communication
  Serial.begin(9600);

  // Send ready signal
  Serial.println("PONG_READY");

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
    // Read button input for paddles
    readButtons();

    // Update game at specified intervals
    unsigned long currentTime = millis();
    if (currentTime - lastMoveTime >= GAME_SPEED) {
      lastMoveTime = currentTime;
      updateGame();
      drawGame();

      // Send game state to Python
      sendGameState();
    }
  } else if (gameOver) {
    // Check for restart (SELECT button)
    int button = getButton();
    if (button == BTN_SELECT_VAL) {
      delay(300); // Debounce
      initializeGame();
      Serial.println("GAME_RESTART");
    }
  } else if (gamePaused) {
    // Check for unpause (SELECT button)
    int button = getButton();
    if (button == BTN_SELECT_VAL) {
      gamePaused = false;
      delay(300); // Debounce
      drawGame();
      Serial.println("GAME_RESUME");
    }
  }

  // Send periodic updates to Python
  unsigned long currentTime = millis();
  if (currentTime - lastSerialSend >= SERIAL_INTERVAL) {
    lastSerialSend = currentTime;
    sendPeriodicUpdate();
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
    } else if (command == "PAUSE") {
      if (!gameOver) {
        gamePaused = !gamePaused;
        if (gamePaused) {
          showPauseScreen();
        } else {
          drawGame();
        }
      }
    }
  }
}

void sendGameState() {
  // Enviar estado completo del juego
  Serial.print("STATE:");
  Serial.print(ballX); Serial.print(",");
  Serial.print(ballY); Serial.print(",");
  Serial.print(leftPaddleActive ? 1 : 0); Serial.print(",");
  Serial.print(rightPaddleActive ? 1 : 0); Serial.print(",");
  Serial.print(score); Serial.print(",");
  Serial.print(gameOver ? 1 : 0); Serial.print(",");
  Serial.print(gamePaused ? 1 : 0);
  Serial.println();
}

void sendPeriodicUpdate() {
  // Enviar actualizaciones de botones
  Serial.print("BUTTONS:");
  Serial.print(leftPaddleActive ? 1 : 0); Serial.print(",");
  Serial.print(rightPaddleActive ? 1 : 0);
  Serial.println();
}

void readButtons() {
  int button = getButton();

  // Handle paddle buttons - paddles are activated when buttons are pressed
  leftPaddleActive = (button == BTN_LEFT_VAL);
  rightPaddleActive = (button == BTN_RIGHT_VAL);

  // Pause game with SELECT
  if (button == BTN_SELECT_VAL) {
    gamePaused = true;
    showPauseScreen();
    Serial.println("GAME_PAUSE");
    delay(300); // Debounce
  }
}

int getButton() {
  int buttonValue = analogRead(BUTTONS_PIN);

  // Return approximate button value
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
  // Wait until a button is pressed
  while (!readAnyButton()) {
    delay(100);
  }
  delay(300); // Debounce
}

void showWelcomeScreen() {
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("PING PONG");
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
  ballX = LCD_WIDTH / 2;
  ballY = 0;

  // Fixed initial direction - always start the same way
  ballDX = 1;  // Move right
  ballDY = 1;  // Move down

  leftPaddleActive = false;
  rightPaddleActive = false;
  score = 0;
  gameOver = false;
  gamePaused = false;

  // Draw initial state
  lcd.clear();
  drawGame();

  // Notify Python
  Serial.println("GAME_START");
  sendGameState();
}

void updateGame() {
  // Update ball position
  ballX += ballDX;
  ballY += ballDY;

  // Ball collision with top and bottom edges
  if (ballY < 0) {
    ballY = 0;
    ballDY = -ballDY;
    Serial.println("BOUNCE_VERTICAL");
  } else if (ballY >= LCD_HEIGHT) {
    ballY = LCD_HEIGHT - 1;
    ballDY = -ballDY;
    Serial.println("BOUNCE_VERTICAL");
  }

  // Ball collision with left edge
  if (ballX <= 0) {
    if (leftPaddleActive) {
      // Ball hits left paddle
      ballX = 1;
      ballDX = -ballDX;
      score++;
      Serial.println("PADDLE_HIT_LEFT");
    } else {
      // Game over - left paddle not activated
      gameOver = true;
      showGameOver("Left miss!");
      Serial.println("GAME_OVER:Left miss!");
      return;
    }
  }

  // Ball collision with right edge
  if (ballX >= LCD_WIDTH - 1) {
    if (rightPaddleActive) {
      // Ball hits right paddle
      ballX = LCD_WIDTH - 2;
      ballDX = -ballDX;
      score++;
      Serial.println("PADDLE_HIT_RIGHT");
    } else {
      // Game over - right paddle not activated
      gameOver = true;
      showGameOver("Right miss!");
      Serial.println("GAME_OVER:Right miss!");
      return;
    }
  }
}

void drawGame() {
  lcd.clear();

  // Draw ball
  lcd.setCursor(ballX, ballY);
  lcd.write(byte(0));

  // Draw left paddle if active (on both rows)
  if (leftPaddleActive) {
    lcd.setCursor(0, 0);
    lcd.write(byte(1));
    lcd.setCursor(0, 1);
    lcd.write(byte(1));
  }

  // Draw right paddle if active (on both rows)
  if (rightPaddleActive) {
    lcd.setCursor(LCD_WIDTH - 1, 0);
    lcd.write(byte(2));
    lcd.setCursor(LCD_WIDTH - 1, 1);
    lcd.write(byte(2));
  }

  // Display score in the center top
  lcd.setCursor(LCD_WIDTH/2 - 1, 0);
  lcd.print(score);
}

void showGameOver(const char* message) {
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("GAME OVER");

  // Show which side missed and the score
  lcd.setCursor(0, 1);
  lcd.print(message);
  lcd.print(" S:");
  lcd.print(score);
}

/*
PROTOCOLO DE COMUNICACIÓN SERIAL:
Arduino -> Python:
- "PONG_READY" -> Arduino inicializado
- "STATE:x,y,leftPaddle,rightPaddle,score,gameOver,paused" -> Estado completo del juego
- "BUTTONS:leftActive,rightActive" -> Estado de botones
- "PADDLE_HIT_LEFT/RIGHT" -> Pala golpeó la pelota
- "BOUNCE_VERTICAL" -> Pelota rebotó en borde vertical
- "GAME_OVER:mensaje" -> Juego terminado
- "GAME_START/PAUSE/RESUME/RESTART" -> Cambios de estado

Python -> Arduino:
- "GET_STATE" -> Solicitar estado actual
- "RESTART" -> Reiniciar juego
- "PAUSE" -> Pausar/reanudar juego
*/
