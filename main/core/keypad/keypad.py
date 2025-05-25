import time
from main.core.arduino_manager import ArduinoManager

class KeypadReader:
    """Lector de keypad 3x2 usando Firmata"""

    def __init__(self, arduino_manager: ArduinoManager):
        self.arduino = arduino_manager

        # Pines digitales
        self.row_pins = [7, 6, 5]  # Filas (OUTPUT)
        self.col_pins = [4, 3]     # Columnas (INPUT)

        # Layout del keypad
        self.keys = [
            ['1', '3'],
            ['4', '6'],
            ['7', '9'],
        ]

        # Configura pines en el Arduino
        for r in self.row_pins:
            self.arduino.get_pin(f'd:{r}:o').write(1)  # OUTPUT
        for c in self.col_pins:
            self.arduino.get_pin(f'd:{c}:i').mode = 0  # INPUT

    def read_keypad(self):
        for r_idx, r_pin in enumerate(self.row_pins):
            # Activar una fila a LOW y las demás HIGH
            for rp in self.row_pins:
                self.arduino.digital[rp].write(1)
            self.arduino.digital[r_pin].write(0)

            # Leer columnas
            for c_idx, c_pin in enumerate(self.col_pins):
                if self.arduino.digital[c_pin].read() is False:
                    return self.keys[r_idx][c_idx]
        return None
