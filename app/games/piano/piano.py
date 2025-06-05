import time
import threading
from typing import Dict, Any

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from .audio_manager import PianoAudioManager
from .visual_manager import PianoVisualManager, GameState
from .hardware_manager import PianoHardwareManager
from .game_logic import PianoGameLogic
from .game_state_manager import GameStateManager

 
class PianoSimonGame(BaseGame):
    """
    Coordinador principal del Piano Simon - VERSIÓN REFACTORIZADA
    Usa GameStateManager robusto para evitar bugs de threading
    """

    def __init__(
        self,
        arduino_manager: ArduinoManager,
        enable_cognitive_logging: bool = False,
        patient_id: str = "default",
    ):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.name = "Piano Simon Says"
        self.description = "Juego Simon Says usando piano digital de 8 notas"

        # NUEVO: Gestor de estado robusto
        self.state_manager = GameStateManager()

        # Mejorar sistema de patient_id
        if patient_id is None:
            patient_id = self._get_or_create_patient_id()

        # Inicializar los 3 managers especializados
        self.audio_manager = PianoAudioManager()
        self.visual_manager = PianoVisualManager()
        self.hardware_manager = PianoHardwareManager(arduino_manager)
        self.game_logic = PianoGameLogic(
            enable_cognitive_logging=enable_cognitive_logging, patient_id=patient_id
        )

        # Configurar callbacks del game logic
        self._setup_callbacks()

        # Registrar funciones de limpieza
        self._register_cleanup_callbacks()

    def _setup_callbacks(self):
        """Configurar callbacks entre componentes"""
        self.game_logic.set_callbacks(
            on_play_note=self.audio_manager.reproducir_nota,
            on_highlight_note=self.visual_manager.activar_highlight_nota,
            on_clear_highlight=self.visual_manager.desactivar_highlight_nota,
            on_game_over=self.audio_manager.reproducir_secuencia_game_over,
            on_victory=self.audio_manager.reproducir_secuencia_victoria,
        )

    def _register_cleanup_callbacks(self):
        """Registrar funciones de limpieza en el state manager"""
        self.state_manager.add_cleanup_callback(
            self.audio_manager.detener_todos_sonidos
        )
        self.state_manager.add_cleanup_callback(self.visual_manager.cerrar)
        self.state_manager.add_cleanup_callback(self.hardware_manager.cleanup)

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego (método abstracto)"""
        return self.hardware_manager.initialize_hardware()

    def start_game(self) -> bool:
        """Iniciar juego Simon de forma ROBUSTA"""
        try:
            if not self.initialize_hardware():
                print("❌ Error inicializando hardware")
                return False

            if not self.state_manager.can_start():
                print("❌ El juego no puede iniciarse en este momento")
                return False

            # Resetear lógica del juego
            self.game_logic.reset_game()

            # Mostrar animación de inicio
            self.visual_manager.mostrar_animacion_inicio(self.audio_manager)

            # Iniciar usando el state manager robusto
            success = self.state_manager.start_game(self._game_loop_wrapper)

            if success:
                print("🎹 Piano Simon Says iniciado correctamente")

            return success

        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            return False

    def start_test_mode(self) -> bool:
        """Iniciar modo de prueba de forma ROBUSTA"""
        try:
            if not self.initialize_hardware():
                print("❌ Error inicializando hardware")
                return False

            if not self.state_manager.can_start():
                print("❌ El modo prueba no puede iniciarse en este momento")
                return False

            print("🧪 Iniciando modo de prueba...")

            # Iniciar usando el state manager robusto
            success = self.state_manager.start_game(self._test_loop_wrapper)

            return success

        except Exception as e:
            print(f"❌ Error iniciando modo prueba: {e}")
            return False

    def stop_game(self):
        """Detener juego de forma ROBUSTA"""
        print("🛑 Solicitando parada del juego...")
        self.state_manager.stop_game()

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        game_status = self.game_logic.get_game_status()
        state_manager_status = self.state_manager.get_status()

        return {
            "name": self.name,
            "running": self.state_manager.is_running(),
            "lifecycle_state": state_manager_status["lifecycle_state"],
            "game_state": game_status["game_state"].name,
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
            "uptime": state_manager_status["uptime"],
            "total_runs": state_manager_status["total_runs"],
        }

    def _game_loop_wrapper(self):
        """Wrapper del loop principal con manejo robusto"""
        print("🎮 Iniciando loop principal del Simon...")

        while self.state_manager.should_continue():
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

                # Procesar eventos de Pygame - AQUÍ ESTÁ LA CLAVE
                self.visual_manager.procesar_eventos_pygame(
                    callback_salir=self._handle_quit_robustly,
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

        print("🔄 Loop principal terminado")

    def _test_loop_wrapper(self):
        """Wrapper del loop de prueba con manejo robusto"""
        print("🧪 Iniciando loop de prueba...")
        test_message = "🧪 MODO PRUEBA - Presiona un botón para probar"

        while self.state_manager.should_continue():
            try:
                # Leer botones del hardware
                self.hardware_manager.read_buttons()
                pressed_buttons = self.hardware_manager.get_pressed_buttons()

                # Solo reproducir si hay botones presionados
                for button_index in pressed_buttons:
                    self.audio_manager.reproducir_nota(button_index, 0.5)
                    self.visual_manager.activar_animacion_tecla(button_index)

                    nota_info = self.audio_manager.obtener_info_nota(button_index)
                    pin_info = self.hardware_manager.get_pin_info()[button_index]
                    test_message = f"🎵 Probando: {nota_info[0]} ({nota_info[1]} Hz) - Pin {pin_info}"

                # Actualizar animaciones
                self.visual_manager.actualizar_animaciones()

                # Procesar eventos de Pygame
                self.visual_manager.procesar_eventos_pygame(
                    callback_salir=self._handle_quit_robustly,
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

        print("🔄 Loop de prueba terminado")

    def _handle_quit_robustly(self):
        """Manejar salida del juego de forma ROBUSTA"""
        print("🚪 Solicitando salida del juego...")
        self.state_manager.stop_game()

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

    def _get_or_create_patient_id(self) -> str:
        """Obtener patient_id del sistema de gestión o crear uno nuevo"""
        try:
            # Intentar cargar del sistema de gestión de pacientes específico de piano_simon
            import json
            import os

            patients_file = "data/cognitive/piano_simon/patients.json"
            if os.path.exists(patients_file):
                with open(patients_file, "r", encoding="utf-8") as f:
                    patients = json.load(f)

                # Si hay pacientes, usar el último
                if patients:
                    latest_patient = max(
                        patients.keys(), key=lambda k: patients[k].get("created", "")
                    )
                    return latest_patient

        except Exception as e:
            print(f"⚠️ No se pudo acceder al sistema de pacientes: {e}")

        # Fallback: crear ID temporal
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"TEMP_PIANO_PLAYER_{timestamp}"


# Funciones de utilidad para compatibilidad
def create_piano_simon_game(arduino_manager: ArduinoManager) -> PianoSimonGame:
    """Factory function para crear el juego Piano Simon"""
    return PianoSimonGame(
        arduino_manager, enable_cognitive_logging=True, patient_id="paciente_actual"
    )


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
