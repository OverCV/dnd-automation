// display.cpp
#include "display.h"

Display::Display(uint8_t rs, uint8_t en, uint8_t d4, uint8_t d5, uint8_t d6, uint8_t d7, bool simulationMode)
  : _rs(rs), _en(en), _d4(d4), _d5(d5), _d6(d6), _d7(d7), _simulationMode(simulationMode) {
}

void Display::init() {
  // Configurar pines
  pinMode(_rs, OUTPUT);
  pinMode(_en, OUTPUT);
  pinMode(_d4, OUTPUT);
  pinMode(_d5, OUTPUT);
  pinMode(_d6, OUTPUT);
  pinMode(_d7, OUTPUT);

  // Set all pins low (might help with random initialization states)
  digitalWrite(_rs, LOW);
  digitalWrite(_en, LOW);
  digitalWrite(_d4, LOW);
  digitalWrite(_d5, LOW);
  digitalWrite(_d6, LOW);
  digitalWrite(_d7, LOW);

  // Esperar más de 40ms después de encender (datasheet)
  delay(50);

  // Secuencia de inicialización especial
  // Primer intento
  sendNibble(0x03);
  delay(5);  // Esperar > 4.1ms

  // Segundo intento
  sendNibble(0x03);
  delay(5);  // Esperar > 100us

  // Tercer intento
  sendNibble(0x03);
  delay(1);

  // Finalmente configurar a 4-bit
  sendNibble(0x02);
  delay(1);

  // Configuración final
  command(LCD_FUNCTIONSET | LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS);           // 4-bit mode, 2 line, 5x8 dots
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF);  // Display on, cursor off, blink off
  command(LCD_ENTRYMODESET | 0x02);                                            // Increment cursor, no display shift
  clear();
}

void Display::pulseEnable() {
  digitalWrite(_en, LOW);
  if (_simulationMode) {
    delayMicroseconds(1);
  }
  digitalWrite(_en, HIGH);
  if (_simulationMode) {
    delayMicroseconds(1);
  }
  digitalWrite(_en, LOW);
  if (_simulationMode) {
    delayMicroseconds(100);  // Extra delay for simulation
  } else {
    delayMicroseconds(50);  // Regular delay
  }
}

void Display::sendNibble(uint8_t nibble) {
  digitalWrite(_d4, nibble & 0x01);
  digitalWrite(_d5, (nibble >> 1) & 0x01);
  digitalWrite(_d6, (nibble >> 2) & 0x01);
  digitalWrite(_d7, (nibble >> 3) & 0x01);
  pulseEnable();
}

void Display::command(uint8_t command) {
  digitalWrite(_rs, LOW);
  sendNibble(command >> 4);
  sendNibble(command & 0x0F);
  waitReady();
}

void Display::writeChar(char c) {
  digitalWrite(_rs, HIGH);
  sendNibble(c >> 4);
  sendNibble(c & 0x0F);
  waitReady();
}

void Display::print(const char* str) {
  while (*str) {
    writeChar(*str++);
  }
}

void Display::print(String str) {
  print(str.c_str());
}

void Display::clear() {
  command(LCD_CLEARDISPLAY);
  if (_simulationMode) {
    delay(2);
  } else {
    delay(2);  // El clear necesita 1.52ms
  }
}

void Display::home() {
  command(LCD_RETURNHOME);
  if (_simulationMode) {
    delay(2);
  } else {
    delay(2);  // El return home necesita 1.52ms
  }
}

void Display::setCursor(uint8_t col, uint8_t row) {
  const uint8_t row_offsets[] = { 0x00, 0x40, 0x14, 0x54 };
  command(LCD_SETDDRAMADDR | (col + row_offsets[row]));
}

void Display::waitReady() {
  if (_simulationMode) {
    delay(2);
  } else {
    delayMicroseconds(50);
  }
}

// Rotacional
void Display::startScroll(String text, uint8_t row, bool direction) {
  if (text.length() <= LCD_COLS) {
    // Si el texto es más corto que el display, solo mostrarlo centrado
    clear();
    setCursor((LCD_COLS - text.length()) / 2, row);
    print(text);
    _isScrolling = false;
    return;
  }

  _scrollText = text;
  _scrollPosition = 0;
  _scrollRow = row;
  _scrollDirection = direction;
  _isScrolling = true;

  // Mostrar los primeros caracteres
  updateScroll();
}

void Display::stopScroll() {
  _isScrolling = false;
  _scrollText = "";
  _scrollPosition = 0;
}

void Display::updateScroll() {
  if (!_isScrolling) return;

  uint16_t textLen = _scrollText.length();
  String displayText = "";

  // Construir el texto a mostrar...
  for (uint8_t i = 0; i < LCD_COLS; i++) {
    uint16_t charPos = (_scrollPosition + i) % textLen;
    displayText += _scrollText[charPos];
  }

  // Actualizar display
  setCursor(0, _scrollRow);
  print(displayText);

  // Actualizar posición para la siguiente actualización.
  if (_scrollDirection) {
    // Rotar derecha
    if (_scrollPosition == 0) {
      _scrollPosition = textLen - 1;
    } else {
      _scrollPosition--;
    }
  } else {
    // Rotar izquierda.
    _scrollPosition = (_scrollPosition + 1) % textLen;
  }
}

void Display::setScrollDirection(bool direction) {
  _scrollDirection = direction;
}

// Custom
bool Display::createChar(uint8_t location, const uint8_t charmap[]) {
  // Validar ubicación
  if (location >= CGRAM_CHARS) return false;

  // Establecer dirección CGRAM (0x40 + (ubicación * 8))
  command(LCD_SETCGRAMADDR | (location << 3));

  // Escribir los 8 bytes del patrón
  for (uint8_t i = 0; i < CHAR_HEIGHT; i++) {
    writeChar(charmap[i]);
  }

  // Volver a modo normal (DDRAM)
  command(LCD_SETDDRAMADDR);

  return true;
}

void Display::writeCustomChar(uint8_t location) {
  if (location >= CGRAM_CHARS) return;
  writeChar(location);  // Los caracteres custom se acceden con códigos 0-7
}

bool Display::createChars(const uint8_t* charmap, uint8_t numChars) {
  if (numChars > CGRAM_CHARS) return false;

  for (uint8_t i = 0; i < numChars; i++) {
    if (!createChar(i, &charmap[i * CHAR_HEIGHT])) {
      return false;
    }
  }
  return true;
}

// Base

void Display::display() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF);
}

void Display::noDisplay() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYOFF | LCD_CURSOROFF | LCD_BLINKOFF);
}

void Display::cursor() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSORON | LCD_BLINKOFF);
}

void Display::noCursor() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF);
}

void Display::blink() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKON);
}

void Display::noBlink() {
  command(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF);
}