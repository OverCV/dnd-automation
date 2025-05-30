"""
Módulo cognitivo para evaluación neurodegenerativa

Componentes simples:
- CognitiveLogger: Logging de métricas cognitivas
- MetricsCalculator: Cálculo de métricas derivadas
- SessionManager: Manejo simple de sesiones
- CognitiveVisualAnalyzer: Visualización de gráficas
- CognitiveDataCleaner: Limpieza y manejo de archivos
"""

from .cognitive_logger import CognitiveLogger
from .metrics_calculator import MetricsCalculator  
from .session_manager import SessionManager
from .visual_analyzer import CognitiveVisualAnalyzer
from .data_cleaner import CognitiveDataCleaner

__all__ = [
    "CognitiveLogger",
    "MetricsCalculator",
    "SessionManager",
    "CognitiveVisualAnalyzer",
    "CognitiveDataCleaner"
] 