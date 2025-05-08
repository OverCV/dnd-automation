/**
 * Ping_Pong.ino - Juego de ping pong con LEDs en Arduino
 */

// Definición de pines para los LEDs (corregido según tus comentarios)
const byte LED_1_ROJO = 2;
const byte LED_2_VERDE = 3;
const byte LED_3_AZUL = 4;
const byte LED_4_VERDE = 5;
const byte LED_5_VERDE = 6;
const byte LED_6_VERDE = 7;
const byte LED_7_VERDE = 8;
const byte LED_8_VERDE = 9;
const byte LED_9_VERDE = 10;
const byte LED_10_VERDE = 11;
const byte LED_11_VERDE = 12;
const byte LED_12_VERDE = 13;
const byte LED_13_AZUL = A2;
const byte LED_14_VERDE = A1;
const byte LED_15_ROJO = A0;

// Array con todos los pines de LEDs (corregido para que coincida con los nombres)
const byte NUM_LEDS = 15;
const byte LED_PINS[NUM_LEDS] = {
  LED_1_ROJO, LED_2_VERDE, LED_3_AZUL,
  LED_4_VERDE, LED_5_VERDE, LED_6_VERDE,
  LED_7_VERDE, LED_8_VERDE, LED_9_VERDE,
  LED_10_VERDE, LED_11_VERDE, LED_12_VERDE,
  LED_13_AZUL, LED_14_VERDE, LED_15_ROJO
};

// Definición de pines para los botones
const byte BOTON_IZQUIERDO_PIN = A5;
const byte BOTON_DERECHO_PIN = A4;

// Constantes para el estado del juego
const byte POSICION_INICIAL = 7;      // Posición inicial de la pelota (LED central)
const int VELOCIDAD_INICIAL = 300;    // Velocidad inicial en ms
const int INCREMENTO_VELOCIDAD = 15;  // Reducción de delay en ms por cada rebote exitoso
const unsigned long INTERVALO_DEBUG = 100; // Tiempo entre mensajes de debug (ms)

// Variables para el estado del juego
byte posicionPelota = POSICION_INICIAL; // Índice en el array (0-14)
int velocidadJuego = VELOCIDAD_INICIAL;
bool haciaDerecha = true;            // true = hacia la derecha, false = hacia la izquierda
bool juegoTerminado = false;

// Variables para depuración
bool ultimoEstadoBotonIzq = HIGH;
bool ultimoEstadoBotonDer = HIGH;
unsigned long ultimoTiempoDebug = 0;

void setup() {
  Serial.begin(9600); // Para depuración
  while (!Serial) { ; } // Esperar a que el puerto serial esté disponible
  Serial.println("=== INICIANDO SISTEMA DE DEBUGGING DE PING PONG ===");

  // Configurar todos los pines de LEDs como salidas
  for (byte i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }

  // Configurar los pines de botones como entradas con resistencias pull-up
  pinMode(BOTON_IZQUIERDO_PIN, INPUT_PULLUP);
  pinMode(BOTON_DERECHO_PIN, INPUT_PULLUP);
  
  // Prueba de botones antes de iniciar el juego
  Serial.println("PRUEBA DE BOTONES: Presiona ambos botones para continuar...");
  bool botonIzqProbado = false;
  bool botonDerProbado = false;
  
  while (!botonIzqProbado || !botonDerProbado) {
    bool estadoIzq = digitalRead(BOTON_IZQUIERDO_PIN) == LOW;
    bool estadoDer = digitalRead(BOTON_DERECHO_PIN) == LOW;
    
    if (estadoIzq && !botonIzqProbado) {
      Serial.println("¡Botón IZQUIERDO detectado!");
      botonIzqProbado = true;
    }
    
    if (estadoDer && !botonDerProbado) {
      Serial.println("¡Botón DERECHO detectado!");
      botonDerProbado = true;
    }
    
    delay(50);
  }
  
  Serial.println("Ambos botones funcionan correctamente.");
  delay(1000);

  // Inicializar el juego
  reiniciarJuego();
}

void loop() {
  // Leer el estado actual de los botones (activo en BAJO por el pull-up)
  bool botonIzquierdoPresionado = digitalRead(BOTON_IZQUIERDO_PIN) == LOW;
  bool botonDerechoPresionado = digitalRead(BOTON_DERECHO_PIN) == LOW;
  
  // Detectar cambios en los botones para depuración
  if (botonIzquierdoPresionado != ultimoEstadoBotonIzq) {
    Serial.print("[DEBUG] Botón IZQUIERDO: ");
    Serial.print(botonIzquierdoPresionado ? "PRESIONADO" : "LIBERADO");
    Serial.print(" | Posición pelota: ");
    Serial.print(posicionPelota);
    Serial.print(" | LED actual: ");
    if (posicionPelota == 0) Serial.println("ROJO IZQ");
    else if (posicionPelota == 1) Serial.println("VERDE IZQ");
    else if (posicionPelota == 2) Serial.println("AZUL IZQ");
    else Serial.println(posicionPelota);
    
    ultimoEstadoBotonIzq = botonIzquierdoPresionado;
  }
  
  if (botonDerechoPresionado != ultimoEstadoBotonDer) {
    Serial.print("[DEBUG] Botón DERECHO: ");
    Serial.print(botonDerechoPresionado ? "PRESIONADO" : "LIBERADO");
    Serial.print(" | Posición pelota: ");
    Serial.print(posicionPelota);
    Serial.print(" | LED actual: ");
    if (posicionPelota == 12) Serial.println("AZUL DER");
    else if (posicionPelota == 13) Serial.println("VERDE DER");
    else if (posicionPelota == 14) Serial.println("ROJO DER");
    else Serial.println(posicionPelota);
    
    ultimoEstadoBotonDer = botonDerechoPresionado;
  }
  
  // Log periódico del estado del juego
  unsigned long tiempoActual = millis();
  if (tiempoActual - ultimoTiempoDebug >= INTERVALO_DEBUG) {
    ultimoTiempoDebug = tiempoActual;
    Serial.print("Posición: ");
    Serial.print(posicionPelota);
    Serial.print(" | Dirección: ");
    Serial.print(haciaDerecha ? "DERECHA" : "IZQUIERDA");
    Serial.print(" | Velocidad: ");
    Serial.println(velocidadJuego);
  }
  
  // Si el juego ha terminado, esperar a que se presione cualquier botón para reiniciar
  if (juegoTerminado) {
    if (botonIzquierdoPresionado || botonDerechoPresionado) {
      Serial.println("[DEBUG] Reiniciando juego por presión de botón...");
      delay(500); // Evitar rebotes
      reiniciarJuego();
    }
    return;
  }

  // ZONA DE REBOTE IZQUIERDA
  if (!haciaDerecha && (posicionPelota == 2)) {  // LED AZUL IZQ
    Serial.print("[REBOTE_IZQ] En azul izquierdo, botón: ");
    Serial.println(botonIzquierdoPresionado ? "PRESIONADO" : "NO PRESIONADO");
    
    if (botonIzquierdoPresionado) {
      // Rebote exitoso
      haciaDerecha = true;
      velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);
      Serial.println("¡REBOTE EXITOSO en LED azul izquierdo!");
    } else {
      // Sin rebote, el juego termina
      posicionPelota = 0;
      juegoTerminado = true;
      apagarTodosLEDs();
      digitalWrite(LED_PINS[0], HIGH);
      Serial.println("¡JUEGO TERMINADO! El jugador izquierdo no rebotó a tiempo.");
      return;
    }
  }
  else if (!haciaDerecha && (posicionPelota == 1) && botonIzquierdoPresionado) {  // LED VERDE junto al AZUL
    // Rebote en LED verde izquierdo
    haciaDerecha = true;
    velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);
    Serial.println("¡REBOTE EXITOSO en LED verde izquierdo!");
  }
  
  // ZONA DE REBOTE DERECHA
  else if (haciaDerecha && (posicionPelota == 12)) {  // LED AZUL DER
    Serial.print("[REBOTE_DER] En azul derecho, botón: ");
    Serial.println(botonDerechoPresionado ? "PRESIONADO" : "NO PRESIONADO");
    
    if (botonDerechoPresionado) {
      // Rebote exitoso
      haciaDerecha = false;
      velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);
      Serial.println("¡REBOTE EXITOSO en LED azul derecho!");
    } else {
      // Sin rebote, el juego termina
      posicionPelota = 14;
      juegoTerminado = true;
      apagarTodosLEDs();
      digitalWrite(LED_PINS[14], HIGH);
      Serial.println("¡JUEGO TERMINADO! El jugador derecho no rebotó a tiempo.");
      return;
    }
  }
  else if (haciaDerecha && (posicionPelota == 13) && botonDerechoPresionado) {  // LED VERDE junto al AZUL
    // Rebote en LED verde derecho
    haciaDerecha = false;
    velocidadJuego = max(velocidadJuego - INCREMENTO_VELOCIDAD, 50);
    Serial.println("¡REBOTE EXITOSO en LED verde derecho!");
  }

  // Mover la pelota en la dirección actual
  if (haciaDerecha) {
    posicionPelota++;
  } else {
    posicionPelota--;
  }

  // Verificar si llegamos a un LED rojo (extremo)
  if (posicionPelota == 0 || posicionPelota == 14) {
    juegoTerminado = true;
    apagarTodosLEDs();
    digitalWrite(LED_PINS[posicionPelota], HIGH);
    Serial.println("¡JUEGO TERMINADO! La pelota llegó a un extremo sin rebote.");
    return;
  }

  // Actualizar la visualización de los LEDs
  actualizarPosicionPelota();

  // Esperar según la velocidad actual del juego
  delay(velocidadJuego);
}

/**
 * Actualiza los LEDs para mostrar la posición actual de la pelota
 */
void actualizarPosicionPelota() {
  apagarTodosLEDs();
  digitalWrite(LED_PINS[posicionPelota], HIGH);
  
  // Debug: mostrar qué LED está encendido
  if (posicionPelota == 0) 
    Serial.println("[LED] Encendido ROJO IZQ");
  else if (posicionPelota == 2) 
    Serial.println("[LED] Encendido AZUL IZQ");
  else if (posicionPelota == 12) 
    Serial.println("[LED] Encendido AZUL DER");
  else if (posicionPelota == 14) 
    Serial.println("[LED] Encendido ROJO DER");
}

/**
 * Apaga todos los LEDs
 */
void apagarTodosLEDs() {
  for (byte i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }
}

/**
 * Reinicia el juego a sus valores iniciales
 */
void reiniciarJuego() {
  posicionPelota = POSICION_INICIAL;
  velocidadJuego = VELOCIDAD_INICIAL;
  haciaDerecha = random(2) == 0; // Dirección aleatoria al inicio
  juegoTerminado = false;
  
  // Secuencia de inicio - muestra todos los LEDs brevemente
  for (byte i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
  }
  delay(500);
  
  apagarTodosLEDs();
  actualizarPosicionPelota();
  Serial.println("=== ¡JUEGO INICIADO! ===");
  Serial.print("Dirección inicial: ");
  Serial.println(haciaDerecha ? "DERECHA" : "IZQUIERDA");
}
