import time
from typing import List, Optional
from core.arduino_manager import ArduinoManager


class PianoHardwareManager:
    """Maneja exclusivamente el hardware y lectura de botones del piano"""

    def __init__(self, arduino_manager: ArduinoManager):
        self.arduino = arduino_manager

        # Pines de los botones (9-2)
        self.BUTTON_PINS = [9, 8, 7, 6, 5, 4, 3, 2]
        self.pyfirm_button_pins = []  # Objetos pin de Firmata
        self.button_states = [False] * 8
        self.button_pressed = [False] * 8
        self.last_button_time = [0] * 8

        # Configuración de debounce
        self.DEBOUNCE_DELAY = 200  # ms

        # Estado de inicialización
        self.hardware_initialized = False

    def initialize_hardware(self) -> bool:
        """Inicializar pines de botones del piano"""
        try:
            if not self.arduino.connected:
                print("❌ Arduino no conectado")
                return False

            print("🎹 Inicializando pines de botones...")

            # Configurar pines de botones como entrada con pull-up
            self.pyfirm_button_pins = []
            for pin_num in self.BUTTON_PINS:
                pin = self.arduino.get_pin(f"d:{pin_num}:i")
                if pin:
                    pin.enable_reporting()
                    self.pyfirm_button_pins.append(pin)
                    print(f"✅ Pin {pin_num} configurado como entrada")
                else:
                    print(f"❌ Error configurando pin {pin_num}")
                    return False

            self.hardware_initialized = True
            print("✅ Hardware de piano inicializado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error inicializando hardware: {e}")
            return False

    def read_buttons(self) -> List[bool]:
        """Leer estado de los botones y devolver lista de presionados"""
        current_time = time.time() * 1000

        # Resetear estado de botones presionados
        for i in range(8):
            self.button_pressed[i] = False

        # Leer cada pin
        for i, pin in enumerate(self.pyfirm_button_pins):
            if pin and pin.read() is not None:
                # Firmata lee HIGH cuando no está presionado (pull-up)
                current_state = not bool(pin.read())

                # Detectar flanco de subida (botón presionado)
                if current_state and not self.button_states[i]:
                    if current_time - self.last_button_time[i] > self.DEBOUNCE_DELAY:
                        self.button_pressed[i] = True
                        self.last_button_time[i] = current_time
                        print(
                            f"🔘 Botón {i + 1} presionado (Pin {self.BUTTON_PINS[i]})"
                        )

                # Actualizar estado previo
                self.button_states[i] = current_state

        return self.button_pressed.copy()

    def get_button_states(self) -> List[bool]:
        """Obtener estado actual de botones (presionados o no)"""
        return self.button_states.copy()

    def get_pressed_buttons(self) -> List[int]:
        """Obtener índices de botones que fueron presionados en esta lectura"""
        pressed = []
        for i, is_pressed in enumerate(self.button_pressed):
            if is_pressed:
                pressed.append(i)
        return pressed

    def is_hardware_ready(self) -> bool:
        """Verificar si el hardware está listo"""
        return self.hardware_initialized and len(self.pyfirm_button_pins) == 8

    def get_pin_info(self) -> List[int]:
        """Obtener información de pines configurados"""
        return self.BUTTON_PINS.copy()

    def cleanup(self):
        """Limpiar recursos de hardware"""
        self.pyfirm_button_pins.clear()
        self.hardware_initialized = False
        print("🧹 Hardware de piano limpiado")
