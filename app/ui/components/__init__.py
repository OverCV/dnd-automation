"""
Componentes UI modularizados para la interfaz principal
"""

from .title_section import TitleSection
from .stats_section import StatsSection
from .games_section import GamesSection
from .control_section import ControlSection
from .analytics_manager import AnalyticsManager
from .arduino_colors import ArduinoColors

__all__ = [
    "TitleSection",
    "StatsSection",
    "GamesSection",
    "ControlSection",
    "AnalyticsManager",
    "ArduinoColors",
]
