"""
Componentes modularizados para el GameController

Responsabilidades separadas:
- GameRegistry: Registro y metadatos de juegos
- GameLifecycle: Inicio, parada y ciclo de vida  
- GameUIManager: Creación de interfaces y widgets
- GameStatusManager: Ventanas de estado detallado
"""

from .game_registry import GameRegistry
from .game_lifecycle import GameLifecycle
from .game_ui_manager import GameUIManager
from .game_status_manager import GameStatusManager

__all__ = [
    "GameRegistry",
    "GameLifecycle", 
    "GameUIManager",
    "GameStatusManager"
] 