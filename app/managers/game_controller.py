"""
Game Controller refactorizado - Solo coordinación entre componentes modularizados

ANTES: 637 líneas mezclando UI, lógica, estado, inicio/parada
DESPUÉS: ~200 líneas de pura coordinación entre componentes especializados
"""

import time
from tkinter import messagebox
from typing import Optional
from core.base_game import BaseGame
from core.arduino_manager import ArduinoManager
from ui.components.arduino_colors import ArduinoColors

# Importar componentes modularizados
from .components import (
    GameRegistry,
    GameLifecycle, 
    GameUIManager,
    GameStatusManager
)


class GameController:
    """
    Controlador ligero que coordina entre componentes especializados.
    
    Ya no maneja lógica específica - solo coordina:
    - GameRegistry: Registro de juegos y metadatos
    - GameLifecycle: Ciclo de vida (inicio/parada)
    - GameUIManager: Interfaz de usuario
    - GameStatusManager: Ventanas de estado
    """
    
    def __init__(self, arduino_manager: ArduinoManager, main_window):
        from ui.main_window import MainWindow

        self.main_window: MainWindow = main_window
        self.root = self.main_window.root
        self.arduino = arduino_manager
        self.colors = ArduinoColors()

        # Inicializar componentes especializados
        self.registry = GameRegistry()
        self.lifecycle = GameLifecycle(arduino_manager, self.registry)
        self.ui_manager = GameUIManager(self.registry)
        self.status_manager = GameStatusManager(main_window, self.lifecycle)

    # ===== PROPIEDADES DE CONVENIENCIA =====
    
    @property
    def current_game(self) -> Optional[BaseGame]:
        """Acceso directo al juego actual"""
        return self.lifecycle.get_current_game()
    
    @property
    def available_games(self):
        """Acceso directo a juegos disponibles (compatibilidad)"""
        return self.registry.get_available_games()
    
    @property 
    def game_widgets(self):
        """Acceso directo a widgets de juegos (compatibilidad)"""
        return self.ui_manager.get_game_widgets()

    # ===== MÉTODOS DE ESTADO =====
    
    def current_game_is_running(self) -> bool:
        """Verificar si hay un juego ejecutándose"""
        return self.lifecycle.is_game_running()

    # ===== MÉTODOS DE CONTROL DE JUEGOS =====
    
    def start_game(self, game_id: str):
        """Iniciar un juego"""
        success, message = self.lifecycle.start_game(game_id)
        
        if success:
            # Actualizar UI para mostrar juego activo
            self.ui_manager.highlight_active_game(game_id)
            self.update_session_stats()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Juego Iniciado", message)
        else:
            # Mostrar error
            if "Arduino" in message:
                messagebox.showwarning("Sin conexión", message)
            else:
                messagebox.showerror("Error", message)

    def start_test_mode(self, game_id: str):
        """Iniciar modo de prueba para un juego específico"""
        success, message = self.lifecycle.start_test_mode(game_id)
        
        if success:
            # Actualizar UI para modo prueba
            self.ui_manager.highlight_test_mode(game_id)
            self.update_session_stats()
            
            # Mostrar información del modo prueba
            messagebox.showinfo("Modo Prueba Iniciado", message)
        else:
            # Mostrar error apropiado
            if "Arduino" in message:
                messagebox.showwarning("Sin conexión", message)
            elif "no está disponible" in message:
                messagebox.showinfo("No disponible", message)
            else:
                messagebox.showerror("Error Crítico", message)

    def stop_game(self):
        """Detener juego actual desde UI con manejo inteligente"""
        if not self.current_game or not self.current_game_is_running():
            messagebox.showinfo("Sin juego", "No hay juegos ejecutándose")
            return

        try:
            game_name = self.current_game.name
            print(f"🛑 Intentando detener {game_name}...")

            # Intentar detención segura
            if self.lifecycle.stop_current_game():
                # Detención exitosa
                self.restore_game_ui()
                messagebox.showinfo(
                    "Juego Detenido", 
                    f"✅ {game_name} detenido correctamente"
                )
            else:
                # Si falla, usar parada de emergencia automáticamente
                print(f"⚠️ Detención normal falló para {game_name}, usando parada forzada...")
                self.force_stop_all()
                self.restore_game_ui()
                messagebox.showwarning(
                    "Detención Forzada",
                    f"⚠️ {game_name} fue detenido usando parada de emergencia.\n"
                    "Esto puede ocurrir si el juego no responde normalmente.",
                )

        except Exception as e:
            print(f"❌ Error crítico deteniendo juego: {e}")
            # Como último recurso, parada de emergencia
            try:
                self.force_stop_all()
                self.restore_game_ui()
                messagebox.showerror(
                    "Error Crítico",
                    f"Error deteniendo juego: {e}\nSe aplicó parada de emergencia.",
                )
            except Exception as emergency_error:
                messagebox.showerror(
                    "Error Fatal",
                    f"Error crítico: {emergency_error}\n"
                    "Reinicia la aplicación si persisten los problemas.",
                )

    def force_stop_all(self):
        """Parada de emergencia para casos críticos"""
        print("🚨 FORZANDO PARADA DE TODOS LOS JUEGOS")
        self.lifecycle.force_stop_all()
        self.restore_game_ui()

    def stop_current_game(self) -> bool:
        """Detener juego actual de forma segura (método directo)"""
        return self.lifecycle.stop_current_game()

    # ===== MÉTODOS DE UI =====
    
    def create_game_entries(self, parent_frame):
        """Crear entradas de juegos usando el UI manager"""
        self.ui_manager.create_game_entries(
            parent_frame,
            start_game_callback=self.start_game,
            start_test_callback=self.start_test_mode,
            stop_game_callback=self.stop_game,
            show_status_callback=self.show_game_status
        )

    def restore_game_ui(self):
        """Restaurar UI de juegos al estado normal"""
        self.ui_manager.restore_game_ui()

    def highlight_active_game(self, active_game_id: str):
        """Resaltar juego activo (método de compatibilidad)"""
        self.ui_manager.highlight_active_game(active_game_id)

    def highlight_test_mode(self, active_game_id: str):
        """Resaltar modo prueba (método de compatibilidad)"""
        self.ui_manager.highlight_test_mode(active_game_id)

    # ===== MÉTODOS DE ESTADO Y ESTADÍSTICAS =====
    
    def show_game_status(self, game_id: str):
        """Mostrar estado detallado del juego"""
        self.status_manager.show_game_status(game_id)

    def update_session_stats(self):
        """Actualizar estadísticas de sesión"""
        if self.current_game and self.current_game_is_running():
            if hasattr(self.current_game, "test_mode") and self.current_game.test_mode:
                active_game = f"{self.current_game.name} (Modo Prueba)"
            else:
                active_game = self.current_game.name
        else:
            active_game = "Ninguno"

        self.main_window.session_stats_var.set(
            f"Juegos disponibles: {self.registry.get_game_count()} | "
            f"Juego activo: {active_game} | "
            f"Sesión: {time.strftime('%H:%M:%S')}"
        )

    def update_status(self):
        """Actualizar estado periódicamente"""
        try:
            # Actualizar estadísticas de sesión
            self.update_session_stats()
            # Actualizar información del juego actual si está ejecutándose
            if self.current_game and self.current_game_is_running():
                # Aquí podrías agregar lógica adicional de monitoreo
                pass
        except Exception as e:
            print(f"❌ Error al actualizar estado: {e}")

        # Programar siguiente actualización
        self.root.after(2000, self.update_status)

    # ===== MÉTODOS DE COMPATIBILIDAD =====
    
    def get_game_tech_info(self, game_id: str) -> str:
        """Obtener información técnica del juego (compatibilidad)"""
        return self.registry.get_tech_info(game_id)

    def update_game_buttons_state(self, enabled: bool):
        """Actualizar estado de botones de juegos (método heredado)"""
        for game_id, widgets in self.game_widgets.items():
            state = "normal" if enabled else "disabled"
            widgets["start_btn"].config(state=state)
            if "test_btn" in widgets:
                widgets["test_btn"].config(state=state) 