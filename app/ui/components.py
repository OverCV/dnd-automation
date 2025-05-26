import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sys

# from app.games.osuclone.testosuclone import start_osu_test_game


class UIComponents:

    def __init__(self, root, colors, arduino_controller):
        self.root = root
        self.colors = colors
        self.arduino = arduino_controller
        self.monitor_text = None
        self.status_var = tk.StringVar(value="Desconectado")
        self.port_var = tk.StringVar(value="Seleccionar puerto")

        # Configurar callbacks del Arduino
        self.arduino.add_callback("on_connect", self.__on_arduino_connect)
        self.arduino.add_callback("on_disconnect", self.__on_arduino_disconnect)
        self.arduino.add_callback("on_message", self.__on_arduino_message)

    def create_arduino_section(self, parent):
        """Crear sección de conexión Arduino"""
        # Frame principal con estilo moderno
        arduino_frame = tk.Frame(
            parent, bg=self.colors["white"], relief=tk.RAISED, bd=1
        )
        arduino_frame.pack(fill=tk.X, pady=(0, 20))

        # Header de la sección
        header_frame = tk.Frame(arduino_frame, bg=self.colors["medium_blue"], height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="🔌 Conexión Arduino",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["medium_blue"],
            fg=self.colors["white"],
        )
        header_label.pack(expand=True)

        # Contenido de la sección
        content_frame = tk.Frame(arduino_frame, bg=self.colors["white"])
        content_frame.pack(fill=tk.X, padx=15, pady=15)

        # Primera fila: Puerto y botones
        row1_frame = tk.Frame(content_frame, bg=self.colors["white"])
        row1_frame.pack(fill=tk.X, pady=(0, 10))

        # Puerto
        tk.Label(
            row1_frame,
            text="Puerto:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.port_combo = ttk.Combobox(
            row1_frame,
            textvariable=self.port_var,
            values=self.arduino.get_available_ports(),
            state="readonly",
            width=20,
        )
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Botón refrescar
        refresh_btn = ttk.Button(
            row1_frame, text="🔄 Refrescar", command=self.refresh_ports
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Botón conectar
        self.connect_btn = ttk.Button(
            row1_frame, text="🔗 Conectar", command=self.toggle_connection
        )
        self.connect_btn.pack(side=tk.LEFT)

        # Segunda fila: Estado
        row2_frame = tk.Frame(content_frame, bg=self.colors["white"])
        row2_frame.pack(fill=tk.X)

        tk.Label(
            row2_frame,
            text="Estado:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.status_label = tk.Label(
            row2_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["white"],
            fg="red",
            relief=tk.SUNKEN,
            padx=10,
            pady=2,
        )
        self.status_label.pack(side=tk.LEFT)

    def create_games_section(self, parent):
        """Crear sección de juegos"""
        games_frame = tk.Frame(parent, bg=self.colors["white"], relief=tk.RAISED, bd=1)
        games_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Header
        header_frame = tk.Frame(games_frame, bg=self.colors["purple"], height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="🎮 Juegos Neurocognitivos",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["purple"],
            fg=self.colors["white"],
        )
        header_label.pack(expand=True)

        # Contenido
        content_frame = tk.Frame(games_frame, bg=self.colors["white"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Grid de juegos
        for i in range(3):
            content_frame.columnconfigure(i, weight=1, pad=10)

        # Juegos
        games_info = [
            ("🎹 Piano Memoria", "Secuencias tipo Simon"),
            ("🕹️ Pacman Atención", "Atención sostenida"),
            ("🎯 Joystick Coord.", "Coordinación visuomotora"),
        ]

        for i, (title, desc) in enumerate(games_info):
            game_frame = tk.Frame(
                content_frame, bg=self.colors["light_blue"], relief=tk.RAISED, bd=2
            )
            game_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            tk.Label(
                game_frame,
                text=title,
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["light_blue"],
                fg=self.colors["dark_blue"],
            ).pack(pady=(10, 5))

            tk.Label(
                game_frame,
                text=desc,
                font=("Segoe UI", 9),
                bg=self.colors["light_blue"],
                fg=self.colors["medium_blue"],
            ).pack(pady=(0, 10))

            # Botones en fila
            buttons_frame = tk.Frame(game_frame, bg=self.colors["light_blue"])
            buttons_frame.pack(pady=(0, 10))

            # Botón Jugar (Arduino)
            play_btn = ttk.Button(
                buttons_frame,
                text="▶ Jugar",
                command=lambda idx=i: self.select_game(idx + 1),
            )
            play_btn.pack(side=tk.LEFT, padx=2)

            # Botón Prueba (Mouse) - solo para joystick por ahora
            if i == 2:  # Solo para el juego de joystick
                test_btn = ttk.Button(
                    buttons_frame, text="🧪 Prueba", command=lambda: self.test_game(3)
                )
                test_btn.pack(side=tk.LEFT, padx=2)

            # Botón Reporte
            report_btn = ttk.Button(
                buttons_frame,
                text="📊 Reporte",
                command=lambda idx=i: self.open_report(idx + 1),
            )
            report_btn.pack(side=tk.LEFT, padx=2)

    def create_monitor_section(self, parent):
        """Crear sección del monitor"""
        monitor_frame = tk.Frame(
            parent, bg=self.colors["white"], relief=tk.RAISED, bd=1
        )
        monitor_frame.pack(fill=tk.X)

        # Header
        header_frame = tk.Frame(monitor_frame, bg=self.colors["dark_blue"], height=35)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="📡 Monitor de Comunicación",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["dark_blue"],
            fg=self.colors["white"],
        )
        header_label.pack(expand=True)

        # Área de texto
        text_frame = tk.Frame(monitor_frame, bg=self.colors["white"])
        text_frame.pack(fill=tk.X, padx=10, pady=10)

        self.monitor_text = tk.Text(
            text_frame,
            height=6,
            bg="#f8f9fa",
            fg=self.colors["dark_blue"],
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            bd=1,
        )
        self.monitor_text.pack(fill=tk.X)
        self.monitor_text.config(state=tk.DISABLED)

    def refresh_ports(self):
        """Refrescar puertos disponibles"""
        ports = self.arduino.get_available_ports()
        self.port_combo["values"] = ports
        if ports and ports[0] != "No hay puertos disponibles":
            self.port_var.set(ports[0])
        else:
            self.port_var.set("No hay puertos disponibles")

    def toggle_connection(self):
        """Alternar conexión Arduino"""
        if not self.arduino.is_connected():
            port = self.port_var.get()
            if port in ["No hay puertos disponibles", "Seleccionar puerto"]:
                messagebox.showerror("Error", "Por favor selecciona un puerto válido")
                return
            self.arduino.connect(port)
        else:
            self.arduino.disconnect()

    def select_game(self, game_num):
        """Seleccionar juego con Arduino"""
        if game_num == 3:  # Juego de joystick
            try:
                # Agregar la carpeta juegos al path
                sys.path.append(
                    os.path.join(os.path.dirname(__file__), "..", "juegos", "osuclone")
                )
                from games.osuclone.joystick import start_joystick_game

                current_port = self.arduino.get_current_port()
                if not current_port:
                    messagebox.showerror("Error", "No hay conexión Arduino activa")
                    return

                # Desconectar temporalmente
                if self.arduino.is_connected():
                    self.arduino.disconnect()

                # Ejecutar juego
                start_joystick_game(current_port, "medio")
                self.add_to_monitor("Juego de joystick completado")
            except Exception as e:
                messagebox.showerror("Error", f"Error ejecutando juego: {str(e)}")
        else:
            # Otros juegos
            command = f"G{game_num}\n"
            self.arduino.send_command(command)

    def test_game(self, game_num):
        """Ejecutar versión de prueba del juego (sin Arduino)"""
        if game_num == 3:  # Juego de joystick
            try:
                # Ejecutar versión de prueba
                # start_osu_test_game("medio")
                self.add_to_monitor("Prueba de juego de coordinación completada")
            except Exception as e:
                messagebox.showerror("Error", f"Error ejecutando prueba: {str(e)}")
        else:
            messagebox.showinfo(
                "Info", f"Versión de prueba no disponible para el juego {game_num}"
            )

    def open_report(self, report_num):
        """Abrir ventana de reporte"""
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Reporte Neurocognitivo {report_num}")
        report_window.geometry("700x600")
        report_window.configure(bg=self.colors["white"])

        # Header del reporte
        header = tk.Frame(report_window, bg=self.colors["medium_blue"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"📈 Análisis Neurocognitivo - Módulo {report_num}",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["medium_blue"],
            fg=self.colors["white"],
        ).pack(expand=True)

        # Contenido del reporte
        content = tk.Frame(report_window, bg=self.colors["white"])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Simulación de gráfica
        graph_frame = tk.Frame(content, bg=self.colors["light_blue"], height=200)
        graph_frame.pack(fill=tk.X, pady=(0, 20))
        graph_frame.pack_propagate(False)

        tk.Label(
            graph_frame,
            text="📊 Métricas de Rendimiento Cognitivo",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors["light_blue"],
            fg=self.colors["dark_blue"],
        ).pack(expand=True)

        # Métricas simuladas
        metrics_frame = tk.Frame(content, bg=self.colors["white"])
        metrics_frame.pack(fill=tk.X)

        metrics = [
            ("Precisión:", "87.5%"),
            ("Tiempo de reacción promedio:", "1.2s"),
            ("Mejora respecto sesión anterior:", "+12%"),
        ]

        for metric, value in metrics:
            row = tk.Frame(metrics_frame, bg=self.colors["white"])
            row.pack(fill=tk.X, pady=5)

            tk.Label(
                row,
                text=metric,
                font=("Segoe UI", 10, "bold"),
                bg=self.colors["white"],
                fg=self.colors["dark_blue"],
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=value,
                font=("Segoe UI", 10),
                bg=self.colors["white"],
                fg=self.colors["medium_blue"],
            ).pack(side=tk.RIGHT)

    def add_to_monitor(self, message):
        """Agregar mensaje al monitor"""
        if self.monitor_text:
            self.monitor_text.config(state=tk.NORMAL)
            self.monitor_text.insert(tk.END, f"• {message}\n")
            self.monitor_text.see(tk.END)
            self.monitor_text.config(state=tk.DISABLED)

    def __on_arduino_connect(self, port):
        """Callback cuando se conecta Arduino"""
        self.status_var.set("✅ Conectado")
        self.status_label.config(fg="green")
        self.connect_btn.config(text="🔌 Desconectar")
        self.add_to_monitor(f"Conectado exitosamente a {port}")

    def __on_arduino_disconnect(self):
        """Callback cuando se desconecta Arduino"""
        self.status_var.set("❌ Desconectado")
        self.status_label.config(fg="red")
        self.connect_btn.config(text="🔗 Conectar")
        self.add_to_monitor("Desconectado del Arduino")

    def __on_arduino_message(self, message):
        """Callback para mensajes del Arduino"""
        self.add_to_monitor(message)
