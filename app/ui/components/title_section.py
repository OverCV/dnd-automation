"""
Componente de sección de título para la interfaz principal
"""

import tkinter as tk
from .arduino_colors import ArduinoColors


class TitleSection:
    """Componente para la sección de título de la aplicación"""

    def __init__(self, parent_frame):
        self.colors = ArduinoColors()
        self.parent = parent_frame
        self.frame = None
        self._create_title_section()

    def _create_title_section(self):
        """Crear sección de título"""
        self.frame = tk.Frame(self.parent, bg=self.colors.BLACK)
        self.frame.pack(fill=tk.X, pady=(0, 10))

        # Título principal
        title_label = tk.Label(
            self.frame,
            text="🎮 ARDUINO GAME PLATFORM",
            bg=self.colors.BLACK,
            fg=self.colors.BLUE_LIGHT,
            font=("Arial", 24, "bold"),
        )
        title_label.pack()

        # Subtítulo
        subtitle_label = tk.Label(
            self.frame,
            text="Plataforma de juegos para Arduino con interfaz Python",
            bg=self.colors.BLACK,
            fg=self.colors.BLUE_LIGHT,
            font=("Arial", 12),
        )
        subtitle_label.pack()

    def get_frame(self):
        """Retorna el frame principal del componente"""
        return self.frame
