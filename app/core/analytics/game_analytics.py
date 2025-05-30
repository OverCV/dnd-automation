"""
Game Analytics refactorizado - Solo coordinación entre componentes modularizados

ANTES: 628 líneas mezclando parseo, visualización, reportes y coordinación  
DESPUÉS: ~100 líneas de pura coordinación entre componentes especializados
"""

from typing import Dict, List, Optional
from .components import LogParser, DataVisualizer, ReportGenerator


class GameAnalytics:
    """
    Coordinador ligero para análisis de juegos.
    
    Ya no maneja lógica específica - solo coordina:
    - LogParser: Carga y parseo de logs
    - DataVisualizer: Visualizaciones matplotlib  
    - ReportGenerator: Reportes y exportación
    """

    def __init__(self, log_dir: str = "app/data"):
        # Inicializar componentes especializados
        self.log_parser = LogParser(log_dir)
        self.data_visualizer = DataVisualizer()
        self.report_generator = ReportGenerator()
        
        # Cargar datos usando el parser
        self.games_data = self.log_parser.load_all_logs()

    # ===== MÉTODOS DE ACCESO A DATOS =====
    
    def list_available_games(self) -> List[str]:
        """Listar juegos disponibles para análisis"""
        return self.log_parser.list_available_games()

    def get_game_summary(self, game_name: str) -> Dict:
        """Obtener resumen rápido de un juego"""
        return self.log_parser.get_game_summary(game_name)
    
    def get_game_data(self, game_name: str) -> List[Dict]:
        """Obtener datos de un juego específico"""
        return self.log_parser.get_game_data(game_name)

    # ===== MÉTODOS DE VISUALIZACIÓN =====
    
    def show_performance_dashboard(self, game_name: Optional[str] = None):
        """Mostrar dashboard completo de rendimiento"""
        self.data_visualizer.show_performance_dashboard(self.games_data, game_name)

    def show_detailed_game_analysis(self, game_name: str):
        """Análisis detallado de un juego específico"""
        events = self.get_game_data(game_name)
        self.data_visualizer.show_detailed_game_analysis(game_name, events)
    
    def create_custom_visualization(self, game_name: str, plot_type: str, **kwargs):
        """Crear visualización personalizada"""
        events = self.get_game_data(game_name)
        self.data_visualizer.create_custom_plot(events, plot_type, **kwargs)

    # ===== MÉTODOS DE REPORTES =====
    
    def generate_performance_report(self, game_name: str) -> str:
        """Generar reporte textual de rendimiento"""
        events = self.get_game_data(game_name)
        return self.report_generator.generate_performance_report(game_name, events)
    
    def generate_summary_report(self) -> str:
        """Generar reporte resumen de todos los juegos"""
        return self.report_generator.generate_summary_report(self.games_data)
    
    def generate_custom_report(self, game_name: str, report_type: str = "basic", **kwargs) -> str:
        """Generar reporte personalizado"""
        events = self.get_game_data(game_name)
        return self.report_generator.generate_custom_report(game_name, events, report_type, **kwargs)

    # ===== MÉTODOS DE EXPORTACIÓN =====
    
    def export_data_to_csv(self, game_name: str, output_path: str = None) -> str:
        """Exportar datos a CSV"""
        events = self.get_game_data(game_name)
        return self.report_generator.export_data_to_csv(game_name, events, output_path)
    
    def export_all_games_to_excel(self, output_path: str = None) -> str:
        """Exportar todos los juegos a Excel"""
        return self.report_generator.export_multiple_games_to_excel(self.games_data, output_path)

    # ===== MÉTODOS DE FILTRADO Y BÚSQUEDA =====
    
    def get_events_by_type(self, game_name: str, event_type: str) -> List[Dict]:
        """Filtrar eventos por tipo específico"""
        return self.log_parser.get_events_by_type(game_name, event_type)
    
    def get_events_by_level(self, game_name: str, level: str) -> List[Dict]:
        """Filtrar eventos por nivel (INFO, WARNING, ERROR)"""
        return self.log_parser.get_events_by_level(game_name, level)

    # ===== MÉTODOS DE ANÁLISIS RÁPIDO =====
    
    def analyze_game_errors(self, game_name: str) -> str:
        """Análisis rápido de errores de un juego"""
        events = self.get_game_data(game_name)
        return self.report_generator.generate_custom_report(game_name, events, "errors")
    
    def get_quick_stats(self, game_name: str) -> Dict:
        """Obtener estadísticas rápidas de un juego"""
        events = self.get_game_data(game_name)
        
        if not events:
            return {"error": f"No hay datos para {game_name}"}
        
        return {
            "total_events": len(events),
            "errors": len([e for e in events if e["level"] == "ERROR"]),
            "warnings": len([e for e in events if e["level"] == "WARNING"]),
            "deaths": len([e for e in events if e.get("is_death", False)]),
            "successes": len([e for e in events if e.get("is_success", False)]),
            "max_score": max([e.get("score", 0) for e in events]),
            "time_span": (events[-1]["timestamp"] - events[0]["timestamp"]).total_seconds()
        }
    
    def reload_logs(self):
        """Recargar logs desde el directorio"""
        print("🔄 Recargando logs...")
        self.games_data = self.log_parser.load_all_logs()
        print(f"✅ {len(self.games_data)} juegos cargados")


def main():
    """Función principal para ejecutar análisis independiente"""
    print("🎮 Game Analytics Modularizado - Analizador de Logs")
    print("=" * 60)

    analytics = GameAnalytics()
    available_games = analytics.list_available_games()

    if not available_games:
        print("❌ No se encontraron logs de juegos")
        return

    print(f"📊 Juegos disponibles: {', '.join(available_games)}")

    # Mostrar dashboard general
    print("\n📈 Mostrando dashboard de rendimiento...")
    analytics.show_performance_dashboard()

    # Mostrar análisis detallado del primer juego
    if available_games:
        first_game = available_games[0]
        print(f"\n📊 Análisis detallado de {first_game}...")
        analytics.show_detailed_game_analysis(first_game)

        # Generar reporte
        print(f"\n📋 Reporte de {first_game}:")
        print(analytics.generate_performance_report(first_game))


if __name__ == "__main__":
    main() 