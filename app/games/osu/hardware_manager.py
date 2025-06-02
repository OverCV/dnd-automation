"""
Manejo de hardware para joystick analógico KY-023
"""

from typing import Tuple, Dict, Any
from core.arduino_manager import ArduinoManager


class OsuHardwareManager:
    """Maneja el joystick analógico KY-023 para el juego Osu"""
    
    def __init__(self, arduino_manager: ArduinoManager):
        self.arduino = arduino_manager
        
        # Configuración de pines para joystick KY-023
        self.X_PIN = 0  # Pin analógico A0 para eje X 
        self.Y_PIN = 1  # Pin analógico A1 para eje Y
        self.BUTTON_PIN = 2  # Pin digital D2 para botón del joystick
        
        # Variables de calibración
        self.x_center = 512  # Centro esperado del joystick (0-1023)
        self.y_center = 512
        self.deadzone = 50   # Zona muerta para evitar drift
        self.sensitivity = 1.0
        
        # Estado actual
        self.x_raw = 512
        self.y_raw = 512
        self.x_normalized = 0.0  # -1.0 a 1.0
        self.y_normalized = 0.0
        self.button_pressed = False
        self.button_just_pressed = False
        self.previous_button_state = False
        
        # Referencias a pines
        self.x_pin = None
        self.y_pin = None
        self.button_pin = None
        
        self.hardware_ready = False
    
    def initialize_hardware(self) -> bool:
        """Inicializar el joystick KY-023"""
        try:
            if not self.arduino.connected:
                print("❌ Arduino no conectado")
                return False
            
            # Configurar pines analógicos usando get_pin()
            self.x_pin = self.arduino.get_pin(f"a:{self.X_PIN}:i")
            self.y_pin = self.arduino.get_pin(f"a:{self.Y_PIN}:i")
            
            if not self.x_pin or not self.y_pin:
                print("❌ No se pudieron configurar los pines analógicos")
                return False
            
            # Configurar pin digital para botón
            self.button_pin = self.arduino.get_pin(f"d:{self.BUTTON_PIN}:i")
            if not self.button_pin:
                print("❌ No se pudo configurar el pin del botón")
                return False
            
            # Habilitar pull-up interno para el botón - Solo si el método existe
            if hasattr(self.button_pin, 'enable_reporting'):
                self.button_pin.enable_reporting()
            
            # Habilitar lectura analógica - Verificar que board tiene los atributos
            if hasattr(self.arduino.board, 'analog') and len(self.arduino.board.analog) > max(self.X_PIN, self.Y_PIN):
                self.arduino.board.analog[self.X_PIN].enable_reporting()
                self.arduino.board.analog[self.Y_PIN].enable_reporting()
            else:
                print("⚠️ No se pudieron habilitar reportes analógicos directamente")
            
            print("✅ Joystick KY-023 inicializado correctamente")
            print(f"📍 Conexiones:")
            print(f"   VCC -> 5V")
            print(f"   GND -> GND") 
            print(f"   VRx -> A{self.X_PIN}")
            print(f"   VRy -> A{self.Y_PIN}")
            print(f"   SW  -> D{self.BUTTON_PIN}")
            
            self.hardware_ready = True
            self.calibrate_center()
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando joystick: {e}")
            return False
    
    def calibrate_center(self):
        """Calibrar el centro del joystick"""
        try:
            if self.x_pin and self.y_pin:
                # Leer valores actuales como centro
                self.x_center = self.x_pin.read() or 512
                self.y_center = self.y_pin.read() or 512
                print(f"🎯 Joystick calibrado - Centro: X={self.x_center}, Y={self.y_center}")
        except Exception as e:
            print(f"⚠️ Error calibrando joystick: {e}")
    
    def read_joystick(self):
        """Leer estado actual del joystick"""
        if not self.hardware_ready:
            return
            
        try:
            # Leer valores analógicos (0-1023)
            self.x_raw = self.x_pin.read() or self.x_center
            self.y_raw = self.y_pin.read() or self.y_center
            
            # Leer estado del botón (invertido porque usa pull-up)
            button_state = not (self.button_pin.read() or False)
            
            # Detectar presión del botón (flanco ascendente)
            self.button_just_pressed = button_state and not self.previous_button_state
            self.button_pressed = button_state
            self.previous_button_state = button_state
            
            # Normalizar valores del joystick
            self._normalize_joystick_values()
            
        except Exception as e:
            print(f"⚠️ Error leyendo joystick: {e}")
    
    def _normalize_joystick_values(self):
        """Normalizar valores del joystick a rango -1.0 a 1.0"""
        try:
            # Calcular diferencia del centro
            x_diff = self.x_raw - self.x_center
            y_diff = self.y_raw - self.y_center
            
            # Aplicar zona muerta
            if abs(x_diff) < self.deadzone:
                x_diff = 0
            if abs(y_diff) < self.deadzone:
                y_diff = 0
            
            # Normalizar a rango -1.0 a 1.0
            max_range = 512 - self.deadzone
            self.x_normalized = max(-1.0, min(1.0, (x_diff / max_range) * self.sensitivity))
            self.y_normalized = max(-1.0, min(1.0, (y_diff / max_range) * self.sensitivity))
            
            # Invertir Y para que arriba sea positivo
            self.y_normalized = -self.y_normalized
            
        except Exception as e:
            print(f"⚠️ Error normalizando joystick: {e}")
            self.x_normalized = 0.0
            self.y_normalized = 0.0
    
    def get_cursor_position(self, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Obtener posición del cursor en coordenadas de pantalla"""
        # Convertir valores normalizados a posición de pantalla
        cursor_x = int((self.x_normalized + 1.0) * screen_width / 2.0)
        cursor_y = int((self.y_normalized + 1.0) * screen_height / 2.0)
        
        # Asegurar que esté dentro de los límites
        cursor_x = max(0, min(screen_width - 1, cursor_x))
        cursor_y = max(0, min(screen_height - 1, cursor_y))
        
        return cursor_x, cursor_y
    
    def is_button_just_pressed(self) -> bool:
        """Verificar si el botón acaba de ser presionado"""
        return self.button_just_pressed
    
    def is_button_pressed(self) -> bool:
        """Verificar si el botón está presionado"""
        return self.button_pressed
    
    def get_joystick_state(self) -> Dict[str, Any]:
        """Obtener estado completo del joystick"""
        return {
            "x_raw": self.x_raw,
            "y_raw": self.y_raw,
            "x_normalized": self.x_normalized,
            "y_normalized": self.y_normalized,
            "button_pressed": self.button_pressed,
            "button_just_pressed": self.button_just_pressed,
            "x_center": self.x_center,
            "y_center": self.y_center,
            "deadzone": self.deadzone,
            "sensitivity": self.sensitivity
        }
    
    def set_sensitivity(self, sensitivity: float):
        """Ajustar sensibilidad del joystick"""
        self.sensitivity = max(0.1, min(3.0, sensitivity))
        print(f"🎛️ Sensibilidad ajustada a {self.sensitivity}")
    
    def set_deadzone(self, deadzone: int):
        """Ajustar zona muerta del joystick"""
        self.deadzone = max(0, min(200, deadzone))
        print(f"🎯 Zona muerta ajustada a {self.deadzone}")
    
    def is_hardware_ready(self) -> bool:
        """Verificar si el hardware está listo"""
        return self.hardware_ready and self.arduino.connected
    
    def cleanup(self):
        """Limpiar recursos del hardware"""
        try:
            # Deshabilitar reportes analógicos de forma segura
            if hasattr(self.arduino, 'board') and hasattr(self.arduino.board, 'analog'):
                if len(self.arduino.board.analog) > self.X_PIN:
                    self.arduino.board.analog[self.X_PIN].disable_reporting()
                if len(self.arduino.board.analog) > self.Y_PIN:
                    self.arduino.board.analog[self.Y_PIN].disable_reporting()
            
            # Deshabilitar reporte del botón
            if self.button_pin and hasattr(self.button_pin, 'disable_reporting'):
                self.button_pin.disable_reporting()
                
            self.hardware_ready = False
            print("🧹 Hardware del joystick limpiado")
            
        except Exception as e:
            print(f"⚠️ Error limpiando hardware: {e}")
    
    def get_connection_info(self) -> Dict[str, str]:
        """Obtener información de conexiones del hardware"""
        return {
            "joystick_model": "KY-023 Analog Joystick",
            "x_pin": f"A{self.X_PIN} (VRx)",
            "y_pin": f"A{self.Y_PIN} (VRy)", 
            "button_pin": f"D{self.BUTTON_PIN} (SW)",
            "power": "VCC -> 5V, GND -> GND",
            "description": "Joystick analógico de 2 ejes con botón integrado"
        } 