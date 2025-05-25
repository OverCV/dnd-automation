import pygame
import time
import threading
from typing import Dict, Any
from abc import ABC, abstractmethod

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager

from core.lcd.lcd_controller import LCDController, ButtonReader

class PingPongGame(BaseGame):
    """Ping Pong que implementa BaseGame"""

    def __init__(self, arduino_manager: ArduinoManager):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Ping Pong"
        self.description = "Juego clásico de Ping Pong con LCD y botones"

        # Componentes del juego
        self.lcd = None
        self.buttons = None

        # Pygame components
        self.screen = None
        self.clock = None
        self.pygame_initialized = False

        # Variables del juego
        self.LCD_WIDTH = 16
        self.LCD_HEIGHT = 2
        self.ball_x = self.LCD_WIDTH // 2
        self.ball_y = 0
        self.ball_dx = 1
        self.ball_dy = 1
        self.left_paddle_active = False
        self.right_paddle_active = False
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.game_speed = 0.3

        # Control de tiempo
        self.last_move_time = time.time()
        self.last_button_time = time.time()
        self.button_debounce = 0.2

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        try:
            if not self.arduino.connected:
                print("❌ Arduino no conectado")
                return False

            print("🎮 Inicializando hardware Ping Pong...")

            # Inicializar LCD
            self.lcd = LCDController(self.arduino)
            print("✅ LCD inicializado")

            # Inicializar botones
            self.buttons = ButtonReader(self.arduino)
            print("✅ Botones inicializados")

            # Inicializar Pygame
            self._initialize_pygame()
            print("✅ Pygame inicializado")

            return True

        except Exception as e:
            print(f"❌ Error inicializando hardware: {e}")
            return False

    def _initialize_pygame(self):
        """Inicializar componentes de Pygame"""
        if not self.pygame_initialized:
            pygame.init()
            self.screen_width = 800
            self.screen_height = 600
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Ping Pong - Arduino + Python")

            # Fuentes y colores
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

            self.BLACK = (0, 0, 0)
            self.WHITE = (255, 255, 255)
            self.GREEN = (0, 255, 0)
            self.BLUE = (0, 100, 255)
            self.RED = (255, 100, 100)
            self.YELLOW = (255, 255, 0)

            self.clock = pygame.time.Clock()
            self.pygame_initialized = True

    def start_game(self) -> bool:
        """Iniciar juego"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self._reset_game_state()

            # Mostrar pantalla de bienvenida
            self._show_welcome_screen()

            # Iniciar hilo del juego
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()

            print("🎮 Ping Pong iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            return False

    def stop_game(self):
        """Detener juego"""
        try:
            print("🛑 Deteniendo Ping Pong...")
            self.running = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            if self.lcd:
                self.lcd.clear()

            if self.pygame_initialized:
                pygame.quit()
                self.pygame_initialized = False

            print("✅ Ping Pong detenido")

        except Exception as e:
            print(f"❌ Error deteniendo juego: {e}")

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        return {
            'name': self.name,
            'running': self.running,
            'score': self.score,
            'game_over': self.game_over,
            'paused': self.game_paused,
            'ball_position': (self.ball_x, self.ball_y),
            'left_paddle': self.left_paddle_active,
            'right_paddle': self.right_paddle_active,
            'hardware_initialized': self.lcd is not None and self.buttons is not None
        }

    def _reset_game_state(self):
        """Resetear estado del juego"""
        self.ball_x = self.LCD_WIDTH // 2
        self.ball_y = 0
        self.ball_dx = 1
        self.ball_dy = 1
        self.left_paddle_active = False
        self.right_paddle_active = False
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.game_speed = 0.3
        self.last_move_time = time.time()

    def _show_welcome_screen(self):
        """Mostrar pantalla de bienvenida"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(3, 0)
            self.lcd.print("PING PONG")
            self.lcd.set_cursor(0, 1)
            self.lcd.print("Press any button")

    def _game_loop(self):
        """Loop principal del juego"""
        # Esperar botón para comenzar
        self._wait_for_start_button()

        if not self.running:
            return

        self._reset_game_state()
        self._draw_game()

        while self.running:
            try:
                # Procesar eventos de Pygame
                self._handle_pygame_events()

                # Leer botones del Arduino
                self._read_buttons()

                # Actualizar lógica del juego
                self._update_game()

                # Dibujar visualización
                if self.pygame_initialized:
                    self._draw_pygame_visualization()
                    pygame.display.flip()
                    self.clock.tick(60)

                time.sleep(0.01)  # Pequeña pausa para no saturar

            except Exception as e:
                print(f"❌ Error en loop del juego: {e}")
                break

    def _wait_for_start_button(self):
        """Esperar que se presione un botón para comenzar"""
        while self.running:
            if self.buttons:
                button = self.buttons.read_button()
                if button != 'NONE':
                    time.sleep(0.3)  # Debounce
                    break

            # Procesar eventos de Pygame para no bloquear la ventana
            if self.pygame_initialized:
                self._handle_pygame_events()
                self._draw_pygame_visualization()
                pygame.display.flip()
                self.clock.tick(60)

            time.sleep(0.05)

    def _read_buttons(self):
        """Leer estado de los botones"""
        if not self.buttons:
            return

        current_time = time.time()
        if current_time - self.last_button_time < self.button_debounce:
            return

        button = self.buttons.read_button()

        if button != 'NONE':
            self.last_button_time = current_time

            if button == 'LEFT':
                self.left_paddle_active = True
            elif button == 'RIGHT':
                self.right_paddle_active = True
            elif button == 'SELECT':
                if self.game_over:
                    self._reset_game_state()
                    self._draw_game()
                else:
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        self._show_pause_screen()
                    else:
                        self._draw_game()
        else:
            self.left_paddle_active = False
            self.right_paddle_active = False

    def _update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.game_paused:
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.game_speed:
            return

        self.last_move_time = current_time

        # Mover pelota
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Colisiones verticales
        if self.ball_y < 0:
            self.ball_y = 0
            self.ball_dy = -self.ball_dy
        elif self.ball_y >= self.LCD_HEIGHT:
            self.ball_y = self.LCD_HEIGHT - 1
            self.ball_dy = -self.ball_dy

        # Colisiones horizontales
        if self.ball_x <= 0:
            if self.left_paddle_active:
                self.ball_x = 1
                self.ball_dx = -self.ball_dx
                self.score += 1
            else:
                self.game_over = True
                self._show_game_over("Left miss!")
                return
        elif self.ball_x >= self.LCD_WIDTH - 1:
            if self.right_paddle_active:
                self.ball_x = self.LCD_WIDTH - 2
                self.ball_dx = -self.ball_dx
                self.score += 1
            else:
                self.game_over = True
                self._show_game_over("Right miss!")
                return

        # Aumentar velocidad gradualmente
        if self.score > 0 and self.score % 5 == 0:
            self.game_speed = max(0.1, self.game_speed - 0.02)

        self._draw_game()

    def _draw_game(self):
        """Dibujar estado del juego en LCD"""
        if not self.lcd:
            return

        self.lcd.clear()

        # Dibujar pelota
        self.lcd.set_cursor(self.ball_x, self.ball_y)
        self.lcd.write_custom_char(0)

        # Dibujar palas
        if self.left_paddle_active:
            self.lcd.set_cursor(0, 0)
            self.lcd.write_custom_char(1)
            self.lcd.set_cursor(0, 1)
            self.lcd.write_custom_char(1)

        if self.right_paddle_active:
            self.lcd.set_cursor(self.LCD_WIDTH - 1, 0)
            self.lcd.write_custom_char(2)
            self.lcd.set_cursor(self.LCD_WIDTH - 1, 1)
            self.lcd.write_custom_char(2)

        # Mostrar puntuación
        score_str = str(self.score)
        score_x = self.LCD_WIDTH // 2 - len(score_str) // 2
        if not (score_x <= self.ball_x < score_x + len(score_str) and self.ball_y == 0):
            self.lcd.set_cursor(score_x, 0)
            self.lcd.print(score_str)

    def _show_pause_screen(self):
        """Mostrar pantalla de pausa"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(4, 0)
            self.lcd.print("PAUSED")
            self.lcd.set_cursor(2, 1)
            self.lcd.print(f"Score: {self.score}")

    def _show_game_over(self, message):
        """Mostrar pantalla de game over"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(3, 0)
            self.lcd.print("GAME OVER")
            self.lcd.set_cursor(0, 1)
            self.lcd.print(f"{message} S:{self.score}")

    def _draw_pygame_visualization(self):
        """Dibujar visualización en Pygame"""
        if not self.pygame_initialized:
            return

        self.screen.fill(self.BLACK)

        # Título
        title = self.font_large.render("Ping Pong - Arduino + Python", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # Simulación del LCD
        lcd_width = 640
        lcd_height = 160
        lcd_x = (self.screen_width - lcd_width) // 2
        lcd_y = 120

        # Marco del LCD
        pygame.draw.rect(self.screen, self.GREEN, (lcd_x - 5, lcd_y - 5, lcd_width + 10, lcd_height + 10), 3)
        pygame.draw.rect(self.screen, self.BLACK, (lcd_x, lcd_y, lcd_width, lcd_height))

        # Grid del LCD
        char_width = lcd_width // self.LCD_WIDTH
        char_height = lcd_height // self.LCD_HEIGHT

        # Dibujar caracteres
        for y in range(self.LCD_HEIGHT):
            for x in range(self.LCD_WIDTH):
                char_x = lcd_x + x * char_width
                char_y = lcd_y + y * char_height

                # Pelota
                if x == self.ball_x and y == self.ball_y:
                    pygame.draw.circle(self.screen, self.WHITE,
                                     (char_x + char_width//2, char_y + char_height//2),
                                     min(char_width, char_height)//3)

                # Palas
                if x == 0 and self.left_paddle_active:
                    pygame.draw.rect(self.screen, self.BLUE,
                                   (char_x, char_y, char_width//3, char_height))
                elif x == self.LCD_WIDTH - 1 and self.right_paddle_active:
                    pygame.draw.rect(self.screen, self.BLUE,
                                   (char_x + 2*char_width//3, char_y, char_width//3, char_height))

        # Información del juego
        info_y = 320
        score_text = self.font_medium.render(f"Puntuación: {self.score}", True, self.YELLOW)
        self.screen.blit(score_text, (50, info_y))

        # Estado del juego
        if self.game_over:
            status = "GAME OVER - Presiona SELECT para reiniciar"
            color = self.RED
        elif self.game_paused:
            status = "PAUSADO - Presiona SELECT para continuar"
            color = self.YELLOW
        else:
            status = "JUGANDO - LEFT/RIGHT para palas, SELECT para pausar"
            color = self.GREEN

        status_text = self.font_medium.render(status, True, color)
        status_rect = status_text.get_rect(center=(self.screen_width // 2, info_y + 40))
        self.screen.blit(status_text, status_rect)

        # Estado de palas
        left_status = "ACTIVA" if self.left_paddle_active else "INACTIVA"
        right_status = "ACTIVA" if self.right_paddle_active else "INACTIVA"

        left_color = self.GREEN if self.left_paddle_active else self.RED
        right_color = self.GREEN if self.right_paddle_active else self.RED

        left_text = self.font_small.render(f"Pala Izq: {left_status}", True, left_color)
        right_text = self.font_small.render(f"Pala Der: {right_status}", True, right_color)

        self.screen.blit(left_text, (50, info_y + 80))
        self.screen.blit(right_text, (50, info_y + 110))

        # Información de conexión
        conn_text = self.font_small.render("✅ Arduino conectado con Firmata", True, self.GREEN)
        self.screen.blit(conn_text, (50, info_y + 150))

    def _handle_pygame_events(self):
        """Manejar eventos de Pygame"""
        if not self.pygame_initialized:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self._reset_game_state()
                    self._draw_game()
                elif event.key == pygame.K_p and not self.game_over:
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        self._show_pause_screen()
                    else:
                        self._draw_game()
