import pygame
import numpy as np
import time
import threading
import math
from typing import Dict, Any

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager

class PianoDigitalGame(BaseGame):
    """Piano Digital que implementa BaseGame"""

    def __init__(self, arduino_manager: ArduinoManager):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Piano Digital"
        self.description = "Piano digital de 8 notas con visualización en tiempo real"

        # Configuración de audio
        self.SAMPLE_RATE = 44100
        self.DURACION_NOTA = 1.0
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
        self.button_press_time = [0] * 8

        # Pygame components
        self.screen = None
        self.clock = None
        self.pygame_initialized = False

        # Estado del piano
        self.active_notes = []  # Notas actualmente sonando
        self.last_note_played = None
        self.total_notes_played = 0

        # Configuración visual
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 600
        self.KEY_WIDTH = 100
        self.KEY_HEIGHT = 300
        self.BLACK_KEY_WIDTH = 60
        self.BLACK_KEY_HEIGHT = 180

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

        # Efectos visuales
        self.key_animations = [0] * 8  # Animación de presión de teclas
        self.wave_amplitude = [0] * 8  # Amplitud de onda visual
        self.note_particles = []  # Partículas de notas

        # Audio
        self.audio_initialized = False
        self.sounds_playing = {}

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del piano"""
        try:
            if not self.arduino.connected:
                print("❌ Arduino no conectado")
                return False

            print("🎹 Inicializando hardware Piano Digital...")

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
            pygame.display.set_caption("Piano Digital - Arduino + Python")

            # Fuentes
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

            self.clock = pygame.time.Clock()
            self.pygame_initialized = True

    def start_game(self) -> bool:
        """Iniciar piano"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self._reset_piano_state()

            # Mostrar pantalla de bienvenida
            self._show_welcome_message()

            # Iniciar hilo del piano
            self.game_thread = threading.Thread(target=self._piano_loop, daemon=True)
            self.game_thread.start()

            print("🎹 Piano Digital iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando piano: {e}")
            return False

    def stop_game(self):
        """Detener piano"""
        try:
            print("🛑 Deteniendo Piano Digital...")
            self.running = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            # Detener todos los sonidos
            if self.audio_initialized:
                pygame.mixer.stop()

            if self.pygame_initialized:
                pygame.quit()
                self.pygame_initialized = False

            print("✅ Piano Digital detenido")

        except Exception as e:
            print(f"❌ Error deteniendo piano: {e}")

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del piano"""
        return {
            'name': self.name,
            'running': self.running,
            'active_notes': len(self.active_notes),
            'last_note': self.last_note_played,
            'total_notes_played': self.total_notes_played,
            'button_states': self.button_states.copy(),
            'audio_initialized': self.audio_initialized,
            'hardware_initialized': len(self.button_pins) == 8,
            'available_notes': [note[0] for note in self.NOTAS]
        }

    def _reset_piano_state(self):
        """Resetear estado del piano"""
        self.active_notes = []
        self.last_note_played = None
        self.total_notes_played = 0
        self.button_states = [False] * 8
        self.button_pressed = [False] * 8
        self.key_animations = [0] * 8
        self.wave_amplitude = [0] * 8
        self.note_particles = []

    def _show_welcome_message(self):
        """Mostrar mensaje de bienvenida"""
        print("🎹 Piano Digital listo")
        print("🎵 Presiona los botones para tocar notas")

    def _piano_loop(self):
        """Loop principal del piano"""
        while self.running:
            try:
                # Leer estado de botones
                self._read_buttons()

                # Actualizar animaciones
                self._update_animations()

                # Procesar eventos de Pygame
                self._handle_pygame_events()

                # Dibujar visualización
                if self.pygame_initialized:
                    self._draw_piano_visualization()
                    pygame.display.flip()
                    self.clock.tick(60)

                time.sleep(0.01)

            except Exception as e:
                print(f"❌ Error en loop del piano: {e}")
                break
        pygame.quit()



    def _read_buttons(self):
        """Leer estado de los botones usando Firmata"""
        for i, pin in enumerate(self.button_pins):
            if pin and pin.read() is not None:
                # Firmata lee HIGH cuando no está presionado (pull-up)
                # LOW cuando está presionado
                current_state = not bool(pin.read())  # Invertir para que True = presionado

                # Detectar flanco de subida (botón presionado)
                if current_state and not self.button_states[i]:
                    self._play_note(i)
                    self.button_pressed[i] = True
                    self.button_press_time[i] = time.time()

                # Detectar flanco de bajada (botón liberado)
                elif not current_state and self.button_states[i]:
                    self.button_pressed[i] = False

                self.button_states[i] = current_state

    def _play_note(self, note_index: int):
        """Tocar nota específica"""
        if 0 <= note_index < len(self.NOTAS):
            nombre, frecuencia, color = self.NOTAS[note_index]

            try:
                if self.audio_initialized:
                    # Generar audio
                    audio_data = self._generate_sine_wave(frecuencia, self.DURACION_NOTA)

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
                self.key_animations[note_index] = 1.0
                self.wave_amplitude[note_index] = 1.0

                # Agregar partículas
                self._add_note_particles(note_index)

                # Agregar a notas activas
                if nombre not in self.active_notes:
                    self.active_notes.append(nombre)

                print(f"🎵 Nota {note_index + 1}: {nombre} ({frecuencia} Hz)")

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
            release_time = 0.2

            if t < attack_time:
                envelope = t / attack_time
            elif t > duration - release_time:
                envelope = (duration - t) / release_time

            # Onda seno con un poco de armónicos para un sonido más rico
            fundamental = np.sin(2 * np.pi * frequency * t)
            harmonic2 = 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
            harmonic3 = 0.1 * np.sin(2 * np.pi * frequency * 3 * t)

            arr[i] = envelope * (fundamental + harmonic2 + harmonic3)

        return (arr * self.VOLUMEN * 32767).astype(np.int16)

    def _update_animations(self):
        """Actualizar animaciones visuales"""
        current_time = time.time()

        for i in range(8):
            # Animación de teclas presionadas
            if self.key_animations[i] > 0:
                self.key_animations[i] -= 0.05
                if self.key_animations[i] < 0:
                    self.key_animations[i] = 0

            # Amplitud de onda
            if self.wave_amplitude[i] > 0:
                self.wave_amplitude[i] -= 0.02
                if self.wave_amplitude[i] < 0:
                    self.wave_amplitude[i] = 0

            # Remover de notas activas si no está presionado
            if not self.button_pressed[i] and current_time - self.button_press_time[i] > 0.5:
                note_name = self.NOTAS[i][0]
                if note_name in self.active_notes:
                    self.active_notes.remove(note_name)

        # Actualizar partículas
        self._update_particles()

    def _add_note_particles(self, note_index: int):
        """Agregar partículas visuales para la nota"""
        key_x = 100 + note_index * (self.KEY_WIDTH + 10)
        key_y = 200

        for _ in range(5):
            particle = {
                'x': key_x + self.KEY_WIDTH // 2,
                'y': key_y,
                'vx': (np.random.random() - 0.5) * 4,
                'vy': -np.random.random() * 3 - 2,
                'life': 1.0,
                'color': self._get_note_color(note_index)
            }
            self.note_particles.append(particle)

    def _update_particles(self):
        """Actualizar partículas de notas"""
        for particle in self.note_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravedad
            particle['life'] -= 0.02

            if particle['life'] <= 0:
                self.note_particles.remove(particle)

    def _get_note_color(self, note_index: int):
        """Obtener color para la nota"""
        colors = [self.RED, self.ORANGE, self.YELLOW, self.GREEN,
                 self.CYAN, self.BLUE, self.PURPLE, self.GOLD]
        return colors[note_index % len(colors)]

    def _draw_piano_visualization(self):
        """Dibujar visualización completa del piano"""
        if not self.pygame_initialized:
            return

        # Fondo
        self.screen.fill(self.BLACK)

        # Título
        title_surface = self.font_large.render("🎹 PIANO DIGITAL ARDUINO", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)

        # Estado de conexión
        connection_color = self.GREEN if self.arduino.connected else self.RED
        connection_text = "CONECTADO" if self.arduino.connected else "DESCONECTADO"
        conn_surface = self.font_small.render(f"Arduino: {connection_text}", True, connection_color)
        self.screen.blit(conn_surface, (20, 20))

        # Dibujar piano
        self._draw_piano_keys()

        # Dibujar onda de sonido
        self._draw_sound_waves()

        # Dibujar información
        self._draw_piano_info()

        # Dibujar partículas
        self._draw_particles()

        # Dibujar visualizador de frecuencias
        self._draw_frequency_visualizer()

    def _draw_piano_keys(self):
        """Dibujar teclas del piano"""
        start_x = 100
        start_y = 200

        # Dibujar teclas blancas
        for i in range(8):
            x = start_x + i * (self.KEY_WIDTH + 10)
            y = start_y

            # Determinar color base
            if self.button_pressed[i]:
                key_color = self._get_note_color(i)
            else:
                # Animación de presión
                animation = self.key_animations[i]
                if animation > 0:
                    color_intensity = int(255 * animation)
                    key_color = (color_intensity, color_intensity, 255)
                else:
                    key_color = self.WHITE

            # Dibujar tecla
            key_rect = pygame.Rect(x, y, self.KEY_WIDTH, self.KEY_HEIGHT)
            pygame.draw.rect(self.screen, key_color, key_rect)
            pygame.draw.rect(self.screen, self.BLACK, key_rect, 3)

            # Nombre de la nota
            note_name = self.NOTAS[i][0]
            text_color = self.BLACK if not self.button_pressed[i] else self.WHITE
            note_surface = self.font_medium.render(note_name, True, text_color)
            note_rect = note_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT - 30))
            self.screen.blit(note_surface, note_rect)

            # Número del botón
            btn_text = f"Pin {self.BUTTON_PINS[i]}"
            btn_surface = self.font_small.render(btn_text, True, text_color)
            btn_rect = btn_surface.get_rect(center=(x + self.KEY_WIDTH // 2, y + self.KEY_HEIGHT - 50))
            self.screen.blit(btn_surface, btn_rect)

            # Indicador de presión
            if self.button_pressed[i]:
                indicator_rect = pygame.Rect(x + 10, y + 10, self.KEY_WIDTH - 20, 20)
                pygame.draw.rect(self.screen, self.GREEN, indicator_rect)
                pressed_text = self.font_small.render("PRESIONADO", True, self.BLACK)
                pressed_rect = pressed_text.get_rect(center=indicator_rect.center)
                self.screen.blit(pressed_text, pressed_rect)

    def _draw_sound_waves(self):
        """Dibujar ondas de sonido"""
        wave_y = 120
        wave_height = 40

        for i in range(8):
            if self.wave_amplitude[i] > 0:
                x_start = 100 + i * (self.KEY_WIDTH + 10)
                x_end = x_start + self.KEY_WIDTH

                # Dibujar onda seno
                points = []
                for x in range(x_start, x_end, 2):
                    wave_x = (x - x_start) / self.KEY_WIDTH * 4 * math.pi
                    wave_value = math.sin(wave_x + time.time() * 10) * self.wave_amplitude[i] * wave_height
                    y = wave_y + wave_value
                    points.append((x, y))

                if len(points) > 1:
                    pygame.draw.lines(self.screen, self._get_note_color(i), False, points, 3)

    def _draw_particles(self):
        """Dibujar partículas de notas"""
        for particle in self.note_particles:
            alpha = int(particle['life'] * 255)
            size = int(particle['life'] * 8) + 2

            # Crear superficie con transparencia
            particle_surface = pygame.Surface((size * 2, size * 2))
            particle_surface.set_alpha(alpha)

            color = particle['color']
            pygame.draw.circle(particle_surface, color, (size, size), size)

            self.screen.blit(particle_surface,
                           (int(particle['x'] - size), int(particle['y'] - size)))

    def _draw_piano_info(self):
        """Dibujar información del piano"""
        info_y = 550

        # Notas activas
        active_text = f"Notas activas: {', '.join(self.active_notes) if self.active_notes else 'Ninguna'}"
        active_surface = self.font_medium.render(active_text, True, self.CYAN)
        self.screen.blit(active_surface, (20, info_y))

        # Última nota
        if self.last_note_played:
            last_text = f"Última nota: {self.last_note_played}"
            last_surface = self.font_medium.render(last_text, True, self.YELLOW)
            self.screen.blit(last_surface, (400, info_y))

        # Contador
        count_text = f"Total reproducidas: {self.total_notes_played}"
        count_surface = self.font_medium.render(count_text, True, self.GREEN)
        self.screen.blit(count_surface, (650, info_y))

        # Instrucciones
        instructions_y = info_y + 30
        instructions = [
            "🎹 Presiona los botones conectados a los pines 2-9 para tocar notas",
            "🔧 Hardware: 8 botones entre pines y GND (pull-up interno activado)"
        ]

        for i, instruction in enumerate(instructions):
            inst_surface = self.font_small.render(instruction, True, self.GRAY)
            self.screen.blit(inst_surface, (20, instructions_y + i * 20))

    def _draw_frequency_visualizer(self):
        """Dibujar visualizador de frecuencias"""
        vis_x = 20
        vis_y = 300
        vis_width = 60
        vis_height = 200

        # Título
        title_surface = self.font_small.render("Frecuencias", True, self.WHITE)
        self.screen.blit(title_surface, (vis_x, vis_y - 25))

        # Barras de frecuencia
        max_freq = 600  # Hz
        for i in range(8):
            freq = self.NOTAS[i][1]
            bar_height = int((freq / max_freq) * vis_height)

            # Color de la barra
            if self.button_pressed[i]:
                bar_color = self._get_note_color(i)
                alpha = 255
            else:
                bar_color = self.DARK_GRAY
                alpha = 100

            # Dibujar barra
            bar_rect = pygame.Rect(vis_x + i * 8, vis_y + vis_height - bar_height, 6, bar_height)
            bar_surface = pygame.Surface((6, bar_height))
            bar_surface.set_alpha(alpha)
            bar_surface.fill(bar_color)
            self.screen.blit(bar_surface, bar_rect)

            # Etiqueta de frecuencia
            if self.button_pressed[i]:
                freq_text = f"{freq}Hz"
                freq_surface = self.font_small.render(freq_text, True, self.WHITE)
                freq_rect = freq_surface.get_rect(center=(vis_x + i * 8 + 3, vis_y + vis_height + 15))
                self.screen.blit(freq_surface, freq_rect)

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
                # Permitir tocar notas con el teclado para testing
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
