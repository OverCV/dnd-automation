"""
Ping Pong Arduino + Python
Lee el estado del juego desde Arduino y muestra visualización mejorada
"""

import serial
import pygame
import time
import threading
from typing import Tuple, Optional
import serial.tools.list_ports

class PingPongArduinoVisualizer:
    """Visualizador del juego de Ping Pong desde Arduino"""

    # Constantes
    LCD_WIDTH = 16
    LCD_HEIGHT = 2
    CHAR_SIZE = 40

    # Colores
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 100, 255)
    RED = (255, 100, 100)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)

    def __init__(self):
        """Inicializar visualizador"""
        pygame.init()

        # Configurar ventana
        self.screen_width = self.LCD_WIDTH * self.CHAR_SIZE
        self.screen_height = self.LCD_HEIGHT * self.CHAR_SIZE + 150
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Ping Pong Arduino Visualizer")

        # Fuentes
        self.font_large = pygame.font.Font(None, self.CHAR_SIZE)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Estado del juego (recibido desde Arduino)
        self.ball_x = 8
        self.ball_y = 0
        self.left_paddle_active = False
        self.right_paddle_active = False
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.game_over_message = ""
        self.arduino_connected = False

        # Serial
        self.arduino: Optional[serial.Serial] = None
        self.running = True

        # Control de tiempo
        self.clock = pygame.time.Clock()
        self.last_update = time.time()

    def find_arduino(self) -> Optional[str]:
        """Buscar puerto del Arduino"""
        print("🔍 Buscando Arduino...")

        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'CH340' in port.description:
                print(f"✅ Arduino encontrado: {port.device}")
                return port.device

        print("⚠️  Arduino no encontrado automáticamente")
        print("Puertos disponibles:")
        for i, port in enumerate(ports):
            print(f"  {i}: {port.device} - {port.description}")

        return None

    def connect_arduino(self, port: Optional[str] = None) -> bool:
        """Conectar con Arduino"""
        try:
            if not port:
                port = self.find_arduino()

            if not port:
                print("📝 Ingresa el puerto manualmente:")
                port = input("Puerto: ").strip()

            print(f"🔌 Conectando a {port}...")
            self.arduino = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Esperar reset de Arduino

            if self.arduino.is_open:
                self.arduino_connected = True
                print("✅ Conexión establecida")
                return True
            else:
                print("❌ No se pudo abrir puerto")
                return False

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
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
        if message == "PONG_READY":
            print("🎮 Arduino Ping Pong listo")

        elif message.startswith("STATE:"):
            # Parsear estado: "STATE:x,y,leftPaddle,rightPaddle,score,gameOver,paused"
            try:
                parts = message[6:].split(',')
                self.ball_x = int(parts[0])
                self.ball_y = int(parts[1])
                self.left_paddle_active = bool(int(parts[2]))
                self.right_paddle_active = bool(int(parts[3]))
                self.score = int(parts[4])
                self.game_over = bool(int(parts[5]))
                self.game_paused = bool(int(parts[6]))
                self.last_update = time.time()
            except (ValueError, IndexError) as e:
                print(f"❌ Error parseando estado: {e}")

        elif message.startswith("BUTTONS:"):
            # Actualizar solo botones
            try:
                parts = message[8:].split(',')
                self.left_paddle_active = bool(int(parts[0]))
                self.right_paddle_active = bool(int(parts[1]))
            except (ValueError, IndexError):
                pass

        elif message.startswith("GAME_OVER:"):
            self.game_over_message = message[10:]
            print(f"💀 Game Over: {self.game_over_message}")

        elif message == "PADDLE_HIT_LEFT":
            print("🏓 ¡Pala izquierda!")

        elif message == "PADDLE_HIT_RIGHT":
            print("🏓 ¡Pala derecha!")

        elif message == "BOUNCE_VERTICAL":
            print("⬆️⬇️ Rebote vertical")

        elif message in ["GAME_START", "GAME_PAUSE", "GAME_RESUME", "GAME_RESTART"]:
            print(f"🎮 {message.replace('_', ' ').title()}")

    def send_command(self, command: str):
        """Enviar comando al Arduino"""
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(f"{command}\n".encode())
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
                    print("🔄 Enviando comando RESTART")
                elif event.key == pygame.K_p:
                    self.send_command("PAUSE")
                    print("⏸️ Enviando comando PAUSE")
                elif event.key == pygame.K_s:
                    self.send_command("GET_STATE")
                    print("📊 Solicitando estado")

    def draw_char_at(self, char: str, x: int, y: int, color: Tuple[int, int, int]):
        """Dibujar carácter en posición LCD"""
        pixel_x = x * self.CHAR_SIZE + self.CHAR_SIZE // 2
        pixel_y = y * self.CHAR_SIZE + self.CHAR_SIZE // 2

        text_surface = self.font_large.render(char, True, color)
        text_rect = text_surface.get_rect(center=(pixel_x, pixel_y))
        self.screen.blit(text_surface, text_rect)

    def draw_lcd_border(self):
        """Dibujar borde LCD"""
        lcd_rect = pygame.Rect(0, 0, self.screen_width, self.LCD_HEIGHT * self.CHAR_SIZE)
        pygame.draw.rect(self.screen, self.WHITE, lcd_rect, 2)

        # Líneas de separación
        for y in range(1, self.LCD_HEIGHT):
            start_pos = (0, y * self.CHAR_SIZE)
            end_pos = (self.screen_width, y * self.CHAR_SIZE)
            pygame.draw.line(self.screen, self.WHITE, start_pos, end_pos, 1)

    def draw_game_visualization(self):
        """Dibujar visualización del juego"""
        self.screen.fill(self.BLACK)
        self.draw_lcd_border()

        # Limpiar área LCD
        lcd_area = pygame.Rect(1, 1, self.screen_width - 2, self.LCD_HEIGHT * self.CHAR_SIZE - 2)
        pygame.draw.rect(self.screen, self.BLACK, lcd_area)

        # Dibujar pelota
        self.draw_char_at("●", self.ball_x, self.ball_y, self.WHITE)

        # Dibujar palas
        if self.left_paddle_active:
            self.draw_char_at("█", 0, 0, self.BLUE)
            self.draw_char_at("█", 0, 1, self.BLUE)

        if self.right_paddle_active:
            self.draw_char_at("█", self.LCD_WIDTH - 1, 0, self.BLUE)
            self.draw_char_at("█", self.LCD_WIDTH - 1, 1, self.BLUE)

        # Mostrar puntuación
        score_str = str(self.score)
        score_x = self.LCD_WIDTH // 2 - len(score_str) // 2
        for i, char in enumerate(score_str):
            if score_x + i < self.LCD_WIDTH and score_x + i != self.ball_x or self.ball_y != 0:
                self.draw_char_at(char, score_x + i, 0, self.YELLOW)

        # Información adicional
        info_y = self.LCD_HEIGHT * self.CHAR_SIZE + 10

        # Estado de conexión
        connection_color = self.GREEN if self.arduino_connected else self.RED
        connection_text = "CONECTADO" if self.arduino_connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (10, info_y))

        # Estado del juego
        if self.game_over:
            game_status = f"GAME OVER - {self.game_over_message}"
            status_color = self.RED
        elif self.game_paused:
            game_status = "PAUSADO"
            status_color = self.YELLOW
        else:
            game_status = "JUGANDO"
            status_color = self.GREEN

        status_surface = self.font_small.render(f"Estado: {game_status}", True, status_color)
        self.screen.blit(status_surface, (10, info_y + 25))

        # Puntuación y palas
        score_surface = self.font_small.render(f"Puntuación: {self.score}", True, self.WHITE)
        self.screen.blit(score_surface, (10, info_y + 50))

        paddle_status = f"Palas: {'IZQ' if self.left_paddle_active else '---'} | {'DER' if self.right_paddle_active else '---'}"
        paddle_surface = self.font_small.render(paddle_status, True, self.PURPLE)
        self.screen.blit(paddle_surface, (10, info_y + 75))

        # Controles
        controls = "Controles: R=Restart | P=Pause | S=Get State | ESC=Exit"
        controls_surface = self.font_small.render(controls, True, self.WHITE)
        self.screen.blit(controls_surface, (10, info_y + 100))

        # Tiempo desde última actualización
        time_since_update = time.time() - self.last_update
        if time_since_update > 2.0:  # Sin datos por más de 2 segundos
            warning_surface = self.font_small.render("⚠️ Sin datos recientes del Arduino", True, self.RED)
            self.screen.blit(warning_surface, (200, info_y))

    def run(self):
        """Ejecutar visualizador"""
        print("🎮 Ping Pong Arduino Visualizer")
        print("Conectando con Arduino...")

        if not self.connect_arduino():
            print("❌ No se pudo conectar. Ejecutando en modo demo.")
            self.arduino_connected = False
        else:
            # Iniciar hilo de lectura
            read_thread = threading.Thread(target=self.read_arduino)
            read_thread.daemon = True
            read_thread.start()

        print("🎮 Visualizador iniciado")
        print("Controles PC: R=Restart, P=Pause, S=Estado, ESC=Salir")

        while self.running:
            self.handle_events()
            self.draw_game_visualization()
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        pygame.quit()
        print("👋 Visualizador cerrado")


def main():
    """Función principal"""
    try:
        visualizer = PingPongArduinoVisualizer()
        visualizer.run()
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

# INSTRUCCIONES:
# 1. Conecta LCD Keypad Shield al Arduino
# 2. Sube el código Arduino al microcontrolador
# 3. Instala: pip install pyserial pygame
# 4. Ejecuta este script Python
# 5. Juega con los botones del shield, observa en PC!
