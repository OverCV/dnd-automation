// display.h
#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>

class Display {
private:
  // Pines
  const uint8_t _rs;
  const uint8_t _en;
  const uint8_t _d4;
  const uint8_t _d5;
  const uint8_t _d6;
  const uint8_t _d7;

  // Configuración
  const bool _simulationMode;

  // Comandos LCD
  static const uint8_t LCD_CLEARDISPLAY = 0x01;
  static const uint8_t LCD_RETURNHOME = 0x02;
  static const uint8_t LCD_ENTRYMODESET = 0x04;
  static const uint8_t LCD_DISPLAYCONTROL = 0x08;
  static const uint8_t LCD_CURSORSHIFT = 0x10;
  static const uint8_t LCD_FUNCTIONSET = 0x20;
  static const uint8_t LCD_SETCGRAMADDR = 0x40;
  static const uint8_t LCD_SETDDRAMADDR = 0x80;

  // Flags para display control
  static const uint8_t LCD_DISPLAYON = 0x04;
  static const uint8_t LCD_DISPLAYOFF = 0x00;
  static const uint8_t LCD_CURSORON = 0x02;
  static const uint8_t LCD_CURSOROFF = 0x00;
  static const uint8_t LCD_BLINKON = 0x01;
  static const uint8_t LCD_BLINKOFF = 0x00;

  // Flags para function set
  static const uint8_t LCD_8BITMODE = 0x10;
  static const uint8_t LCD_4BITMODE = 0x00;
  static const uint8_t LCD_2LINE = 0x08;
  static const uint8_t LCD_1LINE = 0x00;
  static const uint8_t LCD_5x10DOTS = 0x04;
  static const uint8_t LCD_5x8DOTS = 0x00;

  // Scroll
  String _scrollText;                  // Texto completo para rotar
  uint8_t _scrollPosition;             // Posición actual de la rotación
  uint8_t _scrollRow;                  // Fila donde se muestra el texto rotativo
  bool _isScrolling;                   // Flag para indicar si hay rotación activa
  bool _scrollDirection;               // true = derecha, false = izquierda
  static const uint8_t LCD_COLS = 16;  // Número de columnas del LCD

  // Custom
  static const uint8_t CGRAM_CHARS = 8;  // Número máximo de caracteres custom
  static const uint8_t CHAR_HEIGHT = 8;  // Altura de cada caracter en pixels
  uint8_t _customCharCount;              // Número de caracteres custom registrados


  void sendNibble(uint8_t nibble);
  void pulseEnable();
  void waitReady();


public:
  Display(uint8_t rs, uint8_t en, uint8_t d4, uint8_t d5, uint8_t d6, uint8_t d7, bool simulationMode = true);
  void init();
  void command(uint8_t command);
  void writeChar(char c);
  void print(const char* str);
  void print(String str);
  void clear();
  void home();
  void setCursor(uint8_t col, uint8_t row);
  void display();
  void noDisplay();
  void cursor();
  void noCursor();
  void blink();
  void noBlink();

  // Métodos para manejo de texto rotativo
  void startScroll(String text, uint8_t row = 0, bool direction = false);
  void stopScroll();
  void updateScroll();
  bool isScrolling() const {
    return _isScrolling;
  }
  void setScrollDirection(bool direction);

  // Caracteres personalizados
  bool createChar(uint8_t location, const uint8_t charmap[]);
  void writeCustomChar(uint8_t location);
  // Método sobrecargado para crear varios caracteres a la vez
  bool createChars(const uint8_t* charmap, uint8_t numChars);
};

#endif