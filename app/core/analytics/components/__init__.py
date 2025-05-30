"""
Componentes modularizados para GameAnalytics

Responsabilidades separadas:
- LogParser: Carga y parseo de archivos de log
- DataVisualizer: Visualizaciones matplotlib
- ReportGenerator: Generación de reportes y exportación  
- GameAnalytics: Solo coordinación entre componentes
"""

from .log_parser import LogParser
from .data_visualizer import DataVisualizer
from .report_generator import ReportGenerator

__all__ = [
    "LogParser",
    "DataVisualizer", 
    "ReportGenerator"
] 