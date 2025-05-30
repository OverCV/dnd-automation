"""
Componente de sección de control para la interfaz principal
"""

import tkinter as tk
from .arduino_colors import ArduinoColors


class ControlSection:
    """Componente para la sección de control global"""
    
    def __init__(self, parent_frame, analytics_manager):
        self.colors = ArduinoColors()
        self.parent = parent_frame
        self.analytics_manager = analytics_manager
        self.frame = None
        self._create_control_section()
    
    def _create_control_section(self):
        """Crear frame de control global"""
        self.frame = tk.LabelFrame(
            self.parent, text="🎛️ Control Global",
            bg=self.colors.PURPLE, 
            fg=self.colors.LIGHT_GRAY, 
            font=("Arial", 11, "bold"),
            padx=10, pady=5
        )
        self.frame.pack(fill=tk.X, pady=(10, 0))

        control_buttons = tk.Frame(self.frame, bg=self.colors.PURPLE)
        control_buttons.pack(fill=tk.X)

        # Botón de análisis
        tk.Button(
            control_buttons, text="📈 Análisis de Logs",
            command=self.analytics_manager.show_analytics,
            bg=self.colors.ERROR, 
            fg=self.colors.BLUE_DARK, 
            relief=tk.FLAT, 
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Botón de estadísticas globales
        tk.Button(
            control_buttons, text="📊 Estadísticas Globales",
            command=self.analytics_manager.show_global_stats,
            bg=self.colors.INFO, 
            fg=self.colors.BLUE_DARK, 
            relief=tk.FLAT, 
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
    
    def get_frame(self):
        """Retorna el frame principal del componente"""
        return self.frame 