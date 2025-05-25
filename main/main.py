import inspect
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

import tkinter as tk
from tkinter import ttk, messagebox
import time
import sys
from pathlib import Path
import inspect

try:
    import serial.tools.list_ports
    import pygame
except ImportError:
    print("❌ Instalar dependencias:")
    print("   pip install pyfirmata pygame pyserial")
    sys.exit(1)

# Importar las clases base
from core.arduino_manager import ArduinoManager
from games.ping_pong.ping_pong import PingPongGame
from games.two_lanes.two_lanes import TwoLaneRunnerGame


class GameManager:
    """Gestor principal de juegos"""

    def __init__(self):
        self.arduino = ArduinoManager()
        self.current_game = None
        self.available_games = {
            'ping_pong': PingPongGame,
            'two_lane_runner': TwoLaneRunnerGame,
            # Aquí puedes agregar más juegos que implementen BaseGame
            # 'tetris': TetrisGame,
            # 'snake': SnakeGame,
            # 'breakout': BreakoutGame,
        }

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Arduino Game Manager - Multi-Game Platform")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2C3E50")

        # Variables de UI
        self.game_widgets = {}  # Para trackear widgets de cada juego

        self.create_ui()

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Frame principal con scroll
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Título principal
        title_frame = tk.Frame(main_frame, bg="#2C3E50")
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

        # Frame de conexión
        conn_frame = tk.LabelFrame(
            main_frame, text="🔌 Conexión Arduino",
            bg="#34495E", fg="white", font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        # Primera fila de conexión
        conn_row1 = tk.Frame(conn_frame, bg="#34495E")
        conn_row1.pack(fill=tk.X, pady=(0, 5))

        tk.Label(conn_row1, text="Puerto:", bg="#34495E", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_row1, textvariable=self.port_var, width=20, font=("Arial", 10))
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            conn_row1, text="🔄 Refrescar",
            command=self.refresh_ports,
            bg="#3498DB", fg="white", relief=tk.FLAT, font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            conn_row1, text="🔍 Auto-detectar",
            command=self.auto_detect_port,
            bg="#9B59B6", fg="white", relief=tk.FLAT, font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.connect_btn = tk.Button(
            conn_row1, text="Conectar",
            command=self.toggle_connection,
            bg="#27AE60", fg="white", relief=tk.FLAT, width=12, font=("Arial", 10, "bold")
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Estado de conexión
        self.status_var = tk.StringVar(value="❌ Desconectado")
        status_label = tk.Label(
            conn_row1, textvariable=self.status_var,
            bg="#34495E", fg="#E74C3C", font=("Arial", 11, "bold")
        )
        status_label.pack(side=tk.LEFT)

        # Segunda fila - información adicional
        conn_row2 = tk.Frame(conn_frame, bg="#34495E")
        conn_row2.pack(fill=tk.X)

        self.arduino_info_var = tk.StringVar(value="Información del Arduino aparecerá aquí")
        info_label = tk.Label(
            conn_row2, textvariable=self.arduino_info_var,
            bg="#34495E", fg="#BDC3C7", font=("Arial", 9)
        )
        info_label.pack(side=tk.LEFT)

        # Frame de estadísticas generales
        stats_frame = tk.LabelFrame(
            main_frame, text="📊 Estadísticas de la Sesión",
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

        # Frame de juegos con scroll
        games_container = tk.Frame(main_frame, bg="#2C3E50")
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
        self.create_game_entries(games_frame)

        # Frame de control global
        control_frame = tk.LabelFrame(
            main_frame, text="🎛️ Control Global",
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

        tk.Button(
            control_buttons, text="⚙️ Configuración",
            command=self.show_settings,
            bg="#95A5A6", fg="white", relief=tk.FLAT, font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Inicializar
        self.refresh_ports()
        self.update_status()

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

            config_btn = tk.Button(
                controls_frame, text="⚙️ Configurar",
                command=lambda gid=game_id: self.configure_game(gid),
                bg="#9B59B6", fg="white", relief=tk.FLAT, width=15, font=("Arial", 10)
            )
            config_btn.pack()

            # Guardar referencias
            self.game_widgets[game_id] = {
                'frame': game_frame,
                'start_btn': start_btn,
                'stop_btn': stop_btn,
                'status_btn': status_btn,
                'config_btn': config_btn
            }

    def get_game_tech_info(self, game_id):
        """Obtener información técnica del juego"""
        tech_info = {
            'ping_pong': "Hardware: LCD 16x2, Botones L/R\nControles: ←→ (palas), SELECT (pausa)\nObjetivo: Mantener pelota rebotando",
            'two_lane_runner': "Hardware: LCD 16x2, Botones ↑↓\nControles: ↑↓ (cambiar carril), SELECT (pausa)\nObjetivo: Esquivar obstáculos corriendo"
        }
        return tech_info.get(game_id, "Información técnica no disponible")

    def refresh_ports(self):
        """Refrescar lista de puertos"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo['values'] = ports
            if ports:
                self.port_var.set(ports[0])
                # Actualizar información
                port_info = serial.tools.list_ports.comports()
                if port_info:
                    self.arduino_info_var.set(f"Puertos detectados: {len(ports)} | Ejemplo: {port_info[0].description}")
        except Exception as e:
            self.arduino_info_var.set(f"Error detectando puertos: {str(e)}")

    def auto_detect_port(self):
        """Auto-detectar puerto del Arduino"""
        arduino_port = self.arduino.find_arduino_port()
        if arduino_port:
            self.port_var.set(arduino_port)
            self.arduino_info_var.set(f"Arduino detectado automáticamente en {arduino_port}")
        else:
            messagebox.showwarning("Auto-detección", "No se encontró un Arduino conectado automáticamente")
            self.arduino_info_var.set("Arduino no detectado - selecciona puerto manualmente")

    def toggle_connection(self):
        """Conectar/desconectar Arduino"""
        if not self.arduino.connected:
            port = self.port_var.get()
            if not port:
                messagebox.showerror("Error", "Selecciona un puerto")
                return

            if self.arduino.connect(port):
                self.status_var.set("✅ Conectado")
                self.connect_btn.config(text="Desconectar", bg="#E74C3C")
                self.arduino_info_var.set(f"Conectado exitosamente a {port} | Firmata activo")
                # Habilitar botones de juegos
                self.update_game_buttons_state(True)
            else:
                messagebox.showerror("Error", "No se pudo conectar al Arduino")
                self.arduino_info_var.set("Error de conexión - verifica cable y puerto")
        else:
            # Detener juego actual antes de desconectar
            if self.current_game and self.current_game.running:
                self.stop_game()

            self.arduino.disconnect()
            self.status_var.set("❌ Desconectado")
            self.connect_btn.config(text="Conectar", bg="#27AE60")
            self.arduino_info_var.set("Desconectado del Arduino")
            # Deshabilitar botones de juegos
            self.update_game_buttons_state(False)

    def update_game_buttons_state(self, enabled):
        """Actualizar estado de botones de juegos"""
        for game_id, widgets in self.game_widgets.items():
            state = tk.NORMAL if enabled else tk.DISABLED
            widgets['start_btn'].config(state=state)
            widgets['config_btn'].config(state=state)

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

    def highlight_active_game(self, active_game_id):
        """Resaltar juego activo visualmente"""
        for game_id, widgets in self.game_widgets.items():
            if game_id == active_game_id:
                widgets['frame'].config(bg="#1ABC9C", bd=3)  # Verde activo
                widgets['start_btn'].config(text="🎮 Ejecutándose", state=tk.DISABLED)
            else:
                widgets['frame'].config(bg="#2C3E50", bd=2)  # Color normal
                widgets['start_btn'].config(text="▶️ Iniciar Juego", state=tk.NORMAL)

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

    def stop_all_games(self):
        """Detener todos los juegos"""
        if self.current_game and self.current_game.running:
            self.stop_game()

        # Restaurar todos los frames
        self.restore_game_ui()
        messagebox.showinfo("Control Global", "🛑 Todos los juegos han sido detenidos")

    def restore_game_ui(self):
        """Restaurar UI de juegos al estado normal"""
        for game_id, widgets in self.game_widgets.items():
            widgets['frame'].config(bg="#2C3E50", bd=2)
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

    def configure_game(self, game_id):
        """Configurar opciones del juego"""
        config_window = tk.Toplevel(self.root)
        config_window.title(f"⚙️ Configuración - {game_id}")
        config_window.geometry("400x300")
        config_window.configure(bg="#2C3E50")

        tk.Label(
            config_window, text=f"⚙️ Configuración de {game_id}",
            bg="#2C3E50", fg="white", font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Label(
            config_window, text="Configuraciones específicas del juego\n(Próximamente)",
            bg="#2C3E50", fg="#BDC3C7", font=("Arial", 12)
        ).pack(expand=True)

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

📦 Juegos Disponibles: {len(self.available_games)}
🔌 Estado Arduino: {'Conectado' if self.arduino.connected else 'Desconectado'}
⏰ Sesión Iniciada: {time.strftime('%H:%M:%S')}
🎲 Juego Actual: {self.current_game.name if self.current_game and self.current_game.running else 'Ninguno'}

📈 ESTADÍSTICAS DE USO:
   - Tiempo de sesión: {time.strftime('%M:%S', time.gmtime(time.time()))}
   - Conexiones establecidas: 1
   - Juegos ejecutados: Variable según uso

🎯 JUEGOS REGISTRADOS:
"""

        for game_id, game_class in self.available_games.items():
            temp_game = game_class(self.arduino)
            stats_info += f"   • {temp_game.name}\n"

        stats_text = tk.Text(
            stats_window, bg="#34495E", fg="#ECF0F1",
            font=("Consolas", 10), wrap=tk.WORD
        )
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)

    def show_settings(self):
        """Mostrar configuración global"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Configuración Global")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#2C3E50")

        tk.Label(
            settings_window, text="⚙️ Configuración de la Plataforma",
            bg="#2C3E50", fg="white", font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Label(
            settings_window, text="Configuraciones globales\ny preferencias del usuario\n(Próximamente)",
            bg="#2C3E50", fg="#BDC3C7", font=("Arial", 12)
        ).pack(expand=True)

    def update_session_stats(self):
        """Actualizar estadísticas de sesión"""
        active_game = self.current_game.name if self.current_game and self.current_game.running else "Ninguno"
        self.session_stats_var.set(
            f"Juegos disponibles: {len(self.available_games)} | "
            f"Juego activo: {active_game} | "
            f"Sesión: {time.strftime('%H:%M:%S')}"
        )

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
            pass

        # Programar siguiente actualización
        self.root.after(2000, self.update_status)

    def run(self):
        """Ejecutar aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Manejar cierre de aplicación"""
        try:
            if self.current_game and self.current_game.running:
                self.current_game.stop_game()
            if self.arduino.connected:
                self.arduino.disconnect()
            try:
                pygame.quit()
            except Exception as e:
                print(f"Error cerrando Pygame: {e}")
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
        finally:
            self.root.destroy()


def main():
    """Función principal"""
    print("🎮 Arduino Multi-Game Platform - Versión 2.0")
    print("=" * 60)
    print("🎯 Juegos disponibles: Ping Pong, Two-Lane Runner")
    print("🔧 Hardware soportado: Arduino + LCD Keypad Shield")
    print("🚀 Tecnología: Python + Firmata + Pygame")
    print("=" * 60)

    try:
        app = GameManager()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por usuario")
    except Exception as e:
        print(f"❌ Error crítico: {e}")


if __name__ == "__main__":
    main()
