from ui.main_window import MainWindow
from core.arduino_manager import ArduinoManager

def main():
    """Función principal"""
    print("🎮 Arduino Multi-Game Platform - Versión 2.0")
    print("=" * 60)
    print("🎯 Juegos disponibles: Ping Pong, Two-Lane Runner")
    print("🔧 Hardware soportado: Arduino + LCD Keypad Shield")
    print("🚀 Tecnología: Python + Firmata + Pygame")
    print("=" * 60)

    try:
        arduino_manager = ArduinoManager()
        app = MainWindow(arduino_manager)
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")


if __name__ == "__main__":
    main()
