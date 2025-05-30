import time
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
from ui.connection_frame import ConnectionFrame
from core.arduino_manager import ArduinoManager
from managers.game_controller import GameController
from ui.components import (
    TitleSection, 
    StatsSection, 
    GamesSection, 
    ControlSection, 
    AnalyticsManager,
    ArduinoColors
)


class MainWindow:
    def __init__(self, arduino_manager: ArduinoManager):
        # Configuración de colores
        self.colors = ArduinoColors()
        
        # Referencias principales
        self.arduino_manager = arduino_manager
        self.session_start_time = time.strftime("%H:%M:%S")
        
        # Configuración de ventana
        self.root = tk.Tk()
        self.root.title("Arduino Game Manager - Multi-Game Platform")
        self.root.geometry("1200x900")
        self.root.configure(bg=self.colors.BLACK)
        
        # Controlador de juegos
        self.game_controller = GameController(arduino_manager, self)
        
        # Inicializar componentes UI
        self._initialize_components()
        
        # Inicialización final
        self.connection_frame.refresh_ports()
        self.game_controller.update_status()

    def _initialize_components(self):
        """Inicializar todos los componentes de la UI"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors.BLACK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Componentes modularizados
        self.title_section = TitleSection(main_frame)
        self.connection_frame = ConnectionFrame(main_frame, self.arduino_manager, self.game_controller)
        self.stats_section = StatsSection(main_frame)
        
        # Analytics manager
        self.analytics_manager = AnalyticsManager(self)
        
        # Sección de juegos
        self.games_section = GamesSection(main_frame, self.game_controller)
        self.games_section.initialize_games()
        
        # Sección de control
        self.control_section = ControlSection(main_frame, self.analytics_manager)
        
        # Configurar referencia a stats para el game controller
        self.session_stats_var = self.stats_section.get_stats_var()

    def restore_game_ui(self):
        """Restaurar UI de juegos al estado normal"""
        self.game_controller.restore_game_ui()

    def run(self):
        """Ejecutar aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Manejar cierre de aplicación de forma segura"""
        print("💻 Cerrando aplicación de forma segura...")
        
        try:
            # Detener juego actual usando el safe manager
            if (self.game_controller.current_game and 
                self.game_controller.current_game_is_running()):
                print("🛑 Deteniendo juego actual de forma segura...")
                success = self.game_controller.stop_current_game()
                if not success:
                    print("⚠️ Problemas deteniendo juego, usando parada de emergencia...")
                    self.game_controller.force_stop_all()
                
            # Desconectar Arduino
            if self.arduino_manager.connected:
                print("🔌 Desconectando Arduino...")
                self.arduino_manager.disconnect()
                
            # Parada de emergencia final para limpiar todos los recursos
            print("🧹 Limpieza final de recursos...")
            try:
                import pygame
                if pygame.get_init():
                    pygame.mixer.stop()
                    pygame.mixer.quit()
                    pygame.display.quit()
                    pygame.quit()
                print("✅ Pygame cerrado completamente")
            except Exception as e:
                print(f"⚠️ Error cerrando Pygame: {e}")
                    
        except Exception as e:
            print(f"❌ Error durante el cierre: {e}")
            # Intentar parada de emergencia como último recurso
            try:
                self.game_controller.force_stop_all()
            except:
                pass
        finally:
            # Asegurar que la ventana se cierre
            try:
                self.root.quit()
                self.root.destroy()
                print("✅ Aplicación cerrada correctamente")
            except Exception as e:
                print(f"⚠️ Error final cerrando ventana: {e}")
                import sys
                sys.exit(0)
