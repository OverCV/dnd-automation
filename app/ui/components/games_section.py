"""
Componente de sección de juegos para la interfaz principal
"""

import tkinter as tk
from tkinter import ttk
from .arduino_colors import ArduinoColors


class GamesSection:
    """Componente para la sección de juegos con scroll"""
    
    def __init__(self, parent_frame, game_controller):
        self.colors = ArduinoColors()
        self.parent = parent_frame
        self.game_controller = game_controller
        self.frame = None
        self.games_frame = None
        self._create_games_section()
    
    def _create_games_section(self):
        """Crear sección de juegos con scroll"""
        # Frame de juegos con scroll
        games_container = tk.Frame(self.parent, bg=self.colors.BLACK)
        games_container.pack(fill=tk.BOTH, expand=True)

        # Canvas y scrollbar para los juegos
        canvas = tk.Canvas(games_container, bg=self.colors.BLACK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(games_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors.BLACK)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Crear marco para juegos
        self.games_frame = tk.LabelFrame(
            scrollable_frame, text="🎮 Juegos Disponibles",
            bg=self.colors.BLUE_MID, 
            fg=self.colors.LIGHT_GRAY, 
            font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        self.games_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurar el frame principal
        self.frame = games_container
    
    def initialize_games(self):
        """Inicializar entradas de juegos usando el game controller"""
        self.game_controller.create_game_entries(self.games_frame)
    
    def get_frame(self):
        """Retorna el frame principal del componente"""
        return self.frame
    
    def get_games_frame(self):
        """Retorna el frame específico donde van los juegos"""
        return self.games_frame 