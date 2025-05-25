import tkinter as tk
from tkinter import ttk
from controller import InoController
from components import UIComponents


class MainWindow:
    """Clase principal que maneja la ventana y coordina los componentes"""

    # Paleta de colores Arduino
    COLORS = {
        "white": "#ffffff",
        "light_blue": "#4fccf3",
        "medium_blue": "#3186a0",
        "purple": "#4a2370",
        "dark_blue": "#1d2087",
        "black": "#000000",
    }

    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_style()

        # Inicializar controlador Arduino
        self.arduino_controller = InoController()

        # Inicializar componentes UI
        self.ui_components = UIComponents(
            self.root, self.COLORS, self.arduino_controller
        )

        # Crear la interfaz
        self.create_interface()

        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Configurar la ventana principal"""
        self.root.title("Sistema Neurocognitivo Arduino")
        self.root.geometry("800x700")
        self.root.configure(bg=self.COLORS["light_blue"])
        self.root.resizable(True, True)

        # Centrar ventana
        self.center_window()

    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_style(self):
        """Configurar estilos modernos para ttk"""
        style = ttk.Style()

        # Crear tema personalizado Arduino
        style.theme_create(
            "arduino_theme",
            settings={
                "TLabel": {
                    "configure": {
                        "background": self.COLORS["light_blue"],
                        "foreground": self.COLORS["dark_blue"],
                        "font": (10, 10),
                    }
                },
                "TButton": {
                    "configure": {
                        "background": self.COLORS["medium_blue"],
                        "foreground": self.COLORS["white"],
                        "font": (10, 10, "bold"),
                        "borderwidth": 0,
                        "focuscolor": "none",
                        "padding": (10, 8),
                    },
                    "map": {
                        "background": [
                            ("active", self.COLORS["dark_blue"]),
                            ("pressed", self.COLORS["purple"]),
                        ],
                        "foreground": [("active", self.COLORS["white"])],
                    },
                },
                "TFrame": {
                    "configure": {
                        "background": self.COLORS["light_blue"],
                        "borderwidth": 0,
                    }
                },
                "TCombobox": {
                    "configure": {
                        "fieldbackground": self.COLORS["white"],
                        "background": self.COLORS["medium_blue"],
                        "foreground": self.COLORS["dark_blue"],
                        "borderwidth": 1,
                        "relief": "solid",
                    }
                },
            },
        )

        style.theme_use("arduino_theme")

    def create_interface(self):
        """Crear la interfaz principal"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self.create_header(main_frame)

        # Sección de conexión Arduino
        self.ui_components.create_arduino_section(main_frame)

        # Sección de juegos
        self.ui_components.create_games_section(main_frame)

        # Monitor de comunicación
        self.ui_components.create_monitor_section(main_frame)

    def create_header(self, parent):
        """Crear header moderno"""
        header_frame = tk.Frame(parent, bg=self.COLORS["dark_blue"], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        # Título principal
        title_label = tk.Label(
            header_frame,
            text="Sistema Interactivo de Control Adaptativo",
            font=("Segoe UI", 18, "bold"),
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["white"],
        )
        title_label.pack(expand=True)

        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Estimulación y Monitorización Neurocognitiva",
            font=("Segoe UI", 12),
            bg=self.COLORS["dark_blue"],
            fg=self.COLORS["light_blue"],
        )
        subtitle_label.pack()

    def on_closing(self):
        """Manejar cierre de la aplicación"""
        if self.arduino_controller.is_connected():
            self.arduino_controller.disconnect()
        self.root.destroy()
