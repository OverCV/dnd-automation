"""
Manejo de ventanas de estado detallado para juegos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.components.arduino_colors import ArduinoColors
from .game_lifecycle import GameLifecycle


class GameStatusManager:
    """Maneja las ventanas de estado detallado de los juegos"""
    
    def __init__(self, main_window_ref, game_lifecycle: GameLifecycle):
        self.main_window = main_window_ref
        self.lifecycle = game_lifecycle
        self.colors = ArduinoColors()
    
    def show_game_status(self, game_id: str):
        """Mostrar estado detallado del juego - VERSIÓN MEJORADA con análisis cognitivo"""
        current_game = self.lifecycle.get_current_game()
        
        # CORREGIDO: Para Piano Digital, mostrar análisis cognitivo con gráficas
        if game_id == "piano_digital":
            self._show_cognitive_analytics(game_id)
            return
        
        # Para otros juegos, mostrar ventana de estado tradicional
        if current_game and self.lifecycle.is_game_running():
            try:
                status = self.lifecycle.get_current_game_status()
                self._create_status_window(status)
            except Exception as e:
                messagebox.showerror("Error", f"Error obteniendo estado del juego: {e}")
        else:
            messagebox.showinfo(
                "Sin juego activo", 
                "No hay juegos en ejecución para mostrar estado"
            )
    
    def _show_cognitive_analytics(self, game_id: str):
        """Mostrar ventana de análisis cognitivo con gráficas para Piano Simon"""
        try:
            print(f"🧠 Abriendo análisis cognitivo para: {game_id}")
            
            # Importar ventanas específicas según el juego
            if game_id == "piano_digital":
                from ui.cognitive.cognitive_analytics_window import open_cognitive_analytics
                open_cognitive_analytics(self.main_window.root, game_id)
            elif game_id == "osu_rhythm":
                from ui.cognitive.osu_analytics_window import open_osu_cognitive_analytics
                open_osu_cognitive_analytics(self.main_window.root, game_id)
            else:
                # Para juegos sin análisis específico, usar ventana genérica
                from ui.cognitive.cognitive_analytics_window import open_cognitive_analytics
                open_cognitive_analytics(self.main_window.root, game_id)
                
        except ImportError as e:
            print(f"❌ Error importando ventana de análisis: {e}")
            messagebox.showerror("Error", f"No se pudo cargar el análisis cognitivo: {e}")
        except Exception as e:
            print(f"❌ Error abriendo análisis cognitivo: {e}")
            messagebox.showerror("Error", f"Error abriendo análisis: {e}")
            # Fallback: mostrar ventana de estado tradicional
            current_game = self.lifecycle.get_current_game()
            if current_game and self.lifecycle.is_game_running():
                status = self.lifecycle.get_current_game_status()
                self._create_status_window(status)

    def _create_status_window(self, status: dict):
        """Crear ventana de estado mejorada"""
        status_window = tk.Toplevel(self.main_window.root)
        status_window.title(f"📊 Estado Detallado - {status.get('name', 'Juego')}")
        status_window.geometry("600x500")
        status_window.configure(bg=self.colors.BACKGROUND_PRIMARY)

        # Título
        title_label = tk.Label(
            status_window,
            text=f"📊 Estado de {status.get('name', 'Juego')}",
            bg=self.colors.BACKGROUND_PRIMARY,
            fg=self.colors.BLUE_DARK,
            font=("Arial", 18, "bold"),
        )
        title_label.pack(pady=15)

        # Crear notebook para pestañas
        notebook = ttk.Notebook(status_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Pestaña de estado general
        general_frame = tk.Frame(notebook, bg=self.colors.BACKGROUND_SECONDARY)
        notebook.add(general_frame, text="General")

        # Pestaña de estadísticas
        stats_frame = tk.Frame(notebook, bg=self.colors.BACKGROUND_SECONDARY)
        notebook.add(stats_frame, text="Estadísticas")

        # Contenido de estado general
        self._create_general_status_tab(general_frame, status)

        # Contenido de estadísticas
        self._create_stats_tab(stats_frame, status)
    
    def _create_general_status_tab(self, parent, status):
        """Crear pestaña de estado general"""
        # Texto con información del estado
        status_text = tk.Text(
            parent,
            bg=self.colors.BACKGROUND_TERTIARY,
            fg=self.colors.TEXT_PRIMARY,
            font=("Consolas", 11),
            wrap=tk.WORD,
            height=20,
        )
        status_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Formatear información del estado específica para cada juego
        status_info = self._format_game_status(status)
        
        status_text.insert(tk.END, status_info)
        status_text.config(state=tk.DISABLED)
    
    def _format_game_status(self, status: dict) -> str:
        """Formatear información de estado según el tipo de juego"""
        game_name = status.get("name", "Juego Desconocido")
        
        # Información base común a todos los juegos
        base_info = f"""🎮 JUEGO: {game_name}
▶️ Estado: {"🟢 EJECUTÁNDOSE" if status.get("running", False) else "🔴 DETENIDO"}
"""
        
        # Información específica según el tipo de juego
        if "piano" in game_name.lower():
            return self._format_piano_status(status, base_info)
        elif "two_lane_runner" in game_name.lower():
            return self._format_two_lane_status(status, base_info)
        elif "ping_pong" in game_name.lower():
            return self._format_ping_pong_status(status, base_info)
        else:
            return self._format_generic_status(status, base_info)
    
    def _format_piano_status(self, status: dict, base_info: str) -> str:
        """Formatear estado específico del piano"""
        test_mode_info = ""
        if status.get("test_mode", False):
            test_mode_info = f"""
🧪 MODO PRUEBA ACTIVO:
📝 Estado: Modo libre de prueba de botones
🎹 Notas disponibles: {", ".join(status.get("available_notes", []))}
🔧 Hardware: {"✅ Inicializado" if status.get("hardware_initialized", False) else "❌ No inicializado"}
"""
        else:
            test_mode_info = f"""
🎮 JUEGO SIMON SAYS:
📊 Nivel actual: {status.get("level", 0)}/{status.get("max_level", 20)}
🎯 Progreso: {status.get("input_progress", 0)}/{status.get("sequence_length", 0)}
🏆 Mejor nivel: {status.get("best_level", 0)}
🎲 Total partidas: {status.get("total_games", 0)}
⭐ Juegos perfectos: {status.get("perfect_games", 0)}
"""

        return f"""{base_info}🎵 Estado del juego: {status.get("game_state", "N/A")}

{test_mode_info}

🔧 HARDWARE:
🔌 Conectado: {"✅ SÍ" if status.get("hardware_initialized", False) else "❌ NO"}
🎹 Pines configurados: 2, 3, 4, 5, 6, 7, 8, 9
🎼 Notas disponibles: Do, Re, Mi, Fa, Sol, La, Si, Do8

🎮 CONTROLES:
⌨️ Teclado: Teclas 1-8 para prueba
🎹 Hardware: Botones en pines 2-9
🔄 ESC = Salir | R = Reiniciar
"""
    
    def _format_two_lane_status(self, status: dict, base_info: str) -> str:
        """Formatear estado específico del Two Lane Runner"""
        return f"""{base_info}⏸️ Pausado: {"🟡 SÍ" if status.get("paused", False) else "🟢 NO"}
💀 Game Over: {"🔴 SÍ" if status.get("game_over", False) else "🟢 NO"}

🏆 PUNTUACIÓN ACTUAL: {status.get("score", 0)}
🎯 Mejor Puntuación: {status.get("best_score", 0)}
🎲 Total de Partidas: {status.get("total_games", 0)}

🏃 POSICIÓN DEL JUGADOR:
📍 Coordenadas: {status.get("player_position", "N/A")}
🛤️ Carril Actual: {status.get("player_lane", "N/A")}

🚧 OBSTÁCULOS:
📊 Cantidad Activa: {status.get("obstacles_count", 0)}

⚡ VELOCIDAD:
🏃 Velocidad Actual: {status.get("speed_percentage", 0)}%

🔧 HARDWARE:
🔌 Inicializado: {"✅ SÍ" if status.get("hardware_initialized", False) else "❌ NO"}
🖥️ LCD: {"✅ Conectado" if status.get("hardware_initialized", False) else "❌ No disponible"}
🕹️ Botones: {"✅ Funcionando" if status.get("hardware_initialized", False) else "❌ No disponibles"}
"""
    
    def _format_ping_pong_status(self, status: dict, base_info: str) -> str:
        """Formatear estado específico del Ping Pong"""
        return f"""{base_info}⏸️ Pausado: {"🟡 SÍ" if status.get("paused", False) else "🟢 NO"}
💀 Game Over: {"🔴 SÍ" if status.get("game_over", False) else "🟢 NO"}

🏆 PUNTUACIÓN: {status.get("score", 0)}

🏓 PELOTA:
📍 Posición: {status.get("ball_position", "N/A")}

🏓 PALAS:
← Izquierda: {"🟢 ACTIVA" if status.get("left_paddle", False) else "🔴 INACTIVA"}
→ Derecha: {"🟢 ACTIVA" if status.get("right_paddle", False) else "🔴 INACTIVA"}

🔧 HARDWARE:
🔌 Inicializado: {"✅ SÍ" if status.get("hardware_initialized", False) else "❌ NO"}
"""
    
    def _format_generic_status(self, status: dict, base_info: str) -> str:
        """Formatear estado genérico para juegos desconocidos"""
        return f"""{base_info}
📊 INFORMACIÓN GENERAL:
🆔 Tipo: {type(status.get("game", "")).__name__ if status.get("game") else "Desconocido"}
🔧 Hardware: {"✅ Inicializado" if status.get("hardware_initialized", False) else "❌ No inicializado"}

📈 DATOS DISPONIBLES:
{self._format_available_data(status)}
"""
    
    def _format_available_data(self, status: dict) -> str:
        """Formatear datos disponibles en el estado"""
        available_data = []
        for key, value in status.items():
            if key not in ["name", "running", "hardware_initialized"]:
                available_data.append(f"• {key}: {value}")
        
        return "\n".join(available_data) if available_data else "• No hay datos adicionales disponibles"
    
    def _create_stats_tab(self, parent, status):
        """Crear pestaña de estadísticas"""
        stats_label = tk.Label(
            parent,
            text="📈 Estadísticas avanzadas y gráficos\n(Próximamente)",
            bg=self.colors.BACKGROUND_SECONDARY,
            fg=self.colors.TEXT_SECONDARY,
            font=("Arial", 14),
        )
        stats_label.pack(expand=True) 