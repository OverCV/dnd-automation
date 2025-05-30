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
        scrollbar = ttk.Scrollbar(
            games_container, orient="vertical", command=canvas.yview
        )
        scrollable_frame = tk.Frame(canvas, bg=self.colors.BLACK)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Crear marco para juegos
        self.games_frame = tk.LabelFrame(
            scrollable_frame,
            text="🎮 Juegos Disponibles",
            bg=self.colors.BLUE_MID,
            fg=self.colors.LIGHT_GRAY,
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10,
        )
        self.games_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para análisis cognitivo
        cognitive_frame = tk.LabelFrame(
            scrollable_frame,
            text="🧠 Análisis Cognitivo",
            bg=self.colors.GREEN_MID,
            fg=self.colors.LIGHT_GRAY,
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10,
        )
        cognitive_frame.pack(fill=tk.X, padx=5, pady=5)

        # Botón de análisis cognitivo
        cognitive_button = tk.Button(
            cognitive_frame,
            text="📊 Ver Análisis y Gráficas",
            font=("Arial", 11, "bold"),
            bg=self.colors.GREEN_DARK,
            fg=self.colors.WHITE,
            activebackground=self.colors.GREEN_LIGHT,
            activeforeground=self.colors.BLACK,
            relief=tk.RAISED,
            bd=2,
            padx=20,
            pady=10,
            command=self._open_cognitive_analysis,
        )
        cognitive_button.pack(fill=tk.X, padx=5, pady=5)

        # Información del análisis cognitivo
        info_label = tk.Label(
            cognitive_frame,
            text="💡 Los datos se guardan automáticamente al jugar cualquier juego cognitivo",
            font=("Arial", 9),
            bg=self.colors.GREEN_MID,
            fg=self.colors.LIGHT_GRAY,
            wraplength=400,
        )
        info_label.pack(pady=(0, 5))

        # Configurar el frame principal
        self.frame = games_container

    def _open_cognitive_analysis(self):
        """Abrir pantalla de análisis cognitivo"""
        try:
            # Importar la pantalla modular
            from ui.cognitive.cognitive_screen import CognitiveScreen

            print("🧠 Abriendo análisis cognitivo...")

            # Crear y ejecutar pantalla con arduino (no arduino_manager)
            cognitive_screen = CognitiveScreen(self.game_controller.arduino)
            cognitive_screen.run()

        except ImportError:
            self._show_cognitive_error("Módulos cognitivos no disponibles")
        except Exception as e:
            self._show_cognitive_error(f"Error: {e}")

    def _show_cognitive_error(self, message: str):
        """Mostrar error relacionado con análisis cognitivo"""
        from tkinter import messagebox

        messagebox.showerror(
            "Error Análisis Cognitivo",
            f"❌ {message}\n\nAsegúrate de que los módulos cognitivos estén instalados correctamente.",
        )

    def initialize_games(self):
        """Inicializar entradas de juegos usando el game controller"""
        self.game_controller.create_game_entries(self.games_frame)

    def get_frame(self):
        """Retorna el frame principal del componente"""
        return self.frame

    def get_games_frame(self):
        """Retorna el frame específico donde van los juegos"""
        return self.games_frame
