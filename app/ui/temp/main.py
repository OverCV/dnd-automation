import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time


class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Juegos Arduino")
        self.root.geometry("650x500")
        self.root.configure(bg="#4fccf3")  # Fondo arduino

        # Variables para la comunicación serial
        self.arduino_port = None
        self.arduino_connection = None
        self.connected = False

        # Configurar fuente personalizada
        self.title_font = tkfont.Font(family="Arial", size=14, weight="bold")
        self.button_font = tkfont.Font(family="Arial", size=12)

        # Crear marco principal
        self.main_frame = tk.Frame(root, bg="#3186a0", padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para la conexión Arduino
        self.arduino_frame = tk.Frame(
            self.main_frame,
            bg="#1d2087",
            pady=10,
            bd=2,
            relief=tk.RAISED,
        )
        self.arduino_frame.pack(fill=tk.X)

        # Dropdown para puertos COM
        self.port_label = tk.Label(
            self.arduino_frame,
            text="Puerto Arduino:",
            # bg="#1d2087",
            font=(
                "Arial",
                10,
            ),
        )
        self.port_label.pack(side=tk.LEFT, padx=(0, 10))

        self.port_var = tk.StringVar(root)
        self.port_var.set("Seleccionar puerto")
        self.ports_available = self.get_arduino_ports()
        self.port_menu = tk.OptionMenu(
            self.arduino_frame, self.port_var, *self.ports_available
        )
        self.port_menu.config(width=20)
        self.port_menu.pack(side=tk.LEFT, padx=(0, 10))

        # Botón para refrescar puertos
        self.refresh_button = tk.Button(
            self.arduino_frame, text="Refrescar", command=self.refresh_ports
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # Botón para conectar/desconectar
        self.connect_button = tk.Button(
            self.arduino_frame, text="Conectar", command=self.toggle_connection
        )
        self.connect_button.pack(side=tk.LEFT)

        # Estado de conexión
        self.status_var = tk.StringVar(value="Desconectado")
        self.status_label = tk.Label(
            self.arduino_frame,
            textvariable=self.status_var,
            bg="#FFB6B6",
            fg="red",
            font=("Arial", 10, "bold"),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Título
        self.title_frame = tk.Frame(
            self.main_frame,
            # bg="#1d2087",
            padx=10,
            pady=10,
        )
        self.title_frame.pack(fill=tk.X, pady=(0, 20))

        self.title_label = tk.Label(
            self.title_frame,
            text="Título",
            font=self.title_font,
            # bg="#1d2087",
            fg="#000000",
        )
        self.title_label.pack()

        # Crear contenedor para los juegos y reportes
        self.games_container = tk.Frame(self.main_frame, bg="#4fccf3")
        self.games_container.pack(fill=tk.BOTH, expand=True)

        # Definir columnas para los juegos y reportes
        for i in range(3):
            self.games_container.columnconfigure(i, weight=1, pad=10)

        # Crear botones para juegos
        self.game_buttons = []
        self.report_buttons = []

        for i in range(3):
            # Juego
            game_button = tk.Button(
                self.games_container,
                text=f"Juego {i + 1}",
                font=self.button_font,
                # bg="#FFEF99",
                padx=10,
                pady=5,
                relief=tk.RAISED,
                bd=2,
                command=lambda idx=i: self.select_game(idx + 1),
            )
            game_button.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.game_buttons.append(game_button)

            # Reporte
            report_button = tk.Button(
                self.games_container,
                text=f"Reporte {i + 1}",
                font=self.button_font,
                # bg="#FFEF99",
                padx=10,
                pady=5,
                relief=tk.RAISED,
                bd=2,
                command=lambda idx=i: self.open_report(idx + 1),
            )
            report_button.grid(row=1, column=i, padx=10, pady=10, sticky="ew")
            self.report_buttons.append(report_button)

        # Monitor de comunicación serial
        self.monitor_frame = tk.Frame(self.main_frame, bg="#E0E0E0", padx=5, pady=5)
        self.monitor_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        self.monitor_label = tk.Label(
            self.monitor_frame,
            text="Monitor Serial:",
            bg="#E0E0E0",
            font=("Arial", 10, "bold"),
            anchor="w",
        )
        self.monitor_label.pack(fill=tk.X)

        self.monitor_text = tk.Text(
            self.monitor_frame, height=5, bg="white", wrap=tk.WORD
        )
        self.monitor_text.pack(fill=tk.BOTH, expand=True)
        self.monitor_text.config(state=tk.DISABLED)

        # Configurar cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_arduino_ports(self):
        """Obtener lista de puertos seriales disponibles"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if not ports:
            return ["No hay puertos disponibles"]
        return ports

    def refresh_ports(self):
        """Actualizar la lista de puertos disponibles"""
        self.ports_available = self.get_arduino_ports()
        menu = self.port_menu["menu"]
        menu.delete(0, "end")
        for port in self.ports_available:
            menu.add_command(label=port, command=lambda p=port: self.port_var.set(p))

        if self.ports_available:
            self.port_var.set(self.ports_available[0])
        else:
            self.port_var.set("No hay puertos disponibles")

    def toggle_connection(self):
        """Conectar o desconectar del Arduino"""
        if not self.connected:
            port = self.port_var.get()
            if port == "No hay puertos disponibles" or port == "Seleccionar puerto":
                messagebox.showerror("Error", "Por favor selecciona un puerto válido")
                return

            try:
                # Intentar conectar al Arduino (9600 es el baudrate común)
                self.arduino_connection = serial.Serial(port, 9600, timeout=1)
                time.sleep(2)  # Dar tiempo para que se establezca la conexión
                self.connected = True
                self.status_var.set("Conectado")
                self.status_label.config(fg="green")
                self.connect_button.config(text="Desconectar")
                self.add_to_monitor(f"Conectado a {port}")
            except Exception as e:
                messagebox.showerror(
                    "Error de Conexión", f"No se pudo conectar: {str(e)}"
                )
                self.add_to_monitor(f"Error de conexión: {str(e)}")
        else:
            # Desconectar
            if self.arduino_connection:
                self.arduino_connection.close()
            self.connected = False
            self.status_var.set("Desconectado")
            self.status_label.config(fg="red")
            self.connect_button.config(text="Conectar")
            self.add_to_monitor("Desconectado del Arduino")

    def add_to_monitor(self, message):
        """Añadir mensaje al monitor serial"""
        self.monitor_text.config(state=tk.NORMAL)
        self.monitor_text.insert(tk.END, f"{message}\n")
        self.monitor_text.see(tk.END)  # Auto-scroll al final
        self.monitor_text.config(state=tk.DISABLED)

    def select_game(self, game_num):
        """Enviar comando al Arduino para seleccionar un juego"""
        if not self.connected:
            messagebox.showwarning(
                "No Conectado", "Por favor conecta al Arduino primero."
            )
            return

        if game_num == 3:  # Asumiendo que el juego de joystick es el juego 3
            # Importar y ejecutar el juego de joystick
            from joystick_game import start_joystick_game

            # Obtener puerto actual
            current_port = self.port_var.get()

            # Cerrar conexión temporal para el juego
            if self.arduino_connection:
                self.arduino_connection.close()
                self.connected = False
                self.status_var.set("Desconectado")
                self.status_label.config(fg="red")
                self.connect_button.config(text="Conectar")

            # Ejecutar juego
            try:
                start_joystick_game(
                    current_port, "medio"
                )  # Puedes hacer esto configurable
            except Exception as e:
                messagebox.showerror("Error", f"Error ejecutando juego: {str(e)}")

            self.add_to_monitor("Juego de joystick completado")
        else:
            # Tu código original para otros juegos
            try:
                command = f"G{game_num}\n"
                self.arduino_connection.write(command.encode())
                self.add_to_monitor(f"Enviado: Juego {game_num} seleccionado")

                time.sleep(0.5)
                if self.arduino_connection.in_waiting:
                    response = (
                        self.arduino_connection.readline().decode("utf-8").strip()
                    )
                    self.add_to_monitor(f"Recibido: {response}")
            except Exception as e:
                messagebox.showerror(
                    "Error de Comunicación", f"Error al enviar comando: {str(e)}"
                )
                self.add_to_monitor(f"Error: {str(e)}")

    def open_report(self, report_num):
        """Abrir ventana de reporte al hacer clic en un botón de reporte"""
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Reporte {report_num}")
        report_window.geometry("600x500")
        report_window.configure(bg="#FFEF99")  # Fondo amarillo claro

        # Contenido del reporte
        report_frame = tk.Frame(report_window, bg="#FFEF99", padx=20, pady=20)
        report_frame.pack(fill=tk.BOTH, expand=True)

        # Gráfica (simulada con un marco)
        graph_frame = tk.Frame(
            report_frame, bg="#A7D5F2", padx=10, pady=10
        )  # Fondo azul claro
        graph_frame.pack(fill=tk.X, pady=(0, 20), ipady=60)

        graph_label = tk.Label(
            graph_frame,
            text="Estadísticas generales",
            font=self.button_font,
            bg="#A7D5F2",
        )
        graph_label.pack()

        # Canvas para simular la gráfica
        canvas = tk.Canvas(graph_frame, bg="#A7D5F2", height=100, highlightthickness=0)
        canvas.pack(fill=tk.X)
        # Dibujar una línea simulando un gráfico
        canvas.create_line(
            50, 80, 150, 30, 250, 60, 350, 20, 450, 40, fill="blue", width=2
        )

        # Título del reporte
        report_title = tk.Label(
            report_frame,
            text=f"Reporte {report_num}",
            font=self.title_font,
            bg="#FFEF99",
        )
        report_title.pack(pady=(0, 10))

        # Texto del reporte (Lorem ipsum)
        for _ in range(2):
            report_text = tk.Label(
                report_frame,
                text="Lorem ipsum dolor sit amet",
                font=("Arial", 10),
                fg="#3D7AB3",
                bg="#FFEF99",
                justify=tk.LEFT,
            )
            report_text.pack(anchor=tk.W, pady=2)

            report_detail = tk.Label(
                report_frame,
                text="Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet",
                font=("Arial", 10),
                fg="#3D7AB3",
                bg="#FFEF99",
                justify=tk.LEFT,
            )
            report_detail.pack(anchor=tk.W, pady=(0, 10))

        # Botón de conclusión
        conclusion_button = tk.Button(
            report_frame,
            text="Procura comer más nueces",
            font=self.button_font,
            bg="#FFEF99",
            fg="#3D7AB3",
            relief=tk.FLAT,
        )
        conclusion_button.pack(pady=10)

    def on_closing(self):
        """Manejar cierre de la aplicación"""
        if self.connected and self.arduino_connection:
            self.arduino_connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
