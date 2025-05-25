"""
Two-Lane Runner - Arduino + Python
Visualizador del juego de carriles con comunicación serial
"""

import serial
import pygame
import time
import threading
from typing import Optional
import serial.tools.list_ports
import math

class TwoLaneRunnerVisualizer:
    """Visualizador del juego Two-Lane Runner desde Arduino"""

    # Constantes de visualización
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 400
    LCD_WIDTH = 16
    LCD_HEIGHT = 2
    CELL_WIDTH = 50
    CELL_HEIGHT = 80

    # Colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 100, 100)
    GREEN = (100, 255, 100)
    BLUE = (100, 150, 255)
    YELLOW = (255, 255, 100)
    PURPLE = (200, 100, 255)
    ORANGE = (255, 165, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    CYAN = (100, 255, 255)

    def __init__(self):
        """Inicializar visualizador"""
        pygame.init()

        # Configurar ventana
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Two-Lane Runner - Arduino Visualizer")

        # Fuentes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Estado del juego (recibido desde Arduino)
        self.player_y = 0  # 0=top lane, 1=bottom lane
        self.score = 0
        self.speed = 500
        self.game_over = False
        self.game_paused = False
        self.obstacles = []  # Lista de (x, y) posiciones
        self.arduino_connected = False
        self.game_message = "Conectando con Arduino..."

        # Serial
        self.arduino: Optional[serial.Serial] = None
        self.running = True

        # Control de tiempo
        self.clock = pygame.time.Clock()
        self.last_update = time.time()

        # Estadísticas
        self.total_games = 0
        self.best_score = 0
        self.current_speed_display = 500

        # Animaciones
        self.player_animation_offset = 0
        self.background_scroll = 0

        # Área de juego (simulando LCD 16x2)
        self.game_area_x = 100
        self.game_area_y = 50
        self.game_area_width = self.LCD_WIDTH * self.CELL_WIDTH
        self.game_area_height = self.LCD_HEIGHT * self.CELL_HEIGHT

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
                ports = serial.tools.list_ports.comports()
                print("Puertos disponibles:")
                for i, p in enumerate(ports):
                    print(f"  {i}: {p.device} - {p.description}")

                print("📝 Ingresa el puerto manualmente:")
                port = input("Puerto: ").strip()

            print(f"🔌 Conectando a {port}...")
            self.arduino = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)

            if self.arduino.is_open:
                self.arduino_connected = True
                self.game_message = "Arduino conectado - Listo para jugar"
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
            if message == "RUNNER_READY":
                self.game_message = "Two-Lane Runner listo"
                print("🎮 Runner Arduino listo")

            elif message.startswith("STATE:"):
                # Parsear: "STATE:playerY,score,speed,gameOver,gamePaused,numObstacles"
                parts = message[6:].split(",")
                if len(parts) >= 6:
                    self.player_y = int(parts[0])
                    self.score = int(parts[1])
                    self.speed = int(parts[2])
                    self.game_over = bool(int(parts[3]))
                    self.game_paused = bool(int(parts[4]))
                    num_obstacles = int(parts[5])

                    self.current_speed_display = self.speed

            elif message.startswith("OBSTACLES:"):
                # Parsear: "OBSTACLES:x1,y1;x2,y2;..."
                obstacle_data = message[10:]
                self.obstacles = []
                if obstacle_data:
                    pairs = obstacle_data.split(";")
                    for pair in pairs:
                        if "," in pair:
                            x, y = map(int, pair.split(","))
                            self.obstacles.append((x, y))

            elif message.startswith("PLAYER_MOVE:"):
                lane = int(message[12:])
                self.player_y = lane
                print(f"🏃 Jugador se movió al carril {lane}")

            elif message.startswith("COLLISION:"):
                parts = message[10:].split(",")
                x, y = int(parts[0]), int(parts[1])
                self.game_message = f"¡Colisión en ({x},{y})!"
                print(f"💥 Colisión en posición ({x},{y})")

            elif message.startswith("SCORE_UPDATE:"):
                self.score = int(message[13:])
                print(f"📊 Puntuación: {self.score}")

            elif message.startswith("SPEED_INCREASE:"):
                self.speed = int(message[15:])
                self.current_speed_display = self.speed
                print(f"⚡ Velocidad aumentada: {self.speed}ms")

            elif message.startswith("NEW_OBSTACLE:"):
                parts = message[13:].split(",")
                x, y = int(parts[0]), int(parts[1])
                print(f"🚧 Nuevo obstáculo en ({x},{y})")

            elif message == "GAME_START":
                self.game_message = "¡Juego iniciado! Usa ↑↓ para cambiar de carril"

            elif message == "GAME_PAUSE":
                self.game_message = "Juego pausado - Presiona SELECT para continuar"

            elif message == "GAME_RESUME":
                self.game_message = "¡Juego reanudado!"

            elif message.startswith("GAME_OVER:"):
                final_score = int(message[10:])
                self.game_message = f"Game Over - Puntuación final: {final_score}"
                self.total_games += 1
                if final_score > self.best_score:
                    self.best_score = final_score
                print(f"💀 Game Over - Puntuación: {final_score}")

            elif message == "GAME_RESTART":
                self.game_message = "Juego reiniciado"

            elif message == "WELCOME_SCREEN":
                self.game_message = "Bienvenido - Presiona cualquier botón para empezar"

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
        keys = pygame.key.get_pressed()

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
                elif event.key == pygame.K_UP:
                    self.send_command("MOVE_UP")
                elif event.key == pygame.K_DOWN:
                    self.send_command("MOVE_DOWN")

    def draw_background(self):
        """Dibujar fondo animado"""
        self.screen.fill(self.BLACK)

        # Scroll del fondo
        self.background_scroll += 2
        if self.background_scroll >= self.CELL_WIDTH:
            self.background_scroll = 0

        # Líneas de carril
        lane_y_positions = [
            self.game_area_y + self.CELL_HEIGHT // 2,
            self.game_area_y + self.CELL_HEIGHT + self.CELL_HEIGHT // 2
        ]

        # Líneas horizontales de carriles
        for y in lane_y_positions:
            pygame.draw.line(self.screen, self.GRAY,
                           (self.game_area_x, y),
                           (self.game_area_x + self.game_area_width, y), 2)

        # Línea central divisoria
        center_y = self.game_area_y + self.game_area_height // 2
        dash_length = 20
        for x in range(self.game_area_x - self.background_scroll,
                      self.game_area_x + self.game_area_width, dash_length * 2):
            pygame.draw.line(self.screen, self.YELLOW,
                           (x, center_y), (x + dash_length, center_y), 3)

        # Bordes del área de juego
        pygame.draw.rect(self.screen, self.WHITE,
                        (self.game_area_x - 2, self.game_area_y - 2,
                         self.game_area_width + 4, self.game_area_height + 4), 3)

    def draw_player(self):
        """Dibujar jugador"""
        # Posición del jugador
        player_x = self.game_area_x + self.CELL_WIDTH  # Posición fija en columna 1
        player_y = self.game_area_y + self.player_y * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

        # Animación de movimiento
        self.player_animation_offset += 0.3
        bounce = math.sin(self.player_animation_offset) * 3

        # Cuerpo del jugador (rectángulo principal)
        player_rect = pygame.Rect(player_x - 15, player_y - 20 + bounce, 30, 40)
        pygame.draw.rect(self.screen, self.GREEN, player_rect)
        pygame.draw.rect(self.screen, self.WHITE, player_rect, 2)

        # Cabeza
        head_rect = pygame.Rect(player_x - 10, player_y - 35 + bounce, 20, 20)
        pygame.draw.ellipse(self.screen, self.GREEN, head_rect)
        pygame.draw.ellipse(self.screen, self.WHITE, head_rect, 2)

        # Ojos
        pygame.draw.circle(self.screen, self.BLACK, (player_x - 5, player_y - 28 + int(bounce)), 2)
        pygame.draw.circle(self.screen, self.BLACK, (player_x + 5, player_y - 28 + int(bounce)), 2)

        # Piernas (líneas)
        pygame.draw.line(self.screen, self.GREEN,
                        (player_x - 5, player_y + 15 + bounce),
                        (player_x - 8, player_y + 35 + bounce), 4)
        pygame.draw.line(self.screen, self.GREEN,
                        (player_x + 5, player_y + 15 + bounce),
                        (player_x + 8, player_y + 35 + bounce), 4)

    def draw_obstacles(self):
        """Dibujar obstáculos"""
        for obs_x, obs_y in self.obstacles:
            if 0 <= obs_x < self.LCD_WIDTH:
                screen_x = self.game_area_x + obs_x * self.CELL_WIDTH + self.CELL_WIDTH // 2
                screen_y = self.game_area_y + obs_y * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

                # Obstáculo principal (círculo)
                pygame.draw.circle(self.screen, self.RED, (screen_x, screen_y), 20)
                pygame.draw.circle(self.screen, self.WHITE, (screen_x, screen_y), 20, 3)

                # Patrón interior
                pygame.draw.circle(self.screen, self.ORANGE, (screen_x, screen_y), 12)
                pygame.draw.circle(self.screen, self.YELLOW, (screen_x, screen_y), 6)

                # Efecto de peligro
                for i in range(3):
                    angle = time.time() * 5 + i * 2.1
                    spike_x = screen_x + math.cos(angle) * 25
                    spike_y = screen_y + math.sin(angle) * 25
                    pygame.draw.line(self.screen, self.RED,
                                   (screen_x, screen_y), (spike_x, spike_y), 2)

    def draw_ui(self):
        """Dibujar interfaz de usuario"""
        # Título
        title_surface = self.font_large.render("TWO-LANE RUNNER", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 25))
        self.screen.blit(title_surface, title_rect)

        # Estado de conexión
        connection_color = self.GREEN if self.arduino_connected else self.RED
        connection_text = "CONECTADO" if self.arduino_connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (20, 20))

        # Información del juego
        info_y = self.game_area_y + self.game_area_height + 20

        # Puntuación
        score_surface = self.font_medium.render(f"Puntuación: {self.score}", True, self.WHITE)
        self.screen.blit(score_surface, (self.game_area_x, info_y))

        # Velocidad (convertir delay a velocidad visual)
        speed_percentage = max(0, (500 - self.current_speed_display) / 350 * 100)
        speed_surface = self.font_medium.render(f"Velocidad: {speed_percentage:.0f}%", True, self.CYAN)
        self.screen.blit(speed_surface, (self.game_area_x + 200, info_y))

        # Carril actual
        lane_name = "SUPERIOR" if self.player_y == 0 else "INFERIOR"
        lane_surface = self.font_medium.render(f"Carril: {lane_name}", True, self.YELLOW)
        self.screen.blit(lane_surface, (self.game_area_x + 400, info_y))

        # Estado del juego
        if self.game_over:
            status_text = "GAME OVER"
            status_color = self.RED
        elif self.game_paused:
            status_text = "PAUSADO"
            status_color = self.YELLOW
        else:
            status_text = "JUGANDO"
            status_color = self.GREEN

        status_surface = self.font_medium.render(f"Estado: {status_text}", True, status_color)
        self.screen.blit(status_surface, (self.game_area_x + 600, info_y))

        # Estadísticas
        stats_y = info_y + 40
        stats_surface = self.font_small.render(f"Partidas: {self.total_games} | Mejor puntuación: {self.best_score}", True, self.WHITE)
        self.screen.blit(stats_surface, (self.game_area_x, stats_y))

        # Mensaje del juego
        message_surface = self.font_medium.render(self.game_message, True, self.PURPLE)
        message_rect = message_surface.get_rect(center=(self.WINDOW_WIDTH // 2, stats_y + 40))
        self.screen.blit(message_surface, message_rect)

        # Controles
        controls_y = self.WINDOW_HEIGHT - 60
        controls = [
            "Controles Arduino: ↑↓ (cambiar carril) | SELECT (pausa)",
            "Controles PC: ↑↓ (mover) | R (restart) | P (pausa) | S (estado) | ESC (salir)"
        ]

        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, self.GRAY)
            self.screen.blit(control_surface, (20, controls_y + i * 20))

        # Indicador de obstáculos
        obstacles_text = f"Obstáculos activos: {len(self.obstacles)}"
        obstacles_surface = self.font_small.render(obstacles_text, True, self.WHITE)
        self.screen.blit(obstacles_surface, (self.game_area_x + 400, stats_y))

        # Barra de velocidad visual
        speed_bar_x = self.WINDOW_WIDTH - 150
        speed_bar_y = 50
        speed_bar_width = 100
        speed_bar_height = 20

        # Fondo de la barra
        pygame.draw.rect(self.screen, self.DARK_GRAY,
                        (speed_bar_x, speed_bar_y, speed_bar_width, speed_bar_height))

        # Relleno de velocidad
        fill_width = int(speed_bar_width * speed_percentage / 100)
        if fill_width > 0:
            color = self.GREEN if speed_percentage < 50 else self.YELLOW if speed_percentage < 80 else self.RED
            pygame.draw.rect(self.screen, color,
                           (speed_bar_x, speed_bar_y, fill_width, speed_bar_height))

        # Borde de la barra
        pygame.draw.rect(self.screen, self.WHITE,
                        (speed_bar_x, speed_bar_y, speed_bar_width, speed_bar_height), 2)

        # Etiqueta de la barra
        speed_label = self.font_small.render("Velocidad", True, self.WHITE)
        self.screen.blit(speed_label, (speed_bar_x, speed_bar_y - 25))

        # Indicador de tiempo sin datos
        time_since_update = time.time() - self.last_update
        if time_since_update > 3.0:
            warning_surface = self.font_small.render("⚠️ Sin datos del Arduino", True, self.RED)
            self.screen.blit(warning_surface, (self.WINDOW_WIDTH - 200, 20))

    def draw_grid(self):
        """Dibujar grid de referencia (opcional)"""
        # Grid de fondo para referencia
        for x in range(self.LCD_WIDTH + 1):
            line_x = self.game_area_x + x * self.CELL_WIDTH
            pygame.draw.line(self.screen, self.DARK_GRAY,
                           (line_x, self.game_area_y),
                           (line_x, self.game_area_y + self.game_area_height), 1)

        for y in range(self.LCD_HEIGHT + 1):
            line_y = self.game_area_y + y * self.CELL_HEIGHT
            pygame.draw.line(self.screen, self.DARK_GRAY,
                           (self.game_area_x, line_y),
                           (self.game_area_x + self.game_area_width, line_y), 1)

    def draw_game_visualization(self):
        """Dibujar visualización completa del juego"""
        # Fondo animado
        self.draw_background()

        # Grid de referencia (opcional)
        # self.draw_grid()

        # Elementos del juego
        self.draw_obstacles()
        self.draw_player()

        # Interfaz de usuario
        self.draw_ui()

        # Efectos especiales si hay colisión
        if self.game_over and "Colisión" in self.game_message:
            # Efecto de flash rojo
            flash_alpha = int(abs(math.sin(time.time() * 10)) * 100)
            flash_surface = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill(self.RED)
            self.screen.blit(flash_surface, (0, 0))

    def run(self):
        """Ejecutar visualizador"""
        print("🎮 Two-Lane Runner Arduino + Python")
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
        print("Controles: ↑↓=Mover, R=Restart, P=Pause, S=Estado, ESC=Salir")

        while self.running:
            self.handle_events()
            self.draw_game_visualization()
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        pygame.quit()
        print("👋 Two-Lane Runner cerrado")


def main():
    """Función principal"""
    try:
        game = TwoLaneRunnerVisualizer()
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
# 1. Conecta LCD Keypad Shield al Arduino
# 2. Sube el código Arduino al microcontrolador
# 3. Instala dependencias: pip install pyserial pygame
# 4. Ejecuta este script Python
# 5. ¡Juega con los botones UP/DOWN del shield!

"""
=== CARACTERÍSTICAS DEL JUEGO PYTHON ===

🎮 VISUALIZACIÓN MEJORADA:
- Área de juego ampliada que simula LCD 16x2
- Jugador animado con movimiento y rebote
- Obstáculos con efectos visuales y rotación
- Fondo animado con líneas de carril
- Efectos especiales de colisión

📊 INTERFAZ RICA:
- Información en tiempo real (puntuación, velocidad, carril)
- Barra de velocidad visual con colores
- Estadísticas acumuladas (partidas, mejor puntuación)
- Estado de conexión y mensajes del juego
- Grid de referencia opcional

🎯 CARACTERÍSTICAS DEL JUEGO:
- Dos carriles (superior e inferior)
- Obstáculos se mueven de derecha a izquierda
- Velocidad aumenta progresivamente
- Siempre hay al menos un carril libre
- Colisiones detectadas en tiempo real

🔌 COMUNICACIÓN SERIAL:
- Protocolo robusto Arduino ↔ Python
- Estado del juego sincronizado
- Posiciones de obstáculos en tiempo real
- Eventos de juego (colisiones, puntuación, etc.)

🎮 CONTROLES DUALES:
- Arduino: Botones UP/DOWN del shield para jugar
- PC: Flechas ↑↓ para control remoto
- Gestión: R=restart, P=pause, S=estado, ESC=salir

🚀 VENTAJAS SOBRE VERSIÓN SOLO ARDUINO:
- Visualización ampliada y detallada
- Animaciones suaves y efectos visuales
- Estadísticas persistentes entre partidas
- Debugging visual del estado del juego
- Experiencia inmersiva mejorada

=== MECÁNICA DEL JUEGO ===

🏃 JUGADOR:
- Posición fija en columna 1 (X=1)
- Puede moverse entre carril superior (Y=0) e inferior (Y=1)
- Representado con personaje animado verde

🚧 OBSTÁCULOS:
- Aparecen en el borde derecho (X=15)
- Se mueven hacia la izquierda
- Nunca bloquean ambos carriles simultáneamente
- Representados como círculos rojos con efectos

📈 PROGRESIÓN:
- Puntuación aumenta cuando obstáculos salen de pantalla
- Velocidad aumenta cada 10 puntos
- Delay mínimo: 150ms (velocidad máxima)
- Máximo 8 obstáculos simultáneos en pantalla

💥 COLISIONES:
- Detectadas cuando jugador y obstáculo ocupan misma posición
- Game Over inmediato con efectos visuales
- Estadísticas actualizadas automáticamente

=== PROTOCOLO DE COMUNICACIÓN ===

📤 Arduino → Python:
- "RUNNER_READY" - Sistema listo
- "STATE:playerY,score,speed,gameOver,paused,numObstacles" - Estado completo
- "OBSTACLES:x1,y1;x2,y2;..." - Posiciones de obstáculos
- "PLAYER_MOVE:lane" - Cambio de carril
- "COLLISION:x,y" - Colisión detectada
- "SCORE_UPDATE:score" - Puntuación actualizada
- "SPEED_INCREASE:newSpeed" - Aumento de velocidad
- "NEW_OBSTACLE:x,y" - Nuevo obstáculo creado
- Eventos: GAME_START/PAUSE/RESUME/RESTART/OVER

📥 Python → Arduino:
- "GET_STATE" - Solicitar estado actual
- "RESTART" - Reiniciar juego
- "PAUSE" - Pausar/reanudar
- "MOVE_UP/MOVE_DOWN" - Control remoto desde PC

=== CONFIGURACIÓN HARDWARE ===

🔌 CONEXIONES:
- LCD Keypad Shield conectado al Arduino
- Puerto USB para comunicación serial
- No se requieren componentes adicionales

🎮 CONTROLES:
- UP button: Mover a carril superior
- DOWN button: Mover a carril inferior
- SELECT button: Pausar/reanudar juego

=== TROUBLESHOOTING ===

🔧 Si no conecta:
- Verifica puerto serial
- Confirma que Arduino tiene el código cargado
- Revisa cable USB

🔧 Si botones no responden:
- Verifica conexiones del shield
- Prueba otros botones
- Revisa valores analógicos en código

🔧 Si hay lag visual:
- Reduce SERIAL_INTERVAL en Arduino
- Cierra otros programas pesados
- Verifica velocidad 9600 baud

🔧 Si obstáculos no aparecen:
- Verifica comunicación serial
- Usa comando 'S' para solicitar estado
- Revisa parsing de mensajes OBSTACLES
"""
