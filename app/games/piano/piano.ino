// CÓDIGO ARDUINO - Subir al Arduino
// Piano digital con comunicación serial

// Configuración de pines
const int BOTONES[] = {2, 3, 4, 5, 6, 7, 8, 9};  // Pines de los botones
const int NUM_BOTONES = 8;                         // Número total de botones

// Variables para control de botones
bool estadoAnterior[NUM_BOTONES] = {false};        // Estado previo de cada botón
bool estadoActual[NUM_BOTONES] = {false};          // Estado actual de cada botón

void setup() {
    // Configurar pines de botones como entrada con pull-up interno
    for (int i = 0; i < NUM_BOTONES; i++) {
        pinMode(BOTONES[i], INPUT_PULLUP);
    }

    // Inicializar comunicación serie
    Serial.begin(9600);

    // Mensaje de inicio
    Serial.println("PIANO_READY");

    // Pequeña pausa para estabilización
    delay(100);
}

void loop() {
    // Leer el estado actual de todos los botones
    leerBotones();

    // Procesar cada botón
    for (int i = 0; i < NUM_BOTONES; i++) {
        // Detectar flanco de bajada (botón presionado)
        if (!estadoActual[i] && estadoAnterior[i]) {
            enviarNota(i);
        }

        // Actualizar estado anterior
        estadoAnterior[i] = estadoActual[i];
    }

    // Pequeña pausa para estabilidad
    delay(10);
}

// Función para leer el estado de todos los botones
void leerBotones() {
    for (int i = 0; i < NUM_BOTONES; i++) {
        estadoActual[i] = digitalRead(BOTONES[i]);
    }
}

// Función para enviar nota por serial
void enviarNota(int indiceBoton) {
    if (indiceBoton >= 0 && indiceBoton < NUM_BOTONES) {
        // Enviar comando por serial: NOTA:indice
        Serial.print("NOTA:");
        Serial.println(indiceBoton);
    }
}

/*
PROTOCOLO DE COMUNICACIÓN SERIAL:
- "PIANO_READY" -> Arduino listo
- "NOTA:0" hasta "NOTA:7" -> Botón presionado (0=Do, 1=Re, etc.)

CONEXIONES:
- Botones entre pines 2-9 y GND
- No necesitas resistencias (usa INPUT_PULLUP)
- Cable USB para comunicación serial
*/

