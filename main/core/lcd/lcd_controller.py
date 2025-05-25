import time

class LCDController:
    """Controlador LCD HD44780 usando Firmata"""

    def __init__(self, arduino_manager, rs_pin=8, en_pin=9, d4_pin=4, d5_pin=5, d6_pin=6, d7_pin=7, backlight_pin=10):
        """Inicializar LCD con pines específicos"""
        self.arduino = arduino_manager

        # Configurar pines como salida
        self.rs = arduino_manager.get_pin(f'd:{rs_pin}:o')
        self.en = arduino_manager.get_pin(f'd:{en_pin}:o')
        self.d4 = arduino_manager.get_pin(f'd:{d4_pin}:o')
        self.d5 = arduino_manager.get_pin(f'd:{d5_pin}:o')
        self.d6 = arduino_manager.get_pin(f'd:{d6_pin}:o')
        self.d7 = arduino_manager.get_pin(f'd:{d7_pin}:o')

        # Backlight (PWM)
        self.backlight = arduino_manager.get_pin(f'd:{backlight_pin}:p')
        self._brightness = 1.0

        # Caracteres personalizados
        self.custom_chars = {
            'ball': [0b00000, 0b00000, 0b00100, 0b01110, 0b01110, 0b00100, 0b00000, 0b00000],
            'left_paddle': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000],
            'right_paddle': [0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001]
        }

        # Inicializar LCD
        self.initialize()

    def backlight_on(self):
        """Enciende el backlight"""
        self.set_backlight(200)

    def set_backlight(self, value):
        """Ajusta el brillo del backlight (0-255)"""
        pwm_val = max(0, min(255, int(value))) / 255.0
        self._brightness = pwm_val
        if self.backlight:
            self.backlight.write(pwm_val)

    def initialize(self):
        """Secuencia de inicialización del LCD"""
        time.sleep(0.05)
        self._write_4_bits(0x03)
        time.sleep(0.005)
        self._write_4_bits(0x03)
        time.sleep(0.00015)
        self._write_4_bits(0x03)
        time.sleep(0.00015)
        self._write_4_bits(0x02)
        time.sleep(0.00015)

        self._command(0x28)
        self._command(0x0C)
        self._command(0x06)
        self.clear()
        self._create_custom_chars()
        self.backlight_on()

    def _create_custom_chars(self):
        """Crear caracteres personalizados"""
        char_codes = {'ball': 0, 'left_paddle': 1, 'right_paddle': 2}
        for char_name, code in char_codes.items():
            self._command(0x40 + (code * 8))
            for line in self.custom_chars[char_name]:
                self._write(line)

    def _command(self, value):
        """Enviar comando al LCD"""
        self.rs.write(0)
        self._write_4_bits(value >> 4)
        self._write_4_bits(value & 0x0F)

    def _write(self, value):
        """Escribir dato al LCD"""
        self.rs.write(1)
        self._write_4_bits(value >> 4)
        self._write_4_bits(value & 0x0F)

    def _write_4_bits(self, value):
        """Escribir 4 bits al LCD"""
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
        """Limpiar pantalla"""
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

    def write_custom_char(self, char_code):
        """Escribir carácter personalizado"""
        self._write(char_code)


class ButtonReader:
    """Lector de botones del LCD Keypad Shield"""

    def __init__(self, arduino_manager, analog_pin=0):
        """Inicializar lector de botones"""
        self.analog_pin = arduino_manager.get_pin(f'a:{analog_pin}:i')
        self.button_values = {
            'RIGHT': (0, 50),
            'UP': (50, 150),
            'DOWN': (150, 350),
            'LEFT': (350, 500),
            'SELECT': (500, 850),
            'NONE': (850, 1024)
        }

    def read_button(self):
        """Leer botón actual"""
        if self.analog_pin.read() is None:
            return 'NONE'

        analog_value = int(self.analog_pin.read() * 1023)
        for button, (min_val, max_val) in self.button_values.items():
            if min_val <= analog_value < max_val:
                return button
        return 'NONE'
