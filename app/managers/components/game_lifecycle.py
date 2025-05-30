"""
Manejo del ciclo de vida de juegos (inicio, parada, estado)
"""

import time
from typing import Optional
from tkinter import messagebox
from core.base_game import BaseGame
from core.safe_game_manager import SafeGameManager
from core.arduino_manager import ArduinoManager
from .game_registry import GameRegistry


class GameLifecycle:
    """Maneja el ciclo de vida completo de los juegos"""
    
    def __init__(self, arduino_manager: ArduinoManager, game_registry: GameRegistry):
        self.arduino = arduino_manager
        self.registry = game_registry
        self.safe_manager = SafeGameManager()
        self.current_game: Optional[BaseGame] = None
    
    def is_game_running(self) -> bool:
        """Verificar si hay un juego ejecutándose"""
        return self.safe_manager.is_game_running()
    
    def get_current_game(self) -> Optional[BaseGame]:
        """Obtener el juego actual"""
        return self.current_game
    
    def stop_current_game(self) -> bool:
        """Detener juego actual de forma segura"""
        if not self.current_game:
            return True

        try:
            game_name = getattr(self.current_game, "name", "Juego")
            print(f"🛑 Solicitando detención segura de {game_name}")

            # Usar el safe manager para detener de forma segura
            success = self.safe_manager.stop_current_game_safely(timeout=5.0)

            if success:
                self.current_game = None
                print(f"✅ {game_name} detenido de forma segura")
                return True
            else:
                print(f"⚠️ Problemas deteniendo {game_name}, usando parada de emergencia")
                self.safe_manager.emergency_stop_all()
                self.current_game = None
                return True

        except Exception as e:
            print(f"❌ Error crítico deteniendo juego: {e}")
            print("🚨 Usando parada de emergencia")
            try:
                self.safe_manager.emergency_stop_all()
                self.current_game = None
                return True
            except Exception as emergency_error:
                print(f"💀 Error en parada de emergencia: {emergency_error}")
                return False
    
    def start_game(self, game_id: str) -> tuple[bool, str]:
        """
        Iniciar un juego
        Returns: (success: bool, message: str)
        """
        # Validaciones previas
        if not self.arduino.connected:
            return False, "Conecta el Arduino primero"
        
        if not self.registry.is_valid_game(game_id):
            return False, f"Juego '{game_id}' no es válido"

        # Detener juego actual si existe
        if self.current_game and self.is_game_running():
            print("🔄 Deteniendo juego actual antes de iniciar nuevo...")
            if not self.stop_current_game():
                return False, "No se pudo detener el juego actual"
            time.sleep(0.5)  # Pequeña pausa para asegurar limpieza

        # Crear e inicializar nuevo juego
        try:
            game_class = self.registry.get_game_class(game_id)
            new_game = game_class(self.arduino)

            if not new_game.start_game():
                return False, f"No se pudo iniciar {new_game.name}"

            # Establecer como juego actual
            self.current_game = new_game
            self.safe_manager.set_current_game(new_game)

            success_msg = (
                f"🎮 {self.current_game.name} iniciado correctamente!\n\n"
                f"Descripción: {self.current_game.description}\n\n"
                f"¡Diviértete jugando!"
            )
            
            return True, success_msg

        except Exception as e:
            return False, f"Error iniciando juego: {e}"
    
    def start_test_mode(self, game_id: str) -> tuple[bool, str]:
        """
        Iniciar modo de prueba para un juego
        Returns: (success: bool, message: str)
        """
        # Validaciones previas
        if not self.arduino.connected:
            return False, "Conecta el Arduino primero"
        
        if game_id not in self.registry.get_games_with_test_mode():
            return False, f"El modo prueba no está disponible para este juego"

        # Detener juego actual si existe
        if self.current_game and self.is_game_running():
            print("🔄 Deteniendo juego actual antes de iniciar modo prueba...")
            if not self.stop_current_game():
                return False, "No se pudo detener el juego actual"
            time.sleep(0.5)

        # Iniciar modo de prueba
        try:
            game_class = self.registry.get_game_class(game_id)
            new_game = game_class(self.arduino)

            if hasattr(new_game, "start_test_mode"):
                if not new_game.start_test_mode():
                    return False, f"No se pudo iniciar modo prueba para {new_game.name}"

                # Establecer como juego actual
                self.current_game = new_game
                self.safe_manager.set_current_game(new_game)

                test_msg = (
                    f"🧪 Modo de prueba para {self.current_game.name} iniciado!\n\n"
                    f"Presiona los botones conectados a los pines 2-9 para probar\n"
                    f"las notas musicales. También puedes usar las teclas 1-8.\n\n"
                    f"ESC = Salir | R = Reiniciar"
                )
                
                return True, test_msg
            else:
                return False, f"El modo prueba no está disponible para {new_game.name}"

        except Exception as e:
            return False, f"Error iniciando modo prueba: {e}"
    
    def force_stop_all(self):
        """Parada de emergencia para casos críticos"""
        print("🚨 FORZANDO PARADA DE TODOS LOS JUEGOS")
        try:
            self.safe_manager.emergency_stop_all()
            self.current_game = None
            print("✅ Parada forzada completada")
        except Exception as e:
            print(f"💀 Error en parada forzada: {e}")
    
    def get_current_game_status(self) -> dict:
        """Obtener estado del juego actual"""
        if not self.current_game:
            return {"running": False, "game": None}
        
        try:
            status = self.current_game.get_game_status()
            status["running"] = self.is_game_running()
            return status
        except Exception as e:
            print(f"❌ Error obteniendo estado del juego: {e}")
            return {"running": False, "error": str(e)} 