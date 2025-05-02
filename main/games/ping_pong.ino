/**
 * Ping_Pong.ino - Juego de ping pong con LEDs en Arduino
 *
 * Este programa simula un juego de ping pong usando una fila de LEDs.
 * Un LED se mueve de un lado a otro como si fuera una pelota.
 * Los jugadores deben presionar sus botones cuando la "pelota" (LED)
 * llega a los extremos (LEDs amarillos) para rebotar la pelota.
 * Si no presionan el botón a tiempo, se enciende el LED rojo y pierden.
 */

// Definición de pines para los LEDs
// Se usan nombres descriptivos con la convención LED_POSICIÓN_COLOR
const byte LED_1_ROJO = A2;
const byte LED_2_AMARILLO = A1;
const byte LED_3_VERDE = A0;
const byte LED_4_VERDE = 2;
const byte LED_5_VERDE = 3;
const byte LED_6_VERDE = 4;
const byte LED_7_VERDE = 5;
const byte LED_8_VERDE = 6;
const byte LED_9_VERDE = 7;
const byte LED_10_VERDE = 8;
const byte LED_11_VERDE = 9;
const byte LED_12_VERDE = 10;
const byte LED_13_VERDE = 11;
const byte LED_14_AMARILLO = 12;
const byte LED_15_ROJO = 13;

// Array con todos los pines de LEDs para facilitar operaciones en masa
const byte NUM_LEDS = 15;
const byte LED_PINS[NUM_LEDS] = {
  LED_1_ROJO, LED_2_AMARILLO, 
  LED_3_VERDE, LED_4_VERDE, LED_5_VERDE, LED_6_VERDE, LED_7_VERDE, 
  LED_8_VERDE, LED_9_VERDE, LED_10_VERDE, LED_11_VERDE, LED_12_VERDE, LED_13_VERDE, 
  LED_14_AMARILLO, LED_15_ROJO
};

// Definición de pines para los botones
const byte BOTON_IZQUIERDO_PIN = A5;
const byte BOTON_DERECHO_PIN = A4;

// Constantes para el estado del juego
const byte LED_IZQUIERDO_LIMITE = 2;  // Posición del LED amarillo izquierdo
const byte LED_DERECHO_LIMITE = 14;   // Posición del LED amarillo derecho
const byte POSICION_INICIAL = 7;      // Posición inicial de la pelota (LED central)
const int VELOCIDAD_INICIAL = 200;    // Velocidad inicial en ms
const int INCREMENTO_VELOCIDAD = 10;  // Reducción de delay en ms por cada rebote exitoso

// Variables para el estado del juego
byte posicionPelota = POSICION_INICIAL;
int velocidadJuego = VELOCIDAD_INICIAL;
bool direccionDerecha = true;  // true = hacia la derecha, false = hacia la izquierda
bool juegoTerminado = false;

void setup() {
  // Configurar todos los pines de LEDs como salidas
  for (byte i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }

  // Configurar los pines de botones como entradas
  pinMode(BOTON_IZQUIERDO_PIN, INPUT);
  pinMode(BOTON_DERECHO_PIN, INPUT);

  // Inicializar el juego mostrando la posición inicial
  actualizarPosicionPelota();
}

void loop() {
  // Si el juego ha terminado, no hacemos nada más
  if (juegoTerminado) {
    return;
  }

  // Leer el estado de los botones
  bool botonIzquierdoPresionado = digitalRead(BOTON_IZQUIERDO_PIN) == HIGH;
  bool botonDerechoPresionado = digitalRead(BOTON_DERECHO_PIN) == HIGH;

  // Lógica para rebote en el extremo izquierdo
  if (posicionPelota == LED_IZQUIERDO_LIMITE && botonIzquierdoPresionado) {
    direccionDerecha = true;  // Cambio de dirección hacia la derecha
    velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);  // Aumentar velocidad con un límite mínimo
  }
  // Lógica para rebote en el extremo derecho
  else if (posicionPelota == LED_DERECHO_LIMITE && botonDerechoPresionado) {
    direccionDerecha = false;  // Cambio de dirección hacia la izquierda
    velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);  // Aumentar velocidad con un límite mínimo
  }

  // Mover la pelota
  if (direccionDerecha) {
    posicionPelota++;
  } else {
    posicionPelota--;
  }

  // Comprobar si se ha perdido (pelota en posición de LED rojo)
  if (posicionPelota == 1 || posicionPelota == 15) {
    juegoTerminado = true;
  }

  // Actualizar la visualización de los LEDs
  actualizarPosicionPelota();

  // Esperar según la velocidad actual del juego
  delay(velocidadJuego);
}

/**
 * Actualiza los LEDs para mostrar la posición actual de la pelota
 * Apaga todos los LEDs y enciende solo el correspondiente a la posición actual
 */
void actualizarPosicionPelota() {
  // Apagar todos los LEDs primero
  for (byte i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }

  // Encender el LED correspondiente a la posición actual de la pelota
  // Las posiciones van de 1 a 15, pero los índices del array van de 0 a 14
  digitalWrite(LED_PINS[posicionPelota - 1], HIGH);
}

/**
 * Reinicia el juego a sus valores iniciales
 */
void reiniciarJuego() {
  posicionPelota = POSICION_INICIAL;
  velocidadJuego = VELOCIDAD_INICIAL;
  direccionDerecha = true;
  juegoTerminado = false;
  actualizarPosicionPelota();
}