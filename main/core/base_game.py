# ===== base_game.py =====
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseGame(ABC):
    """Clase base para todos los juegos"""

    def __init__(self, arduino_manager):
        self.arduino = arduino_manager
        self.running = False
        self.game_thread = None
        self.name = "Base Game"
        self.description = "Juego base"

    @abstractmethod
    def initialize_hardware(self) -> bool:
        """Inicializar hardware específico del juego"""
        pass

    @abstractmethod
    def start_game(self) -> bool:
        """Iniciar juego"""
        pass

    @abstractmethod
    def stop_game(self):
        """Detener juego"""
        pass

    @abstractmethod
    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado del juego"""
        pass
