/**
 * Piano.ino - Un piano simple controlado por Arduino
 *
 * Este programa implementa un piano digital de 8 teclas utilizando
 * botones conectados a pines digitales y un buzzer para generar sonidos.
 * Cada botón reproduce una nota musical diferente cuando se presiona.
 */

// Definición de constantes para mejorar la legibilidad y mantenimiento
// Pines para los botones
const int NUM_BUTTONS = 8;
const int BUTTON_PINS[NUM_BUTTONS] = {2, 3, 4, 5, 6, 7, 8, 9};

// Pin para el buzzer
const int BUZZER_PIN = 13;

// Frecuencias de notas musicales (en Hz)
// Usando frecuencias de notas reales para un mejor sonido musical
const int NOTE_FREQUENCIES[NUM_BUTTONS] = {
  262, // Do (C4)
  294, // Re (D4)
  330, // Mi (E4)
  349, // Fa (F4)
  392, // Sol (G4)
  440, // La (A4)
  494, // Si (B4)
  523  // Do (C5)
};

// Duración de la nota en milisegundos
const int NOTE_DURATION = 100;

// Tiempo de espera entre lecturas para evitar rebotes
const int LOOP_DELAY = 10;

void setup() {
  // Configurar todos los pines de botones como entradas
  // Usando un bucle para reducir la repetición de código
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(BUTTON_PINS[i], INPUT);
  }

  // Configurar el pin del buzzer como salida
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // Revisar el estado de cada botón
  for (int i = 0; i < NUM_BUTTONS; i++) {
    // Leer el estado del botón actual
    int buttonState = digitalRead(BUTTON_PINS[i]);

    // Si el botón está presionado (HIGH o 1), tocar la nota correspondiente
    if (buttonState == HIGH) {
      tone(BUZZER_PIN, NOTE_FREQUENCIES[i], NOTE_DURATION);

      // Pequeña pausa para evitar solapamiento de tonos
      // cuando se presionan múltiples botones rápidamente
      delay(NOTE_DURATION / 2);
    }
  }

  // Pequeña pausa para estabilizar el loop
  delay(LOOP_DELAY);
}