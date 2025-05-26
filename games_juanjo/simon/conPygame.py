from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
import threading
import time
import random
from typing import Dict, Any
from core.keypad.keypad import KeypadReader
from core.audio.audio_engine import AudioEngine

class SimonSaysGame(BaseGame):
    """Simon Says - 100% Python"""

    def __init__(self, arduino_manager: ArduinoManager):
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
        self.running = False
        self.game_thread = None


    def initialize_hardware(self) -> bool:
        try:
            for pin in self.led_pins:
                led = self.arduino.get_pin(f'd:{pin}:o')
                led.write(0)
                self.leds.append(led)

            self.keypad = KeypadReader(self.arduino)
            self.buzzer = self.arduino.get_pin(f'd:{self.buzzer_pin}:o')
            self.buzzer.write(0)
            self.audio_engine = AudioEngine()
            print(f"✅ {self.name} hardware configurado")
            return True
        except Exception as e:
            print(f"❌ Error configurando {self.name}: {e}")
            return False

    def start_game(self) -> bool:

        if not self.initialize_hardware() :
            return False

        self.running = True
        self._reset_game()
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
        return True

    def _reset_game(self):
        self.sequence = []
        self.player_sequence = []
        self.level = 1
        self.game_over = False
        self.showing_sequence = False
        self.waiting_input = False
        for led in self.leds:
            led.write(0)

    def _game_loop(self):
        print("🔴 Simon Says iniciado...")
        while self.running and not self.game_over:
            self.sequence.append(random.randint(0, 5))
            self._show_sequence()
            self.player_sequence = []
            self.waiting_input = True

            if not self._wait_for_player_input():
                self.game_over = True
                self._show_game_over()
                break

            self.level += 1
            if self.level > self.max_level:
                self._show_victory()
                break
            time.sleep(1)

    def _show_sequence(self):
        self.showing_sequence = True
        delay = max(0.2, 0.6 - (self.level * 0.02))
        print(f"🔴 Mostrando secuencia nivel {self.level}")
        time.sleep(1)
        for note in self.sequence:
            if 0 <= note < len(self.leds):
                self.leds[note].write(1)
                threading.Thread(target=    self.audio_engine.play_tone,
                                 args=(self.tones[note], delay), daemon=True).start()
                time.sleep(delay)
                self.leds[note].write(0)
                time.sleep(0.2)
            else:
                print(f"⚠️ Nota fuera de rango: {note}")
        self.showing_sequence = False

    def _wait_for_player_input(self):
        timeout = time.time() + 10
        print("🔵 Esperando entrada del jugador..."
              f" (Nivel {self.level})")
        while len(self.player_sequence) < len(self.sequence) and time.time() < timeout:
            if not self.running:
                return False
            key = self.keypad.read_key()
            print(f"🔵 Tecla presionada: {key}")
            if key and key in self.button_keys:
                led_index = self.button_keys.index(key)
                self.player_sequence.append(led_index)
                self.leds[led_index].write(1)
                threading.Thread(target=self.audio_engine.play_tone,
                                 args=(self.tones[led_index], 0.2), daemon=True).start()
                time.sleep(0.2)
                self.leds[led_index].write(0)
                pos = len(self.player_sequence) - 1
                if self.player_sequence[pos] != self.sequence[pos]:
                    return False
                print(f"✅ Correcto: {pos + 1}/{len(self.sequence)}")
                # Add a short debounce delay
                time.sleep(0.3)
            time.sleep(0.01)
        return len(self.player_sequence) == len(self.sequence)

    def _show_game_over(self):
        print(f"💀 Game Over - Nivel alcanzado: {self.level}")
        for _ in range(3):
            for led in self.leds:
                led.write(1)
            time.sleep(0.3)
            for led in self.leds:
                led.write(0)
            time.sleep(0.3)

    def _show_victory(self):
        print("🎉 ¡VICTORIA! ¡Completaste todos los niveles!")
        for _ in range(3):
            for i, led in enumerate(self.leds):
                led.write(1)
                threading.Thread(target=self.audio_engine.play_tone,
                                 args=(self.tones[i] + 200, 0.1), daemon=True).start()
                time.sleep(0.1)
                led.write(0)

    def stop_game(self):
        self.running = False
        self.waiting_input = False
        if self.game_thread:
            self.game_thread.join(timeout=1)
        for led in self.leds:
            led.write(0)
        if self.buzzer:
            self.buzzer.write(0)

    def get_game_status(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'running': self.running,
            'level': self.level,
            'sequence_length': len(self.sequence),
            'showing_sequence': self.showing_sequence,
            'waiting_input': self.waiting_input,
            'game_over': self.game_over
        }
