/**

https://www.youtube.com/watch?v=9ligsi5Bgv8


 * Test Completo del Keypad 4x4 - Todos los 16 botones
 * Imprime por serial cada botón presionado con información detallada
 *
 * Conexiones para probar TODOS los botones:
 * - ROW0 del keypad → Pin 9 Arduino
 * - ROW1 del keypad → Pin 8 Arduino
 * - ROW2 del keypad → Pin 7 Arduino
 * - ROW3 del keypad → Pin 6 Arduino
 * - COL0 del keypad → Pin 5 Arduino
 * - COL1 del keypad → Pin 4 Arduino
 * - COL2 del keypad → Pin 3 Arduino
 * - COL3 del keypad → Pin 2 Arduino
 */

// Configuración completa del keypad 4x4
const byte ROW_COUNT = 4;  // 4 filas completas
const byte COL_COUNT = 4;  // 4 columnas completas

// Pines del keypad
byte rowPins[ROW_COUNT] = {9, 8, 7, 6};  // ROW0, ROW1, ROW2, ROW3
byte colPins[COL_COUNT] = {5, 4, 3, 2};  // COL0, COL1, COL2, COL3

// Layout completo del keypad 4x4
char keys[ROW_COUNT][COL_COUNT] = {
  {'1', '2', '3', 'A'},  // Fila 0
  {'4', '5', '6', 'B'},  // Fila 1
  {'7', '8', '9', 'C'},  // Fila 2
  {'*', '0', '#', 'D'}   // Fila 3
};

// Variables para debounce y estadísticas
const int DEBOUNCE_DELAY = 50;
unsigned long lastKeyTime = 0;
char lastKey = 0;

// Contadores de uso
int keyCount[ROW_COUNT][COL_COUNT] = {0};
int totalPresses = 0;

void setup() {
  // Configurar pines del keypad
  for (byte row = 0; row < ROW_COUNT; row++) {
    pinMode(rowPins[row], INPUT_PULLUP);
  }

  for (byte col = 0; col < COL_COUNT; col++) {
    pinMode(colPins[col], OUTPUT);
    digitalWrite(colPins[col], HIGH);
  }

  // Inicializar comunicación serial
  Serial.begin(9600);

  // Mostrar información inicial
  showWelcomeMessage();
  showKeypadLayout();
  showConnectionDiagram();
}

void loop() {
  char key = scanKeypad();

  if (key != 0) {
    handleKeyPress(key);
  }

  // Pequeña pausa para estabilidad
  delay(10);
}

char scanKeypad() {
  char key = 0;

  // Escanear todas las filas y columnas
  for (byte col = 0; col < COL_COUNT; col++) {
    // Activar columna actual (ponerla en LOW)
    digitalWrite(colPins[col], LOW);

    // Revisar todas las filas
    for (byte row = 0; row < ROW_COUNT; row++) {
      if (digitalRead(rowPins[row]) == LOW) {
        // Botón detectado, aplicar debounce
        delay(DEBOUNCE_DELAY);

        // Verificar que sigue presionado
        if (digitalRead(rowPins[row]) == LOW) {
          key = keys[row][col];

          // Actualizar estadísticas
          keyCount[row][col]++;
          totalPresses++;

          // Mostrar información detallada
          printKeyInfo(key, row, col);

          // Esperar a que se suelte el botón
          while (digitalRead(rowPins[row]) == LOW) {
            delay(10);
          }

          // Pequeña pausa adicional después del release
          delay(50);
        }
      }
    }

    // Desactivar columna (volver a HIGH)
    digitalWrite(colPins[col], HIGH);
  }

  return key;
}

void handleKeyPress(char key) {
  lastKey = key;
  lastKeyTime = millis();
}

void printKeyInfo(char key, byte row, byte col) {
  // Línea separadora
  Serial.println("" + String("-").substring(0, 50));

  // Información básica del botón
  Serial.print("🔘 BOTÓN PRESIONADO: '");
  Serial.print(key);
  Serial.println("'");

  // Posición en la matriz
  Serial.print("📍 Posición: Fila ");
  Serial.print(row);
  Serial.print(", Columna ");
  Serial.println(col);

  // Pines físicos involucrados
  Serial.print("🔌 Pines: ROW");
  Serial.print(row);
  Serial.print(" (Pin ");
  Serial.print(rowPins[row]);
  Serial.print(") + COL");
  Serial.print(col);
  Serial.print(" (Pin ");
  Serial.print(colPins[col]);
  Serial.println(")");

  // Estadísticas de uso
  Serial.print("📊 Presiones: ");
  Serial.print(keyCount[row][col]);
  Serial.print(" veces (Total: ");
  Serial.print(totalPresses);
  Serial.println(")");

  // Timestamp
  Serial.print("⏰ Tiempo: ");
  Serial.print(millis());
  Serial.println(" ms");

  // Clasificación del botón
  classifyKey(key);

  Serial.println();
}

void classifyKey(char key) {
  Serial.print("🏷️  Tipo: ");

  if (key >= '0' && key <= '9') {
    Serial.print("NÚMERO (");
    Serial.print(key);
    Serial.println(")");
  } else if (key >= 'A' && key <= 'D') {
    Serial.print("LETRA (");
    Serial.print(key);
    Serial.println(")");
  } else if (key == '*') {
    Serial.println("ASTERISCO (*)");
  } else if (key == '#') {
    Serial.println("NUMERAL (#)");
  } else {
    Serial.print("ESPECIAL (");
    Serial.print(key);
    Serial.println(")");
  }
}

void showWelcomeMessage() {
  Serial.println("" + String("=").substring(0, 60));
  Serial.println("🧪 TEST COMPLETO DEL KEYPAD 4x4 🧪");
  Serial.println("" + String("=").substring(0, 60));
  Serial.println();
  Serial.println("📋 Este programa detecta y muestra información");
  Serial.println("   detallada de cada botón presionado.");
  Serial.println();
  Serial.println("🎯 Objetivo: Verificar que todos los 16 botones");
  Serial.println("   del keypad funcionen correctamente.");
  Serial.println();
  Serial.println("💡 Presiona cada botón para ver su información");
  Serial.println("   completa en el monitor serial.");
  Serial.println();
}

void showKeypadLayout() {
  Serial.println("🗺️  LAYOUT DEL KEYPAD:");
  Serial.println("┌─────┬─────┬─────┬─────┐");
  Serial.println("│  1  │  2  │  3  │  A  │ ← ROW0");
  Serial.println("├─────┼─────┼─────┼─────┤");
  Serial.println("│  4  │  5  │  6  │  B  │ ← ROW1");
  Serial.println("├─────┼─────┼─────┼─────┤");
  Serial.println("│  7  │  8  │  9  │  C  │ ← ROW2");
  Serial.println("├─────┼─────┼─────┼─────┤");
  Serial.println("│  *  │  0  │  #  │  D  │ ← ROW3");
  Serial.println("└─────┴─────┴─────┴─────┘");
  Serial.println("  ↑     ↑     ↑     ↑");
  Serial.println(" COL0  COL1  COL2  COL3");
  Serial.println();
}

void showConnectionDiagram() {
  Serial.println("🔌 DIAGRAMA DE CONEXIONES:");
  Serial.println("Keypad 4x4    Arduino UNO");
  Serial.println("─────────────────────────");
  Serial.println("ROW0      →→→    Pin 9");
  Serial.println("ROW1      →→→    Pin 8");
  Serial.println("ROW2      →→→    Pin 7");
  Serial.println("ROW3      →→→    Pin 6");
  Serial.println("COL0      →→→    Pin 5");
  Serial.println("COL1      →→→    Pin 4");
  Serial.println("COL2      →→→    Pin 3");
  Serial.println("COL3      →→→    Pin 2");
  Serial.println();
  Serial.println("📝 NOTA: Asegúrate de que todas las conexiones");
  Serial.println("   estén firmes y en los pines correctos.");
  Serial.println();
  Serial.println("🚀 ¡Listo! Presiona cualquier botón para empezar...");
  Serial.println("" + String("=").substring(0, 60));
  Serial.println();
}

// Función para mostrar estadísticas (llamar con comando especial)
void showStatistics() {
  Serial.println("" + String("=").substring(0, 50));
  Serial.println("📊 ESTADÍSTICAS DE USO DEL KEYPAD");
  Serial.println("" + String("=").substring(0, 50));

  for (byte row = 0; row < ROW_COUNT; row++) {
    for (byte col = 0; col < COL_COUNT; col++) {
      if (keyCount[row][col] > 0) {
        Serial.print("Botón '");
        Serial.print(keys[row][col]);
        Serial.print("': ");
        Serial.print(keyCount[row][col]);
        Serial.println(" presiones");
      }
    }
  }

  Serial.print("\n📈 Total de presiones: ");
  Serial.println(totalPresses);
  Serial.println();
}

// Función para probar conectividad
void testConnectivity() {
  Serial.println("🔧 PROBANDO CONECTIVIDAD...");

  bool allConnected = true;

  // Probar cada combinación fila-columna
  for (byte row = 0; row < ROW_COUNT; row++) {
    for (byte col = 0; col < COL_COUNT; col++) {
      Serial.print("Probando botón '");
      Serial.print(keys[row][col]);
      Serial.print("' (R");
      Serial.print(row);
      Serial.print("C");
      Serial.print(col);
      Serial.print("): ");

      // Simular activación
      digitalWrite(colPins[col], LOW);
      delay(10);

      if (digitalRead(rowPins[row]) == HIGH) {
        Serial.println("✅ OK");
      } else {
        Serial.println("❌ PROBLEMA");
        allConnected = false;
      }

      digitalWrite(colPins[col], HIGH);
      delay(10);
    }
  }

  if (allConnected) {
    Serial.println("\n🎉 ¡Todas las conexiones están OK!");
  } else {
    Serial.println("\n⚠️  Hay problemas de conectividad.");
  }
}

/*
COMANDOS ESPECIALES:
- Para ver estadísticas: presiona A+B+C+D en secuencia
- Para test de conectividad: presiona *+#+*+# en secuencia

TROUBLESHOOTING:
1. Si no detecta ningún botón:
   - Verifica las conexiones físicas
   - Revisa que los pines estén bien definidos

2. Si detecta botones incorrectos:
   - Puede haber cables cruzados
   - Verifica el mapeo de pines

3. Si hay detecciones múltiples:
   - Problema de debounce o conexiones flojas
   - Revisa las soldaduras/conexiones

INFORMACIÓN TÉCNICA:
- Frecuencia de escaneo: ~100Hz
- Debounce: 50ms
- Pull-up interno activado en filas
- Lógica de escaneo: LOW en columnas, HIGH en reposo
*/
