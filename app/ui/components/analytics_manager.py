"""
Manager de analíticas para la interfaz principal
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.analytics.game_analytics import GameAnalytics
from .arduino_colors import ArduinoColors


class AnalyticsManager:
    """Manager para funcionalidades de análisis y estadísticas"""
    
    def __init__(self, main_window_ref):
        self.main_window = main_window_ref
        self.colors = ArduinoColors()
    
    def show_analytics(self):
        """Mostrar análisis de logs con matplotlib"""
        try:
            analytics = GameAnalytics()
            available_games = analytics.list_available_games()
            
            if not available_games:
                messagebox.showwarning("Sin datos", "No se encontraron logs de juegos para analizar")
                return
            
            # Crear ventana de selección de juego
            analytics_window = tk.Toplevel(self.main_window.root)
            analytics_window.title("📈 Análisis de Logs")
            analytics_window.geometry("600x400")
            analytics_window.configure(bg=self.colors.BACKGROUND_PRIMARY)
            
            tk.Label(
                analytics_window, text="📈 Análisis de Rendimiento",
                bg=self.colors.BACKGROUND_PRIMARY, fg=self.colors.BLUE_DARK, font=("Arial", 16, "bold")
            ).pack(pady=20)
            
            # Información de juegos disponibles
            info_text = f"Juegos con logs disponibles: {len(available_games)}\n"
            for game in available_games:
                summary = analytics.get_game_summary(game)
                info_text += f"\n• {game}: {summary.get('total_events', 0)} eventos, "
                info_text += f"{summary.get('deaths', 0)} partidas"
            
            info_label = tk.Label(
                analytics_window, text=info_text,
                bg=self.colors.BACKGROUND_PRIMARY, fg=self.colors.TEXT_SECONDARY, font=("Arial", 11),
                justify=tk.LEFT
            )
            info_label.pack(pady=10, padx=20)
            
            # Botones de acción
            buttons_frame = tk.Frame(analytics_window, bg=self.colors.BACKGROUND_PRIMARY)
            buttons_frame.pack(pady=20)
            
            tk.Button(
                buttons_frame, text="📈 Dashboard General",
                command=lambda: self._show_dashboard_all(analytics),
                bg=self.colors.INFO, fg=self.colors.TEXT_PRIMARY, relief=tk.FLAT,
                width=20, height=2, font=("Arial", 10, "bold")
            ).pack(pady=5)
            
            # Selector de juego para análisis detallado
            game_frame = tk.Frame(analytics_window, bg=self.colors.BACKGROUND_PRIMARY)
            game_frame.pack(pady=10)
            
            tk.Label(game_frame, text="Análisis detallado de:", 
                    bg=self.colors.BACKGROUND_PRIMARY, fg=self.colors.TEXT_SECONDARY, font=("Arial", 12)).pack()
            
            game_var = tk.StringVar(value=available_games[0] if available_games else "")
            game_combo = ttk.Combobox(game_frame, textvariable=game_var, 
                                    values=available_games, width=30)
            game_combo.pack(pady=5)
            
            detail_buttons_frame = tk.Frame(analytics_window, bg=self.colors.BACKGROUND_PRIMARY)
            detail_buttons_frame.pack(pady=10)
            
            tk.Button(
                detail_buttons_frame, text="📊 Análisis Detallado",
                command=lambda: self._show_detailed_analysis(analytics, game_var.get()),
                bg=self.colors.ERROR, fg=self.colors.TEXT_PRIMARY, relief=tk.FLAT,
                width=20, height=2, font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                detail_buttons_frame, text="📋 Reporte de Texto",
                command=lambda: self._show_text_report(analytics, game_var.get()),
                bg=self.colors.WARNING, fg=self.colors.TEXT_PRIMARY, relief=tk.FLAT,
                width=20, height=2, font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                detail_buttons_frame, text="💾 Exportar CSV",
                command=lambda: self._export_to_csv(analytics, game_var.get()),
                bg=self.colors.SUCCESS, fg=self.colors.TEXT_PRIMARY, relief=tk.FLAT,
                width=20, height=2, font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando análisis: {e}")
    
    def show_global_stats(self):
        """Mostrar estadísticas globales"""
        stats_window = tk.Toplevel(self.main_window.root)
        stats_window.title("📊 Estadísticas Globales")
        stats_window.geometry("500x400")
        stats_window.configure(bg=self.colors.BACKGROUND_PRIMARY)

        tk.Label(
            stats_window, text="📊 Estadísticas de la Plataforma",
            bg=self.colors.BACKGROUND_PRIMARY, fg=self.colors.BLUE_DARK, font=("Arial", 16, "bold")
        ).pack(pady=20)

        stats_info = f"""🎮 PLATAFORMA DE JUEGOS ARDUINO
📦 Juegos Disponibles: {len(self.main_window.game_controller.available_games)}
🔌 Estado Arduino: {'Conectado' if self.main_window.arduino_manager.connected else 'Desconectado'}
⏰ Sesión Iniciada: {self.main_window.session_start_time}
🎲 Juego Actual: {self.main_window.game_controller.current_game.name if self.main_window.game_controller.current_game and self.main_window.game_controller.current_game.running else 'Ninguno'}

📈 ESTADÍSTICAS DE USO:
- Tiempo de sesión: Variable según uso
- Conexiones establecidas: 1
- Juegos ejecutados: Variable según uso

🎯 JUEGOS REGISTRADOS:
"""

        for game_id, game_class in self.main_window.game_controller.available_games.items():
            temp_game = game_class(self.main_window.arduino_manager)
            stats_info += f"   • {temp_game.name}\n"

        stats_text = tk.Text(
            stats_window, bg=self.colors.BACKGROUND_SECONDARY, fg=self.colors.TEXT_PRIMARY,
            font=("Consolas", 10), wrap=tk.WORD
        )
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        stats_text.insert(tk.END, stats_info)
        stats_text.config(state=tk.DISABLED)
    
    def _show_dashboard_all(self, analytics):
        """Mostrar dashboard de todos los juegos"""
        try:
            analytics.show_performance_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando dashboard: {e}")
    
    def _show_detailed_analysis(self, analytics, game_name):
        """Mostrar análisis detallado de un juego"""
        if not game_name:
            messagebox.showwarning("Advertencia", "Selecciona un juego")
            return
        
        try:
            analytics.show_detailed_game_analysis(game_name)
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando análisis detallado: {e}")
    
    def _show_text_report(self, analytics, game_name):
        """Mostrar reporte textual en ventana"""
        if not game_name:
            messagebox.showwarning("Advertencia", "Selecciona un juego")
            return
        
        try:
            report = analytics.generate_performance_report(game_name)
            
            # Crear ventana para el reporte
            report_window = tk.Toplevel(self.main_window.root)
            report_window.title(f"📋 Reporte: {game_name}")
            report_window.geometry("800x600")
            report_window.configure(bg=self.colors.BACKGROUND_PRIMARY)
            
            # Área de texto para el reporte
            text_area = tk.Text(
                report_window, bg=self.colors.BACKGROUND_SECONDARY, fg=self.colors.TEXT_PRIMARY,
                font=("Consolas", 10), wrap=tk.WORD
            )
            text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            text_area.insert(tk.END, report)
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def _export_to_csv(self, analytics, game_name):
        """Exportar datos a CSV"""
        if not game_name:
            messagebox.showwarning("Advertencia", "Selecciona un juego")
            return
        
        try:
            analytics.export_data_to_csv(game_name)
            messagebox.showinfo("Exportación", f"Datos de {game_name} exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando a CSV: {e}") 