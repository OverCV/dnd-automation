/**
 * Two-Lane Runner Game for Arduino with LCD Keypad Shield
 *
 * The player controls a character that can move between top and bottom lanes.
 * Obstacles scroll from right to left, and the player must switch lanes to avoid them.
 * There will always be at least one open path (no simultaneous obstacles in both lanes).
 * Speed increases as the game progresses.
 *
 * Controls:
 * - UP: Move to top lane
 * - DOWN: Move to bottom lane
 * - SELECT: Pause/Resume game
 */

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
 const int MAX_OBSTACLES = 8;  // Maximum number of obstacles on screen
 const unsigned long INITIAL_SPEED = 500; // milliseconds between moves
 const unsigned long MIN_SPEED = 150; // fastest speed
 const int PLAYER_X = 1; // Fixed X position of player

 // Game variables
 int playerY = 0; // 0 for top lane, 1 for bottom lane
 unsigned long lastMoveTime = 0;
 unsigned long moveDelay;
 int score = 0;
 bool gameOver = false;
 bool gamePaused = false;
 int obstacleX[MAX_OBSTACLES];  // X positions of obstacles
 int obstacleY[MAX_OBSTACLES];  // Y positions of obstacles (0=top, 1=bottom)
 int numObstacles = 0;          // Current number of active obstacles
 int scrollCounter = 0;         // Counter to control obstacle generation

 void setup() {
   // Initialize LCD
   lcd.begin(LCD_WIDTH, LCD_HEIGHT);

   // Create custom characters
   lcd.createChar(0, playerChar);
   lcd.createChar(1, obstacleChar);

   // Initialize analog input for buttons
   pinMode(BUTTONS_PIN, INPUT);

   // Seed random number generator
   randomSeed(analogRead(A1));

   // Show welcome screen
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
       drawGame();
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
   if (button == BTN_UP_VAL) {
     playerY = 0; // Move to top lane
     delay(50);   // Small debounce
   } else if (button == BTN_DOWN_VAL) {
     playerY = 1; // Move to bottom lane
     delay(50);   // Small debounce
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

   // Return approximate button value based on analog reading
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
   lcd.print("TWO LANES");
   lcd.setCursor(0, 1);
   lcd.print("Press any button");
 }

 void initializeGame() {
   // Reset game variables
   playerY = 0; // Start at top lane
   score = 0;
   gameOver = false;
   gamePaused = false;
   moveDelay = INITIAL_SPEED;
   numObstacles = 0;
   scrollCounter = 0;

   // Clear obstacles
   for (int i = 0; i < MAX_OBSTACLES; i++) {
     obstacleX[i] = -1; // Off-screen
   }

   // Draw initial state
   lcd.clear();
   drawGame();
 }

 void updateGame() {
   // Move all obstacles left
   for (int i = 0; i < numObstacles; i++) {
     obstacleX[i]--;

     // Check collision with player
     if (obstacleX[i] == PLAYER_X && obstacleY[i] == playerY) {
       gameOver = true;
       showGameOver();
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
       i--; // Adjust index since we removed an element

       // Increase score when obstacle passes
       score++;

       // Increase speed every 10 points
       if (score % 10 == 0) {
         moveDelay = max(MIN_SPEED, moveDelay - 30);
       }
     }
   }

   // Generate new obstacles
   scrollCounter++;
   if (scrollCounter >= 3 && numObstacles < MAX_OBSTACLES) { // Create obstacle every 3 steps
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
       newObstacleY = 0; // Put obstacle in top lane
     } else if (bottomLaneBlocked) {
       newObstacleY = 1; // Put obstacle in bottom lane
     } else {
       // Randomly choose lane if neither is blocked
       newObstacleY = random(2); // 0 or 1
     }

     // Add the new obstacle
     obstacleX[numObstacles] = LCD_WIDTH - 1; // Right edge
     obstacleY[numObstacles] = newObstacleY;
     numObstacles++;
   }
 }

 void drawGame() {
   lcd.clear();

   // Draw player
   lcd.setCursor(PLAYER_X, playerY);
   lcd.write(byte(0)); // Player character

   // Draw obstacles
   for (int i = 0; i < numObstacles; i++) {
     if (obstacleX[i] >= 0 && obstacleX[i] < LCD_WIDTH) {
       lcd.setCursor(obstacleX[i], obstacleY[i]);
       lcd.write(byte(1)); // Obstacle character
     }
   }

   // Optionally display score in the corner
   if (LCD_WIDTH >= 14) { // Only if there's enough space
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
