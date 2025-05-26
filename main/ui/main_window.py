import time
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
from ui.connection_frame import ConnectionFrame
from core.arduino_manager import ArduinoManager
from managers.game_controller import GameController

class MainWindow:
    def __init__(self, arduino_manager: ArduinoManager):

        self.arduino_manager = arduino_manager
        self.root = tk.Tk()
        self.root.title("Arduino Game Manager - Multi-Game Platform")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2C3E50")
        self.game_controller = GameController(arduino_manager, self)
        # Frame principal con scroll
        main_frame = self.create_main_frame()

        # Frames de la aplicación
        self.create_title_section(main_frame)
        self.connection_frame = self.create_connection_frame(main_frame)
        self.create_stats_frame(main_frame)
        self.create_games_section(main_frame)
        self.create_control_frame(main_frame)

        # Inicializar
        self.connection_frame.refresh_ports()
        self.game_controller.update_status()

    def create_main_frame(self):
        """Crear frame principal"""
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        return main_frame

    def create_title_section(self, parent_frame):
        """Crear sección de título"""
        title_frame = tk.Frame(parent_frame, bg="#2C3E50")
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            title_frame,
            text="🎮 ARDUINO GAME PLATFORM",
            bg="#2C3E50", fg="#ECF0F1",
            font=("Arial", 24, "bold")
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Plataforma de juegos para Arduino con interfaz Python",
            bg="#2C3E50", fg="#BDC3C7",
            font=("Arial", 12)
        )
        subtitle_label.pack()

    def create_connection_frame(self, parent_frame):
        self.connection_frame = ConnectionFrame(parent_frame, self.arduino_manager, self.game_controller)
        return self.connection_frame

    def create_stats_frame(self, parent_frame):
        """Crear frame de estadísticas generales"""
        stats_frame = tk.LabelFrame(
            parent_frame, text="📊 Estadísticas de la Sesión",
            bg="#34495E", fg="white", font=("Arial", 11, "bold"),
            padx=10, pady=5
        )
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        stats_content = tk.Frame(stats_frame, bg="#34495E")
        stats_content.pack(fill=tk.X)

        self.session_stats_var = tk.StringVar(value="Juegos disponibles: 2 | Sesión iniciada: " + time.strftime("%H:%M:%S"))
        tk.Label(
            stats_content, textvariable=self.session_stats_var,
            bg="#34495E", fg="#BDC3C7", font=("Arial", 10)
        ).pack(side=tk.LEFT)

    def create_games_section(self, parent_frame):
        """Crear sección de juegos con scroll"""
        # Frame de juegos con scroll
        games_container = tk.Frame(parent_frame, bg="#2C3E50")
        games_container.pack(fill=tk.BOTH, expand=True)

        # Canvas y scrollbar para los juegos
        canvas = tk.Canvas(games_container, bg="#2C3E50", highlightthickness=0)
        scrollbar = ttk.Scrollbar(games_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2C3E50")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Crear marco para juegos
        games_frame = tk.LabelFrame(
            scrollable_frame, text="🎮 Juegos Disponibles",
            bg="#34495E", fg="white", font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        games_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lista de juegos con información detallada
        self.game_controller.create_game_entries(games_frame)

    def create_control_frame(self, parent_frame):
        """Crear frame de control global"""
        control_frame = tk.LabelFrame(
            parent_frame, text="🎛️ Control Global",
            bg="#34495E", fg="white", font=("Arial", 11, "bold"),
            padx=10, pady=5
        )
        control_frame.pack(fill=tk.X, pady=(10, 0))

        control_buttons = tk.Frame(control_frame, bg="#34495E")
        control_buttons.pack(fill=tk.X)

        tk.Button(
            control_buttons, text="🛑 Detener Todo",
            command=self.stop_all_games,
            bg="#E74C3C", fg="white", relief=tk.FLAT, font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            control_buttons, text="📊 Estadísticas Globales",
            command=self.show_global_stats,
            bg="#F39C12", fg="white", relief=tk.FLAT, font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

    def stop_all_games(self):
        """Detener todos los juegos"""
        if self.game_controller.current_game and self.game_controller.current_game_is_running():
            self.game_controller.stop_current_game()

        # Restaurar todos los frames
        self.restore_game_ui()
        messagebox.showinfo("Control Global", "🛑 Todos los juegos han sido detenidos")

    def restore_game_ui(self):
        self.game_controller.restore_game_ui()

    def show_global_stats(self):
        """Mostrar estadísticas globales"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estadísticas Globales")
        stats_window.geometry("500x400")
        stats_window.configure(bg="#2C3E50")

        tk.Label(
            stats_window, text="📊 Estadísticas de la Plataforma",
            bg="#2C3E50", fg="white", font=("Arial", 16, "bold")
        ).pack(pady=20)

        stats_info = f"""🎮 PLATAFORMA DE JUEGOS ARDUINO
                        📦 Juegos Disponibles: {len(self.game_controller.available_games)}
                        🔌 Estado Arduino: {'Conectado' if self.arduino_manager.connected else 'Desconectado'}
                        ⏰ Sesión Iniciada: {time.strftime('%H:%M:%S')}
                        🎲 Juego Actual: {self.game_controller.current_game.name if self.game_controller.current_game and self.game_controller.current_game.running else 'Ninguno'}

                        📈 ESTADÍSTICAS DE USO:
                        - Tiempo de sesión: {time.strftime('%M:%S', time.gmtime(time.time()))}
                        - Conexiones establecidas: 1
                        - Juegos ejecutados: Variable según uso

                        🎯 JUEGOS REGISTRADOS:
                        """

        for game_id, game_class in self.game_controller.available_games.items():
            temp_game = game_class(self.arduino_manager)
            stats_info += f"   • {temp_game.name}\n"

        stats_text = tk.Text(
            stats_window, bg="#34495E", fg="#ECF0F1",
            font=("Consolas", 10), wrap=tk.WORD
        )
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)

    def run(self):
        """Ejecutar aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Manejar cierre de aplicación"""
        try:
            if self.game_controller.current_game and self.game_controller.current_game.running:
                self.game_controller.current_game.stop_game()
            if self.arduino_manager.connected:
                self.arduino_manager.disconnect()
            try:
                pygame.quit()
            except Exception as e:
                print(f"Error cerrando Pygame: {e}")
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
        finally:
            self.root.destroy()
