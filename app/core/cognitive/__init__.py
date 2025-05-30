"""
Módulo cognitivo para evaluación neurodegenerativa

Componentes simples:
- CognitiveLogger: Logging de métricas cognitivas
- MetricsCalculator: Cálculo de métricas derivadas
- SessionManager: Manejo simple de sesiones
"""

from .cognitive_logger import CognitiveLogger
from .metrics_calculator import MetricsCalculator  
from .session_manager import SessionManager

__all__ = [
    "CognitiveLogger",
    "MetricsCalculator",
    "SessionManager"
] 