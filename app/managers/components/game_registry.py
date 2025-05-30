"""
Registro de juegos disponibles y sus metadatos
"""

from typing import Dict, Type
from core.base_game import BaseGame
from games.ping_pong.ping_pong import PingPongGame
from games.two_lanes.two_lanes import TwoLaneRunnerGame
from games.piano.piano import PianoSimonGame


class GameRegistry:
    """Registro centralizado de juegos disponibles y sus metadatos"""
    
    def __init__(self):
        # Registro de juegos disponibles
        self.available_games: Dict[str, Type[BaseGame]] = {
            "ping_pong": PingPongGame,
            "two_lane_runner": TwoLaneRunnerGame,
            "piano_digital": PianoSimonGame,
            # Futuros juegos:
            # 'simon_says': SimonGame,
            # 'tetris': TetrisGame,
            # 'snake': SnakeGame,
            # 'breakout': BreakoutGame,
        }
        
        # Información técnica de cada juego
        self.tech_info: Dict[str, str] = {
            "ping_pong": "Juego de Ping Pong con dos palas y una pelota. Requiere sensores de movimiento.",
            "two_lane_runner": "Juego de carreras en dos carriles. Utiliza sensores de distancia para detectar obstáculos.",
            "piano_digital": "Piano digital con teclas táctiles. Requiere sensores capacitivos en pines 2-9.",
            "simon_says": "Juego de memoria Simon Says con 6 LEDs y keypad 4x4. Comunicación serial directa.",
        }
        
        # NUEVO: Juegos que soportan logging cognitivo - SÚPER SIMPLE
        self.cognitive_games: Dict[str, str] = {
            "piano_digital": "🧠 Evalúa memoria, secuencias, tiempo de reacción, fatiga cognitiva",
            # Futuros:
            # "two_lane_runner": "🧠 Evalúa atención dividida, coordinación, tiempo de reacción",
        }
        
        # Iconos para cada juego
        self.game_icons: Dict[str, str] = {
            "ping_pong": "🏓",
            "two_lane_runner": "🏃",
            "piano_digital": "🎹",
            "tetris": "🧩",
            "snake": "🐍",
            "breakout": "🧱",
        }
    
    def get_available_games(self) -> Dict[str, Type[BaseGame]]:
        """Obtener diccionario de juegos disponibles"""
        return self.available_games
    
    def get_game_class(self, game_id: str) -> Type[BaseGame]:
        """Obtener clase de un juego específico"""
        return self.available_games.get(game_id)
    
    def get_tech_info(self, game_id: str) -> str:
        """Obtener información técnica de un juego"""
        return self.tech_info.get(game_id, "Información técnica no disponible")
    
    def get_game_icon(self, game_id: str) -> str:
        """Obtener icono de un juego"""
        return self.game_icons.get(game_id, "🎮")
    
    def get_game_count(self) -> int:
        """Obtener cantidad total de juegos disponibles"""
        return len(self.available_games)
    
    def is_valid_game(self, game_id: str) -> bool:
        """Verificar si un game_id es válido"""
        return game_id in self.available_games
    
    def get_games_with_test_mode(self) -> list:
        """Obtener lista de juegos que tienen modo de prueba"""
        # Por ahora solo piano digital
        return ["piano_digital"]
    
    def supports_cognitive_logging(self, game_id: str) -> bool:
        """Verificar si un juego soporta logging cognitivo"""
        return game_id in self.cognitive_games
    
    def get_cognitive_info(self, game_id: str) -> str:
        """Obtener información sobre capacidades cognitivas de un juego"""
        return self.cognitive_games.get(game_id, "")
    
    def get_cognitive_enabled_games(self) -> Dict[str, str]:
        """Obtener todos los juegos con capacidades cognitivas"""
        return self.cognitive_games
    
    def create_temp_game_instance(self, game_id: str, arduino_manager, enable_cognitive_logging: bool = False, patient_id: str = "default"):
        """Crear instancia temporal de un juego para obtener información"""
        if not self.is_valid_game(game_id):
            return None
        
        game_class = self.get_game_class(game_id)
        
        try:
            # Verificar si el juego soporta logging cognitivo
            if self.supports_cognitive_logging(game_id) and enable_cognitive_logging:
                return game_class(arduino_manager, enable_cognitive_logging=True, patient_id=patient_id)
            else:
                return game_class(arduino_manager)
        except TypeError:
            # Si el constructor no acepta parámetros cognitivos, usar constructor normal
            return game_class(arduino_manager) 