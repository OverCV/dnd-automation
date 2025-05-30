import pygame
import time
import threading
import math
import random
from typing import Dict, Any, List, Tuple
from abc import ABC, abstractmethod

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from core.lcd.lcd_controller import LCDController, ButtonReader
from core.game_logger import GameLogger

class TwoLaneRunnerGame(BaseGame):
    """Two-Lane Runner que implementa BaseGame"""

    def __init__(self, arduino_manager: ArduinoManager):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Two-Lane Runner"
        self.description = "Esquiva obstáculos corriendo entre dos carriles"

        # Inicializar logger
        self.logger = GameLogger("TwoLaneRunner")
        
        # Componentes del juego
        self.lcd = None
        self.buttons = None

        # Pygame components
        self.screen = None
        self.clock = None
        self.pygame_initialized = False

        # Constantes del juego
        self.LCD_WIDTH = 16
        self.LCD_HEIGHT = 2
        self.MAX_OBSTACLES = 8
        self.PLAYER_X = 1
        self.INITIAL_SPEED = 0.5  # segundos
        self.MIN_SPEED = 0.15

        # Variables del juego
        self.player_y = 0  # 0=top lane, 1=bottom lane
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.game_speed = self.INITIAL_SPEED
        self.obstacles = []  # Lista de {'x': int, 'y': int}
        self.scroll_counter = 0

        # Control de tiempo
        self.last_move_time = time.time()
        self.last_button_time = time.time()
        self.button_debounce = 0.15

        # Pygame específico
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 400
        self.CELL_WIDTH = 50
        self.CELL_HEIGHT = 80
        self.game_area_x = 100
        self.game_area_y = 50
        self.game_area_width = self.LCD_WIDTH * self.CELL_WIDTH
        self.game_area_height = self.LCD_HEIGHT * self.CELL_HEIGHT

        # Animaciones
        self.player_animation_offset = 0
        self.background_scroll = 0

        # Estadísticas y tiempo
        self.total_games = 0
        self.best_score = 0
        self.game_start_time = None
        self.total_lane_changes = 0
        self.obstacles_dodged = 0

        # Colores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 100, 100)
        self.GREEN = (100, 255, 100)
        self.BLUE = (100, 150, 255)
        self.YELLOW = (255, 255, 100)
        self.PURPLE = (200, 100, 255)
        self.ORANGE = (255, 165, 0)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.CYAN = (100, 255, 255)

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        try:
            if not self.arduino.connected:
                self.logger.log_game_event("HARDWARE", "Arduino no conectado", "ERROR")
                print("❌ Arduino no conectado")
                return False

            self.logger.log_game_event("HARDWARE", "Inicializando hardware Two-Lane Runner...")
            print("🏃 Inicializando hardware Two-Lane Runner...")

            # Inicializar LCD
            self.lcd = LCDController(self.arduino)
            self.logger.log_game_event("HARDWARE", "LCD inicializado correctamente")
            print("✅ LCD inicializado")

            # Crear caracteres personalizados específicos del juego
            self._create_custom_characters()
            self.logger.log_game_event("HARDWARE", "Caracteres personalizados creados")
            print("✅ Caracteres personalizados creados")

            # Inicializar botones
            self.buttons = ButtonReader(self.arduino)
            self.logger.log_game_event("HARDWARE", "Botones inicializados correctamente")
            print("✅ Botones inicializados")

            # Inicializar Pygame
            self._initialize_pygame()
            self.logger.log_game_event("HARDWARE", "Pygame inicializado correctamente")
            print("✅ Pygame inicializado")

            return True

        except Exception as e:
            self.logger.log_game_event("HARDWARE", f"Error inicializando hardware: {e}", "ERROR")
            print(f"❌ Error inicializando hardware: {e}")
            return False

    def _create_custom_characters(self):
        """Crear caracteres personalizados para Two-Lane Runner"""
        if not self.lcd:
            return

        try:
            # Carácter del jugador (corredor)
            player_char = [
                0b01110,  # ┌─┬─┐
                0b01110,  # │ │ │ (cabeza)
                0b00100,  # └─┼─┘
                0b01110,  # ┌─┼─┐ (cuerpo)
                0b10101,  # │ │ │
                0b00100,  # └─┼─┘
                0b01010,  # ╱ │ ╲ (piernas)
                0b10001   # ╱  │  ╲
            ]

            # Carácter del obstáculo
            obstacle_char = [
                0b00000,
                0b01110,  # ┌───┐
                0b11111,  # │███│
                0b11111,  # │███│
                0b11111,  # │███│
                0b01110,  # └───┘
                0b00000,
                0b00000
            ]

            # Programar caracteres personalizados en el LCD
            # Carácter 0: Jugador
            self.lcd._command(0x40)  # Dirección del carácter 0
            for line in player_char:
                self.lcd._write(line)

            # Carácter 1: Obstáculo
            self.lcd._command(0x48)  # Dirección del carácter 1
            for line in obstacle_char:
                self.lcd._write(line)

        except Exception as e:
            print(f"❌ Error creando caracteres personalizados: {e}")

    def _initialize_pygame(self):
        """Inicializar componentes de Pygame"""
        if not self.pygame_initialized:
            pygame.init()
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            pygame.display.set_caption("Two-Lane Runner - Arduino + Python")

            # Fuentes
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

            self.clock = pygame.time.Clock()
            self.pygame_initialized = True

    def start_game(self) -> bool:
        """Iniciar juego"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self._reset_game_state()

            # Registrar inicio del juego
            self.game_start_time = time.time()
            self.logger.log_game_event("GAME", "🏃 Juego iniciado - Esperando al jugador...")

            # Mostrar pantalla de bienvenida
            self._show_welcome_screen()

            # Iniciar hilo del juego
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()

            print("🏃 Two-Lane Runner iniciado correctamente")
            return True

        except Exception as e:
            self.logger.log_game_event("GAME", f"Error iniciando juego: {e}", "ERROR")
            print(f"❌ Error iniciando juego: {e}")
            return False

    def stop_game(self):
        """Detener juego"""
        try:
            self.logger.log_game_event("GAME", "🛑 Deteniendo juego...")
            print("🛑 Deteniendo Two-Lane Runner...")
            self.running = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            if self.lcd:
                self.lcd.clear()

            if self.pygame_initialized:
                try:
                    pygame.display.quit()
                    pygame.quit()
                    self.pygame_initialized = False
                    self.logger.log_game_event("HARDWARE", "Pygame cerrado correctamente")
                except Exception as e:
                    self.logger.log_game_event("HARDWARE", f"Error cerrando Pygame: {e}", "WARNING")
                    try:
                        pygame.quit()
                        self.pygame_initialized = False
                    except:
                        pass

            # Log final del juego
            if self.game_start_time:
                total_duration = time.time() - self.game_start_time
                self.logger.log_game_event("GAME", f"✅ Juego detenido - Duración total: {total_duration:.2f}s")

            print("✅ Two-Lane Runner detenido")

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
            'player_position': (self.PLAYER_X, self.player_y),
            'player_lane': 'Superior' if self.player_y == 0 else 'Inferior',
            'obstacles_count': len(self.obstacles),
            'current_speed': self.game_speed,
            'speed_percentage': round((self.INITIAL_SPEED - self.game_speed) / (self.INITIAL_SPEED - self.MIN_SPEED) * 100, 1),
            'total_games': self.total_games,
            'best_score': self.best_score,
            'hardware_initialized': self.lcd is not None and self.buttons is not None
        }

    def _reset_game_state(self):
        """Resetear estado del juego"""
        self.player_y = 0
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.game_speed = self.INITIAL_SPEED
        self.obstacles = []
        self.scroll_counter = 0
        self.last_move_time = time.time()
        
        # Reset estadísticas
        self.total_lane_changes = 0
        self.obstacles_dodged = 0
        
        self.logger.log_game_event("GAME", "🔄 Estado del juego reseteado")

    def _show_welcome_screen(self):
        """Mostrar pantalla de bienvenida"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(3, 0)
            self.lcd.print("TWO LANES")
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
        self.logger.log_game_event("GAME", "🎯 Gameplay iniciado - Jugador en movimiento")
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

                time.sleep(0.01)

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
                    time.sleep(0.3)
                    break

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

            if button == 'UP':
                if not self.game_over and not self.game_paused:
                    old_y = self.player_y
                    self.player_y = 0
                    if old_y != self.player_y:
                        self.total_lane_changes += 1
                        self.logger.log_game_event("INPUT", f"Jugador cambió al carril SUPERIOR (total cambios: {self.total_lane_changes})")
            elif button == 'DOWN':
                if not self.game_over and not self.game_paused:
                    old_y = self.player_y
                    self.player_y = 1
                    if old_y != self.player_y:
                        self.total_lane_changes += 1
                        self.logger.log_game_event("INPUT", f"Jugador cambió al carril INFERIOR (total cambios: {self.total_lane_changes})")

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

    def _update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.game_paused:
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.game_speed:
            return

        self.last_move_time = current_time

        # Mover todos los obstáculos hacia la izquierda
        for obstacle in self.obstacles[:]:  # Copia para poder modificar durante iteración
            obstacle['x'] -= 1

            # Verificar colisión con jugador
            if obstacle['x'] == self.PLAYER_X and obstacle['y'] == self.player_y:
                self._handle_collision(obstacle)
                return

            # Remover obstáculos que salen de pantalla y aumentar puntuación
            if obstacle['x'] < 0:
                self.obstacles.remove(obstacle)
                self.score += 1
                self.obstacles_dodged += 1
                self.logger.log_game_event("SCORE", f"🎯 Obstáculo esquivado - Score: {self.score} | Total esquivados: {self.obstacles_dodged}")

                # Aumentar velocidad cada 10 puntos
                if self.score % 10 == 0:
                    old_speed = self.game_speed
                    self.game_speed = max(self.MIN_SPEED, self.game_speed - 0.03)
                    self.logger.log_game_event("SPEED", f"⚡ Velocidad aumentada de {old_speed:.2f}s a {self.game_speed:.2f}s")

        # Generar nuevos obstáculos
        self.scroll_counter += 1
        if self.scroll_counter >= 3 and len(self.obstacles) < self.MAX_OBSTACLES:
            self.scroll_counter = 0
            self._generate_new_obstacle()

        self._draw_game()
    
    def _handle_collision(self, obstacle):
        """Manejar colisión con obstáculo"""
        game_duration = time.time() - self.game_start_time if self.game_start_time else 0
        lane_name = "SUPERIOR" if self.player_y == 0 else "INFERIOR"
        
        self.logger.log_player_death_two_lanes(
            reason="Colisión con obstáculo",
            lane=lane_name,
            final_score=self.score,
            obstacles_dodged=self.obstacles_dodged,
            lane_changes=self.total_lane_changes,
            game_duration=game_duration,
            game_speed=self.game_speed
        )
        
        self.game_over = True
        self._show_game_over()

    def _generate_new_obstacle(self):
        """Generar nuevo obstáculo asegurando que siempre haya un carril libre"""
        # Verificar qué carriles están bloqueados en el borde derecho
        rightmost_obstacles = [obs for obs in self.obstacles if obs['x'] == self.LCD_WIDTH - 1]

        blocked_lanes = [obs['y'] for obs in rightmost_obstacles]
        available_lanes = [y for y in [0, 1] if y not in blocked_lanes]

        # Si no hay carriles disponibles, forzar uno (no debería pasar)
        if not available_lanes:
            available_lanes = [0, 1]

        # Seleccionar carril aleatoriamente de los disponibles
        new_y = random.choice(available_lanes)

        # Crear nuevo obstáculo
        new_obstacle = {'x': self.LCD_WIDTH - 1, 'y': new_y}
        self.obstacles.append(new_obstacle)
        
        # Log de nuevo obstáculo ocasionalmente
        if len(self.obstacles) % 3 == 0:
            lane_name = "SUPERIOR" if new_y == 0 else "INFERIOR"
            self.logger.log_game_event("OBSTACLE", f"🚧 Nuevo obstáculo generado en carril {lane_name} (total activos: {len(self.obstacles)})")


    def _draw_game(self):
        """Dibujar estado del juego en LCD"""
        if not self.lcd:
            return

        self.lcd.clear()

        # Dibujar jugador
        self.lcd.set_cursor(self.PLAYER_X, self.player_y)
        self.lcd.write_custom_char(0)  # Carácter del jugador

        # Dibujar obstáculos
        for obstacle in self.obstacles:
            if 0 <= obstacle['x'] < self.LCD_WIDTH:
                self.lcd.set_cursor(obstacle['x'], obstacle['y'])
                self.lcd.write_custom_char(1)  # Carácter del obstáculo

        # Mostrar puntuación
        if self.LCD_WIDTH >= 14:
            self.lcd.set_cursor(self.LCD_WIDTH - 3, 0)
            self.lcd.print(str(self.score))

    def _show_pause_screen(self):
        """Mostrar pantalla de pausa"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(4, 0)
            self.lcd.print("PAUSED")
            self.lcd.set_cursor(2, 1)
            self.lcd.print(f"Score: {self.score}")

    def _show_game_over(self):
        """Mostrar pantalla de game over"""
        if self.lcd:
            self.lcd.clear()
            self.lcd.set_cursor(3, 0)
            self.lcd.print("GAME OVER")
            self.lcd.set_cursor(0, 1)
            self.lcd.print(f"Score: {self.score}")

        # Actualizar estadísticas
        self.total_games += 1
        if self.score > self.best_score:
            self.best_score = self.score
            
        self.logger.log_game_event("GAME", f"💀 GAME OVER mostrado - Score final: {self.score}")

    def _draw_pygame_visualization(self):
        """Dibujar visualización completa en Pygame"""
        if not self.pygame_initialized:
            return

        # Fondo animado
        self._draw_background()

        # Elementos del juego
        self._draw_obstacles_pygame()
        self._draw_player_pygame()

        # Interfaz de usuario
        self._draw_ui()

        # Efectos especiales si hay colisión
        if self.game_over:
            self._draw_collision_effect()

    def _draw_background(self):
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

        # Línea central divisoria (línea punteada)
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

    def _draw_player_pygame(self):
        """Dibujar jugador en Pygame"""
        # Posición del jugador
        player_x = self.game_area_x + self.PLAYER_X * self.CELL_WIDTH + self.CELL_WIDTH // 2
        player_y = self.game_area_y + self.player_y * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

        # Animación de movimiento
        self.player_animation_offset += 0.3
        bounce = math.sin(self.player_animation_offset) * 3

        # Cuerpo del jugador
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

        # Piernas
        pygame.draw.line(self.screen, self.GREEN,
                        (player_x - 5, player_y + 15 + bounce),
                        (player_x - 8, player_y + 35 + bounce), 4)
        pygame.draw.line(self.screen, self.GREEN,
                        (player_x + 5, player_y + 15 + bounce),
                        (player_x + 8, player_y + 35 + bounce), 4)

    def _draw_obstacles_pygame(self):
        """Dibujar obstáculos en Pygame"""
        for obstacle in self.obstacles:
            if 0 <= obstacle['x'] < self.LCD_WIDTH:
                screen_x = self.game_area_x + obstacle['x'] * self.CELL_WIDTH + self.CELL_WIDTH // 2
                screen_y = self.game_area_y + obstacle['y'] * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

                # Obstáculo principal
                pygame.draw.circle(self.screen, self.RED, (screen_x, screen_y), 20)
                pygame.draw.circle(self.screen, self.WHITE, (screen_x, screen_y), 20, 3)

                # Patrón interior
                pygame.draw.circle(self.screen, self.ORANGE, (screen_x, screen_y), 12)
                pygame.draw.circle(self.screen, self.YELLOW, (screen_x, screen_y), 6)

                # Efecto de peligro (rayos rotativos)
                for i in range(3):
                    angle = time.time() * 5 + i * 2.1
                    spike_x = screen_x + math.cos(angle) * 25
                    spike_y = screen_y + math.sin(angle) * 25
                    pygame.draw.line(self.screen, self.RED,
                                   (screen_x, screen_y), (spike_x, spike_y), 2)

    def _draw_ui(self):
        """Dibujar interfaz de usuario"""
        # Título
        title_surface = self.font_large.render("TWO-LANE RUNNER", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 25))
        self.screen.blit(title_surface, title_rect)

        # Estado de conexión
        connection_color = self.GREEN if self.arduino.connected else self.RED
        connection_text = "CONECTADO" if self.arduino.connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (20, 20))

        # Información del juego
        info_y = self.game_area_y + self.game_area_height + 20

        # Puntuación
        score_surface = self.font_medium.render(f"Puntuación: {self.score}", True, self.WHITE)
        self.screen.blit(score_surface, (self.game_area_x, info_y))

        # Velocidad
        speed_percentage = (self.INITIAL_SPEED - self.game_speed) / (self.INITIAL_SPEED - self.MIN_SPEED) * 100
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
        stats_surface = self.font_small.render(f"Partidas: {self.total_games} | Mejor: {self.best_score} | Obstáculos: {len(self.obstacles)}", True, self.WHITE)
        self.screen.blit(stats_surface, (self.game_area_x, stats_y))

        # Controles
        controls_y = self.WINDOW_HEIGHT - 60
        controls = [
            "Controles Arduino: ↑↓ (cambiar carril) | SELECT (pausa)",
            "Controles PC: ↑↓ (mover) | R (restart) | P (pausa) | ESC (salir)"
        ]

        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, self.GRAY)
            self.screen.blit(control_surface, (20, controls_y + i * 20))

        # Barra de velocidad visual
        self._draw_speed_bar(speed_percentage)

    def _draw_speed_bar(self, speed_percentage):
        """Dibujar barra visual de velocidad"""
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
            if speed_percentage < 50:
                color = self.GREEN
            elif speed_percentage < 80:
                color = self.YELLOW
            else:
                color = self.RED

            pygame.draw.rect(self.screen, color,
                           (speed_bar_x, speed_bar_y, fill_width, speed_bar_height))

        # Borde de la barra
        pygame.draw.rect(self.screen, self.WHITE,
                        (speed_bar_x, speed_bar_y, speed_bar_width, speed_bar_height), 2)

        # Etiqueta
        speed_label = self.font_small.render("Velocidad", True, self.WHITE)
        self.screen.blit(speed_label, (speed_bar_x, speed_bar_y - 25))

    def _draw_collision_effect(self):
        """Dibujar efecto de colisión"""
        # Efecto de flash rojo
        flash_alpha = int(abs(math.sin(time.time() * 10)) * 100)
        flash_surface = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        flash_surface.set_alpha(flash_alpha)
        flash_surface.fill(self.RED)
        self.screen.blit(flash_surface, (0, 0))

    def _handle_pygame_events(self):
        """Manejar eventos de Pygame"""
        if not self.pygame_initialized:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.logger.log_game_event("INPUT", "Salida solicitada desde Pygame")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.logger.log_game_event("INPUT", "Escape presionado - saliendo del juego")
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.logger.log_game_event("INPUT", "Reset solicitado desde Pygame")
                    self._reset_game_state()
                    self._draw_game()
                elif event.key == pygame.K_p and not self.game_over:
                    self.game_paused = not self.game_paused
                    if self.game_paused:
                        self.logger.log_game_event("INPUT", "Pausa solicitada desde Pygame")
                        self._show_pause_screen()
                    else:
                        self.logger.log_game_event("INPUT", "Reanudación solicitada desde Pygame")
                        self._draw_game()
                elif event.key == pygame.K_UP and not self.game_over and not self.game_paused:
                    old_y = self.player_y
                    self.player_y = 0
                    if old_y != self.player_y:
                        self.total_lane_changes += 1
                        self.logger.log_game_event("INPUT", f"Tecla UP - Carril SUPERIOR (Pygame - total cambios: {self.total_lane_changes})")
                elif event.key == pygame.K_DOWN and not self.game_over and not self.game_paused:
                    old_y = self.player_y
                    self.player_y = 1
                    if old_y != self.player_y:
                        self.total_lane_changes += 1
                        self.logger.log_game_event("INPUT", f"Tecla DOWN - Carril INFERIOR (Pygame - total cambios: {self.total_lane_changes})")

        # Manejar cierre de ventana correctamente
        return True
