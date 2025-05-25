import inspect
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec


"""
Sistema Completo de Juegos Arduino - 100% Python con Firmata
Reemplaza TODOS los archivos .ino por implementaciones Python puras

ANTES: 5 juegos × 2 archivos (.ino + .py) = 10 archivos + compilación
AHORA: 1 archivo Python = Todo integrado sin compilación

JUEGOS INCLUIDOS:
1. Piano Digital (8 botones → 8 notas)
2. Ping Pong (LCD + Keypad Shield)
3. Simon Says (6 LEDs + 6 botones keypad)
4. Two-Lane Runner (LCD + Keypad Shield)
5. Snake Game (LCD + Keypad Shield)
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import pygame
import numpy as np
import time
import threading
import math
import random
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any
import sys
from pathlib import Path

try:
    import pyfirmata
    from pyfirmata import util
    import serial.tools.list_ports
except ImportError:
    print("❌ Instalar dependencias:")
    print("   pip install pyfirmata pygame numpy pyserial")
    sys.exit(1)


class ArduinoManager:
    """Gestor singleton del Arduino con Firmata"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.board = None
        self.connected = False
        self.port = None
        self.pins = {}  # Cache de pines configurados
        self.iterator = None
        self.initialized = True

    def connect(self, port: str) -> bool:
        """Conectar al Arduino"""
        try:
            print(f"🔌 Conectando a Arduino en {port}...")
            self.board = pyfirmata.Arduino(port)

            # Inicializar iterator
            self.iterator = util.Iterator(self.board)
            self.iterator.start()
            time.sleep(3)  # Tiempo para estabilización

            self.connected = True
            self.port = port
            print("✅ Arduino conectado con StandardFirmata")
            return True

        except Exception as e:
            print(f"❌ Error conectando: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Desconectar Arduino"""
        if self.board and self.connected:
            try:
                self.board.exit()
                self.connected = False
                self.pins.clear()
                print("🔌 Arduino desconectado")
            except:
                pass

    def get_pin(self, pin_spec: str):
        """Obtener pin (con cache)"""
        if not self.connected:
            raise Exception("Arduino no conectado")

        if pin_spec not in self.pins:
            self.pins[pin_spec] = self.board.get_pin(pin_spec)

        return self.pins[pin_spec]

    def find_arduino_port(self) -> Optional[str]:
        """Buscar puerto Arduino automáticamente"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if any(keyword in port.description.upper() for keyword in
                   ['ARDUINO', 'CH340', 'CH341', 'CP210', 'FTDI']):
                return port.device
        return None


class LCDController:
    """Controlador LCD HD44780 usando Firmata"""

    def __init__(self, arduino_manager, rs=8, en=9, d4=4, d5=5, d6=6, d7=7):
        self.arduino = arduino_manager

        # Configurar pines
        self.rs = self.arduino.get_pin(f'd:{rs}:o')
        self.en = self.arduino.get_pin(f'd:{en}:o')
        self.d4 = self.arduino.get_pin(f'd:{d4}:o')
        self.d5 = self.arduino.get_pin(f'd:{d5}:o')
        self.d6 = self.arduino.get_pin(f'd:{d6}:o')
        self.d7 = self.arduino.get_pin(f'd:{d7}:o')

        # Inicializar LCD
        self._initialize()

    def _initialize(self):
        """Secuencia de inicialización LCD"""
        time.sleep(0.05)
        self._write_4_bits(0x03)
        time.sleep(0.005)
        self._write_4_bits(0x03)
        time.sleep(0.00015)
        self._write_4_bits(0x03)
        time.sleep(0.00015)
        self._write_4_bits(0x02)
        time.sleep(0.00015)

        self._command(0x28)  # 4-bit, 2 líneas
        self._command(0x0C)  # Display on
        self._command(0x06)  # Entry mode
        self.clear()

    def _command(self, value):
        """Enviar comando"""
        self.rs.write(0)
        self._write_4_bits(value >> 4)
        self._write_4_bits(value & 0x0F)

    def _write(self, value):
        """Escribir dato"""
        self.rs.write(1)
        self._write_4_bits(value >> 4)
        self._write_4_bits(value & 0x0F)

    def _write_4_bits(self, value):
        """Escribir 4 bits"""
        self.d4.write((value >> 0) & 1)
        self.d5.write((value >> 1) & 1)
        self.d6.write((value >> 2) & 1)
        self.d7.write((value >> 3) & 1)

        self.en.write(0)
        time.sleep(0.000001)
        self.en.write(1)
        time.sleep(0.000001)
        self.en.write(0)
        time.sleep(0.0001)

    def clear(self):
        """Limpiar LCD"""
        self._command(0x01)
        time.sleep(0.002)

    def set_cursor(self, col, row):
        """Posicionar cursor"""
        row_offsets = [0x00, 0x40]
        if row < len(row_offsets):
            self._command(0x80 + col + row_offsets[row])

    def print(self, text):
        """Imprimir texto"""
        for char in str(text):
            self._write(ord(char))

    def create_char(self, location, pattern):
        """Crear carácter personalizado"""
        self._command(0x40 + (location * 8))
        for line in pattern:
            self._write(line)

    def write_custom_char(self, char_code):
        """Escribir carácter personalizado"""
        self._write(char_code)


class KeypadReader:
    """Lector de keypad 4x4 usando Firmata"""

    def __init__(self, arduino_manager):
        self.arduino = arduino_manager

        # Configuración keypad 4x4
        self.row_pins = [7, 6, 5, 4]  # Filas
        self.col_pins = [3, 2, 1, 0]  # Columnas (A3, A2, A1, A0)

        # Layout del keypad
        self.keys = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]

        # Configurar pines
        self.rows = []
        self.cols = []

        for pin in self.row_pins:
            row_pin = self.arduino.get_pin(f'd:{pin}:i')
            self.rows.append(row_pin)

        for pin in self.col_pins:
            col_pin = self.arduino.get_pin(f'a:{pin}:o')  # Analógicos como salida
            self.cols.append(col_pin)

        # Inicializar columnas en HIGH
        for col in self.cols:
            col.write(1)

    def read_key(self):
        """Leer tecla presionada"""
        for col_idx, col_pin in enumerate(self.cols):
            # Activar columna (LOW)
            col_pin.write(0)
            time.sleep(0.001)

            for row_idx, row_pin in enumerate(self.rows):
                if row_pin.read() == 0:  # Tecla presionada
                    key = self.keys[row_idx][col_idx]

                    # Restaurar columna
                    col_pin.write(1)

                    # Debounce
                    time.sleep(0.1)

                    return key

            # Restaurar columna
            col_pin.write(1)

        return None


class LCDKeypadShieldReader:
    """Lector especializado para LCD Keypad Shield"""

    def __init__(self, arduino_manager, analog_pin=0):
        self.arduino = arduino_manager
        self.analog_pin = self.arduino.get_pin(f'a:{analog_pin}:i')

        # Valores del LCD Keypad Shield
        self.button_values = {
            'RIGHT': (0, 50),
            'UP': (50, 150),
            'DOWN': (150, 350),
            'LEFT': (350, 500),
            'SELECT': (500, 850),
            'NONE': (850, 1024)
        }

    def read_button(self):
        """Leer botón presionado"""
        if self.analog_pin.read() is None:
            return 'NONE'

        analog_value = int(self.analog_pin.read() * 1023)

        for button, (min_val, max_val) in self.button_values.items():
            if min_val <= analog_value < max_val:
                return button

        return 'NONE'


class AudioEngine:
    """Motor de audio para generar sonidos"""

    def __init__(self):
        self.sample_rate = 44100
        self.volume = 0.3

        # Inicializar pygame audio
        pygame.mixer.pre_init(
            frequency=self.sample_rate,
            size=-16,
            channels=2,
            buffer=512
        )
        pygame.mixer.init()

    def generate_tone(self, frequency: float, duration: float) -> np.ndarray:
        """Generar tono senoidal"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)

        for i in range(frames):
            time_val = float(i) / self.sample_rate

            # Envelope para evitar clicks
            envelope = 1.0
            fade_time = 0.02

            if time_val < fade_time:
                envelope = time_val / fade_time
            elif time_val > duration - fade_time:
                envelope = (duration - time_val) / fade_time

            arr[i] = envelope * np.sin(2 * np.pi * frequency * time_val)

        return (arr * self.volume * 32767).astype(np.int16)

    def play_tone(self, frequency: float, duration: float):
        """Reproducir tono"""
        audio_data = self.generate_tone(frequency, duration)
        stereo_data = np.column_stack((audio_data, audio_data))
        stereo_data = np.ascontiguousarray(stereo_data, dtype=np.int16)

        sound = pygame.sndarray.make_sound(stereo_data)
        sound.play()


class BaseGame(ABC):
    """Clase base para todos los juegos"""

    def __init__(self, arduino_manager):
        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Base Game"
        self.description = "Juego base"

    @abstractmethod
    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        pass

    @abstractmethod
    def start_game(self) -> bool:
        """Iniciar juego"""
        pass

    @abstractmethod
    def stop_game(self):
        """Detener juego"""
        pass

    @abstractmethod
    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        pass


class PianoGame(BaseGame):
    """Piano Digital - 100% Python"""

    def __init__(self, arduino_manager):
        super().__init__(arduino_manager)
        self.name = "Piano Digital"
        self.description = "Piano de 8 notas con botones físicos"

        # Configuración
        self.button_pins = [2, 3, 4, 5, 6, 7, 8, 9]
        self.notes = [
            ('Do', 262), ('Re', 294), ('Mi', 330), ('Fa', 349),
            ('Sol', 392), ('La', 440), ('Si', 494), ('Do8', 523)
        ]

        # Hardware
        self.buttons = []
        self.button_states = [False] * 8
        self.audio_engine = None

    def initialize_hardware(self) -> bool:
        """Configurar botones del piano"""
        try:
            # Configurar botones como entrada
            for pin in self.button_pins:
                button = self.arduino.get_pin(f'd:{pin}:i')
                self.buttons.append(button)

            # Inicializar audio
            self.audio_engine = AudioEngine()

            print(f"✅ {self.name} hardware configurado")
            return True

        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def start_game(self) -> bool:
        """Iniciar piano"""
        if not self.arduino.connected:
            return False

        self.running = True
        self.game_thread = threading.Thread(target=self._piano_loop)
        self.game_thread.daemon = True
        self.game_thread.start()

        return True

    def _piano_loop(self):
        """Bucle principal del piano"""
        print("🎹 Piano funcionando...")

        while self.running:
            for i, button in enumerate(self.buttons):
                try:
                    # Leer estado (invertir para pull-up)
                    current_state = not button.read() if button.read() is not None else False
                    previous_state = self.button_states[i]

                    # Detectar presión de botón (flanco de subida)
                    if current_state and not previous_state:
                        self._play_note(i)

                    self.button_states[i] = current_state

                except Exception as e:
                    print(f"❌ Error leyendo botón {i}: {e}")

            time.sleep(0.01)  # 100Hz

    def _play_note(self, note_index: int):
        """Tocar nota"""
        if 0 <= note_index < len(self.notes):
            name, frequency = self.notes[note_index]
            pin = self.button_pins[note_index]

            # Reproducir en hilo separado para no bloquear
            threading.Thread(
                target=self.audio_engine.play_tone,
                args=(frequency, 0.5),
                daemon=True
            ).start()

            print(f"🎵 Pin {pin}: {name} ({frequency} Hz)")

    def stop_game(self):
        """Detener piano"""
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)

    def get_game_status(self) -> Dict[str, Any]:
        """Estado del piano"""
        return {
            'name': self.name,
            'running': self.running,
            'buttons_pressed': [i for i, state in enumerate(self.button_states) if state],
            'notes_available': len(self.notes)
        }


class PingPongGame(BaseGame):
    """Ping Pong - 100% Python"""

    def __init__(self, arduino_manager):
        super().__init__(arduino_manager)
        self.name = "Ping Pong"
        self.description = "Juego de ping pong en LCD con keypad shield"

        # Hardware
        self.lcd = None
        self.keypad = None

        # Estado del juego
        self.ball_x = 8
        self.ball_y = 0
        self.ball_dx = 1
        self.ball_dy = 1
        self.left_paddle = False
        self.right_paddle = False
        self.score = 0
        self.game_over = False
        self.game_speed = 0.3

    def initialize_hardware(self) -> bool:
        """Configurar LCD y keypad"""
        try:
            self.lcd = LCDController(self.arduino)
            self.keypad = LCDKeypadShieldReader(self.arduino)

            # Crear caracteres personalizados
            self._create_custom_chars()

            print(f"✅ {self.name} hardware configurado")
            return True

        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def _create_custom_chars(self):
        """Crear caracteres para el juego"""
        # Pelota
        ball = [0x00, 0x00, 0x04, 0x0E, 0x0E, 0x04, 0x00, 0x00]
        self.lcd.create_char(0, ball)

        # Pala izquierda
        left_paddle = [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10]
        self.lcd.create_char(1, left_paddle)

        # Pala derecha
        right_paddle = [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01]
        self.lcd.create_char(2, right_paddle)

    def start_game(self) -> bool:
        """Iniciar ping pong"""
        if not self.arduino.connected:
            return False

        self.running = True
        self._reset_game()

        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()

        return True

    def _reset_game(self):
        """Reiniciar juego"""
        self.ball_x = 8
        self.ball_y = 0
        self.ball_dx = 1
        self.ball_dy = 1
        self.score = 0
        self.game_over = False

    def _game_loop(self):
        """Bucle principal del ping pong"""
        last_move = time.time()
        last_button_check = time.time()

        print("🏓 Ping Pong iniciado...")

        while self.running and not self.game_over:
            current_time = time.time()

            # Leer botones cada 50ms
            if current_time - last_button_check > 0.05:
                button = self.keypad.read_button()
                self.left_paddle = (button == 'LEFT')
                self.right_paddle = (button == 'RIGHT')

                if button == 'SELECT':
                    break  # Salir

                last_button_check = current_time

            # Mover pelota
            if current_time - last_move > self.game_speed:
                self._update_ball()
                self._draw_game()
                last_move = current_time

            time.sleep(0.01)

    def _update_ball(self):
        """Actualizar posición de la pelota"""
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Rebotes verticales
        if self.ball_y < 0:
            self.ball_y = 0
            self.ball_dy = -self.ball_dy
        elif self.ball_y >= 2:
            self.ball_y = 1
            self.ball_dy = -self.ball_dy

        # Colisiones horizontales
        if self.ball_x <= 0:
            if self.left_paddle:
                self.ball_x = 1
                self.ball_dx = -self.ball_dx
                self.score += 1
            else:
                self.game_over = True
                self._show_game_over("Left miss!")
        elif self.ball_x >= 15:
            if self.right_paddle:
                self.ball_x = 14
                self.ball_dx = -self.ball_dx
                self.score += 1
            else:
                self.game_over = True
                self._show_game_over("Right miss!")

    def _draw_game(self):
        """Dibujar juego en LCD"""
        self.lcd.clear()

        # Pelota
        self.lcd.set_cursor(self.ball_x, self.ball_y)
        self.lcd.write_custom_char(0)

        # Palas
        if self.left_paddle:
            self.lcd.set_cursor(0, 0)
            self.lcd.write_custom_char(1)
            self.lcd.set_cursor(0, 1)
            self.lcd.write_custom_char(1)

        if self.right_paddle:
            self.lcd.set_cursor(15, 0)
            self.lcd.write_custom_char(2)
            self.lcd.set_cursor(15, 1)
            self.lcd.write_custom_char(2)

        # Puntuación
        self.lcd.set_cursor(7, 0)
        self.lcd.print(str(self.score))

    def _show_game_over(self, message):
        """Mostrar game over"""
        self.lcd.clear()
        self.lcd.set_cursor(3, 0)
        self.lcd.print("GAME OVER")
        self.lcd.set_cursor(0, 1)
        self.lcd.print(f"{message[:10]} S:{self.score}")

    def stop_game(self):
        """Detener ping pong"""
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        if self.lcd:
            self.lcd.clear()

    def get_game_status(self) -> Dict[str, Any]:
        """Estado del ping pong"""
        return {
            'name': self.name,
            'running': self.running,
            'score': self.score,
            'game_over': self.game_over,
            'ball_position': (self.ball_x, self.ball_y),
            'paddles': (self.left_paddle, self.right_paddle)
        }


class SimonSaysGame(BaseGame):
    """Simon Says - 100% Python"""

    def __init__(self, arduino_manager):
        super().__init__(arduino_manager)
        self.name = "Simon Says"
        self.description = "Juego de memoria con 6 LEDs y botones"

        # Configuración hardware
        self.led_pins = [8, 9, 10, 11, 12, 13]  # 6 LEDs
        self.button_keys = ['1', '4', '7', '3', '6', '9']  # Keypad 4x4
        self.buzzer_pin = 2

        # Hardware
        self.leds = []
        self.keypad = None
        self.buzzer = None
        self.audio_engine = None

        # Estado del juego
        self.sequence = []
        self.player_sequence = []
        self.level = 1
        self.max_level = 20
        self.showing_sequence = False
        self.waiting_input = False
        self.game_over = False

        # Tonos para cada LED
        self.tones = [262, 294, 330, 349, 392, 440]

    def initialize_hardware(self) -> bool:
        """Configurar LEDs, keypad y buzzer"""
        try:
            # Configurar LEDs
            for pin in self.led_pins:
                led = self.arduino.get_pin(f'd:{pin}:o')
                led.write(0)  # Apagar
                self.leds.append(led)

            # Configurar keypad
            self.keypad = KeypadReader(self.arduino)

            # Configurar buzzer (digital)
            self.buzzer = self.arduino.get_pin(f'd:{self.buzzer_pin}:o')
            self.buzzer.write(0)

            # Audio engine para tonos
            self.audio_engine = AudioEngine()

            print(f"✅ {self.name} hardware configurado")
            return True

        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def start_game(self) -> bool:
        """Iniciar Simon Says"""
        if not self.arduino.connected:
            return False

        self.running = True
        self._reset_game()

        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()

        return True

    def _reset_game(self):
        """Reiniciar juego"""
        self.sequence = []
        self.player_sequence = []
        self.level = 1
        self.game_over = False
        self.showing_sequence = False
        self.waiting_input = False

        # Apagar todos los LEDs
        for led in self.leds:
            led.write(0)

    def _game_loop(self):
        """Bucle principal Simon Says"""
        print("🔴 Simon Says iniciado...")

        while self.running and not self.game_over:
            # Añadir nueva nota a la secuencia
            self.sequence.append(random.randint(0, 5))

            # Mostrar secuencia
            self._show_sequence()

            # Esperar entrada del jugador
            self.player_sequence = []
            self.waiting_input = True

            if not self._wait_for_player_input():
                self.game_over = True
                self._show_game_over()
                break

            # Siguiente nivel
            self.level += 1
            if self.level > self.max_level:
                self._show_victory()
                break

            time.sleep(1)

    def _show_sequence(self):
        """Mostrar secuencia de LEDs"""
        self.showing_sequence = True
        delay = max(0.2, 0.6 - (self.level * 0.02))

        print(f"🔴 Mostrando secuencia nivel {self.level}")
        time.sleep(1)

        for note in self.sequence:
            # Encender LED y tocar tono
            self.leds[note].write(1)

            # Tono usando PWM digital (aproximado)
            threading.Thread(
                target=self.audio_engine.play_tone,
                args=(self.tones[note], delay),
                daemon=True
            ).start()

            time.sleep(delay)

            # Apagar LED
            self.leds[note].write(0)
            time.sleep(0.2)

        self.showing_sequence = False

    def _wait_for_player_input(self):
        """Esperar entrada del jugador"""
        timeout = time.time() + 10  # 10 segundos timeout

        while len(self.player_sequence) < len(self.sequence) and time.time() < timeout:
            if not self.running:
                return False

            # Leer keypad
            key = self.keypad.read_key()

            if key in self.button_keys:
                led_index = self.button_keys.index(key)
                self.player_sequence.append(led_index)

                # Feedback visual/audio
                self.leds[led_index].write(1)
                threading.Thread(
                    target=self.audio_engine.play_tone,
                    args=(self.tones[led_index], 0.2),
                    daemon=True
                ).start()

                time.sleep(0.2)
                self.leds[led_index].write(0)

                # Verificar si es correcto
                pos = len(self.player_sequence) - 1
                if self.player_sequence[pos] != self.sequence[pos]:
                    return False

                print(f"✅ Correcto: {pos + 1}/{len(self.sequence)}")

            time.sleep(0.01)

        return len(self.player_sequence) == len(self.sequence)

    def _show_game_over(self):
        """Mostrar game over"""
        print(f"💀 Game Over - Nivel alcanzado: {self.level}")

        # Parpadear LEDs
        for _ in range(3):
            for led in self.leds:
                led.write(1)
            time.sleep(0.3)
            for led in self.leds:
                led.write(0)
            time.sleep(0.3)

    def _show_victory(self):
        """Mostrar victoria"""
        print("🎉 ¡VICTORIA! ¡Completaste todos los niveles!")

        # Animación de victoria
        for _ in range(3):
            for i, led in enumerate(self.leds):
                led.write(1)
                threading.Thread(
                    target=self.audio_engine.play_tone,
                    args=(self.tones[i] + 200, 0.1),
                    daemon=True
                ).start()
                time.sleep(0.1)
                led.write(0)

    def stop_game(self):
        """Detener Simon Says"""
        self.running = False
        self.waiting_input = False
        if self.game_thread:
            self.game_thread.join(timeout=1)

        # Apagar todos los LEDs
        for led in self.leds:
            led.write(0)
        self.buzzer.write(0)

    def get_game_status(self) -> Dict[str, Any]:
        """Estado de Simon Says"""
        return {
            'name': self.name,
            'running': self.running,
            'level': self.level,
            'sequence_length': len(self.sequence),
            'showing_sequence': self.showing_sequence,
            'waiting_input': self.waiting_input,
            'game_over': self.game_over
        }


class TwoLaneRunnerGame(BaseGame):
    """Two-Lane Runner - 100% Python"""

    def __init__(self, arduino_manager):
        super().__init__(arduino_manager)
        self.name = "Two-Lane Runner"
        self.description = "Esquiva obstáculos en 2 carriles"

        # Hardware
        self.lcd = None
        self.keypad = None

        # Estado del juego
        self.player_y = 0  # 0=superior, 1=inferior
        self.score = 0
        self.speed = 500  # ms entre movimientos
        self.game_over = False
        self.obstacles = []  # Lista de (x, y)
        self.max_obstacles = 8

    def initialize_hardware(self) -> bool:
        """Configurar LCD y keypad"""
        try:
            self.lcd = LCDController(self.arduino)
            self.keypad = LCDKeypadShieldReader(self.arduino)

            # Crear caracteres personalizados
            self._create_custom_chars()

            print(f"✅ {self.name} hardware configurado")
            return True

        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def _create_custom_chars(self):
        """Crear caracteres del juego"""
        # Jugador
        player = [0x0E, 0x0E, 0x04, 0x0E, 0x15, 0x04, 0x0A, 0x11]
        self.lcd.create_char(0, player)

        # Obstáculo
        obstacle = [0x00, 0x0E, 0x1F, 0x1F, 0x1F, 0x0E, 0x00, 0x00]
        self.lcd.create_char(1, obstacle)

    def start_game(self) -> bool:
        """Iniciar runner"""
        if not self.arduino.connected:
            return False

        self.running = True
        self._reset_game()

        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()

        return True

    def _reset_game(self):
        """Reiniciar juego"""
        self.player_y = 0
        self.score = 0
        self.speed = 500
        self.game_over = False
        self.obstacles = []

    def _game_loop(self):
        """Bucle principal del runner"""
        last_move = time.time()
        last_button_check = time.time()
        scroll_counter = 0

        print("🏃 Two-Lane Runner iniciado...")

        while self.running and not self.game_over:
            current_time = time.time()

            # Leer botones
            if current_time - last_button_check > 0.05:
                button = self.keypad.read_button()

                if button == 'UP':
                    self.player_y = 0
                elif button == 'DOWN':
                    self.player_y = 1
                elif button == 'SELECT':
                    break  # Pausar/salir

                last_button_check = current_time

            # Actualizar juego
            if current_time - last_move > (self.speed / 1000.0):
                self._update_game()
                self._draw_game()
                last_move = current_time
                scroll_counter += 1

            time.sleep(0.01)

    def _update_game(self):
        """Actualizar lógica del juego"""
        # Mover obstáculos hacia la izquierda
        new_obstacles = []

        for obs_x, obs_y in self.obstacles:
            new_x = obs_x - 1

            # Verificar colisión con jugador
            if new_x == 1 and obs_y == self.player_y:
                self.game_over = True
                self._show_game_over()
                return

            # Mantener obstáculos en pantalla
            if new_x >= 0:
                new_obstacles.append((new_x, obs_y))
            else:
                # Aumentar puntuación
                self.score += 1

                # Aumentar velocidad cada 10 puntos
                if self.score % 10 == 0:
                    self.speed = max(150, self.speed - 30)

        self.obstacles = new_obstacles

        # Generar nuevos obstáculos
        if len(self.obstacles) < self.max_obstacles and random.random() < 0.3:
            # Asegurar que siempre hay un carril libre
            occupied_lanes = [obs_y for obs_x, obs_y in self.obstacles if obs_x >= 14]

            if 0 in occupied_lanes and 1 not in occupied_lanes:
                new_lane = 1
            elif 1 in occupied_lanes and 0 not in occupied_lanes:
                new_lane = 0
            else:
                new_lane = random.randint(0, 1)

            self.obstacles.append((15, new_lane))

    def _draw_game(self):
        """Dibujar juego en LCD"""
        self.lcd.clear()

        # Jugador
        self.lcd.set_cursor(1, self.player_y)
        self.lcd.write_custom_char(0)

        # Obstáculos
        for obs_x, obs_y in self.obstacles:
            if 0 <= obs_x < 16:
                self.lcd.set_cursor(obs_x, obs_y)
                self.lcd.write_custom_char(1)

        # Puntuación
        self.lcd.set_cursor(13, 0)
        self.lcd.print(str(self.score))

    def _show_game_over(self):
        """Mostrar game over"""
        self.lcd.clear()
        self.lcd.set_cursor(3, 0)
        self.lcd.print("GAME OVER")
        self.lcd.set_cursor(0, 1)
        self.lcd.print(f"Score: {self.score}")

    def stop_game(self):
        """Detener runner"""
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        if self.lcd:
            self.lcd.clear()

    def get_game_status(self) -> Dict[str, Any]:
        """Estado del runner"""
        return {
            'name': self.name,
            'running': self.running,
            'score': self.score,
            'player_lane': self.player_y,
            'speed': self.speed,
            'obstacles_count': len(self.obstacles),
            'game_over': self.game_over
        }


class SnakeGame(BaseGame):
    """Snake Game - 100% Python"""

    def __init__(self, arduino_manager):
        super().__init__(arduino_manager)
        self.name = "Snake Game"
        self.description = "Juego clásico de la serpiente en LCD"

        # Hardware
        self.lcd = None
        self.keypad = None

        # Estado del juego
        self.snake_x = []
        self.snake_y = []
        self.snake_length = 3
        self.direction = 'RIGHT'
        self.food_x = 0
        self.food_y = 0
        self.score = 0
        self.speed = 500
        self.game_over = False

    def initialize_hardware(self) -> bool:
        """Configurar LCD y keypad"""
        try:
            self.lcd = LCDController(self.arduino)
            self.keypad = LCDKeypadShieldReader(self.arduino)

            # Crear caracteres personalizados
            self._create_custom_chars()

            print(f"✅ {self.name} hardware configurado")
            return True

        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def _create_custom_chars(self):
        """Crear caracteres del snake"""
        # Cabeza de serpiente
        head = [0x00, 0x00, 0x04, 0x0E, 0x0E, 0x00, 0x00, 0x00]
        self.lcd.create_char(0, head)

        # Cuerpo de serpiente
        body = [0x00, 0x00, 0x00, 0x0E, 0x0E, 0x00, 0x00, 0x00]
        self.lcd.create_char(1, body)

        # Comida
        food = [0x00, 0x00, 0x04, 0x0A, 0x0A, 0x04, 0x00, 0x00]
        self.lcd.create_char(2, food)

    def start_game(self) -> bool:
        """Iniciar snake"""
        if not self.arduino.connected:
            return False

        self.running = True
        self._reset_game()

        self.game_thread = threading.Thread(target=self._game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()

        return True

    def _reset_game(self):
        """Reiniciar snake"""
        self.snake_x = [2, 1, 0]
        self.snake_y = [0, 0, 0]
        self.snake_length = 3
        self.direction = 'RIGHT'
        self.score = 0
        self.speed = 500
        self.game_over = False
        self._place_food()

    def _place_food(self):
        """Colocar comida en posición válida"""
        while True:
            self.food_x = random.randint(0, 15)
            self.food_y = random.randint(0, 1)

            # Verificar que no esté en la serpiente
            valid = True
            for i in range(self.snake_length):
                if self.food_x == self.snake_x[i] and self.food_y == self.snake_y[i]:
                    valid = False
                    break

            if valid:
                break

    def _game_loop(self):
        """Bucle principal del snake"""
        last_move = time.time()
        last_button_check = time.time()

        print("🐍 Snake iniciado...")

        while self.running and not self.game_over:
            current_time = time.time()

            # Leer botones
            if current_time - last_button_check > 0.1:
                button = self.keypad.read_button()

                if button == 'UP' and self.direction != 'DOWN':
                    self.direction = 'UP'
                elif button == 'DOWN' and self.direction != 'UP':
                    self.direction = 'DOWN'
                elif button == 'LEFT' and self.direction != 'RIGHT':
                    self.direction = 'LEFT'
                elif button == 'RIGHT' and self.direction != 'LEFT':
                    self.direction = 'RIGHT'
                elif button == 'SELECT':
                    break  # Pausar/salir

                last_button_check = current_time

            # Mover serpiente
            if current_time - last_move > (self.speed / 1000.0):
                self._update_snake()
                self._draw_game()
                last_move = current_time

            time.sleep(0.01)

    def _update_snake(self):
        """Actualizar posición de la serpiente"""
        # Calcular nueva posición de cabeza
        new_head_x = self.snake_x[0]
        new_head_y = self.snake_y[0]

        if self.direction == 'UP':
            new_head_y -= 1
        elif self.direction == 'DOWN':
            new_head_y += 1
        elif self.direction == 'LEFT':
            new_head_x -= 1
        elif self.direction == 'RIGHT':
            new_head_x += 1

        # Wrap around
        if new_head_x < 0:
            new_head_x = 15
        elif new_head_x > 15:
            new_head_x = 0
        if new_head_y < 0:
            new_head_y = 1
        elif new_head_y > 1:
            new_head_y = 0

        # Verificar colisión consigo misma
        for i in range(self.snake_length):
            if new_head_x == self.snake_x[i] and new_head_y == self.snake_y[i]:
                self.game_over = True
                self._show_game_over()
                return

        # Verificar si comió
        ate_food = (new_head_x == self.food_x and new_head_y == self.food_y)

        # Mover serpiente
        if not ate_food:
            # Remover cola
            self.snake_x.pop()
            self.snake_y.pop()
        else:
            # Crecer serpiente
            self.score += 10
            self.speed = max(150, self.speed - 20)
            self._place_food()

        # Añadir nueva cabeza
        self.snake_x.insert(0, new_head_x)
        self.snake_y.insert(0, new_head_y)
        self.snake_length = len(self.snake_x)

    def _draw_game(self):
        """Dibujar snake en LCD"""
        self.lcd.clear()

        # Serpiente
        for i in range(self.snake_length):
            self.lcd.set_cursor(self.snake_x[i], self.snake_y[i])
            if i == 0:
                self.lcd.write_custom_char(0)  # Cabeza
            else:
                self.lcd.write_custom_char(1)  # Cuerpo

        # Comida
        self.lcd.set_cursor(self.food_x, self.food_y)
        self.lcd.write_custom_char(2)

    def _show_game_over(self):
        """Mostrar game over"""
        self.lcd.clear()
        self.lcd.set_cursor(3, 0)
        self.lcd.print("GAME OVER")
        self.lcd.set_cursor(0, 1)
        self.lcd.print(f"Score: {self.score}")

    def stop_game(self):
        """Detener snake"""
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        if self.lcd:
            self.lcd.clear()

    def get_game_status(self) -> Dict[str, Any]:
        """Estado del snake"""
        return {
            'name': self.name,
            'running': self.running,
            'score': self.score,
            'snake_length': self.snake_length,
            'direction': self.direction,
            'speed': self.speed,
            'game_over': self.game_over
        }


class GameManagerUI:
    """Interfaz principal del gestor de juegos"""

    def __init__(self):
        # Arduino manager
        self.arduino = ArduinoManager()

        # Juegos disponibles
        self.games = {
            'piano': PianoGame(self.arduino),
            'ping_pong': PingPongGame(self.arduino),
            'simon': SimonSaysGame(self.arduino),
            'runner': TwoLaneRunnerGame(self.arduino),
            'snake': SnakeGame(self.arduino)
        }

        self.current_game = None

        # Crear interfaz
        self.root = tk.Tk()
        self.root.title("Arduino Games Manager - 100% Python + Firmata")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a1a")

        self.setup_styles()
        self.create_interface()

    def setup_styles(self):
        """Configurar estilos"""
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'accent': '#4CAF50',
            'danger': '#f44336',
            'warning': '#ff9800',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }

        self.fonts = {
            'title': tkfont.Font(family="Arial", size=18, weight="bold"),
            'subtitle': tkfont.Font(family="Arial", size=14, weight="bold"),
            'normal': tkfont.Font(family="Arial", size=11),
            'small': tkfont.Font(family="Arial", size=9)
        }

    def create_interface(self):
        """Crear interfaz principal"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🎮 Arduino Games Manager",
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(side=tk.TOP, pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="Sistema completo de juegos - 100% Python con Firmata",
            font=self.fonts['normal'],
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(side=tk.TOP)

        # Connection section
        self.create_connection_section()

        # Games grid
        self.create_games_section()

        # Status section
        self.create_status_section()

        # Inicializar
        self.refresh_ports()
        self.update_status()

    def create_connection_section(self):
        """Sección de conexión"""
        conn_frame = tk.LabelFrame(
            self.root,
            text=" 🔌 Conexión Arduino ",
            font=self.fonts['subtitle'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=2,
            relief=tk.RIDGE
        )
        conn_frame.pack(fill=tk.X, padx=20, pady=10)

        # Controls frame
        controls_frame = tk.Frame(conn_frame, bg=self.colors['card'])
        controls_frame.pack(fill=tk.X, padx=15, pady=10)

        # Port selection
        tk.Label(
            controls_frame,
            text="Puerto:",
            font=self.fonts['normal'],
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.port_var,
            width=15,
            state="readonly"
        )
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        self.refresh_btn = tk.Button(
            controls_frame,
            text="🔄",
            command=self.refresh_ports,
            bg=self.colors['warning'],
            fg="white",
            font=self.fonts['small'],
            width=3,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Connect button
        self.connect_btn = tk.Button(
            controls_frame,
            text="Conectar",
            command=self.toggle_connection,
            bg=self.colors['accent'],
            fg="white",
            font=self.fonts['normal'],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Status
        self.status_var = tk.StringVar(value="❌ Desconectado")
        self.status_label = tk.Label(
            controls_frame,
            textvariable=self.status_var,
            font=self.fonts['normal'],
            bg=self.colors['card'],
            fg=self.colors['danger']
        )
        self.status_label.pack(side=tk.LEFT)

        # Info
        info_label = tk.Label(
            conn_frame,
            text="💡 Asegúrate de que el Arduino tenga StandardFirmata cargado",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        info_label.pack(pady=(0, 10))

    def create_games_section(self):
        """Sección de juegos"""
        games_frame = tk.LabelFrame(
            self.root,
            text=" 🎯 Juegos Disponibles ",
            font=self.fonts['subtitle'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=2,
            relief=tk.RIDGE
        )
        games_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Games grid
        grid_frame = tk.Frame(games_frame, bg=self.colors['card'])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Configure grid
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1)
        for i in range(2):
            grid_frame.rowconfigure(i, weight=1)

        # Create game cards
        self.game_cards = {}
        games_list = list(self.games.items())

        for i, (game_id, game) in enumerate(games_list):
            row = i // 3
            col = i % 3

            card = self.create_game_card(grid_frame, game_id, game)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.game_cards[game_id] = card

    def create_game_card(self, parent, game_id, game):
        """Crear tarjeta de juego"""
        card_frame = tk.Frame(
            parent,
            bg="#3d3d3d",
            relief=tk.RIDGE,
            bd=2
        )

        # Header
        header_frame = tk.Frame(card_frame, bg="#4d4d4d", height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text=game.name,
            font=self.fonts['subtitle'],
            bg="#4d4d4d",
            fg=self.colors['text']
        )
        title_label.pack(pady=10)

        # Description
        desc_label = tk.Label(
            card_frame,
            text=game.description,
            font=self.fonts['small'],
            bg="#3d3d3d",
            fg=self.colors['text_secondary'],
            wraplength=200,
            justify=tk.CENTER
        )
        desc_label.pack(pady=10)

        # Status
        status_label = tk.Label(
            card_frame,
            text="⚪ Listo",
            font=self.fonts['small'],
            bg="#3d3d3d",
            fg=self.colors['text_secondary']
        )
        status_label.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(card_frame, bg="#3d3d3d")
        btn_frame.pack(pady=15)

        start_btn = tk.Button(
            btn_frame,
            text="▶️ Iniciar",
            command=lambda: self.start_game(game_id),
            bg=self.colors['accent'],
            fg="white",
            font=self.fonts['small'],
            relief=tk.FLAT,
            cursor="hand2",
            width=12
        )
        start_btn.pack(pady=2)

        stop_btn = tk.Button(
            btn_frame,
            text="⏹️ Detener",
            command=lambda: self.stop_game(game_id),
            bg=self.colors['danger'],
            fg="white",
            font=self.fonts['small'],
            relief=tk.FLAT,
            cursor="hand2",
            width=12
        )
        stop_btn.pack(pady=2)

        # Store references
        setattr(card_frame, 'status_label', status_label)
        setattr(card_frame, 'start_btn', start_btn)
        setattr(card_frame, 'stop_btn', stop_btn)

        return card_frame

    def create_status_section(self):
        """Sección de estado"""
        status_frame = tk.LabelFrame(
            self.root,
            text=" 📊 Estado del Sistema ",
            font=self.fonts['subtitle'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            bd=2,
            relief=tk.RIDGE
        )
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.status_text = tk.Text(
            status_frame,
            height=6,
            bg="black",
            fg="#00ff00",
            font=("Consolas", 9),
            wrap=tk.WORD
        )

        scrollbar = tk.Scrollbar(status_frame, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)

        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def refresh_ports(self):
        """Refrescar lista de puertos"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo['values'] = ports

            # Auto-detectar Arduino
            arduino_port = self.arduino.find_arduino_port()
            if arduino_port and arduino_port in ports:
                self.port_var.set(arduino_port)
            elif ports:
                self.port_var.set(ports[0])

        except Exception as e:
            self.log_message(f"❌ Error refrescando puertos: {e}")

    def toggle_connection(self):
        """Conectar/desconectar Arduino"""
        if not self.arduino.connected:
            port = self.port_var.get()
            if not port:
                messagebox.showerror("Error", "Selecciona un puerto válido")
                return

            if self.arduino.connect(port):
                self.status_var.set("✅ Conectado")
                self.status_label.config(fg=self.colors['accent'])
                self.connect_btn.config(text="Desconectar", bg=self.colors['danger'])
                self.log_message(f"✅ Arduino conectado en {port}")
                self.update_game_buttons_state()
            else:
                messagebox.showerror("Error", "No se pudo conectar al Arduino")
        else:
            # Detener juego actual
            if self.current_game:
                self.current_game.stop_game()
                self.current_game = None

            self.arduino.disconnect()
            self.status_var.set("❌ Desconectado")
            self.status_label.config(fg=self.colors['danger'])
            self.connect_btn.config(text="Conectar", bg=self.colors['accent'])
            self.log_message("❌ Arduino desconectado")
            self.update_game_buttons_state()

    def start_game(self, game_id):
        """Iniciar un juego"""
        if not self.arduino.connected:
            messagebox.showwarning("Sin conexión", "Conecta el Arduino primero")
            return

        # Detener juego actual
        if self.current_game and self.current_game.running:
            self.current_game.stop_game()

        game = self.games[game_id]

        try:
            # Inicializar hardware
            if game.initialize_hardware():
                # Iniciar juego
                if game.start_game():
                    self.current_game = game
                    self.log_message(f"🎮 {game.name} iniciado")
                    self.update_game_status(game_id, "running")
                else:
                    self.log_message(f"❌ Error iniciando {game.name}")
            else:
                self.log_message(f"❌ Error inicializando hardware de {game.name}")

        except Exception as e:
            self.log_message(f"❌ Error con {game.name}: {e}")

    def stop_game(self, game_id):
        """Detener un juego"""
        game = self.games[game_id]
        if game.running:
            game.stop_game()
            if self.current_game == game:
                self.current_game = None
            self.log_message(f"⏹️ {game.name} detenido")
            self.update_game_status(game_id, "stopped")

    def update_game_status(self, game_id, status):
        """Actualizar estado visual de un juego"""
        if game_id in self.game_cards:
            card = self.game_cards[game_id]

            if status == "running":
                card.status_label.config(text="🟢 Ejecutando", fg=self.colors['accent'])
                card.start_btn.config(state=tk.DISABLED)
                card.stop_btn.config(state=tk.NORMAL)
            else:
                card.status_label.config(text="⚪ Listo", fg=self.colors['text_secondary'])
                card.start_btn.config(state=tk.NORMAL if self.arduino.connected else tk.DISABLED)
                card.stop_btn.config(state=tk.DISABLED)

    def update_game_buttons_state(self):
        """Actualizar estado de todos los botones de juegos"""
        for game_id, card in self.game_cards.items():
            game = self.games[game_id]

            if game.running:
                continue  # No cambiar juegos en ejecución

            if self.arduino.connected:
                card.start_btn.config(state=tk.NORMAL)
            else:
                card.start_btn.config(state=tk.DISABLED)

            card.stop_btn.config(state=tk.DISABLED)

    def log_message(self, message):
        """Agregar mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)

    def update_status(self):
        """Actualizar estado periódicamente"""
        try:
            # Actualizar estado de juegos
            for game_id, game in self.games.items():
                if game.running:
                    status = game.get_game_status()
                    # Aquí podrías actualizar información específica del juego

            # Programar siguiente actualización
            self.root.after(1000, self.update_status)

        except Exception as e:
            self.log_message(f"❌ Error actualizando estado: {e}")
            self.root.after(1000, self.update_status)

    def run(self):
        """Ejecutar aplicación"""
        self.log_message("🚀 Sistema de juegos iniciado")
        self.log_message("💡 Conecta Arduino con StandardFirmata para comenzar")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

