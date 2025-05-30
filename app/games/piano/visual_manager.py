import pygame
import math
import time
import numpy as np
from typing import List, Dict, Any
from enum import Enum


class GameState(Enum):
    WAITING_TO_START = 0
    SHOWING_SEQUENCE = 1
    PLAYER_INPUT = 2
    GAME_OVER = 3
    GAME_WON = 4
    LEVEL_COMPLETE = 5


class PianoVisualManager:
    """Maneja toda la visualización y UI con Pygame del piano"""
    
    def __init__(self):
        # Configuración visual
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 700
        self.KEY_WIDTH = 120
        self.KEY_HEIGHT = 200
        
        # Colores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.RED = (255, 100, 100)
        self.GREEN = (100, 255, 100)
        self.BLUE = (100, 150, 255)
        self.YELLOW = (255, 255, 100)
        self.PURPLE = (200, 100, 255)
        self.ORANGE = (255, 165, 0)
        self.CYAN = (100, 255, 255)
        self.GOLD = (255, 215, 0)
        
        # Colores de teclas Simon
        self.SIMON_COLORS = [
            self.RED,    # Do
            self.ORANGE, # Re
            self.YELLOW, # Mi
            self.GREEN,  # Fa
            self.CYAN,   # Sol
            self.BLUE,   # La
            self.PURPLE, # Si
            self.GOLD,   # Do8
        ]
        self.SIMON_COLORS_DIM = [
            tuple(c // 3 for c in color) for color in self.SIMON_COLORS
        ]
        
        # Estado visual
        self.key_animations = [0] * 8
        self.key_highlights = [0] * 8
        self.note_particles = []
        self.showing_sequence_note = -1
        
        # Pygame components
        self.screen = None
        self.clock = None
        self.pygame_initialized = False
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        # Pines de botones para mostrar
        self.BUTTON_PINS = [9, 8, 7, 6, 5, 4, 3, 2]
        
        # NO inicializar Pygame automáticamente - solo cuando se use
        # self._initialize_pygame()
    
    def _initialize_pygame(self):
        """Inicializar componentes de Pygame"""
        if not self.pygame_initialized:
            try:
                pygame.init()
                self.screen = pygame.display.set_mode(
                    (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
                )
                pygame.display.set_caption("Piano Simon Says - Arduino + Python")
                
                # Fuentes
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 32)
                self.font_small = pygame.font.Font(None, 24)
                
                self.clock = pygame.time.Clock()
                self.pygame_initialized = True
                print("✅ Pygame inicializado correctamente")
            except Exception as e:
                print(f"❌ Error inicializando Pygame: {e}")
                self.pygame_initialized = False
    
    def mostrar_animacion_inicio(self, audio_manager):
        """Mostrar animación de inicio"""
        # Inicializar Pygame si no está inicializado
        if not self.pygame_initialized:
            self._initialize_pygame()
            
        if not self.pygame_initialized:
            print("❌ No se pudo inicializar Pygame para animación de inicio")
            return
            
        print("🎵 Mostrando animación de inicio...")
        
        # Animación de teclas en secuencia
        for i in range(8):
            if audio_manager:
                audio_manager.reproducir_nota(i, 0.3)
            self.key_highlights[i] = 1.0
            
            # Dibujar frame de animación
            self.dibujar_todo(
                game_state=GameState.WAITING_TO_START,
                game_message="Iniciando...",
                player_level=1,
                max_level=20,
                game_sequence=[],
                input_count=0,
                button_pressed=[False]*8,
                arduino_connected=True,
                total_games=0,
                best_level=0,
                perfect_games=0
            )
            pygame.display.flip()
            
            time.sleep(0.2)
            self.key_highlights[i] = 0
        
        # Parpadeo final
        for _ in range(3):
            for i in range(8):
                self.key_highlights[i] = 1.0
            self.dibujar_todo(
                game_state=GameState.WAITING_TO_START,
                game_message="¡Presiona cualquier tecla!",
                player_level=1,
                max_level=20,
                game_sequence=[],
                input_count=0,
                button_pressed=[False]*8,
                arduino_connected=True,
                total_games=0,
                best_level=0,
                perfect_games=0
            )
            pygame.display.flip()
            time.sleep(0.15)
            
            for i in range(8):
                self.key_highlights[i] = 0
            self.dibujar_todo(
                game_state=GameState.WAITING_TO_START,
                game_message="¡Presiona cualquier tecla!",
                player_level=1,
                max_level=20,
                game_sequence=[],
                input_count=0,
                button_pressed=[False]*8,
                arduino_connected=True,
                total_games=0,
                best_level=0,
                perfect_games=0
            )
            pygame.display.flip()
            time.sleep(0.15)
    
    def activar_highlight_nota(self, note_index: int):
        """Activar highlight para una nota específica"""
        if 0 <= note_index < 8:
            self.key_highlights[note_index] = 1.0
            self.showing_sequence_note = note_index
    
    def desactivar_highlight_nota(self, note_index: int):
        """Desactivar highlight para una nota específica"""
        if 0 <= note_index < 8:
            self.key_highlights[note_index] = 0
            if self.showing_sequence_note == note_index:
                self.showing_sequence_note = -1
    
    def activar_animacion_tecla(self, note_index: int):
        """Activar animación de presión de tecla"""
        if 0 <= note_index < 8:
            self.key_animations[note_index] = 1.0
            self.agregar_particulas_nota(note_index)
    
    def agregar_particulas_nota(self, note_index: int):
        """Agregar partículas visuales para la nota"""
        key_x = 100 + note_index * (self.KEY_WIDTH + 15)
        key_y = 250
        
        for _ in range(3):
            particle = {
                "x": key_x + self.KEY_WIDTH // 2,
                "y": key_y,
                "vx": (np.random.random() - 0.5) * 3,
                "vy": -np.random.random() * 2 - 1,
                "life": 1.0,
                "color": self.SIMON_COLORS[note_index],
            }
            self.note_particles.append(particle)
    
    def actualizar_animaciones(self):
        """Actualizar todas las animaciones visuales"""
        for i in range(8):
            # Animación de teclas presionadas
            if self.key_animations[i] > 0:
                self.key_animations[i] -= 0.08
                if self.key_animations[i] < 0:
                    self.key_animations[i] = 0
            
            # Highlights de secuencia
            if self.key_highlights[i] > 0:
                self.key_highlights[i] -= 0.05
                if self.key_highlights[i] < 0:
                    self.key_highlights[i] = 0
        
        # Actualizar partículas
        self._actualizar_particulas()
    
    def _actualizar_particulas(self):
        """Actualizar partículas de notas"""
        for particle in self.note_particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.08  # Gravedad
            particle["life"] -= 0.025
            
            if particle["life"] <= 0:
                self.note_particles.remove(particle)
    
    def dibujar_todo(self, game_state, game_message, player_level, max_level, 
                     game_sequence, input_count, button_pressed, arduino_connected,
                     total_games, best_level, perfect_games):
        """Dibujar toda la visualización del juego"""
        # Inicializar Pygame si no está inicializado
        if not self.pygame_initialized:
            self._initialize_pygame()
            
        if not self.pygame_initialized:
            return
        
        # Fondo degradado
        self._dibujar_fondo_degradado()
        
        # Título
        title_text = "🎹 PIANO SIMON SAYS"
        title_surface = self.font_large.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)
        
        # Estado de conexión
        connection_color = self.GREEN if arduino_connected else self.RED
        connection_text = "CONECTADO" if arduino_connected else "DESCONECTADO"
        conn_surface = self.font_small.render(
            f"Arduino: {connection_text}", True, connection_color
        )
        self.screen.blit(conn_surface, (20, 20))
        
        # Información del juego
        self._dibujar_info_juego(game_state, player_level, max_level, input_count)
        
        # Dibujar piano
        self._dibujar_teclas_piano(button_pressed)
        
        # Dibujar secuencia actual
        self._dibujar_display_secuencia(game_sequence, player_level, input_count, game_state)
        
        # Dibujar mensaje del juego
        self._dibujar_mensaje_juego(game_message)
        
        # Dibujar partículas
        self._dibujar_particulas()
        
        # Dibujar estadísticas
        self._dibujar_estadisticas(total_games, best_level, perfect_games)
    
    def _dibujar_fondo_degradado(self):
        """Dibujar fondo con degradado"""
        for y in range(self.WINDOW_HEIGHT):
            color_ratio = y / self.WINDOW_HEIGHT
            r = int(10 + color_ratio * 20)
            g = int(10 + color_ratio * 30)
            b = int(30 + color_ratio * 40)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.WINDOW_WIDTH, y))
    
    def _dibujar_info_juego(self, game_state, player_level, max_level, input_count):
        """Dibujar información del estado del juego"""
        info_y = 80
        
        # Estado del juego
        state_text = f"Estado: {game_state.name.replace('_', ' ').title()}"
        state_surface = self.font_medium.render(state_text, True, self.YELLOW)
        self.screen.blit(state_surface, (50, info_y))
        
        # Nivel actual
        level_text = f"Nivel: {player_level}/{max_level}"
        level_surface = self.font_medium.render(level_text, True, self.CYAN)
        self.screen.blit(level_surface, (300, info_y))
        
        # Progreso en nivel
        if game_state == GameState.PLAYER_INPUT:
            progress_text = f"Progreso: {input_count}/{player_level}"
            progress_surface = self.font_medium.render(progress_text, True, self.GREEN)
            self.screen.blit(progress_surface, (500, info_y))
    
    def _dibujar_teclas_piano(self, button_pressed):
        """Dibujar teclas del piano estilo Simon"""
        start_x = 100
        start_y = 250
        
        # Nombres de notas
        notas = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si", "Do8"]
        
        for i in range(8):
            x = start_x + i * (self.KEY_WIDTH + 15)
            y = start_y
            
            # Determinar color y estado de la tecla
            base_color = self.SIMON_COLORS[i]
            
            # Calcular color final basado en estado
            if button_pressed[i] or self.key_animations[i] > 0:
                # Tecla presionada - color brillante
                brightness = max(
                    self.key_animations[i], 1.0 if button_pressed[i] else 0
                )
                key_color = tuple(
                    min(255, int(c + (255 - c) * brightness * 0.5)) for c in base_color
                )
            elif self.key_highlights[i] > 0:
                # Destacar durante secuencia
                highlight_intensity = self.key_highlights[i]
                key_color = tuple(
                    min(255, int(c + (255 - c) * highlight_intensity))
                    for c in base_color
                )
            else:
                # Estado normal - color atenuado
                key_color = self.SIMON_COLORS_DIM[i]
            
            # Dibujar tecla principal
            key_rect = pygame.Rect(x, y, self.KEY_WIDTH, self.KEY_HEIGHT)
            pygame.draw.rect(self.screen, key_color, key_rect)
            pygame.draw.rect(self.screen, self.WHITE, key_rect, 3)
            
            # Efecto de brillo si está activa
            if button_pressed[i] or self.key_highlights[i] > 0:
                glow_surface = pygame.Surface(
                    (self.KEY_WIDTH - 10, self.KEY_HEIGHT - 10)
                )
                glow_surface.set_alpha(100)
                glow_surface.fill(self.WHITE)
                self.screen.blit(glow_surface, (x + 5, y + 5))
            
            # Nombre de la nota
            note_name = notas[i]
            text_color = (
                self.WHITE
                if (button_pressed[i] or self.key_highlights[i] > 0)
                else self.BLACK
            )
            note_surface = self.font_medium.render(note_name, True, text_color)
            note_rect = note_surface.get_rect(
                center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT // 2)
            )
            self.screen.blit(note_surface, note_rect)
            
            # Número del pin
            pin_text = f"Pin {self.BUTTON_PINS[i]}"
            pin_surface = self.font_small.render(pin_text, True, text_color)
            pin_rect = pin_surface.get_rect(
                center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT - 25)
            )
            self.screen.blit(pin_surface, pin_rect)
            
            # Número de tecla
            key_num = f"{i + 1}"
            num_surface = self.font_small.render(key_num, True, text_color)
            num_rect = num_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + 15))
            self.screen.blit(num_surface, num_rect)
    
    def _dibujar_display_secuencia(self, game_sequence, player_level, input_count, game_state):
        """Dibujar visualización de la secuencia actual"""
        if not game_sequence or player_level == 0:
            return
        
        seq_y = 180
        seq_x = 50
        
        # Título
        seq_title = "Secuencia a repetir:"
        title_surface = self.font_medium.render(seq_title, True, self.WHITE)
        self.screen.blit(title_surface, (seq_x, seq_y))
        
        # Mostrar secuencia del nivel actual
        circle_size = 25
        spacing = 35
        start_x = seq_x + 200
        
        for i in range(player_level):
            if i < len(game_sequence):
                note_index = game_sequence[i]
                circle_x = start_x + i * spacing
                circle_y = seq_y + 15
                
                # Color del círculo
                if i < input_count:
                    # Ya completado - verde
                    circle_color = self.GREEN
                elif i == input_count and game_state == GameState.PLAYER_INPUT:
                    # Actual esperado - amarillo parpadeante
                    pulse = (math.sin(time.time() * 8) + 1) / 2
                    circle_color = tuple(
                        int(c * pulse + self.YELLOW[j] * (1 - pulse))
                        for j, c in enumerate(self.SIMON_COLORS[note_index])
                    )
                else:
                    # Pendiente - color normal
                    circle_color = self.SIMON_COLORS[note_index]
                
                # Dibujar círculo
                pygame.draw.circle(
                    self.screen, circle_color, (circle_x, circle_y), circle_size
                )
                pygame.draw.circle(
                    self.screen, self.WHITE, (circle_x, circle_y), circle_size, 2
                )
                
                # Letra de la nota
                notas = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si", "Do8"]
                note_letter = notas[note_index]
                note_surface = self.font_small.render(note_letter, True, self.WHITE)
                note_rect = note_surface.get_rect(center=(circle_x, circle_y))
                self.screen.blit(note_surface, note_rect)
    
    def _dibujar_mensaje_juego(self, game_message):
        """Dibujar mensaje principal del juego"""
        message_y = 500
        
        # Fondo del mensaje
        message_surface = self.font_large.render(game_message, True, self.WHITE)
        message_rect = message_surface.get_rect(
            center=(self.WINDOW_WIDTH // 2, message_y)
        )
        
        # Fondo semitransparente
        bg_rect = message_rect.inflate(40, 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill(self.BLACK)
        self.screen.blit(bg_surface, bg_rect)
        
        # Texto del mensaje
        self.screen.blit(message_surface, message_rect)
    
    def _dibujar_particulas(self):
        """Dibujar partículas de notas"""
        for particle in self.note_particles:
            alpha = int(particle["life"] * 255)
            size = int(particle["life"] * 6) + 2
            
            # Crear superficie con transparencia
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)
            
            color = particle["color"]
            pygame.draw.circle(particle_surface, color, (size, size), size)
            
            self.screen.blit(
                particle_surface, (int(particle["x"] - size), int(particle["y"] - size))
            )
    
    def _dibujar_estadisticas(self, total_games, best_level, perfect_games):
        """Dibujar estadísticas del juego"""
        stats_y = 600
        
        stats_text = [
            f"Partidas jugadas: {total_games}",
            f"Mejor nivel: {best_level}",
            f"Juegos perfectos: {perfect_games}",
        ]
        
        for i, stat in enumerate(stats_text):
            stat_surface = self.font_small.render(stat, True, self.GRAY)
            self.screen.blit(stat_surface, (50 + i * 200, stats_y))
        
        # Controles
        controls_y = stats_y + 25
        controls = [
            "Controles: ESC=Salir | R=Reiniciar | Números 1-8=Test",
            "Usa los botones físicos conectados a los pines 2-9 para jugar",
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, self.DARK_GRAY)
            self.screen.blit(control_surface, (50, controls_y + i * 20))
    
    def procesar_eventos_pygame(self, callback_salir=None, callback_reiniciar=None, callback_test_nota=None):
        """Procesar eventos de Pygame con callbacks"""
        if not self.pygame_initialized:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if callback_salir:
                    callback_salir()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if callback_salir:
                        callback_salir()
                elif event.key == pygame.K_r:
                    if callback_reiniciar:
                        callback_reiniciar()
                # Testing con teclado
                elif event.key == pygame.K_1 and callback_test_nota:
                    callback_test_nota(0)
                elif event.key == pygame.K_2 and callback_test_nota:
                    callback_test_nota(1)
                elif event.key == pygame.K_3 and callback_test_nota:
                    callback_test_nota(2)
                elif event.key == pygame.K_4 and callback_test_nota:
                    callback_test_nota(3)
                elif event.key == pygame.K_5 and callback_test_nota:
                    callback_test_nota(4)
                elif event.key == pygame.K_6 and callback_test_nota:
                    callback_test_nota(5)
                elif event.key == pygame.K_7 and callback_test_nota:
                    callback_test_nota(6)
                elif event.key == pygame.K_8 and callback_test_nota:
                    callback_test_nota(7)
    
    def actualizar_display(self):
        """Actualizar display y mantener 60 FPS"""
        if self.pygame_initialized:
            pygame.display.flip()
            self.clock.tick(60)
    
    def cerrar(self):
        """Cerrar y limpiar recursos de Pygame de forma ROBUSTA"""
        print("🧹 Limpiando recursos visuales...")
        
        try:
            # Limpiar animaciones y partículas
            self.key_animations = [0.0] * 8
            self.key_highlights = [0.0] * 8
            self.note_particles.clear()
            
            # Cerrar Pygame solo si está inicializado
            if self.pygame_initialized:
                if self.screen:
                    # Llenar pantalla de negro antes de cerrar
                    self.screen.fill((0, 0, 0))
                    pygame.display.flip()
                
                # Cerrar Pygame limpiamente
                pygame.quit()
                self.pygame_initialized = False
                self.screen = None
                print("✅ Pygame cerrado correctamente")
            
        except Exception as e:
            print(f"⚠️ Error cerrando visual manager: {e}")
            # Forzar cierre si hay problemas
            try:
                pygame.quit()
            except:
                pass
            finally:
                self.pygame_initialized = False
                self.screen = None
    
    def is_initialized(self) -> bool:
        """¿Está el visual manager inicializado?"""
        return self.pygame_initialized and self.screen is not None
    
    def reiniciar_animaciones(self):
        """Reiniciar todas las animaciones"""
        self.key_animations = [0] * 8
        self.key_highlights = [0] * 8
        self.note_particles = []
        self.showing_sequence_note = -1 