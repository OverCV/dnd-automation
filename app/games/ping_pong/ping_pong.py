import pygame
import time
import threading
from typing import Dict, Any
from abc import ABC, abstractmethod

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from core.lcd.lcd_controller import LCDController, ButtonReader
from core.game_logger import GameLogger

from games.ping_pong.ping_pong_pygame_renderer import PingPongPygameRenderer

class PingPongGame(BaseGame):
    """Ping Pong que implementa BaseGame con sistema de logging"""

    def __init__(self, arduino_manager: ArduinoManager):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Ping Pong"
        self.description = "Juego clásico de Ping Pong con LCD y botones"

        # Inicializar componentes separados
        self.logger = GameLogger("PingPongGame")
        self.renderer = PingPongPygameRenderer()

        # Componentes del juego
        self.lcd = None
        self.buttons = None

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

        # Variables para estadísticas
        self.game_start_time = None
        self.total_hits = 0
        self.left_paddle_hits = 0
        self.right_paddle_hits = 0

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        try:
            if not self.arduino.connected:
                self.logger.log_game_event("HARDWARE", "Arduino no conectado", "ERROR")
                print("❌ Arduino no conectado")
                return False

            self.logger.log_game_event("HARDWARE", "Inicializando hardware Ping Pong...")
            print("🎮 Inicializando hardware Ping Pong...")

            # Inicializar LCD
            self.lcd = LCDController(self.arduino)
            self.logger.log_game_event("HARDWARE", "LCD inicializado correctamente")
            print("✅ LCD inicializado")

            # Inicializar botones
            self.buttons = ButtonReader(self.arduino)
            self.logger.log_game_event("HARDWARE", "Botones inicializados correctamente")
            print("✅ Botones inicializados")

            # Inicializar Pygame
            self.renderer.initialize()
            self.logger.log_game_event("HARDWARE", "Pygame inicializado correctamente")
            print("✅ Pygame inicializado")

            return True

        except Exception as e:
            self.logger.log_game_event("HARDWARE", f"Error inicializando hardware: {e}", "ERROR")
            print(f"❌ Error inicializando hardware: {e}")
            return False

    def start_game(self) -> bool:
        """Iniciar juego"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self._reset_game_state()

            # Registrar inicio del juego
            self.game_start_time = time.time()
            self.logger.log_game_event("GAME", "🎮 Juego iniciado - Esperando al jugador...")

            # Mostrar pantalla de bienvenida
            self._show_welcome_screen()

            # Iniciar hilo del juego
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()

            print("🎮 Ping Pong iniciado correctamente")
            return True

        except Exception as e:
            self.logger.log_game_event("GAME", f"Error iniciando juego: {e}", "ERROR")
            print(f"❌ Error iniciando juego: {e}")
            return False

    def stop_game(self):
        """Detener juego"""
        try:
            self.logger.log_game_event("GAME", "🛑 Deteniendo juego...")
            print("🛑 Deteniendo Ping Pong...")
            self.running = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            if self.lcd:
                self.lcd.clear()

            self.renderer.quit()

            # Log final del juego
            if self.game_start_time:
                total_duration = time.time() - self.game_start_time
                self.logger.log_game_event("GAME", f"✅ Juego detenido - Duración total: {total_duration:.2f}s")

            print("✅ Ping Pong detenido")

        except Exception as e:
            self.logger.log_game_event("GAME", f"Error deteniendo juego: {e}", "ERROR")
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
            'hardware_initialized': self.lcd is not None and self.buttons is not None,
            'total_hits': self.total_hits,
            'game_duration': time.time() - self.game_start_time if self.game_start_time else 0
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

        # Reset estadísticas
        self.total_hits = 0
        self.left_paddle_hits = 0
        self.right_paddle_hits = 0

        self.logger.log_game_event("GAME", "🔄 Estado del juego reseteado")

    def _show_welcome_screen(self):
        """Mostrar pantalla de bienvenida"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(3, 0)
            self.lcd.print("PING PONG")
            self.lcd.set_cursor(0, 1)
            self.lcd.print("Press any button")

        self.logger.log_game_event("UI", "Pantalla de bienvenida mostrada")

    def _game_loop(self):
        """Loop principal del juego"""
        # Esperar botón para comenzar
        self._wait_for_start_button()

        if not self.running:
            return

        self._reset_game_state()
        self.logger.log_game_event("GAME", "🎯 Gameplay iniciado - Pelota en movimiento")
        self._draw_game()

        while self.running:
            try:
                # Procesar eventos de Pygame
                continue_game, action = self.renderer.handle_events()
                if not continue_game:
                    self.logger.log_game_event("INPUT", f"Salida solicitada: {action}")
                    self.running = False
                    break

                # Manejar acciones de Pygame
                if action == "RESET" and self.game_over:
                    self.logger.log_game_event("INPUT", "Reset solicitado desde Pygame")
                    self._reset_game_state()
                    self._draw_game()
                elif action == "PAUSE" and not self.game_over:
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        self.logger.log_game_event("INPUT", "Pausa solicitada desde Pygame")
                        self._show_pause_screen()
                    else:
                        self.logger.log_game_event("INPUT", "Reanudación solicitada desde Pygame")
                        self._draw_game()

                # Leer botones del Arduino
                self._read_buttons()

                # Actualizar lógica del juego
                self._update_game()

                # Dibujar visualización
                self._update_visualization()

                time.sleep(0.01)  # Pequeña pausa para no saturar

            except Exception as e:
                self.logger.log_game_event("GAME", f"Error en loop del juego: {e}", "ERROR")
                print(f"❌ Error en loop del juego: {e}")
                break

    def _wait_for_start_button(self):
        """Esperar que se presione un botón para comenzar"""
        self.logger.log_game_event("INPUT", "Esperando botón de inicio...")

        while self.running:
            if self.buttons:
                button = self.buttons.read_button()
                if button != 'NONE':
                    self.logger.log_game_event("INPUT", f"Botón de inicio presionado: {button}")
                    time.sleep(0.3)  # Debounce
                    break

            # Procesar eventos de Pygame para no bloquear la ventana
            continue_game, _ = self.renderer.handle_events()
            if not continue_game:
                self.running = False
                break

            self._update_visualization()
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
                if not self.left_paddle_active:
                    self.left_paddle_active = True
                    self.logger.log_game_event("INPUT", "Pala izquierda ACTIVADA")
            elif button == 'RIGHT':
                if not self.right_paddle_active:
                    self.right_paddle_active = True
                    self.logger.log_game_event("INPUT", "Pala derecha ACTIVADA")
            elif button == 'SELECT':
                if self.game_over:
                    self.logger.log_game_event("GAME", "🔄 Reinicio solicitado por jugador")
                    self._reset_game_state()
                    self._draw_game()
                else:
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        self.logger.log_game_event("GAME", "⏸️ Juego PAUSADO por jugador")
                        self._show_pause_screen()
                    else:
                        self.logger.log_game_event("GAME", "▶️ Juego REANUDADO por jugador")
                        self._draw_game()
        else:
            # Log cuando las palas se desactivan
            if self.left_paddle_active:
                self.logger.log_game_event("INPUT", "Pala izquierda DESACTIVADA")
            if self.right_paddle_active:
                self.logger.log_game_event("INPUT", "Pala derecha DESACTIVADA")

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

        # Guardar posición anterior para logging
        old_x, old_y = self.ball_x, self.ball_y

        # Mover pelota
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Log movimiento de pelota (solo ocasionalmente para no saturar)
        if self.score % 3 == 0 or abs(self.ball_x - old_x) > 1:
            self.logger.log_game_event("BALL", f"Pelota movida de ({old_x}, {old_y}) a ({self.ball_x}, {self.ball_y})")

        # Colisiones verticales
        if self.ball_y < 0:
            self.ball_y = 0
            self.ball_dy = -self.ball_dy
            self.logger.log_game_event("COLLISION", "Rebote vertical - techo")
        elif self.ball_y >= self.LCD_HEIGHT:
            self.ball_y = self.LCD_HEIGHT - 1
            self.ball_dy = -self.ball_dy
            self.logger.log_game_event("COLLISION", "Rebote vertical - suelo")

        # Colisiones horizontales
        if self.ball_x <= 0:
            if self.left_paddle_active:
                self.ball_x = 1
                self.ball_dx = -self.ball_dx
                self.score += 1
                self.total_hits += 1
                self.left_paddle_hits += 1
                self.logger.log_game_event("HIT", f"🏓 GOLPE EXITOSO con pala IZQUIERDA - Nuevo score: {self.score}")
            else:
                self._handle_game_over("LEFT", "Pala izquierda no estaba activa")
                return
        elif self.ball_x >= self.LCD_WIDTH - 1:
            if self.right_paddle_active:
                self.ball_x = self.LCD_WIDTH - 2
                self.ball_dx = -self.ball_dx
                self.score += 1
                self.total_hits += 1
                self.right_paddle_hits += 1
                self.logger.log_game_event("HIT", f"🏓 GOLPE EXITOSO con pala DERECHA - Nuevo score: {self.score}")
            else:
                self._handle_game_over("RIGHT", "Pala derecha no estaba activa")
                return

        # Aumentar velocidad gradualmente
        if self.score > 0 and self.score % 5 == 0:
            old_speed = self.game_speed
            self.game_speed = max(0.1, self.game_speed - 0.02)
            if old_speed != self.game_speed:
                self.logger.log_game_event("SPEED", f"⚡ Velocidad aumentada de {old_speed:.2f}s a {self.game_speed:.2f}s")

        self._draw_game()

    def _handle_game_over(self, side: str, reason: str):
        """Manejar el game over"""
        game_duration = time.time() - self.game_start_time if self.game_start_time else 0

        self.logger.log_player_death_ping_pong(
            reason, side, self.score, self.total_hits,
            self.left_paddle_hits, self.right_paddle_hits,
            game_duration, self.game_speed
        )

        self.game_over = True
        message = f"{side.capitalize()} miss!"
        self._show_game_over(message)

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

        self.logger.log_game_event("GAME", f"💀 GAME OVER mostrado: {message}")

    def _update_visualization(self):
        """Actualizar visualización en Pygame"""
        self.renderer.draw_game(
            self.ball_x, self.ball_y,
            self.left_paddle_active, self.right_paddle_active,
            self.score, self.game_over, self.game_paused,
            self.total_hits, self.left_paddle_hits, self.right_paddle_hits
        )
        self.renderer.update_display()
