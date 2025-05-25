import pyfirmata
import time
from pyfirmata import util
from typing import Optional
import serial.tools.list_ports

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
            except Exception as e:
                print(f"❌ Error al desconectar: {e}")

    def get_pin(self, pin_spec: str):
        """Obtener pin (con cache)"""
        if not self.connected:
            raise ConnectionError("Arduino no conectado")

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
