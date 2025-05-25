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
    import pyfirmata
    from pyfirmata import util
    import serial.tools.list_ports
    import pygame
except ImportError:
    print("❌ Instalar dependencias:")
    print("   pip install pyfirmata pygame pyserial")
    sys.exit(1)

# Importar las clases base
from main.core.arduino_manager import ArduinoManager
from games.ping_pong.ping_pong import PingPongGame


class GameManager:
    """Gestor principal de juegos"""

    def __init__(self):
        self.arduino = ArduinoManager()
        self.current_game = None
        self.available_games = {
            'ping_pong': PingPongGame,
            # Aquí puedes agregar más juegos que implementen BaseGame
        }

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Arduino Game Manager - 100% Python")
        self.root.geometry("900x700")
        self.root.configure(bg="#2C3E50")

        self.create_ui()

    def create_ui(self):
        """Crear interfaz de usuario"""
        # Frame de conexión
        conn_frame = tk.LabelFrame(
            self.root, text="Conexión Arduino",
            bg="#34495E", fg="white", font=("Arial", 12, "bold")
        )
        conn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Puerto
        tk.Label(conn_frame, text="Puerto:", bg="#34495E", fg="white").pack(side=tk.LEFT, padx=5)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        tk.Button(
            conn_frame, text="🔄 Refrescar",
            command=self.refresh_ports,
            bg="#3498DB", fg="white", relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            conn_frame, text="🔍 Auto-detectar",
            command=self.auto_detect_port,
            bg="#9B59B6", fg="white", relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        self.connect_btn = tk.Button(
            conn_frame, text="Conectar",
            command=self.toggle_connection,
            bg="#27AE60", fg="white", relief=tk.FLAT, width=10
        )
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        # Estado
        self.status_var = tk.StringVar(value="❌ Desconectado")
        tk.Label(
            conn_frame, textvariable=self.status_var,
            bg="#34495E", fg="#E74C3C", font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=10)

        # Frame de juegos
        games_frame = tk.LabelFrame(
            self.root, text="Juegos Disponibles",
            bg="#34495E", fg="white", font=("Arial", 12, "bold")
        )
        games_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Lista de juegos
        for game_id, game_class in self.available_games.items():
            game_frame = tk.Frame(games_frame, bg="#2C3E50", relief=tk.RAISED, bd=2)
            game_frame.pack(fill=tk.X, padx=5, pady=5)

            # Crear instancia temporal para obtener info
            temp_game = game_class(arduino_manager=self.arduino)

            # Información del juego
            info_frame = tk.Frame(game_frame, bg="#2C3E50")
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(
                info_frame, text=temp_game.name,
                bg="#2C3E50", fg="white", font=("Arial", 16, "bold")
            ).pack(anchor=tk.W)

            tk.Label(
                info_frame, text=temp_game.description,
                bg="#2C3E50", fg="#BDC3C7", font=("Arial", 11), wraplength=400
            ).pack(anchor=tk.W)

            # Botones
            btn_frame = tk.Frame(game_frame, bg="#2C3E50")
            btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)

            start_btn = tk.Button(
                btn_frame, text="▶️ Iniciar",
                command=lambda gid=game_id: self.start_game(gid),
                bg="#27AE60", fg="white", relief=tk.FLAT, width=12, height=2
            )
            start_btn.pack(pady=3)

            stop_btn = tk.Button(
                btn_frame, text="⏹️ Detener",
                command=self.stop_game,
                bg="#E74C3C", fg="white", relief=tk.FLAT, width=12, height=2
            )
            stop_btn.pack(pady=3)

            status_btn = tk.Button(
                btn_frame, text="📊 Estado",
                command=lambda gid=game_id: self.show_game_status(gid),
                bg="#F39C12", fg="white", relief=tk.FLAT, width=12
            )
            status_btn.pack(pady=3)

        # Inicializar
        self.refresh_ports()
        self.update_status()

    def refresh_ports(self):
        """Refrescar lista de puertos"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo['values'] = ports
            if ports:
                self.port_var.set(ports[0])
        except Exception as e:
            pass

    def auto_detect_port(self):
        """Auto-detectar puerto del Arduino"""
        arduino_port = self.arduino.find_arduino_port()
        if arduino_port:
            self.port_var.set(arduino_port)
        else:
            messagebox.showwarning("Auto-detección", "No se encontró un Arduino conectado")

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
            else:
                messagebox.showerror("Error", "No se pudo conectar al Arduino")
        else:
            # Detener juego actual antes de desconectar
            if self.current_game and self.current_game.running:
                self.stop_game()

            self.arduino.disconnect()
            self.status_var.set("❌ Desconectado")
            self.connect_btn.config(text="Conectar", bg="#27AE60")

    def start_game(self, game_id):
        """Iniciar un juego"""
        if not self.arduino.connected:
            messagebox.showwarning("Sin conexión", "Conecta el Arduino primero")
            return

        # Detener juego actual
        if self.current_game and self.current_game.running:
            self.current_game.stop_game()
            time.sleep(1)  # Dar tiempo para que se detenga completamente

        # Crear e inicializar nuevo juego
        try:
            game_class = self.available_games[game_id]
            self.current_game = game_class(self.arduino)

            if not self.current_game.start_game():
                messagebox.showerror("Error", f"No se pudo iniciar {self.current_game.name}")

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Error iniciando juego: {e}")

    def stop_game(self):
        """Detener juego actual"""
        if self.current_game and self.current_game.running:
            try:
                self.current_game.stop_game()
            except Exception as e:
                pass

    def show_game_status(self, game_id):
        """Mostrar estado detallado del juego"""
        if self.current_game and self.current_game.running:
            status = self.current_game.get_game_status()

            # Crear ventana de estado
            status_window = tk.Toplevel(self.root)
            status_window.title(f"Estado - {status['name']}")
            status_window.geometry("400x300")
            status_window.configure(bg="#2C3E50")

            # Contenido
            title_label = tk.Label(
                status_window, text=f"Estado de {status['name']}",
                bg="#2C3E50", fg="white", font=("Arial", 16, "bold")
            )
            title_label.pack(pady=10)

            # Crear texto con el estado
            status_text = tk.Text(
                status_window, bg="black", fg="#00FF00",
                font=("Consolas", 10), wrap=tk.WORD, height=15
            )
            status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Formatear información del estado
            status_info = f"""🎮 Juego: {status['name']}
                            ▶️ En ejecución: {'Sí' if status['running'] else 'No'}
                            🏆 Puntuación: {status.get('score', 'N/A')}
                            ⏸️ Pausado: {'Sí' if status.get('paused', False) else 'No'}
                            💀 Game Over: {'Sí' if status.get('game_over', False) else 'No'}

                            📍 Posición de pelota: {status.get('ball_position', 'N/A')}
                            🏓 Pala izquierda: {'Activa' if status.get('left_paddle', False) else 'Inactiva'}
                            🏓 Pala derecha: {'Activa' if status.get('right_paddle', False) else 'Inactiva'}

                            🔧 Hardware inicializado: {'Sí' if status.get('hardware_initialized', False) else 'No'}
                            """

            status_text.insert(tk.END, status_info)
            status_text.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Sin juego", "No hay juegos en ejecución para mostrar estado")

    def update_status(self):
        """Actualizar estado periódicamente"""
        try:
            if self.current_game and self.current_game.running:
                # Actualizar información del juego si es necesario
                pass
        except Exception as e:
            pass

        # Programar siguiente actualización
        self.root.after(2000, self.update_status)  # Cada 2 segundos

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
            self.root.destroy()
        finally:
            self.root.destroy()


def main():
    """Función principal"""
    print("🎮 Arduino Games Manager - 100% Python con Firmata")
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
