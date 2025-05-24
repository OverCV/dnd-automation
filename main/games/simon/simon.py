"""
Simon Game Arduino + Python
Visualizador y controlador del juego Simon con keypad 4x4
"""

import serial
import pygame
import time
import threading
from typing import Optional, List, Tuple
import serial.tools.list_ports
import random

class SimonArduinoGame:
    """Juego Simon con Arduino y visualización Python"""

    # Constantes de visualización
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    LED_SIZE = 80

    # Colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 100, 100)
    GREEN = (100, 255, 100)
    BLUE = (100, 100, 255)
    YELLOW = (255, 255, 100)
    PURPLE = (255, 100, 255)
    ORANGE = (255, 165, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)

    # Colores de LEDs
    LED_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
    LED_COLORS_DIM = [(r//3, g//3, b//3) for r, g, b in LED_COLORS]

    def __init__(self):
        """Inicializar el juego"""
        pygame.init()

        # Configurar ventana
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Simon Game - Arduino + Python")

        # Fuentes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Estado del juego
        self.arduino: Optional[serial.Serial] = None
        self.arduino_connected = False
        self.running = True

        # Variables del juego (recibidas desde Arduino)
        self.player_level = 1
        self.input_count = 0
        self.game_state = 0  # 0=WAITING, 1=SHOWING, 2=INPUT, 3=OVER, 4=WON
        self.game_sequence = []
        self.led_states = [False] * 6
        self.last_key_pressed = ""
        self.game_message = "Conectando con Arduino..."

        # Posiciones de LEDs (disposición 2x3)
        self.led_positions = [
            (200, 200),  # LED 1 (botón 1)
            (200, 300),  # LED 2 (botón 4)
            (200, 400),  # LED 3 (botón 7)
            (500, 200),  # LED 4 (botón 3)
            (500, 300),  # LED 5 (botón 6)
            (500, 400),  # LED 6 (botón 9)
        ]

        # Mapeo de botones a LEDs
        self.button_names = ['1', '4', '7', '3', '6', '9']

        # Control de tiempo
        self.clock = pygame.time.Clock()
        self.last_update = time.time()

        # Estadísticas
        self.total_games = 0
        self.best_level = 0

    def find_arduino(self) -> Optional[str]:
        """Buscar puerto del Arduino"""
        print("🔍 Buscando Arduino...")

        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                print(f"✅ Arduino encontrado: {port.device}")
                return port.device

        print("⚠️  Arduino no encontrado automáticamente")
        return None

    def connect_arduino(self, port: Optional[str] = None) -> bool:
        """Conectar con Arduino"""
        try:
            if not port:
                port = self.find_arduino()

            if not port:
                # Mostrar puertos disponibles
                ports = serial.tools.list_ports.comports()
                print("Puertos disponibles:")
                for i, p in enumerate(ports):
                    print(f"  {i}: {p.device} - {p.description}")

                print("📝 Ingresa el puerto manualmente:")
                port = input("Puerto: ").strip()

            print(f"🔌 Conectando a {port}...")
            self.arduino = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Esperar reset de Arduino

            if self.arduino.is_open:
                self.arduino_connected = True
                self.game_message = "Arduino conectado - Iniciando..."
                print("✅ Conexión establecida")
                return True
            else:
                print("❌ No se pudo abrir puerto")
                return False

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            self.game_message = f"Error: {str(e)}"
            return False

    def read_arduino(self):
        """Leer datos de Arduino en hilo separado"""
        while self.running and self.arduino and self.arduino.is_open:
            try:
                if self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8').strip()
                    self.process_arduino_message(line)

            except Exception as e:
                print(f"❌ Error leyendo Arduino: {e}")
                time.sleep(0.1)

    def process_arduino_message(self, message: str):
        """Procesar mensaje del Arduino"""
        try:
            if message == "SIMON_READY":
                self.game_message = "Arduino listo - Presiona cualquier botón"
                print("🎮 Simon Arduino listo")

            elif message.startswith("STATE:"):
                # Parsear: "STATE:level,input,gameState,SEQ:1-2-3..."
                parts = message[6:].split(",")
                if len(parts) >= 3:
                    self.player_level = int(parts[0])
                    self.input_count = int(parts[1])
                    self.game_state = int(parts[2])

                    # Parsear secuencia si existe
                    for part in parts:
                        if part.startswith("SEQ:"):
                            seq_str = part[4:]
                            if seq_str and seq_str != "":
                                self.game_sequence = [int(x) for x in seq_str.split("-")]
                            else:
                                self.game_sequence = []

            elif message.startswith("KEY_PRESS:"):
                # Parsear: "KEY_PRESS:key,ledNumber"
                parts = message[10:].split(",")
                if len(parts) >= 2:
                    key = parts[0]
                    led_num = int(parts[1])
                    self.last_key_pressed = f"Botón {key} → LED{led_num}"
                    print(f"🔘 {self.last_key_pressed}")

            elif message.startswith("LED_ON:"):
                led_num = int(message[7:]) - 1
                if 0 <= led_num < 6:
                    self.led_states[led_num] = True

            elif message.startswith("LED_OFF:"):
                led_num = int(message[8:]) - 1
                if 0 <= led_num < 6:
                    self.led_states[led_num] = False

            elif message == "GAME_START":
                self.game_message = "¡Juego iniciado!"

            elif message == "SEQUENCE_START":
                self.game_message = f"Nivel {self.player_level} - Observa la secuencia"

            elif message == "SEQUENCE_END":
                self.game_message = "Tu turno - Repite la secuencia"

            elif message.startswith("CORRECT:"):
                progress = message[8:]
                self.game_message = f"¡Correcto! {progress}"

            elif message.startswith("WRONG:"):
                parts = message[6:].split(",")
                expected = parts[0]
                received = parts[1]
                self.game_message = f"Error: esperaba LED{expected}, presionaste LED{received}"

            elif message == "LEVEL_COMPLETE":
                self.game_message = f"¡Nivel {self.player_level} completado!"

            elif message.startswith("NEXT_LEVEL:"):
                new_level = int(message[11:])
                self.game_message = f"¡Avanzando al nivel {new_level}!"

            elif message == "GAME_OVER":
                self.game_message = f"Game Over - Nivel alcanzado: {self.player_level}"
                self.total_games += 1
                if self.player_level > self.best_level:
                    self.best_level = self.player_level

            elif message == "GAME_WON":
                self.game_message = "¡FELICITACIONES! ¡Ganaste todos los niveles!"
                self.total_games += 1
                self.best_level = 20

            elif message == "GAME_RESTART":
                self.game_message = "Juego reiniciado"

            elif message == "STARTUP_COMPLETE":
                self.game_message = "Sistema listo - Presiona cualquier botón para empezar"

            self.last_update = time.time()

        except (ValueError, IndexError) as e:
            print(f"❌ Error parseando mensaje: {message} - {e}")

    def send_command(self, command: str):
        """Enviar comando al Arduino"""
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(f"{command}\n".encode())
                print(f"📤 Enviado: {command}")
            except Exception as e:
                print(f"❌ Error enviando comando: {e}")

    def handle_events(self):
        """Manejar eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.send_command("RESTART")
                elif event.key == pygame.K_p:
                    self.send_command("PAUSE")
                elif event.key == pygame.K_s:
                    self.send_command("GET_STATE")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Detectar clicks en LEDs para demo
                mouse_pos = pygame.mouse.get_pos()
                for i, (x, y) in enumerate(self.led_positions):
                    if ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) < (self.LED_SIZE // 2) ** 2:
                        print(f"🖱️ Click en LED{i+1} (botón {self.button_names[i]})")

    def draw_led(self, surface, position: Tuple[int, int], color: Tuple[int, int, int],
                 is_on: bool, label: str):
        """Dibujar un LED"""
        x, y = position

        # Color del LED según estado
        led_color = color if is_on else tuple(c//4 for c in color)

        # Círculo principal
        pygame.draw.circle(surface, led_color, (x, y), self.LED_SIZE // 2)

        # Borde
        border_color = self.WHITE if is_on else self.GRAY
        pygame.draw.circle(surface, border_color, (x, y), self.LED_SIZE // 2, 3)

        # Efecto de brillo si está encendido
        if is_on:
            glow_color = tuple(min(255, c + 100) for c in color)
            pygame.draw.circle(surface, glow_color, (x, y), self.LED_SIZE // 3)

        # Etiqueta del botón
        label_surface = self.font_medium.render(label, True, self.WHITE)
        label_rect = label_surface.get_rect(center=(x, y + self.LED_SIZE // 2 + 20))
        surface.blit(label_surface, label_rect)

    def draw_game_state(self):
        """Dibujar estado del juego"""
        self.screen.fill(self.BLACK)

        # Título
        title_surface = self.font_large.render("SIMON GAME - Arduino + Python", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)

        # Estado de conexión
        connection_color = self.GREEN if self.arduino_connected else self.RED
        connection_text = "CONECTADO" if self.arduino_connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (20, 20))

        # Dibujar LEDs en disposición 2x3
        for i in range(6):
            self.draw_led(
                self.screen,
                self.led_positions[i],
                self.LED_COLORS[i],
                self.led_states[i],
                f"Botón {self.button_names[i]}"
            )

        # Información del juego
        info_y = 520

        # Nivel actual
        level_surface = self.font_medium.render(f"Nivel: {self.player_level}/20", True, self.WHITE)
        self.screen.blit(level_surface, (50, info_y))

        # Progreso en nivel actual
        if self.game_state == 2:  # PLAYER_INPUT
            progress = f"Progreso: {self.input_count}/{self.player_level}"
            progress_surface = self.font_medium.render(progress, True, self.YELLOW)
            self.screen.blit(progress_surface, (200, info_y))

        # Secuencia actual (si está visible)
        if self.game_sequence and len(self.game_sequence) > 0:
            seq_text = "Secuencia: " + "-".join(map(str, self.game_sequence[:self.player_level]))
            if len(seq_text) > 50:
                seq_text = seq_text[:50] + "..."
            seq_surface = self.font_small.render(seq_text, True, self.WHITE)
            self.screen.blit(seq_surface, (400, info_y))

        # Estadísticas
        stats_y = info_y + 30
        stats_surface = self.font_small.render(f"Partidas: {self.total_games} | Mejor nivel: {self.best_level}", True, self.WHITE)
        self.screen.blit(stats_surface, (50, stats_y))

        # Última tecla presionada
        if self.last_key_pressed:
            key_surface = self.font_small.render(f"Última tecla: {self.last_key_pressed}", True, self.GREEN)
            self.screen.blit(key_surface, (400, stats_y))

        # Mensaje del juego
        message_surface = self.font_medium.render(self.game_message, True, self.YELLOW)
        message_rect = message_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 120))
        self.screen.blit(message_surface, message_rect)

        # Controles
        controls = [
            "Controles PC: R=Restart | P=Pause | S=Estado | ESC=Salir",
            "Usa los botones físicos del Arduino para jugar"
        ]

        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, self.GRAY)
            self.screen.blit(control_surface, (20, self.WINDOW_HEIGHT - 40 + i * 20))

        # Indicador de tiempo desde última actualización
        time_since_update = time.time() - self.last_update
        if time_since_update > 3.0:
            warning_surface = self.font_small.render("⚠️ Sin datos del Arduino", True, self.RED)
            self.screen.blit(warning_surface, (self.WINDOW_WIDTH - 200, 20))

    def run(self):
        """Ejecutar el juego"""
        print("🎮 Simon Game Arduino + Python")
        print("Conectando con Arduino...")

        if not self.connect_arduino():
            print("❌ No se pudo conectar.")
            self.game_message = "Error de conexión - Verifica Arduino"
            self.arduino_connected = False
        else:
            # Iniciar hilo de lectura
            read_thread = threading.Thread(target=self.read_arduino)
            read_thread.daemon = True
            read_thread.start()

        print("🎮 Visualizador iniciado")
        print("Controles: R=Restart, P=Pause, S=Estado, ESC=Salir")

        while self.running:
            self.handle_events()
            self.draw_game_state()
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        pygame.quit()
        print("👋 Juego cerrado")


def main():
    """Función principal"""
    try:
        game = SimonArduinoGame()
        game.run()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    try:
        import serial
        import pygame
        main()
    except ImportError as e:
        print("❌ Instala dependencias:")
        print("   pip install pyserial pygame")
        print(f"   Error: {e}")

# INSTRUCCIONES DE USO:
# 1. Conecta el keypad 4x4 al Arduino según el diagrama
# 2. Conecta 6 LEDs a los pines 8-13 con resistores
# 3. Sube el código Arduino al microcontrolador
# 4. Instala dependencias: pip install pyserial pygame
# 5. Ejecuta este script Python
# 6. ¡Juega con los botones del keypad!

"""
=== CARACTERÍSTICAS DEL JUEGO PYTHON ===

🎮 VISUALIZACIÓN MEJORADA:
- LEDs virtuales en pantalla que sincronizan con hardware
- Disposición visual 2x3 (izquierda: 1,4,7 | derecha: 3,6,9)
- Colores diferentes para cada LED
- Efectos de brillo cuando están activos
- Información en tiempo real del estado del juego

📊 INFORMACIÓN EN PANTALLA:
- Nivel actual (1-20)
- Progreso en el nivel
- Secuencia a seguir
- Estadísticas (partidas jugadas, mejor nivel)
- Última tecla presionada
- Estado de conexión Arduino

🎯 CARACTERÍSTICAS DEL JUEGO:
- 20 niveles de dificultad progresiva
- Velocidad aumenta con cada nivel
- Feedback visual y auditivo sincronizado
- Detección de errores en tiempo real
- Animaciones de victoria y game over

🔌 COMUNICACIÓN SERIAL:
- Protocolo robusto Arduino ↔ Python
- Estado del juego en tiempo real
- Comandos de control desde PC
- Detección automática de puerto Arduino

🎮 CONTROLES:
- Botones físicos del Arduino para jugar
- Controles PC para gestión (R, P, S, ESC)
- Click en LEDs virtuales para demo

🚀 VENTAJAS SOBRE VERSIÓN SOLO ARDUINO:
- Visualización ampliada y colorida
- Estadísticas persistentes
- Interface más rica
- Debugging visual
- Experiencia híbrida hardware/software

=== LAYOUT DEL KEYPAD (RECORDATORIO) ===

Keypad físico 4x4:
[1] [2] [3] [A]
[4] [5] [6] [B]
[7] [8] [9] [C]
[*] [0] [#] [D]

Botones CONECTADOS:
[●] [ ] [●] [ ]  ← ROW0 (Pin 7)
[●] [ ] [●] [ ]  ← ROW1 (Pin 6)
[●] [ ] [●] [ ]  ← ROW2 (Pin 5)
[ ] [ ] [ ] [ ]  ← ROW3 sin conectar
 ↑       ↑
COL0    COL2
Pin4    Pin3

=== DISPOSICIÓN VISUAL PYTHON ===

Pantalla del juego:
    LED1(1)         LED4(3)
    [ROJO]         [AMARILLO]

    LED2(4)         LED5(6)
    [VERDE]        [PÚRPURA]

    LED3(7)         LED6(9)
    [AZUL]         [NARANJA]

Columna izq: 1,4,7  |  Columna der: 3,6,9

=== TROUBLESHOOTING ===

🔧 Si no conecta con Arduino:
- Verifica puerto serial correcto
- Asegúrate que Arduino esté programado
- Revisa cable USB
- Cierra otros programas que usen serial

🔧 Si los LEDs no responden:
- Verifica conexiones físicas
- Revisa resistores en LEDs
- Confirma pines correctos en código

🔧 Si botones no funcionan:
- Verifica conexiones keypad
- Usa código de test previo
- Revisa que COL1 esté desconectada

🔧 Si hay lag en comunicación:
- Reduce SERIAL_INTERVAL en Arduino
- Verifica velocidad 9600 baud
- Cierra otros programas pesados
"""
