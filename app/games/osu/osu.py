"""
Juego Osu! - Coordinador principal que integra todos los componentes
"""

import time
import threading
from typing import Dict, Any

from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from .hardware_manager import OsuHardwareManager
from .audio_manager import OsuAudioManager
from .visual_manager import OsuVisualManager
from .game_logic import OsuGameLogic, GameState, HitResult


class OsuGame(BaseGame):
    """Juego Osu! - Ritmo y precisión con joystick analógico"""

    def __init__(
        self,
        arduino_manager: ArduinoManager,
        enable_cognitive_logging: bool = False,
        patient_id: str = "default",
    ):
        super().__init__(arduino_manager)

        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None

        # Información del juego
        self.name = "Ossa! Rhythm Game"
        self.description = "Juego de ritmo y precisión usando joystick analógico KY-023"

        # Configuración de pantalla
        self.screen_width = 800
        self.screen_height = 600

        # Inicializar managers especializados
        self.hardware_manager = OsuHardwareManager(arduino_manager)
        self.audio_manager = OsuAudioManager()
        self.visual_manager = OsuVisualManager(self.screen_width, self.screen_height)
        self.game_logic = OsuGameLogic(
            self.screen_width,
            self.screen_height,
            enable_cognitive_logging=enable_cognitive_logging,
            patient_id=patient_id,
        )

        # Estado del juego
        self.current_cursor_x = self.screen_width // 2
        self.current_cursor_y = self.screen_height // 2

        # Configurar callbacks
        self._setup_callbacks()

        print("🎯 Osu Game creado correctamente")

    def _setup_callbacks(self):
        """Configurar callbacks entre componentes"""
        self.game_logic.set_callbacks(
            on_circle_spawn=self._on_circle_spawn,
            on_circle_hit=self._on_circle_hit,
            on_circle_miss=self._on_circle_miss,
            on_combo_milestone=self._on_combo_milestone,
        )

    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        print("🔧 Inicializando hardware Osu...")

        # Inicializar hardware del joystick
        if not self.hardware_manager.initialize_hardware():
            print("❌ Error inicializando joystick")
            return False

        # Inicializar sistema visual
        if not self.visual_manager.initialize_pygame():
            print("⚠️ Visual no disponible - Modo consola")

        print("✅ Hardware Osu inicializado")
        return True

    def start_game(self) -> bool:
        """Iniciar juego principal"""
        try:
            if not self.initialize_hardware():
                print("[DEBUG OsuGame] initialize_hardware() falló.")
                return False
            
            print("🎮 Iniciando Osu Game...")
            self.running = True
            
            # Mostrar animación de inicio
            print("[DEBUG OsuGame] Llamando a visual_manager.mostrar_animacion_inicio...")
            self.visual_manager.mostrar_animacion_inicio(self.audio_manager)
            print("[DEBUG OsuGame] visual_manager.mostrar_animacion_inicio terminó.")
            
            # Inicializar juego en menú
            self.game_logic.game_state = GameState.MENU
            print(f"[DEBUG OsuGame] game_state establecido a: {self.game_logic.game_state}")
            
            # Iniciar ritmo de fondo
            self.audio_manager.start_background_rhythm(120)  # 120 BPM
            
            # Iniciar hilo principal del juego
            self.game_thread = threading.Thread(
                target=self._main_game_loop, daemon=True
            )
            self.game_thread.start()

            print("✅ Osu Game iniciado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error iniciando Osu Game: {e}")
            return False

    def start_test_mode(self) -> bool:
        """Modo de prueba del joystick"""
        try:
            if not self.initialize_hardware():
                return False

            print("🧪 Iniciando modo prueba del joystick...")
            self.running = True

            # Iniciar hilo de prueba
            self.game_thread = threading.Thread(target=self._test_loop, daemon=True)
            self.game_thread.start()

            return True

        except Exception as e:
            print(f"❌ Error iniciando modo prueba: {e}")
            return False

    def stop_game(self):
        """Detener el juego"""
        try:
            print("🛑 Deteniendo Osu Game...")
            self.running = False

            # Esperar que termine el hilo
            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=2)

            # Limpiar managers
            self.audio_manager.cleanup()
            self.visual_manager.cleanup()
            self.hardware_manager.cleanup()

            print("✅ Osu Game detenido")

        except Exception as e:
            print(f"❌ Error deteniendo Osu Game: {e}")

    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        game_status = self.game_logic.get_game_status()
        hardware_status = self.hardware_manager.get_joystick_state()

        return {
            "name": self.name,
            "running": self.running,
            "game_state": game_status["game_state"].name,
            "score": game_status["score"],
            "combo": game_status["combo"],
            "max_combo": game_status["max_combo"],
            "accuracy": game_status["accuracy"],
            "total_circles": game_status["total_circles"],
            "circles_hit": game_status["circles_hit"],
            "circles_missed": game_status["circles_missed"],
            "perfect_hits": game_status["perfect_hits"],
            "good_hits": game_status["good_hits"],
            "normal_hits": game_status["normal_hits"],
            "difficulty_level": game_status["difficulty_level"],
            "game_duration": game_status["game_duration"],
            "hardware_initialized": self.hardware_manager.is_hardware_ready(),
            "joystick_x": hardware_status["x_normalized"],
            "joystick_y": hardware_status["y_normalized"],
            "cursor_position": (self.current_cursor_x, self.current_cursor_y),
            "visual_initialized": self.visual_manager.initialized,
        }

    def _main_game_loop(self):
        """Loop principal del juego"""
        print("🎮 Loop principal Osu iniciado (desde _main_game_loop)")

        if not self.visual_manager.initialized:
            print("[DEBUG OsuGame _main_game_loop] ERROR: VisualManager no está inicializado al entrar al loop!")
            self.running = False # Detener si no hay visuales
            return

        while self.running:
            try:
                current_time = time.time() * 1000

                # Leer estado del joystick
                self.hardware_manager.read_joystick()

                # Obtener posición del cursor
                self.current_cursor_x, self.current_cursor_y = (
                    self.hardware_manager.get_cursor_position(
                        self.screen_width, self.screen_height
                    )
                )

                # Obtener entrada del botón
                button_just_pressed = self.hardware_manager.is_button_just_pressed()

                # Procesar eventos de pygame
                pygame_events = self.visual_manager.process_events()

                # Manejar eventos especiales
                if pygame_events["quit"] or pygame_events["key_escape"]:
                    break

                # Lógica según el estado del juego
                current_state = self.game_logic.game_state

                if current_state == GameState.MENU:
                    # En menú, esperar click para empezar
                    if button_just_pressed or pygame_events["key_space"]:
                        self.game_logic.start_game()
                        self.audio_manager.play_click_sound()

                elif current_state == GameState.PLAYING:
                    # Actualizar lógica del juego
                    self.game_logic.update(
                        current_time,
                        self.current_cursor_x,
                        self.current_cursor_y,
                        button_just_pressed,
                    )

                    # Pausar con P
                    if pygame_events["key_p"]:
                        self.game_logic.pause_game()

                elif current_state == GameState.PAUSED:
                    # Reanudar con click o P
                    if button_just_pressed or pygame_events["key_p"]:
                        self.game_logic.resume_game()

                elif current_state == GameState.RESULTS:
                    # Reiniciar con click o R
                    if (
                        button_just_pressed
                        or pygame_events["key_r"]
                        or pygame_events["key_space"]
                    ):
                        self.game_logic.start_game()

                # Renderizar frame
                game_status = self.game_logic.get_game_status()
                self.visual_manager.render_frame(
                    current_state,
                    game_status["circles"],
                    self.current_cursor_x,
                    self.current_cursor_y,
                    game_status,
                )

                # Control de framerate
                time.sleep(0.016)  # ~60 FPS

            except Exception as e:
                print(f"❌ Error en loop principal: {e}")
                break

        print("🏁 Loop principal Osu terminado")

    def _test_loop(self):
        """Loop de prueba del joystick"""
        print("🧪 Iniciando loop de prueba del joystick")

        while self.running:
            try:
                # Leer joystick
                self.hardware_manager.read_joystick()
                joystick_state = self.hardware_manager.get_joystick_state()

                # Obtener posición del cursor
                cursor_x, cursor_y = self.hardware_manager.get_cursor_position(
                    self.screen_width, self.screen_height
                )

                # Mostrar información cada segundo
                print(
                    f"🕹️ Joystick - X: {joystick_state['x_normalized']:.2f}, "
                    f"Y: {joystick_state['y_normalized']:.2f}, "
                    f"Cursor: ({cursor_x}, {cursor_y}), "
                    f"Button: {'PRESSED' if joystick_state['button_pressed'] else 'Released'}"
                )

                # Reproducir sonido al presionar botón
                if joystick_state["button_just_pressed"]:
                    self.audio_manager.play_click_sound()
                    print("🔊 Click!")

                time.sleep(1.0)

            except Exception as e:
                print(f"❌ Error en loop de prueba: {e}")
                break

        print("🏁 Loop de prueba terminado")

    def _on_circle_spawn(self):
        """Callback cuando aparece un círculo"""
        self.audio_manager.play_spawn_sound()

    def _on_circle_hit(self, hit_result: HitResult, points: int):
        """Callback cuando se golpea un círculo"""
        # Reproducir sonido basado en precisión
        if hit_result == HitResult.PERFECT:
            accuracy_score = 95
        elif hit_result == HitResult.GOOD:
            accuracy_score = 80
        elif hit_result == HitResult.NORMAL:
            accuracy_score = 65
        else:
            accuracy_score = 30

        self.audio_manager.play_hit_sound(accuracy_score)

        # Agregar efecto visual
        self.visual_manager.add_hit_effect(
            self.current_cursor_x, self.current_cursor_y, hit_result, points
        )

    def _on_circle_miss(self):
        """Callback cuando se pierde un círculo"""
        self.audio_manager.play_miss_sound()

    def _on_combo_milestone(self, combo_count: int):
        """Callback cuando se alcanza un hito de combo"""
        self.audio_manager.play_combo_sound(combo_count)
        print(f"🔥 Combo milestone: {combo_count}x!")

    def set_difficulty(self, level: int):
        """Ajustar dificultad del juego"""
        if hasattr(self.game_logic, "difficulty_level"):
            self.game_logic.difficulty_level = max(1, min(10, level))
            print(f"🎚️ Dificultad ajustada a nivel {level}")

    def calibrate_joystick(self):
        """Calibrar el joystick"""
        self.hardware_manager.calibrate_center()

    def adjust_sensitivity(self, sensitivity: float):
        """Ajustar sensibilidad del joystick"""
        self.hardware_manager.set_sensitivity(sensitivity)

    def get_hardware_info(self) -> Dict[str, Any]:
        """Obtener información del hardware"""
        connection_info = self.hardware_manager.get_connection_info()
        audio_info = self.audio_manager.get_audio_info()
        visual_info = self.visual_manager.get_visual_info()

        return {
            "joystick": connection_info,
            "audio": audio_info,
            "visual": visual_info,
            "hardware_ready": self.hardware_manager.is_hardware_ready(),
        }


def create_osu_game(arduino_manager: ArduinoManager) -> OsuGame:
    """Factory function para crear el juego Osu"""
    return OsuGame(
        arduino_manager, enable_cognitive_logging=True, patient_id="paciente_actual"
    )


def get_osu_info() -> Dict[str, Any]:
    """Obtener información técnica del juego Osu"""
    return {
        "name": "Ossa! Rhythm Game",
        "description": "Juego de ritmo y precisión con joystick analógico",
        "hardware_requirements": [
            "Joystick analógico KY-023",
            "Arduino compatible con Firmata",
            "Conexiones: VCC->5V, GND->GND, VRx->A0, VRy->A1, SW->D2",
        ],
        "features": [
            "Precisión espacial y temporal",
            "Sistema de combos dinámico",
            "Dificultad adaptativa",
            "Análisis cognitivo detallado",
            "Efectos visuales y sonoros",
        ],
        "cognitive_metrics": [
            "Tiempo de reacción",
            "Precisión espacial",
            "Precisión temporal",
            "Coordinación ojo-mano",
            "Velocidad de procesamiento",
        ],
        "controls": {
            "joystick_x": "Movimiento horizontal del cursor",
            "joystick_y": "Movimiento vertical del cursor",
            "joystick_button": "Click para golpear círculos",
            "keyboard_p": "Pausar/Reanudar juego",
            "keyboard_r": "Reiniciar juego",
            "keyboard_esc": "Salir del juego",
        },
    }
