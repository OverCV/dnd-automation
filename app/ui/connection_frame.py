import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports

from core.arduino_manager import ArduinoManager
from managers.game_controller import GameController


class ConnectionFrame:
    """Crear frame de conexión Arduino"""

    def __init__(
        self, parent, arduino: ArduinoManager, game_controller: GameController
    ):
        self.arduino = arduino
        self.game_controller = game_controller
        conn_frame = tk.LabelFrame(
            parent,
            text="🔌 Conexión Arduino",
            bg="#34495E",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10,
        )
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        # Primera fila de conexión
        self._create_connection_row1(conn_frame)

        # Segunda fila - información adicional
        self._create_connection_row2(conn_frame)

    def _create_connection_row1(self, conn_frame):
        """Crear primera fila del frame de conexión"""
        conn_row1 = tk.Frame(conn_frame, bg="#34495E")
        conn_row1.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            conn_row1, text="Puerto:", bg="#34495E", fg="white", font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            conn_row1, textvariable=self.port_var, width=20, font=("Arial", 10)
        )
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            conn_row1,
            text="🔄 Refrescar",
            command=self.refresh_ports,
            bg="#3498DB",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            conn_row1,
            text="🔍 Auto-detectar",
            command=self.auto_detect_port,
            bg="#9B59B6",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 9),
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.connect_btn = tk.Button(
            conn_row1,
            text="Conectar",
            command=self.toggle_connection,
            bg="#27AE60",
            fg="white",
            relief=tk.FLAT,
            width=12,
            font=("Arial", 10, "bold"),
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Estado de conexión
        self.status_var = tk.StringVar(value="❌ Desconectado")
        status_label = tk.Label(
            conn_row1,
            textvariable=self.status_var,
            bg="#34495E",
            fg="#E74C3C",
            font=("Arial", 11, "bold"),
        )
        status_label.pack(side=tk.LEFT)

        return conn_row1

    def _create_connection_row2(self, conn_frame):
        """Crear segunda fila del frame de conexión"""
        conn_row2 = tk.Frame(conn_frame, bg="#34495E")
        conn_row2.pack(fill=tk.X)

        self.arduino_info_var = tk.StringVar(
            value="Información del Arduino aparecerá aquí"
        )
        info_label = tk.Label(
            conn_row2,
            textvariable=self.arduino_info_var,
            bg="#34495E",
            fg="#BDC3C7",
            font=("Arial", 9),
        )
        info_label.pack(side=tk.LEFT)

        return conn_row2

    def refresh_ports(self):
        """Refrescar lista de puertos"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo["values"] = ports
            if ports:
                self.port_var.set(ports[0])
                # Actualizar información
                port_info = serial.tools.list_ports.comports()
                if port_info:
                    self.arduino_info_var.set(
                        f"Puertos detectados: {len(ports)} | Ejemplo: {port_info[0].description}"
                    )
        except Exception as e:
            self.arduino_info_var.set(f"Error detectando puertos: {str(e)}")

    def auto_detect_port(self):
        """Auto-detectar puerto del Arduino"""
        arduino_port = self.arduino.find_arduino_port()
        if arduino_port:
            self.port_var.set(arduino_port)
            self.arduino_info_var.set(
                f"Arduino detectado automáticamente en {arduino_port}"
            )
        else:
            messagebox.showwarning(
                "Auto-detección", "No se encontró un Arduino conectado automáticamente"
            )
            self.arduino_info_var.set(
                "Arduino no detectado - selecciona puerto manualmente"
            )

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
                self.arduino_info_var.set(
                    f"Conectado exitosamente a {port} | Firmata activo"
                )
                # Habilitar botones de juegos
                self.game_controller.update_game_buttons_state(True)
            else:
                messagebox.showerror("Error", "No se pudo conectar al Arduino")
                self.arduino_info_var.set("Error de conexión - verifica cable y puerto")
        else:
            self.stop_game()
            self.arduino.disconnect()
            self.status_var.set("❌ Desconectado")
            self.connect_btn.config(text="Conectar", bg="#27AE60")
            self.arduino_info_var.set("Desconectado del Arduino")
            # Deshabilitar botones de juegos
            self.game_controller.update_game_buttons_state(False)

    def stop_game(self):
        # Detener juego actual antes de desconectar
        if (
            self.game_controller.current_game
            and self.game_controller.current_game_is_running()
        ):
            self.game_controller.stop_current_game()
