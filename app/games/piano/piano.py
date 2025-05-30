import time
import threading
from typing import Dict, Any

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from .audio_manager import PianoAudioManager
from .visual_manager import PianoVisualManager, GameState
from .hardware_manager import PianoHardwareManager
from .game_logic import PianoGameLogic


class PianoSimonGame(BaseGame):
    """Coordinador principal - VERSIÓN MODULAR usando 3 managers especializados"""

    def __init__(self, arduino_manager: ArduinoManager, enable_cognitive_logging: bool = False, patient_id: str = "default"):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Piano Simon Says"
        self.description = "Juego Simon Says usando piano digital de 8 notas"

        # Inicializar los 3 managers especializados
        self.audio_manager = PianoAudioManager()
        self.visual_manager = PianoVisualManager()
        self.hardware_manager = PianoHardwareManager(arduino_manager)
        self.game_logic = PianoGameLogic(
            enable_cognitive_logging=enable_cognitive_logging,
            patient_id=patient_id
        )

        # Control de modo
        self.test_mode = False

        # Configurar callbacks del game logic
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Configurar callbacks entre componentes"""
        self.game_logic.set_callbacks(
            on_play_note=self.audio_manager.reproducir_nota,
            on_highlight_note=self.visual_manager.activar_highlight_nota,
            on_clear_highlight=self.visual_manager.desactivar_highlight_nota,
            on_game_over=self.audio_manager.reproducir_secuencia_game_over,
            on_victory=self.audio_manager.reproducir_secuencia_victoria,
        )

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego (método abstracto)"""
        return self.hardware_manager.initialize_hardware()

    def start_game(self) -> bool:
        """Iniciar juego Simon"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self.test_mode = False
            self.game_logic.reset_game()

            # Mostrar animación de inicio
            self.visual_manager.mostrar_animacion_inicio(self.audio_manager)

            # Iniciar hilo del juego
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()

            print("🎹 Piano Simon Says iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            return False

    def start_test_mode(self) -> bool:
        """Iniciar modo de prueba libre (ARREGLADO)"""
        try:
            if not self.initialize_hardware():
                return False

            self.running = True
            self.test_mode = True
            print("🧪 Modo de prueba iniciado")

            # Iniciar hilo del modo prueba
            self.game_thread = threading.Thread(target=self._test_loop, daemon=True)
            self.game_thread.start()

            return True

        except Exception as e:
            print(f"❌ Error iniciando modo prueba: {e}")
            return False

    def stop_game(self):
        """Detener juego"""
        try:
            print("🛑 Deteniendo Piano Simon Says...")
            self.running = False
            self.test_mode = False

            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            # Limpiar recursos
            self.audio_manager.detener_todos_sonidos()
            self.visual_manager.cerrar()
            self.hardware_manager.cleanup()

            print("✅ Piano Simon Says detenido")

        except Exception as e:
            print(f"❌ Error deteniendo juego: {e}")

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        game_status = self.game_logic.get_game_status()

        return {
            "name": self.name,
            "running": self.running,
            "test_mode": self.test_mode,
            "game_state": game_status["game_state"].name
            if not self.test_mode
            else "TEST_MODE",
            "level": game_status["player_level"],
            "max_level": game_status["max_level"],
            "sequence_length": game_status["sequence_length"],
            "input_progress": game_status["input_progress"],
            "total_games": game_status["total_games"],
            "best_level": game_status["best_level"],
            "perfect_games": game_status["perfect_games"],
            "current_sequence": game_status["current_sequence"],
            "available_notes": [
                nota[0] for nota in self.audio_manager.obtener_todas_notas()
            ],
            "hardware_initialized": self.hardware_manager.is_hardware_ready(),
        }

    def _test_loop(self):
        """Loop para modo de prueba - ARREGLADO para solo reproducir cuando presiones"""
        print("🧪 Iniciando modo de prueba libre...")
        test_message = "🧪 MODO PRUEBA - Presiona un botón para probar"

        while self.running and self.test_mode:
            try:
                # Leer botones del hardware
                self.hardware_manager.read_buttons()
                pressed_buttons = self.hardware_manager.get_pressed_buttons()

                # Solo reproducir si hay botones presionados (ARREGLO AQUÍ)
                for button_index in pressed_buttons:
                    # Reproducir nota del botón presionado
                    self.audio_manager.reproducir_nota(button_index, 0.5)

                    # Activar animación visual
                    self.visual_manager.activar_animacion_tecla(button_index)

                    # Actualizar mensaje
                    nota_info = self.audio_manager.obtener_info_nota(button_index)
                    pin_info = self.hardware_manager.get_pin_info()[button_index]
                    test_message = f"🎵 Probando: {nota_info[0]} ({nota_info[1]} Hz) - Pin {pin_info}"

                # Actualizar animaciones
                self.visual_manager.actualizar_animaciones()

                # Procesar eventos de Pygame
                self.visual_manager.procesar_eventos_pygame(
                    callback_salir=self._handle_quit,
                    callback_reiniciar=self._handle_restart_test,
                    callback_test_nota=self._handle_keyboard_test,
                )

                # Dibujar visualización
                self.visual_manager.dibujar_todo(
                    game_state=GameState.WAITING_TO_START,
                    game_message=test_message,
                    player_level=0,
                    max_level=8,
                    game_sequence=[],
                    input_count=0,
                    button_pressed=self.hardware_manager.get_button_states(),
                    arduino_connected=self.arduino.connected,
                    total_games=0,
                    best_level=0,
                    perfect_games=0,
                )

                self.visual_manager.actualizar_display()
                time.sleep(0.01)

            except Exception as e:
                print(f"❌ Error en loop de prueba: {e}")
                break

    def _game_loop(self):
        """Loop principal del juego Simon"""
        while self.running and not self.test_mode:
            try:
                current_time = time.time() * 1000

                # Leer botones del hardware
                self.hardware_manager.read_buttons()
                pressed_buttons = self.hardware_manager.get_pressed_buttons()

                # Procesar lógica del juego
                for button_index in pressed_buttons:
                    if self.game_logic.is_waiting_to_start():
                        self.game_logic.start_game_with_button(button_index)
                    elif self.game_logic.is_waiting_for_input():
                        self.game_logic.process_player_input(button_index)
                        self.visual_manager.activar_animacion_tecla(button_index)

                # Actualizar lógica del juego
                self.game_logic.update_sequence_display(current_time)
                self.game_logic.check_player_timeout(current_time)
                self.game_logic.handle_level_complete()
                self.game_logic.handle_game_over()
                self.game_logic.handle_game_won()

                # Actualizar animaciones
                self.visual_manager.actualizar_animaciones()

                # Procesar eventos de Pygame
                self.visual_manager.procesar_eventos_pygame(
                    callback_salir=self._handle_quit,
                    callback_reiniciar=self._handle_restart,
                    callback_test_nota=self._handle_keyboard_test,
                )

                # Dibujar visualización
                game_status = self.game_logic.get_game_status()
                self.visual_manager.dibujar_todo(
                    game_state=game_status["game_state"],
                    game_message=game_status["game_message"],
                    player_level=game_status["player_level"],
                    max_level=game_status["max_level"],
                    game_sequence=game_status["current_sequence"],
                    input_count=game_status["input_progress"],
                    button_pressed=self.hardware_manager.get_button_states(),
                    arduino_connected=self.arduino.connected,
                    total_games=game_status["total_games"],
                    best_level=game_status["best_level"],
                    perfect_games=game_status["perfect_games"],
                )

                self.visual_manager.actualizar_display()
                time.sleep(0.01)

            except Exception as e:
                print(f"❌ Error en loop del juego: {e}")
                break

    def _handle_quit(self):
        """Manejar salida del juego"""
        self.running = False

    def _handle_restart(self):
        """Manejar reinicio del juego"""
        print("🔄 Reinicio manual solicitado")
        self.game_logic.reset_game()
        self.visual_manager.reiniciar_animaciones()

    def _handle_restart_test(self):
        """Manejar reinicio del modo prueba"""
        print("🔄 Reiniciando modo prueba")
        self.visual_manager.reiniciar_animaciones()

    def _handle_keyboard_test(self, note_index):
        """Manejar prueba de nota desde teclado"""
        if 0 <= note_index < 8:
            self.audio_manager.reproducir_nota(note_index)
            self.visual_manager.activar_animacion_tecla(note_index)

    def probar_nota_individual(self, note_index: int):
        """Probar una nota individual (para uso externo)"""
        if 0 <= note_index < 8:
            return self.audio_manager.reproducir_nota(note_index)
        return False

    def probar_todas_notas(self):
        """Probar todas las notas en secuencia"""
        self.audio_manager.probar_todas_notas()


# Funciones de utilidad para compatibilidad
def create_piano_simon_game(arduino_manager: ArduinoManager) -> PianoSimonGame:
    """Factory function para crear el juego Piano Simon"""
    return PianoSimonGame(arduino_manager)


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
