import time
import serial
import serial.tools.list_ports
from tkinter import messagebox


class InoController:
    """Clase para manejar toda la comunicación con Arduino"""

    def __init__(self):
        self.connection = None
        self.connected = False
        self.current_port = None
        self.callbacks = {"on_connect": [], "on_disconnect": [], "on_message": []}

    def get_available_ports(self):
        """Obtener lista de puertos seriales disponibles"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["No hay puertos disponibles"]

    def add_callback(self, event, callback):
        """Agregar callback para eventos"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def __trigger_callbacks(self, event, *args):
        """Ejecutar callbacks para un evento"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args)
            except Exception as e:
                print(f"Error en callback {event}: {e}")

    def connect(self, port, baudrate=9600):
        """Conectar al Arduino"""
        if self.connected:
            return True

        try:
            self.connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Tiempo para estabilizar conexión
            self.connected = True
            self.current_port = port
            self.__trigger_callbacks("on_connect", port)
            return True
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar: {str(e)}")
            self.__trigger_callbacks("on_message", f"Error de conexión: {str(e)}")
            return False

    def disconnect(self):
        """Desconectar del Arduino"""
        if self.connection:
            self.connection.close()
        self.connected = False
        self.current_port = None
        self.__trigger_callbacks("on_disconnect")

    def send_command(self, command):
        """Enviar comando al Arduino"""
        if not self.connected:
            messagebox.showwarning(
                "No Conectado", "Por favor conecta al Arduino primero."
            )
            return False

        try:
            self.connection.write(command.encode())
            self.__trigger_callbacks("on_message", f"Enviado: {command.strip()}")

            # Leer respuesta si está disponible
            time.sleep(0.5)
            if self.connection.in_waiting:
                response = self.connection.readline().decode("utf-8").strip()
                self.__trigger_callbacks("on_message", f"Recibido: {response}")
                return response
            return True
        except Exception as e:
            messagebox.showerror(
                "Error de Comunicación", f"Error al enviar comando: {str(e)}"
            )
            self.__trigger_callbacks("on_message", f"Error: {str(e)}")
            return False

    def is_connected(self):
        """Verificar si está conectado"""
        return self.connected

    def get_current_port(self):
        """Obtener puerto actual"""
        return self.current_port
