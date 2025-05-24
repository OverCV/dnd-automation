/**
 * Snake Game for Arduino with LCD Keypad Shield
 *
 * Controls:
 * - UP: Move snake up
 * - DOWN: Move snake down
 * - LEFT: Move snake left
 * - RIGHT: Move snake right
 * - SELECT: Pause/Resume game
 */

 #include <LiquidCrystal.h>

 // Define LCD pins for the LCD Keypad Shield
 const int RS = 8, EN = 9, D4 = 4, D5 = 5, D6 = 6, D7 = 7;
 LiquidCrystal lcd(RS, EN, D4, D5, D6, D7);

 // Custom characters
 byte snakeBody[8] = {
   B00000,
   B00000,
   B00000,
   B01110,
   B01110,
   B00000,
   B00000,
   B00000
 };

 byte snakeHead[8] = {
   B00000,
   B00000,
   B00100,
   B01110,
   B01110,
   B00000,
   B00000,
   B00000
 };

 byte food[8] = {
   B00000,
   B00000,
   B00100,
   B01010,
   B01010,
   B00100,
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
 const int MAX_SNAKE_LENGTH = 20;
 const unsigned long INITIAL_SPEED = 500; // milliseconds between moves
 const unsigned long MIN_SPEED = 150; // fastest speed

 // Game state
 enum Direction { UP, DOWN, LEFT, RIGHT, NONE };
 Direction currentDirection = NONE;
 Direction lastDirection = NONE;

 // Snake coordinates (max length = 20)
 int snakeX[MAX_SNAKE_LENGTH];
 int snakeY[MAX_SNAKE_LENGTH];
 int snakeLength;

 // Food coordinates
 int foodX;
 int foodY;

 // Game variables
 unsigned long lastMoveTime = 0;
 unsigned long moveDelay;
 int score;
 bool gameOver;
 bool gamePaused;

 void setup() {
   // Initialize LCD
   lcd.begin(LCD_WIDTH, LCD_HEIGHT);

   // Create custom characters
   lcd.createChar(0, snakeBody);
   lcd.createChar(1, snakeHead);
   lcd.createChar(2, food);

   // Initialize analog input for buttons
   pinMode(BUTTONS_PIN, INPUT);

   // Seed random number generator
   randomSeed(analogRead(A1));

   // Show welcome message
   showWelcomeScreen();
   waitForButtonPress();

   // Initialize game
   initializeGame();
 }

 void loop() {
   if (!gameOver && !gamePaused) {
     // Read button input
     readButtons();

     // Update game at specified intervals
     unsigned long currentTime = millis();
     if (currentTime - lastMoveTime >= moveDelay) {
       lastMoveTime = currentTime;
       updateGame();
     }
   } else if (gameOver) {
     // Wait for button press to restart
     if (readAnyButton()) {
       initializeGame();
     }
   } else if (gamePaused) {
     // Check for unpause (SELECT button)
     int button = getButton();
     if (button == BTN_SELECT_VAL) {
       gamePaused = false;
       delay(300); // Debounce
       drawGame();
     }
   }
 }

 void readButtons() {
   int button = getButton();

   // Handle direction buttons
   if (button == BTN_UP_VAL && lastDirection != DOWN) {
     currentDirection = UP;
   } else if (button == BTN_DOWN_VAL && lastDirection != UP) {
     currentDirection = DOWN;
   } else if (button == BTN_LEFT_VAL && lastDirection != RIGHT) {
     currentDirection = LEFT;
   } else if (button == BTN_RIGHT_VAL && lastDirection != LEFT) {
     currentDirection = RIGHT;
   } else if (button == BTN_SELECT_VAL) {
     gamePaused = true;
     lcd.clear();
     lcd.setCursor(4, 0);
     lcd.print("PAUSED");
     lcd.setCursor(2, 1);
     lcd.print("Score: ");
     lcd.print(score);
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
   lcd.setCursor(4, 0);
   lcd.print("SNAKE");
   lcd.setCursor(0, 1);
   lcd.print("Press any button");
 }

 void initializeGame() {
   // Reset game variables
   snakeLength = 3;
   score = 0;
   gameOver = false;
   gamePaused = false;
   moveDelay = INITIAL_SPEED;
   currentDirection = RIGHT;
   lastDirection = RIGHT;

   // Initialize snake position (start from left side)
   for (int i = 0; i < snakeLength; i++) {
     snakeX[i] = 2 - i;
     snakeY[i] = 0;
   }

   // Place initial food
   placeFood();

   // Draw initial state
   drawGame();
 }

 void placeFood() {
   bool validPosition;

   // Keep trying positions until we find one that's not on the snake
   do {
     validPosition = true;
     foodX = random(0, LCD_WIDTH);
     foodY = random(0, LCD_HEIGHT);

     // Check if food overlaps with the snake
     for (int i = 0; i < snakeLength; i++) {
       if (foodX == snakeX[i] && foodY == snakeY[i]) {
         validPosition = false;
         break;
       }
     }
   } while (!validPosition);
 }

 void updateGame() {
   // Save last direction
   lastDirection = currentDirection;

   // Calculate new head position
   int newHeadX = snakeX[0];
   int newHeadY = snakeY[0];

   // Update based on direction
   switch (currentDirection) {
     case UP:
       newHeadY--;
       break;
     case DOWN:
       newHeadY++;
       break;
     case LEFT:
       newHeadX--;
       break;
     case RIGHT:
       newHeadX++;
       break;
     case NONE:
       return;
   }

   // Check for wrap-around
   if (newHeadX < 0) newHeadX = LCD_WIDTH - 1;
   if (newHeadX >= LCD_WIDTH) newHeadX = 0;
   if (newHeadY < 0) newHeadY = LCD_HEIGHT - 1;
   if (newHeadY >= LCD_HEIGHT) newHeadY = 0;

   // Check for collision with self
   for (int i = 0; i < snakeLength; i++) {
     if (newHeadX == snakeX[i] && newHeadY == snakeY[i]) {
       gameOver = true;
       showGameOver();
       return;
     }
   }

   // Check for food collision
   bool ate = (newHeadX == foodX && newHeadY == foodY);

   // Move snake (shift all elements)
   if (!ate) {
     // Clear last segment position on screen
     lcd.setCursor(snakeX[snakeLength-1], snakeY[snakeLength-1]);
     lcd.print(" ");
   } else {
     // Increase length if food was eaten
     if (snakeLength < MAX_SNAKE_LENGTH) {
       snakeLength++;
     }
     score += 10;

     // Place new food
     placeFood();

     // Increase speed (decrease delay)
     moveDelay = max(MIN_SPEED, INITIAL_SPEED - (score / 10) * 20);
   }

   // Shift snake body positions
   for (int i = snakeLength - 1; i > 0; i--) {
     snakeX[i] = snakeX[i-1];
     snakeY[i] = snakeY[i-1];
   }

   // Set new head position
   snakeX[0] = newHeadX;
   snakeY[0] = newHeadY;

   // Update display
   drawGame();
 }

 void drawGame() {
   // Clear LCD (optional, can be more efficient by only updating changed positions)
   lcd.clear();

   // Draw snake
   for (int i = 0; i < snakeLength; i++) {
     lcd.setCursor(snakeX[i], snakeY[i]);
     if (i == 0) {
       // Draw head
       lcd.write(byte(1));
     } else {
       // Draw body
       lcd.write(byte(0));
     }
   }

   // Draw food
   lcd.setCursor(foodX, foodY);
   lcd.write(byte(2));
 }

 void showGameOver() {
   lcd.clear();
   lcd.setCursor(3, 0);
   lcd.print("GAME OVER");
   lcd.setCursor(0, 1);
   lcd.print("Score: ");
   lcd.print(score);
 }
