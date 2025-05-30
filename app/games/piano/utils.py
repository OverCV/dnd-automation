"""
Utilidades y funciones auxiliares para el módulo Piano Digital
"""

from typing import Dict, Any
from core.arduino_manager import ArduinoManager
from .piano import PianoSimonGame


def create_piano_simon_game(arduino_manager: ArduinoManager) -> PianoSimonGame:
    """Factory function para crear el juego Piano Simon"""
    return PianoSimonGame(arduino_manager, enable_cognitive_logging=True, patient_id="paciente_actual")


def validate_hardware_setup(arduino_manager: ArduinoManager) -> bool:
    """Validar que el hardware esté correctamente configurado"""
    if not arduino_manager.connected:
        print("❌ Arduino no conectado")
        return False

    # Verificar que los pines 2-9 estén disponibles
    required_pins = [2, 3, 4, 5, 6, 7, 8, 9]

    for pin_num in required_pins:
        try:
            pin = arduino_manager.get_pin(f"d:{pin_num}:i")
            if not pin:
                print(f"❌ Pin {pin_num} no disponible")
                return False
        except Exception as e:
            print(f"❌ Error verificando pin {pin_num}: {e}")
            return False

    print("✅ Hardware validado correctamente")
    return True


def get_piano_info() -> Dict[str, Any]:
    """Obtener información técnica del piano digital"""
    return {
        "name": "Piano Digital Simon Says",
        "description": "Piano de 8 notas con juego Simon Says integrado",
        "required_pins": [2, 3, 4, 5, 6, 7, 8, 9],
        "notes": ["Do", "Re", "Mi", "Fa", "Sol", "La", "Si", "Do8"],
        "frequencies": [262, 294, 330, 349, 392, 440, 494, 523],
        "game_modes": ["Simon Says", "Test Mode"],
        "max_level": 20,
        "hardware_requirements": [
            "Arduino compatible con Firmata",
            "8 botones conectados a pines 2-9",
            "Pull-up resistors (preferible interno)",
            "Audio output capability (pygame)"
        ]
    }


def get_troubleshooting_tips() -> Dict[str, str]:
    """Obtener consejos de resolución de problemas"""
    return {
        "no_arduino": "Verifica conexión USB y que Firmata esté cargado",
        "no_sound": "Verifica que pygame esté instalado y audio funcionando",
        "buttons_not_working": "Revisa conexiones en pines 2-9 y pull-ups",
        "game_slow": "Cierra otras aplicaciones que usen audio",
        "pygame_error": "Reinstala pygame: pip install pygame",
        "import_error": "Verifica que todos los archivos estén en su lugar"
    } 