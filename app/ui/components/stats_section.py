"""
Componente de sección de estadísticas para la interfaz principal
"""

import time
import tkinter as tk
from .arduino_colors import ArduinoColors


class StatsSection:
    """Componente para la sección de estadísticas de sesión"""
    
    def __init__(self, parent_frame):
        self.colors = ArduinoColors()
        self.parent = parent_frame
        self.frame = None
        self.session_stats_var = None
        self._create_stats_section()
    
    def _create_stats_section(self):
        """Crear frame de estadísticas generales"""
        self.frame = tk.LabelFrame(
            self.parent, text="📊 Estadísticas de la Sesión",
            bg=self.colors.BLUE_DARK, 
            fg=self.colors.LIGHT_GRAY, 
            font=("Arial", 11, "bold"),
            padx=10, pady=5
        )
        self.frame.pack(fill=tk.X, pady=(0, 10))

        stats_content = tk.Frame(self.frame, bg=self.colors.BLUE_DARK)
        stats_content.pack(fill=tk.X)

        self.session_stats_var = tk.StringVar(
            value=f"Juegos disponibles: 3 | Sesión iniciada: {time.strftime('%H:%M:%S')}"
        )
        
        tk.Label(
            stats_content, 
            textvariable=self.session_stats_var,
            bg=self.colors.BLUE_DARK, 
            fg=self.colors.LIGHT_GRAY, 
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
    
    def update_stats(self, available_games_count, active_game_name="Ninguno"):
        """Actualizar estadísticas mostradas"""
        stats_text = (
            f"Juegos disponibles: {available_games_count} | "
            f"Juego activo: {active_game_name} | "
            f"Sesión: {time.strftime('%H:%M:%S')}"
        )
        self.session_stats_var.set(stats_text)
    
    def get_frame(self):
        """Retorna el frame principal del componente"""
        return self.frame
    
    def get_stats_var(self):
        """Retorna la variable de estadísticas para acceso externo"""
        return self.session_stats_var 