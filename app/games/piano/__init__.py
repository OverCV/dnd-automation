"""
Módulo Piano Digital Simon Says

VERSIÓN MODULARIZADA en 4 clases especializadas:
- PianoAudioManager: Maneja audio y generación de sonidos
- PianoVisualManager: Maneja visualización con Pygame
- PianoHardwareManager: Maneja lectura de botones Arduino
- PianoGameLogic: Maneja lógica pura del juego Simon Says
- PianoSimonGame: Coordinador principal (pequeño)

El juego incluye modo normal (Simon Says) y modo de prueba libre.
Funciones auxiliares disponibles en utils.py
"""

from .piano import PianoSimonGame
from .audio_manager import PianoAudioManager
from .visual_manager import PianoVisualManager, GameState
from .hardware_manager import PianoHardwareManager
from .game_logic import PianoGameLogic
from .utils import create_piano_simon_game, validate_hardware_setup

__all__ = [
    "PianoSimonGame",
    "PianoAudioManager",
    "PianoVisualManager",
    "PianoHardwareManager",
    "PianoGameLogic",
    "GameState",
    "create_piano_simon_game",
    "validate_hardware_setup",
]
