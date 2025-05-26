import time
import tkinter as tk
from tkinter import ttk, messagebox
from core.base_game import BaseGame
from typing import Optional, Dict
from core.arduino_manager import ArduinoManager
from games.ping_pong.ping_pong import PingPongGame
from games.two_lanes.two_lanes import TwoLaneRunnerGame
from games.piano.piano import PianoDigitalGame

class GameController:
    def __init__(self, arduino_manager: ArduinoManager, main_window):
        from ui.main_window import MainWindow
        self.main_window:MainWindow = main_window
        self.root = self.main_window.root
        self.arduino = arduino_manager
        self.current_game: Optional[BaseGame] = None
        self.game_widgets = {}
        self.available_games = {
            'ping_pong': PingPongGame,
            'two_lane_runner': TwoLaneRunnerGame,
            'piano_digital': PianoDigitalGame,
            # 'simon': SimonSaysGame,
            # Aquí puedes agregar más juegos que implementen BaseGame
            # 'tetris': TetrisGame,
            # 'snake': SnakeGame,
            # 'breakout': BreakoutGame,
        }
        self.tech_info = {
            'ping_pong': "Juego de Ping Pong con dos palas y una pelota. Requiere sensores de movimiento.",
            'two_lane_runner': "Juego de carreras en dos carriles. Utiliza sensores de distancia para detectar obstáculos.",
            'piano_digital': "Piano digital con teclas táctiles. Requiere sensores capacitivos.",
            # 'simon': "Juego de Simon Says con luces y sonidos. Utiliza LEDs y buzzer.",
            # 'tetris': "Juego clásico de Tetris. Requiere pantalla LCD y botones.",
            # 'snake': "Juego clásico de Snake. Utiliza pantalla OLED y joystick.",
            # 'breakout': "Juego Breakout con bola y paleta. Requiere sensores de movimiento y pantalla."
        }

    def current_game_is_running(self):
        return self.current_game is not None and self.current_game.running

    def stop_current_game(self) -> bool:
        if not self.current_game:
            return True
        try:
            self.current_game.stop_game()
            game_name = self.current_game.name if hasattr(self.current_game, 'name') else 'Juego'
            print(f"🛑 {game_name} detenido")
            self.current_game = None
            # self._notify_status_change()
            return True
        except Exception as e:
            print(f"❌ Error al detener juego: {e}")
            return False


    def start_game(self, game_id):
        """Iniciar un juego"""
        if not self.arduino.connected:
            messagebox.showwarning("Sin conexión", "Conecta el Arduino primero")
            return

        # Detener juego actual
        if self.current_game and self.current_game.running:
            self.current_game.stop_game()
            time.sleep(1)

        # Crear e inicializar nuevo juego
        try:
            game_class = self.available_games[game_id]
            self.current_game = game_class(self.arduino)

            if not self.current_game.start_game():
                messagebox.showerror("Error", f"No se pudo iniciar {self.current_game.name}")
                return

            # Actualizar UI
            self.highlight_active_game(game_id)
            self.update_session_stats()

            # Mostrar información del juego iniciado
            messagebox.showinfo("Juego Iniciado",
                              f"🎮 {self.current_game.name} iniciado correctamente!\n\n"
                              f"Descripción: {self.current_game.description}\n\n"
                              f"¡Diviértete jugando!")

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Error iniciando juego: {e}")


    def stop_game(self):
        """Detener juego actual"""
        if self.current_game and self.current_game.running:
            try:
                game_name = self.current_game.name
                self.current_game.stop_game()

                # Restaurar UI
                self.restore_game_ui()

                messagebox.showinfo("Juego Detenido", f"🛑 {game_name} ha sido detenido correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error deteniendo juego: {e}")

    def update_game_buttons_state(self, enabled):
        """Actualizar estado de botones de juegos"""
        for game_id, widgets in self.game_widgets.items():
            state = tk.NORMAL if enabled else tk.DISABLED
            widgets['start_btn'].config(state=state)

    def create_game_entries(self, parent_frame):
        """Crear entradas para cada juego disponible"""
        for game_id, game_class in self.available_games.items():
            # Crear instancia temporal para obtener info
            temp_game = game_class(arduino_manager=self.arduino)

            # Frame principal del juego
            game_frame = tk.Frame(parent_frame, bg="#2C3E50", relief=tk.RAISED, bd=2)
            game_frame.pack(fill=tk.X, padx=5, pady=8)

            # Frame de información (lado izquierdo)
            info_frame = tk.Frame(game_frame, bg="#2C3E50")
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

            # Título del juego con icono
            game_icons = {
                'ping_pong': '🏓',
                'two_lane_runner': '🏃',
                'tetris': '🧩',
                'snake': '🐍',
                'breakout': '🧱'
            }

            icon = game_icons.get(game_id, '🎮')

            title_label = tk.Label(
                info_frame, text=f"{icon} {temp_game.name}",
                bg="#2C3E50", fg="white", font=("Arial", 18, "bold")
            )
            title_label.pack(anchor=tk.W)

            # Descripción
            desc_label = tk.Label(
                info_frame, text=temp_game.description,
                bg="#2C3E50", fg="#BDC3C7", font=("Arial", 12),
                wraplength=500, justify=tk.LEFT
            )
            desc_label.pack(anchor=tk.W, pady=(5, 10))

            # Información técnica
            tech_info = self.get_game_tech_info(game_id)
            tech_label = tk.Label(
                info_frame, text=tech_info,
                bg="#2C3E50", fg="#95A5A6", font=("Arial", 10),
                justify=tk.LEFT
            )
            tech_label.pack(anchor=tk.W)

            # Frame de controles (lado derecho)
            controls_frame = tk.Frame(game_frame, bg="#2C3E50")
            controls_frame.pack(side=tk.RIGHT, padx=15, pady=15)

            # Botones principales
            start_btn = tk.Button(
                controls_frame, text="▶️ Iniciar Juego",
                command=lambda gid=game_id: self.start_game(gid),
                bg="#27AE60", fg="white", relief=tk.FLAT,
                width=15, height=2, font=("Arial", 11, "bold")
            )
            start_btn.pack(pady=(0, 8))

            stop_btn = tk.Button(
                controls_frame, text="⏹️ Detener",
                command=self.stop_game,
                bg="#E74C3C", fg="white", relief=tk.FLAT,
                width=15, height=2, font=("Arial", 11, "bold")
            )
            stop_btn.pack(pady=(0, 8))

            # Botones secundarios
            status_btn = tk.Button(
                controls_frame, text="📊 Estado Detallado",
                command=lambda gid=game_id: self.show_game_status(gid),
                bg="#F39C12", fg="white", relief=tk.FLAT, width=15, font=("Arial", 10)
            )
            status_btn.pack(pady=(0, 5))

            # Guardar referencias
            self.game_widgets[game_id] = {
                'frame': game_frame,
                'start_btn': start_btn,
                'stop_btn': stop_btn,
                'status_btn': status_btn
            }

    def get_game_tech_info(self, game_id):
        """Obtener información técnica del juego"""
        tech_info: Dict[str, str] = self.tech_info
        return tech_info.get(game_id, "Información técnica no disponible")

    def update_status(self):
        """Actualizar estado periódicamente"""
        try:
            # Actualizar estadísticas de sesión
            self.update_session_stats()
            # Actualizar información del juego actual si está ejecutándose
            if self.current_game and self.current_game.running:
                # Aquí podrías agregar lógica adicional de monitoreo
                pass
        except Exception as e:
            print(f"❌ Error al actualizar estado: {e}")

        # Programar siguiente actualización
        self.root.after(2000, self.update_status)

    def update_session_stats(self):
        """Actualizar estadísticas de sesión"""
        active_game = self.current_game.name if self.current_game and self.current_game.running else "Ninguno"
        self.main_window.session_stats_var.set(
            f"Juegos disponibles: {len(self.available_games)} | "
            f"Juego activo: {active_game} | "
            f"Sesión: {time.strftime('%H:%M:%S')}"
        )

    def restore_game_ui(self):
        """Restaurar UI de juegos al estado normal"""
        for game_id, widgets in self.game_widgets.items():
            widgets['frame'].config(bg="#2C3E50", bd=2)
            widgets['start_btn'].config(text="▶️ Iniciar Juego", state=tk.NORMAL)

    def highlight_active_game(self, active_game_id):
        """Resaltar juego activo visualmente"""
        for game_id, widgets in self.game_widgets.items():
            if game_id == active_game_id:
                widgets['frame'].config(bg="#1ABC9C", bd=3)  # Verde activo
                widgets['start_btn'].config(text="🎮 Ejecutándose", state=tk.DISABLED)
            else:
                widgets['frame'].config(bg="#2C3E50", bd=2)  # Color normal
                widgets['start_btn'].config(text="▶️ Iniciar Juego", state=tk.NORMAL)

    def show_game_status(self, game_id):
        """Mostrar estado detallado del juego"""
        if self.current_game and self.current_game.running:
            status = self.current_game.get_game_status()

            # Crear ventana de estado mejorada
            status_window = tk.Toplevel(self.root)
            status_window.title(f"📊 Estado Detallado - {status['name']}")
            status_window.geometry("600x500")
            status_window.configure(bg="#2C3E50")

            # Título
            title_label = tk.Label(
                status_window, text=f"📊 Estado de {status['name']}",
                bg="#2C3E50", fg="white", font=("Arial", 18, "bold")
            )
            title_label.pack(pady=15)

            # Crear notebook para pestañas
            notebook = ttk.Notebook(status_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

            # Pestaña de estado general
            general_frame = tk.Frame(notebook, bg="#34495E")
            notebook.add(general_frame, text="General")

            # Pestaña de estadísticas
            stats_frame = tk.Frame(notebook, bg="#34495E")
            notebook.add(stats_frame, text="Estadísticas")

            # Contenido de estado general
            self.create_general_status_tab(general_frame, status)

            # Contenido de estadísticas
            self.create_stats_tab(stats_frame, status)

        else:
            messagebox.showinfo("Sin juego activo", "No hay juegos en ejecución para mostrar estado")

    def create_general_status_tab(self, parent, status):
        """Crear pestaña de estado general"""
        # Texto con información del estado
        status_text = tk.Text(
            parent, bg="#2C3E50", fg="#00FF00",
            font=("Consolas", 11), wrap=tk.WORD, height=20
        )
        status_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Formatear información del estado específica para cada juego
        if 'two_lane_runner' in status.get('name', '').lower():
            status_info = f"""🎮 JUEGO: {status['name']}
                            ▶️ Estado: {'🟢 EJECUTÁNDOSE' if status['running'] else '🔴 DETENIDO'}
                            ⏸️ Pausado: {'🟡 SÍ' if status.get('paused', False) else '🟢 NO'}
                            💀 Game Over: {'🔴 SÍ' if status.get('game_over', False) else '🟢 NO'}

                            🏆 PUNTUACIÓN ACTUAL: {status.get('score', 0)}
                            🎯 Mejor Puntuación: {status.get('best_score', 0)}
                            🎲 Total de Partidas: {status.get('total_games', 0)}

                            🏃 POSICIÓN DEL JUGADOR:
                            📍 Coordenadas: {status.get('player_position', 'N/A')}
                            🛤️ Carril Actual: {status.get('player_lane', 'N/A')}

                            🚧 OBSTÁCULOS:
                            📊 Cantidad Activa: {status.get('obstacles_count', 0)}

                            ⚡ VELOCIDAD:
                            🏃 Velocidad Actual: {status.get('speed_percentage', 0)}%

                            🔧 HARDWARE:
                            🔌 Inicializado: {'✅ SÍ' if status.get('hardware_initialized', False) else '❌ NO'}
                            🖥️ LCD: {'✅ Conectado' if status.get('hardware_initialized', False) else '❌ No disponible'}
                            🕹️ Botones: {'✅ Funcionando' if status.get('hardware_initialized', False) else '❌ No disponibles'}
                            """
        else:  # ping_pong
            status_info = f"""🎮 JUEGO: {status['name']}
                                ▶️ Estado: {'🟢 EJECUTÁNDOSE' if status['running'] else '🔴 DETENIDO'}
                                ⏸️ Pausado: {'🟡 SÍ' if status.get('paused', False) else '🟢 NO'}
                                💀 Game Over: {'🔴 SÍ' if status.get('game_over', False) else '🟢 NO'}

                                🏆 PUNTUACIÓN: {status.get('score', 0)}

                                🏓 PELOTA:
                                📍 Posición: {status.get('ball_position', 'N/A')}

                                🏓 PALAS:
                                ← Izquierda: {'🟢 ACTIVA' if status.get('left_paddle', False) else '🔴 INACTIVA'}
                                → Derecha: {'🟢 ACTIVA' if status.get('right_paddle', False) else '🔴 INACTIVA'}

                                🔧 HARDWARE:
                                🔌 Inicializado: {'✅ SÍ' if status.get('hardware_initialized', False) else '❌ NO'}
                                """

        status_text.insert(tk.END, status_info)
        status_text.config(state=tk.DISABLED)

    def create_stats_tab(self, parent, status):
        """Crear pestaña de estadísticas"""
        stats_label = tk.Label(
            parent, text="📈 Estadísticas avanzadas y gráficos\n(Próximamente)",
            bg="#34495E", fg="#BDC3C7", font=("Arial", 14)
        )
        stats_label.pack(expand=True)
