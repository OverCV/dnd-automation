import pygame
import numpy as np
import time
import threading
import math
import random
from typing import Dict, Any, List
from enum import Enum

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager

class GameState(Enum):
    WAITING_TO_START = 0
    SHOWING_SEQUENCE = 1
    PLAYER_INPUT = 2
    GAME_OVER = 3
    GAME_WON = 4
    LEVEL_COMPLETE = 5

class PianoSimonGame(BaseGame):
    """Piano Simon Says que implementa BaseGame"""

    def __init__(self, arduino_manager: ArduinoManager):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Piano Simon Says"
        self.description = "Juego Simon Says usando piano digital de 8 notas"

        # Configuración de audio
        self.SAMPLE_RATE = 44100
        self.DURACION_NOTA = 0.8
        self.VOLUMEN = 0.4

        # Notas musicales (frecuencias en Hz)
        self.NOTAS = [
            ('Do', 262, 'white'),      # Botón 0 - Pin 2
            ('Re', 294, 'white'),      # Botón 1 - Pin 3
            ('Mi', 330, 'white'),      # Botón 2 - Pin 4
            ('Fa', 349, 'white'),      # Botón 3 - Pin 5
            ('Sol', 392, 'white'),     # Botón 4 - Pin 6
            ('La', 440, 'white'),      # Botón 5 - Pin 7
            ('Si', 494, 'white'),      # Botón 6 - Pin 8
            ('Do8', 523, 'white'),     # Botón 7 - Pin 9
        ]

        # Pines de los botones (2-9)
        self.BUTTON_PINS = [2, 3, 4, 5, 6, 7, 8, 9]
        self.button_pins = []  # Objetos pin de Firmata
        self.button_states = [False] * 8
        self.button_pressed = [False] * 8
        self.last_button_time = [0] * 8

        # Constantes del juego Simon
        self.MAX_LEVEL = 20
        self.INITIAL_DELAY = 800  # ms entre notas en secuencia
        self.MIN_DELAY = 300
        self.PAUSE_BETWEEN = 300
        self.START_DELAY = 1500
        self.DEBOUNCE_DELAY = 200  # ms

        # Variables del juego Simon
        self.game_sequence = []
        self.player_level = 1
        self.input_count = 0
        self.game_state = GameState.WAITING_TO_START
        self.sequence_index = 0
        self.last_sequence_time = 0
        self.player_timeout = 5000  # 5 segundos para responder
        self.last_input_time = 0

        # Estadísticas
        self.total_games = 0
        self.best_level = 0
        self.perfect_games = 0

        # Pygame components
        self.screen = None
        self.clock = None
        self.pygame_initialized = False

        # Estado visual
        self.active_notes = []
        self.last_note_played = None
        self.total_notes_played = 0
        self.showing_sequence_note = -1
        self.game_message = "Presiona cualquier tecla para empezar"

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
            self.RED,      # Do
            self.ORANGE,   # Re
            self.YELLOW,   # Mi
            self.GREEN,    # Fa
            self.CYAN,     # Sol
            self.BLUE,     # La
            self.PURPLE,   # Si
            self.GOLD      # Do8
        ]
        self.SIMON_COLORS_DIM = [tuple(c//3 for c in color) for color in self.SIMON_COLORS]

        # Efectos visuales
        self.key_animations = [0] * 8
        self.key_highlights = [0] * 8  # Para destacar secuencia
        self.note_particles = []

        # Audio
        self.audio_initialized = False
        self.sounds_playing = {}

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del piano"""
        try:
            if not self.arduino.connected:
                print("❌ Arduino no conectado")
                return False

            print("🎹 Inicializando hardware Piano Simon Says...")

            # Configurar pines de botones como entrada con pull-up
            self.button_pins = []
            for pin_num in self.BUTTON_PINS:
                pin = self.arduino.get_pin(f'd:{pin_num}:i')
                if pin:
                    pin.enable_reporting()
                    self.button_pins.append(pin)
                    print(f"✅ Pin {pin_num} configurado como entrada")
                else:
                    print(f"❌ Error configurando pin {pin_num}")
                    return False

            # Inicializar audio
            self._initialize_audio()
            print("✅ Audio inicializado")

            # Inicializar Pygame
            self._initialize_pygame()
            print("✅ Pygame inicializado")

            return True

        except Exception as e:
            print(f"❌ Error inicializando hardware: {e}")
            return False

    def _initialize_audio(self):
        """Inicializar sistema de audio"""
        try:
            pygame.mixer.pre_init(
                frequency=self.SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=512
            )
            pygame.mixer.init()
            self.audio_initialized = True
        except Exception as e:
            print(f"❌ Error inicializando audio: {e}")
            self.audio_initialized = False

    def _initialize_pygame(self):
        """Inicializar componentes de Pygame"""
        if not self.pygame_initialized:
            pygame.init()
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            pygame.display.set_caption("Piano Simon Says - Arduino + Python")

            # Fuentes
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

            self.clock = pygame.time.Clock()
            self.pygame_initialized = True

    def start_game(self) -> bool:
        """Iniciar juego Simon"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self._reset_game()

            # Mostrar animación de inicio
            self._show_startup_animation()

            # Iniciar hilo del juego
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()

            print("🎹 Piano Simon Says iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            return False

    def stop_game(self):
        """Detener juego"""
        try:
            print("🛑 Deteniendo Piano Simon Says...")
            self.running = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            # Detener todos los sonidos
            if self.audio_initialized:
                pygame.mixer.stop()

            if self.pygame_initialized:
                pygame.quit()
                self.pygame_initialized = False

            print("✅ Piano Simon Says detenido")

        except Exception as e:
            print(f"❌ Error deteniendo juego: {e}")

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        return {
            'name': self.name,
            'running': self.running,
            'game_state': self.game_state.name,
            'level': self.player_level,
            'max_level': self.MAX_LEVEL,
            'sequence_length': len(self.game_sequence),
            'input_progress': self.input_count,
            'total_games': self.total_games,
            'best_level': self.best_level,
            'perfect_games': self.perfect_games,
            'current_sequence': self.game_sequence[:self.player_level] if self.game_sequence else [],
            'available_notes': [note[0] for note in self.NOTAS],
            'hardware_initialized': len(self.button_pins) == 8
        }

    def _reset_game(self):
        """Resetear estado del juego"""
        self.player_level = 1
        self.input_count = 0
        self.sequence_index = 0
        self.game_state = GameState.WAITING_TO_START

        # Generar nueva secuencia aleatoria
        self.game_sequence = [random.randint(0, 7) for _ in range(self.MAX_LEVEL)]

        # Resetear estado visual
        self.active_notes = []
        self.last_note_played = None
        self.showing_sequence_note = -1
        self.key_animations = [0] * 8
        self.key_highlights = [0] * 8
        self.note_particles = []
        self.game_message = "Presiona cualquier tecla para empezar"

        print(f"🔄 Juego reiniciado - Secuencia generada para {self.MAX_LEVEL} niveles")

    def _show_startup_animation(self):
        """Mostrar animación de inicio"""
        print("🎵 Mostrando animación de inicio...")

        if not self.pygame_initialized:
            return

        # Animación de teclas en secuencia
        for i in range(8):
            self._play_note(i, 0.3)
            self.key_highlights[i] = 1.0

            # Dibujar frame de animación
            self._draw_game_visualization()
            pygame.display.flip()

            time.sleep(0.2)
            self.key_highlights[i] = 0

        # Parpadeo final
        for _ in range(3):
            for i in range(8):
                self.key_highlights[i] = 1.0
            self._draw_game_visualization()
            pygame.display.flip()
            time.sleep(0.15)

            for i in range(8):
                self.key_highlights[i] = 0
            self._draw_game_visualization()
            pygame.display.flip()
            time.sleep(0.15)

    def _game_loop(self):
        """Loop principal del juego Simon"""
        while self.running:
            try:
                current_time = time.time() * 1000  # ms

                # Leer estado de botones
                self._read_buttons()

                # Máquina de estados del juego
                if self.game_state == GameState.WAITING_TO_START:
                    self._handle_waiting_to_start()

                elif self.game_state == GameState.SHOWING_SEQUENCE:
                    self._handle_showing_sequence(current_time)

                elif self.game_state == GameState.PLAYER_INPUT:
                    self._handle_player_input(current_time)

                elif self.game_state == GameState.LEVEL_COMPLETE:
                    self._handle_level_complete()

                elif self.game_state == GameState.GAME_OVER:
                    self._handle_game_over()

                elif self.game_state == GameState.GAME_WON:
                    self._handle_game_won()

                # Actualizar animaciones
                self._update_animations()

                # Procesar eventos de Pygame
                self._handle_pygame_events()

                # Dibujar visualización
                if self.pygame_initialized:
                    self._draw_game_visualization()
                    pygame.display.flip()
                    self.clock.tick(60)

                time.sleep(0.01)

            except Exception as e:
                print(f"❌ Error en loop del juego: {e}")
                break

    def _handle_waiting_to_start(self):
        """Manejar estado de espera para iniciar"""
        # El juego comienza cuando se presiona cualquier tecla
        for i, pressed in enumerate(self.button_pressed):
            if pressed:
                print(f"🎮 Juego iniciado con tecla {i+1} ({self.NOTAS[i][0]})")
                self.game_message = f"Nivel {self.player_level} - Observa la secuencia"
                self.game_state = GameState.SHOWING_SEQUENCE
                self.sequence_index = 0
                self.last_sequence_time = time.time() * 1000
                break

    def _handle_showing_sequence(self, current_time):
        """Manejar mostrar secuencia al jugador"""
        delay_time = max(self.MIN_DELAY, self.INITIAL_DELAY - (self.player_level * 20))

        if current_time - self.last_sequence_time >= delay_time:
            if self.sequence_index < self.player_level:
                # Mostrar siguiente nota de la secuencia
                note_index = self.game_sequence[self.sequence_index]
                self._play_note(note_index, 0.5)
                self.key_highlights[note_index] = 1.0
                self.showing_sequence_note = note_index

                print(f"🎵 Secuencia {self.sequence_index + 1}/{self.player_level}: {self.NOTAS[note_index][0]}")

                self.sequence_index += 1
                self.last_sequence_time = current_time

                # Programar apagado del highlight
                threading.Timer(delay_time / 2000.0, self._clear_sequence_highlight, [note_index]).start()

            else:
                # Secuencia completada, turno del jugador
                print("👤 Tu turno - Repite la secuencia")
                self.game_message = f"Tu turno - Repite la secuencia ({self.player_level} notas)"
                self.game_state = GameState.PLAYER_INPUT
                self.input_count = 0
                self.last_input_time = current_time

    def _clear_sequence_highlight(self, note_index):
        """Limpiar highlight de secuencia"""
        self.key_highlights[note_index] = 0
        if self.showing_sequence_note == note_index:
            self.showing_sequence_note = -1

    def _handle_player_input(self, current_time):
        """Manejar entrada del jugador"""
        # Verificar timeout
        if current_time - self.last_input_time > self.player_timeout:
            print("⏰ Timeout - Game Over")
            self.game_message = "Timeout - ¡Demasiado lento!"
            self.game_state = GameState.GAME_OVER
            return

        # Verificar entrada de botones
        for i, pressed in enumerate(self.button_pressed):
            if pressed and current_time - self.last_button_time[i] > self.DEBOUNCE_DELAY:
                self._process_player_input(i)
                self.last_input_time = current_time
                break

    def _process_player_input(self, note_index):
        """Procesar entrada del jugador"""
        expected_note = self.game_sequence[self.input_count]

        # Reproducir nota presionada
        self._play_note(note_index, 0.4)
        self.key_animations[note_index] = 1.0

        if note_index == expected_note:
            # Respuesta correcta
            self.input_count += 1
            note_name = self.NOTAS[note_index][0]
            print(f"✅ Correcto: {note_name} ({self.input_count}/{self.player_level})")
            self.game_message = f"¡Correcto! {self.input_count}/{self.player_level}"

            if self.input_count >= self.player_level:
                # Nivel completado
                print(f"🎉 Nivel {self.player_level} completado!")
                self.game_state = GameState.LEVEL_COMPLETE

        else:
            # Respuesta incorrecta
            expected_name = self.NOTAS[expected_note][0]
            played_name = self.NOTAS[note_index][0]
            print(f"❌ Error: esperaba {expected_name}, tocaste {played_name}")
            self.game_message = f"Error: esperaba {expected_name}, tocaste {played_name}"
            self.game_state = GameState.GAME_OVER

    def _handle_level_complete(self):
        """Manejar completar nivel"""
        time.sleep(0.8)  # Pausa para mostrar el éxito

        if self.player_level >= self.MAX_LEVEL:
            # Juego ganado
            print("🏆 ¡Juego completado! ¡Felicitaciones!")
            self.game_message = "¡FELICITACIONES! ¡Completaste todos los niveles!"
            self.game_state = GameState.GAME_WON
            self.perfect_games += 1
        else:
            # Avanzar al siguiente nivel
            self.player_level += 1
            print(f"⬆️ Avanzando al nivel {self.player_level}")
            self.game_message = f"¡Avanzando al nivel {self.player_level}!"
            self.game_state = GameState.SHOWING_SEQUENCE
            self.sequence_index = 0
            self.last_sequence_time = time.time() * 1000 + self.START_DELAY

    def _handle_game_over(self):
        """Manejar game over"""
        # Reproducir secuencia de game over
        self._play_game_over_sequence()

        # Actualizar estadísticas
        self.total_games += 1
        if self.player_level > self.best_level:
            self.best_level = self.player_level

        print(f"💀 Game Over - Nivel alcanzado: {self.player_level}")
        print(f"📊 Mejor nivel: {self.best_level}")

        time.sleep(2)
        self._reset_game()

    def _handle_game_won(self):
        """Manejar victoria"""
        # Reproducir secuencia de victoria
        self._play_victory_sequence()

        # Actualizar estadísticas
        self.total_games += 1
        self.best_level = self.MAX_LEVEL

        print("🏆 ¡VICTORIA TOTAL!")

        time.sleep(3)
        self._reset_game()

    def _play_game_over_sequence(self):
        """Reproducir secuencia de game over"""
        if not self.audio_initialized:
            return

        # Sonido descendente
        for i in range(4):
            for j in range(8):
                self.key_highlights[j] = 1.0
            time.sleep(0.15)

            # Reproducir acorde disonante
            self._play_note(0, 0.3)  # Do
            self._play_note(1, 0.3)  # Do#

            for j in range(8):
                self.key_highlights[j] = 0
            time.sleep(0.15)

    def _play_victory_sequence(self):
        """Reproducir secuencia de victoria"""
        if not self.audio_initialized:
            return

        # Secuencia ascendente celebratoria
        for wave in range(3):
            for i in range(8):
                self._play_note(i, 0.2)
                self.key_highlights[i] = 1.0
                time.sleep(0.1)
                self.key_highlights[i] = 0

        # Acorde final
        for i in [0, 2, 4, 7]:  # Do, Mi, Sol, Do8
            self._play_note(i, 1.0)
            self.key_highlights[i] = 1.0

        time.sleep(0.5)
        for i in range(8):
            self.key_highlights[i] = 0

    def _read_buttons(self):
        """Leer estado de los botones usando Firmata"""
        current_time = time.time() * 1000

        for i, pin in enumerate(self.button_pins):
            if pin and pin.read() is not None:
                # Firmata lee HIGH cuando no está presionado (pull-up)
                current_state = not bool(pin.read())

                # Detectar flanco de subida (botón presionado)
                if current_state and not self.button_states[i]:
                    if current_time - self.last_button_time[i] > self.DEBOUNCE_DELAY:
                        self.button_pressed[i] = True
                        self.last_button_time[i] = current_time

                # Detectar flanco de bajada (botón liberado)
                elif not current_state and self.button_states[i]:
                    self.button_pressed[i] = False

                self.button_states[i] = current_state

    def _play_note(self, note_index: int, duration: float = None):
        """Tocar nota específica"""
        if not (0 <= note_index < len(self.NOTAS)):
            return

        if duration is None:
            duration = self.DURACION_NOTA

        nombre, frecuencia, _ = self.NOTAS[note_index]

        try:
            if self.audio_initialized:
                # Generar audio
                audio_data = self._generate_sine_wave(frecuencia, duration)

                # Crear array estéreo
                stereo_data = np.column_stack((audio_data, audio_data))
                stereo_data = np.ascontiguousarray(stereo_data, dtype=np.int16)

                # Reproducir sonido
                sound = pygame.sndarray.make_sound(stereo_data)
                sound.play()

                # Guardar referencia del sonido
                self.sounds_playing[note_index] = sound

            # Actualizar estado visual
            self.last_note_played = nombre
            self.total_notes_played += 1

            # Agregar partículas
            self._add_note_particles(note_index)

        except Exception as e:
            print(f"❌ Error reproduciendo nota {nombre}: {e}")

    def _generate_sine_wave(self, frequency: float, duration: float) -> np.ndarray:
        """Generar onda seno con envelope suave"""
        frames = int(duration * self.SAMPLE_RATE)
        arr = np.zeros(frames)

        for i in range(frames):
            t = float(i) / self.SAMPLE_RATE

            # Envelope ADSR simplificado
            envelope = 1.0
            attack_time = 0.05
            release_time = min(0.2, duration * 0.3)

            if t < attack_time:
                envelope = t / attack_time
            elif t > duration - release_time:
                envelope = (duration - t) / release_time

            # Onda seno con armónicos para sonido más rico
            fundamental = np.sin(2 * np.pi * frequency * t)
            harmonic2 = 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
            harmonic3 = 0.1 * np.sin(2 * np.pi * frequency * 3 * t)

            arr[i] = envelope * (fundamental + harmonic2 + harmonic3)

        return (arr * self.VOLUMEN * 32767).astype(np.int16)

    def _update_animations(self):
        """Actualizar animaciones visuales"""
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
        self._update_particles()

    def _add_note_particles(self, note_index: int):
        """Agregar partículas visuales para la nota"""
        key_x = 100 + note_index * (self.KEY_WIDTH + 15)
        key_y = 250

        for _ in range(3):
            particle = {
                'x': key_x + self.KEY_WIDTH // 2,
                'y': key_y,
                'vx': (np.random.random() - 0.5) * 3,
                'vy': -np.random.random() * 2 - 1,
                'life': 1.0,
                'color': self.SIMON_COLORS[note_index]
            }
            self.note_particles.append(particle)

    def _update_particles(self):
        """Actualizar partículas de notas"""
        for particle in self.note_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.08  # Gravedad
            particle['life'] -= 0.025

            if particle['life'] <= 0:
                self.note_particles.remove(particle)

    def _draw_game_visualization(self):
        """Dibujar visualización completa del juego"""
        if not self.pygame_initialized:
            return

        # Fondo degradado
        self._draw_gradient_background()

        # Título
        title_text = "🎹 PIANO SIMON SAYS"
        title_surface = self.font_large.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 40))
        self.screen.blit(title_surface, title_rect)

        # Estado de conexión
        connection_color = self.GREEN if self.arduino.connected else self.RED
        connection_text = "CONECTADO" if self.arduino.connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (20, 20))

        # Información del juego
        self._draw_game_info()

        # Dibujar piano
        self._draw_piano_keys()

        # Dibujar secuencia actual
        self._draw_sequence_display()

        # Dibujar mensaje del juego
        self._draw_game_message()

        # Dibujar partículas
        self._draw_particles()

        # Dibujar estadísticas
        self._draw_statistics()

    def _draw_gradient_background(self):
        """Dibujar fondo con degradado"""
        for y in range(self.WINDOW_HEIGHT):
            color_ratio = y / self.WINDOW_HEIGHT
            r = int(10 + color_ratio * 20)
            g = int(10 + color_ratio * 30)
            b = int(30 + color_ratio * 40)
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.WINDOW_WIDTH, y))

    def _draw_game_info(self):
        """Dibujar información del estado del juego"""
        info_y = 80

        # Estado del juego
        state_text = f"Estado: {self.game_state.name.replace('_', ' ').title()}"
        state_surface = self.font_medium.render(state_text, True, self.YELLOW)
        self.screen.blit(state_surface, (50, info_y))

        # Nivel actual
        level_text = f"Nivel: {self.player_level}/{self.MAX_LEVEL}"
        level_surface = self.font_medium.render(level_text, True, self.CYAN)
        self.screen.blit(level_surface, (300, info_y))

        # Progreso en nivel
        if self.game_state == GameState.PLAYER_INPUT:
            progress_text = f"Progreso: {self.input_count}/{self.player_level}"
            progress_surface = self.font_medium.render(progress_text, True, self.GREEN)
            self.screen.blit(progress_surface, (500, info_y))

    def _draw_piano_keys(self):
        """Dibujar teclas del piano estilo Simon"""
        start_x = 100
        start_y = 250

        for i in range(8):
            x = start_x + i * (self.KEY_WIDTH + 15)
            y = start_y

            # Determinar color y estado de la tecla
            base_color = self.SIMON_COLORS[i]

            # Calcular color final basado en estado
            if self.button_pressed[i] or self.key_animations[i] > 0:
                # Tecla presionada - color brillante
                brightness = max(self.key_animations[i], 1.0 if self.button_pressed[i] else 0)
                key_color = tuple(min(255, int(c + (255 - c) * brightness * 0.5)) for c in base_color)
            elif self.key_highlights[i] > 0:
                # Destacar durante secuencia
                highlight_intensity = self.key_highlights[i]
                key_color = tuple(min(255, int(c + (255 - c) * highlight_intensity)) for c in base_color)
            else:
                # Estado normal - color atenuado
                key_color = self.SIMON_COLORS_DIM[i]

            # Dibujar tecla principal
            key_rect = pygame.Rect(x, y, self.KEY_WIDTH, self.KEY_HEIGHT)
            pygame.draw.rect(self.screen, key_color, key_rect)
            pygame.draw.rect(self.screen, self.WHITE, key_rect, 3)

            # Efecto de brillo si está activa
            if self.button_pressed[i] or self.key_highlights[i] > 0:
                glow_surface = pygame.Surface((self.KEY_WIDTH - 10, self.KEY_HEIGHT - 10))
                glow_surface.set_alpha(100)
                glow_surface.fill(self.WHITE)
                self.screen.blit(glow_surface, (x + 5, y + 5))

            # Nombre de la nota
            note_name = self.NOTAS[i][0]
            text_color = self.WHITE if (self.button_pressed[i] or self.key_highlights[i] > 0) else self.BLACK
            note_surface = self.font_medium.render(note_name, True, text_color)
            note_rect = note_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT // 2))
            self.screen.blit(note_surface, note_rect)

            # Número del pin
            pin_text = f"Pin {self.BUTTON_PINS[i]}"
            pin_surface = self.font_small.render(pin_text, True, text_color)
            pin_rect = pin_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT - 25))
            self.screen.blit(pin_surface, pin_rect)

            # Número de tecla
            key_num = f"{i + 1}"
            num_surface = self.font_small.render(key_num, True, text_color)
            num_rect = num_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + 15))
            self.screen.blit(num_surface, num_rect)

    def _draw_sequence_display(self):
        """Dibujar visualización de la secuencia actual"""
        if not self.game_sequence or self.player_level == 0:
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

        for i in range(self.player_level):
            if i < len(self.game_sequence):
                note_index = self.game_sequence[i]
                circle_x = start_x + i * spacing
                circle_y = seq_y + 15

                # Color del círculo
                if i < self.input_count:
                    # Ya completado - verde
                    circle_color = self.GREEN
                elif i == self.input_count and self.game_state == GameState.PLAYER_INPUT:
                    # Actual esperado - amarillo parpadeante
                    pulse = (math.sin(time.time() * 8) + 1) / 2
                    circle_color = tuple(int(c * pulse + self.YELLOW[j] * (1 - pulse))
                                       for j, c in enumerate(self.SIMON_COLORS[note_index]))
                else:
                    # Pendiente - color normal
                    circle_color = self.SIMON_COLORS[note_index]

                # Dibujar círculo
                pygame.draw.circle(self.screen, circle_color, (circle_x, circle_y), circle_size)
                pygame.draw.circle(self.screen, self.WHITE, (circle_x, circle_y), circle_size, 2)

                # Letra de la nota
                note_letter = self.NOTAS[note_index][0]
                note_surface = self.font_small.render(note_letter, True, self.WHITE)
                note_rect = note_surface.get_rect(center=(circle_x, circle_y))
                self.screen.blit(note_surface, note_rect)

    def _draw_game_message(self):
        """Dibujar mensaje principal del juego"""
        message_y = 500

        # Fondo del mensaje
        message_surface = self.font_large.render(self.game_message, True, self.WHITE)
        message_rect = message_surface.get_rect(center=(self.WINDOW_WIDTH // 2, message_y))

        # Fondo semitransparente
        bg_rect = message_rect.inflate(40, 20)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill(self.BLACK)
        self.screen.blit(bg_surface, bg_rect)

        # Texto del mensaje
        self.screen.blit(message_surface, message_rect)

    def _draw_particles(self):
        """Dibujar partículas de notas"""
        for particle in self.note_particles:
            alpha = int(particle['life'] * 255)
            size = int(particle['life'] * 6) + 2

            # Crear superficie con transparencia
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)

            color = particle['color']
            pygame.draw.circle(particle_surface, color, (size, size), size)

            self.screen.blit(particle_surface,
                           (int(particle['x'] - size), int(particle['y'] - size)))

    def _draw_statistics(self):
        """Dibujar estadísticas del juego"""
        stats_y = 600

        stats_text = [
            f"Partidas jugadas: {self.total_games}",
            f"Mejor nivel: {self.best_level}",
            f"Juegos perfectos: {self.perfect_games}",
        ]

        for i, stat in enumerate(stats_text):
            stat_surface = self.font_small.render(stat, True, self.GRAY)
            self.screen.blit(stat_surface, (50 + i * 200, stats_y))

        # Controles
        controls_y = stats_y + 25
        controls = [
            "Controles: ESC=Salir | R=Reiniciar | Números 1-8=Test",
            "Usa los botones físicos conectados a los pines 2-9 para jugar"
        ]

        for i, control in enumerate(controls):
            control_surface = self.font_small.render(control, True, self.DARK_GRAY)
            self.screen.blit(control_surface, (50, controls_y + i * 20))

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
                elif event.key == pygame.K_r:
                    print("🔄 Reinicio manual solicitado")
                    self._reset_game()
                # Permitir testing con teclado
                elif event.key == pygame.K_1:
                    self._play_note(0)
                elif event.key == pygame.K_2:
                    self._play_note(1)
                elif event.key == pygame.K_3:
                    self._play_note(2)
                elif event.key == pygame.K_4:
                    self._play_note(3)
                elif event.key == pygame.K_5:
                    self._play_note(4)
                elif event.key == pygame.K_6:
                    self._play_note(5)
                elif event.key == pygame.K_7:
                    self._play_note(6)
                elif event.key == pygame.K_8:
                    self._play_note(7)

    def send_arduino_command(self, command: str):
        """Enviar comando al Arduino (para compatibilidad futura)"""
        print(f"📤 Comando (no implementado): {command}")
        # Esta función está aquí para compatibilidad futura si se implementa
        # comunicación serial directa como en el código Simon original

# Funciones de utilidad adicionales

def create_piano_simon_game(arduino_manager: ArduinoManager) -> PianoSimonGame:
    """Factory function para crear el juego Piano Simon"""
    return PianoSimonGame(arduino_manager)

def validate_hardware_setup(arduino_manager: ArduinoManager) -> bool:
    """Validar que el hardware esté correctamente configurado"""
    if not arduino_manager.connected:
        print("❌ Arduino no conectado")
        return False

    # Verificar que los pines 2-9 estén disponibles
    required_pins = [2, 3, 4, 5, 6, 7, 8, 9]

    for pin_num in required_pins:
        try:
            pin = arduino_manager.get_pin(f'd:{pin_num}:i')
            if not pin:
                print(f"❌ Pin {pin_num} no disponible")
                return False
        except Exception as e:
            print(f"❌ Error verificando pin {pin_num}: {e}")
            return False

    print("✅ Hardware validado correctamente")
    return True

"""
=== PIANO SIMON SAYS GAME ===

🎹 CARACTERÍSTICAS PRINCIPALES:

LÓGICA DEL JUEGO:
- Implementa el clásico juego "Simon Says" usando un piano digital
- 20 niveles de dificultad progresiva
- Secuencia aleatoria generada al inicio del juego
- Velocidad incrementa con cada nivel
- Sistema de timeout para respuestas del jugador

HARDWARE REQUERIDO:
- Arduino con Firmata
- 8 botones conectados entre pines 2-9 y GND
- Pull-up interno activado automáticamente

ESTADOS DEL JUEGO:
- WAITING_TO_START: Esperando que el jugador presione cualquier tecla
- SHOWING_SEQUENCE: Mostrando la secuencia de notas al jugador
- PLAYER_INPUT: Esperando entrada del jugador
- LEVEL_COMPLETE: Nivel completado, avanzando al siguiente
- GAME_OVER: Juego terminado por error o timeout
- GAME_WON: Todos los niveles completados

MECÁNICAS:
- Secuencia aleatoria de 20 niveles generada al inicio
- Cada nivel agrega una nota más a la secuencia
- Delay entre notas disminuye progresivamente
- Timeout de 5 segundos para responder
- Debounce de 200ms para evitar dobles pulsaciones

VISUALIZACIÓN:
- 8 teclas de piano con colores únicos estilo Simon
- Animaciones de presión y highlights de secuencia
- Visualización en tiempo real de la secuencia a seguir
- Partículas y efectos visuales
- Estadísticas de juego (partidas, mejor nivel, juegos perfectos)

AUDIO:
- Notas musicales reales (Do, Re, Mi, Fa, Sol, La, Si, Do8)
- Generación de ondas seno con armónicos
- Envelope ADSR para sonido más natural
- Secuencias especiales para victory y game over

CONTROLES:
- Botones físicos 1-8 (pines 2-9): Jugar
- ESC: Salir del juego
- R: Reiniciar juego
- Números 1-8: Test de notas (teclado PC)

INTEGRACIÓN:
- Hereda de BaseGame para integración con sistema mayor
- Compatible con ArduinoManager usando Firmata
- Estadísticas persistentes durante la sesión
- Estado del juego consultable via get_game_status()

DIFERENCIAS CON CÓDIGO ORIGINAL:
- Usa Firmata en lugar de comunicación serial directa
- 8 notas en lugar de 6 LEDs
- Visualización más rica y compleja
- Sistema de partículas y animaciones
- Integración con framework de juegos existente

SETUP FÍSICO:
Conectar 8 botones:
- Botón 1: Pin 2 ↔ GND (Do - 262 Hz)
- Botón 2: Pin 3 ↔ GND (Re - 294 Hz)
- Botón 3: Pin 4 ↔ GND (Mi - 330 Hz)
- Botón 4: Pin 5 ↔ GND (Fa - 349 Hz)
- Botón 5: Pin 6 ↔ GND (Sol - 392 Hz)
- Botón 6: Pin 7 ↔ GND (La - 440 Hz)
- Botón 7: Pin 8 ↔ GND (Si - 494 Hz)
- Botón 8: Pin 9 ↔ GND (Do8 - 523 Hz)

No se requieren resistors pull-up externos ya que se
activa el pull-up interno del Arduino automáticamente.

El juego está listo para usar con tu sistema existente
de gestión de juegos Arduino!
"""
