import os
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple, Optional
import numpy as np

class GameAnalytics:
    """Analizador de logs de juegos con visualizaciones matplotlib"""
    
    def __init__(self, log_dir: str = "main/data"):
        self.log_dir = log_dir
        self.games_data = {}
        self.load_all_logs()
    
    def load_all_logs(self):
        """Cargar todos los archivos de log disponibles"""
        if not os.path.exists(self.log_dir):
            print(f"❌ Directorio de logs no encontrado: {self.log_dir}")
            return
            
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
        
        for log_file in log_files:
            game_name = log_file.replace('.log', '').replace('_', ' ').title()
            log_path = os.path.join(self.log_dir, log_file)
            
            try:
                self.games_data[game_name] = self._parse_log_file(log_path)
                print(f"✅ Log cargado: {game_name} ({len(self.games_data[game_name])} eventos)")
            except Exception as e:
                print(f"❌ Error cargando {log_file}: {e}")
    
    def _parse_log_file(self, log_path: str) -> List[Dict]:
        """Parsear archivo de log y extraer eventos estructurados"""
        events = []
        
        with open(log_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    # Patrón: 2025-05-25 22:57:24 | INFO | [EVENT_TYPE] message
                    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+) \| \[([A-Z_]+)\] (.+)'
                    match = re.match(pattern, line.strip())
                    
                    if match:
                        timestamp_str, level, event_type, message = match.groups()
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        event = {
                            'timestamp': timestamp,
                            'level': level,
                            'event_type': event_type,
                            'message': message,
                            'line_number': line_num
                        }
                        
                        # Extraer información específica según el tipo de evento
                        self._extract_specific_data(event)
                        events.append(event)
                        
                except Exception as e:
                    print(f"⚠️ Error parseando línea {line_num}: {e}")
                    continue
        
        return events
    
    def _extract_specific_data(self, event: Dict):
        """Extraer datos específicos según el tipo de evento"""
        message = event['message']
        
        # Extraer scores
        score_match = re.search(r'Score:?\s*(\d+)', message)
        if score_match:
            event['score'] = int(score_match.group(1))
        
        # Extraer posiciones de pelota/jugador
        pos_match = re.search(r'\((\d+),\s*(\d+)\)', message)
        if pos_match:
            event['x_pos'] = int(pos_match.group(1))
            event['y_pos'] = int(pos_match.group(2))
        
        # Extraer velocidad
        speed_match = re.search(r'Speed:?\s*([\d.]+)s?', message)
        if speed_match:
            event['speed'] = float(speed_match.group(1))
        
        # Extraer duración de juego
        duration_match = re.search(r'Duration:?\s*([\d.]+)s', message)
        if duration_match:
            event['game_duration'] = float(duration_match.group(1))
        
        # Detectar muertes/game over
        if 'PLAYER DEATH' in message or 'GAME OVER' in message:
            event['is_death'] = True
            
        # Detectar hits exitosos
        if 'GOLPE EXITOSO' in message or 'esquivado' in message:
            event['is_success'] = True
    
    def show_performance_dashboard(self, game_name: Optional[str] = None):
        """Mostrar dashboard completo de rendimiento"""
        if not self.games_data:
            print("❌ No hay datos de logs disponibles")
            return
        
        # Si no se especifica juego, mostrar todos
        games_to_show = [game_name] if game_name and game_name in self.games_data else list(self.games_data.keys())
        
        # Crear subplots dinámicamente
        fig_rows = len(games_to_show)
        fig, axes = plt.subplots(fig_rows, 3, figsize=(18, 6 * fig_rows))
        if fig_rows == 1:
            axes = axes.reshape(1, -1)
        
        fig.suptitle('🎮 Game Performance Dashboard', fontsize=16, fontweight='bold')
        
        for idx, game in enumerate(games_to_show):
            events = self.games_data[game]
            
            # Gráfico 1: Eventos por tiempo
            self._plot_events_timeline(events, axes[idx, 0], f'{game} - Timeline de Eventos')
            
            # Gráfico 2: Distribución de errores
            self._plot_error_distribution(events, axes[idx, 1], f'{game} - Distribución de Errores')
            
            # Gráfico 3: Rendimiento por sesión
            self._plot_performance_trends(events, axes[idx, 2], f'{game} - Tendencias de Rendimiento')
        
        plt.tight_layout()
        plt.show()
    
    def _plot_events_timeline(self, events: List[Dict], ax, title: str):
        """Gráfico de timeline de eventos"""
        if not events:
            ax.text(0.5, 0.5, 'No hay datos', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # Separar eventos por tipo
        timestamps = [e['timestamp'] for e in events]
        event_types = [e['event_type'] for e in events]
        levels = [e['level'] for e in events]
        
        # Crear colores por nivel
        color_map = {'INFO': 'blue', 'WARNING': 'orange', 'ERROR': 'red'}
        colors = [color_map.get(level, 'gray') for level in levels]
        
        # Convertir tipos de evento a números para scatter plot
        unique_types = list(set(event_types))
        type_to_num = {t: i for i, t in enumerate(unique_types)}
        y_positions = [type_to_num[et] for et in event_types]
        
        ax.scatter(timestamps, y_positions, c=colors, alpha=0.6, s=30)
        ax.set_yticks(range(len(unique_types)))
        ax.set_yticklabels(unique_types, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Tiempo')
        
        # Formatear eje x
        if timestamps:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_error_distribution(self, events: List[Dict], ax, title: str):
        """Gráfico de distribución de errores por tipo"""
        error_events = [e for e in events if e['level'] == 'ERROR']
        
        if not error_events:
            ax.text(0.5, 0.5, 'No hay errores registrados\n✅ ¡Excelente!', 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, color='green')
            ax.set_title(title)
            return
        
        # Contar errores por tipo
        error_types = [e['event_type'] for e in error_events]
        error_counts = pd.Series(error_types).value_counts()
        
        # Gráfico de barras
        bars = ax.bar(range(len(error_counts)), error_counts.values, color='red', alpha=0.7)
        ax.set_xticks(range(len(error_counts)))
        ax.set_xticklabels(error_counts.index, rotation=45, ha='right')
        ax.set_title(title, fontsize=10)
        ax.set_ylabel('Cantidad de Errores')
        
        # Agregar números en las barras
        for bar, count in zip(bars, error_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(count), ha='center', va='bottom')
    
    def _plot_performance_trends(self, events: List[Dict], ax, title: str):
        """Gráfico de tendencias de rendimiento"""
        # Extraer eventos con score
        score_events = [e for e in events if 'score' in e]
        death_events = [e for e in events if e.get('is_death', False)]
        
        if not score_events and not death_events:
            ax.text(0.5, 0.5, 'No hay datos de rendimiento', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # Línea de scores a lo largo del tiempo
        if score_events:
            score_times = [e['timestamp'] for e in score_events]
            scores = [e['score'] for e in score_events]
            ax.plot(score_times, scores, 'b-', linewidth=2, label='Score', marker='o', markersize=4)
        
        # Marcar muertes
        if death_events:
            death_times = [e['timestamp'] for e in death_events]
            max_score = max([e.get('score', 0) for e in events]) if score_events else 10
            death_y = [max_score * 1.1] * len(death_times)
            ax.scatter(death_times, death_y, c='red', s=100, marker='X', label='Game Over', zorder=5)
        
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Score')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Formatear eje x
        if score_events or death_events:
            all_times = (score_times if score_events else []) + (death_times if death_events else [])
            if all_times:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def show_detailed_game_analysis(self, game_name: str):
        """Análisis detallado de un juego específico"""
        if game_name not in self.games_data:
            print(f"❌ No hay datos para el juego: {game_name}")
            return
        
        events = self.games_data[game_name]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'📊 Análisis Detallado: {game_name}', fontsize=16, fontweight='bold')
        
        # 1. Heatmap de actividad por hora
        self._plot_activity_heatmap(events, axes[0, 0], 'Actividad por Hora del Día')
        
        # 2. Duración de sesiones
        self._plot_session_durations(events, axes[0, 1], 'Duración de Sesiones')
        
        # 3. Velocidad vs Rendimiento
        self._plot_speed_performance(events, axes[1, 0], 'Velocidad vs Rendimiento')
        
        # 4. Progresión de habilidad
        self._plot_skill_progression(events, axes[1, 1], 'Progresión de Habilidad')
        
        plt.tight_layout()
        plt.show()
    
    def _plot_activity_heatmap(self, events: List[Dict], ax, title: str):
        """Heatmap de actividad por hora"""
        if not events:
            ax.text(0.5, 0.5, 'No hay datos', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # Crear matriz de horas (24h) x días
        hours = [e['timestamp'].hour for e in events]
        activity_by_hour = pd.Series(hours).value_counts().sort_index()
        
        # Rellenar horas faltantes con 0
        all_hours = pd.Series(0, index=range(24))
        all_hours.update(activity_by_hour)
        
        # Crear heatmap simple
        ax.bar(range(24), all_hours.values, color='skyblue', alpha=0.7)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Hora del Día')
        ax.set_ylabel('Número de Eventos')
        ax.grid(True, alpha=0.3)
    
    def _plot_session_durations(self, events: List[Dict], ax, title: str):
        """Duración de sesiones de juego"""
        duration_events = [e for e in events if 'game_duration' in e]
        
        if not duration_events:
            ax.text(0.5, 0.5, 'No hay datos de duración', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        durations = [e['game_duration'] for e in duration_events]
        
        ax.hist(durations, bins=10, color='lightgreen', alpha=0.7, edgecolor='black')
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Duración (segundos)')
        ax.set_ylabel('Frecuencia')
        ax.grid(True, alpha=0.3)
        
        # Estadísticas
        avg_duration = np.mean(durations)
        ax.axvline(avg_duration, color='red', linestyle='--', 
                  label=f'Promedio: {avg_duration:.1f}s')
        ax.legend()
    
    def _plot_speed_performance(self, events: List[Dict], ax, title: str):
        """Relación entre velocidad y rendimiento"""
        speed_events = [e for e in events if 'speed' in e and 'score' in e]
        
        if not speed_events:
            ax.text(0.5, 0.5, 'No hay datos de velocidad', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        speeds = [e['speed'] for e in speed_events]
        scores = [e['score'] for e in speed_events]
        
        ax.scatter(speeds, scores, alpha=0.6, color='purple')
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Velocidad (segundos)')
        ax.set_ylabel('Score')
        ax.grid(True, alpha=0.3)
        
        # Línea de tendencia
        if len(speeds) > 1:
            z = np.polyfit(speeds, scores, 1)
            p = np.poly1d(z)
            ax.plot(speeds, p(speeds), "r--", alpha=0.8, label='Tendencia')
            ax.legend()
    
    def _plot_skill_progression(self, events: List[Dict], ax, title: str):
        """Progresión de habilidad a lo largo del tiempo"""
        death_events = [e for e in events if e.get('is_death', False) and 'score' in e]
        
        if not death_events:
            ax.text(0.5, 0.5, 'No hay datos de progresión', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # Ordenar por tiempo
        death_events.sort(key=lambda x: x['timestamp'])
        
        times = [e['timestamp'] for e in death_events]
        final_scores = [e['score'] for e in death_events]
        
        ax.plot(times, final_scores, 'o-', color='darkblue', linewidth=2, markersize=6)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Score Final por Partida')
        ax.grid(True, alpha=0.3)
        
        # Formatear eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Tendencia
        if len(final_scores) > 2:
            z = np.polyfit(range(len(final_scores)), final_scores, 1)
            trend_line = np.poly1d(z)
            ax.plot(times, trend_line(range(len(final_scores))), "r--", alpha=0.8, label='Tendencia')
            ax.legend()
    
    def generate_performance_report(self, game_name: str) -> str:
        """Generar reporte textual de rendimiento"""
        if game_name not in self.games_data:
            return f"❌ No hay datos para el juego: {game_name}"
        
        events = self.games_data[game_name]
        
        # Estadísticas básicas
        total_events = len(events)
        error_events = [e for e in events if e['level'] == 'ERROR']
        death_events = [e for e in events if e.get('is_death', False)]
        score_events = [e for e in events if 'score' in e]
        duration_events = [e for e in events if 'game_duration' in e]
        
        report = f"""🎮 REPORTE DE RENDIMIENTO: {game_name.upper()}
{'='*60}

📊 ESTADÍSTICAS GENERALES:
• Total de eventos registrados: {total_events}
• Errores totales: {len(error_events)}
• Partidas completadas: {len(death_events)}
• Eventos con score: {len(score_events)}
"""
        
        # Scores
        if score_events:
            scores = [e['score'] for e in score_events]
            max_score = max(scores)
            avg_score = sum(scores) / len(scores)
            report += f"\n🎯 PUNTUACIONES:\n• Score máximo alcanzado: {max_score}\n• Score promedio: {avg_score:.1f}\n"
        
        # Duraciones
        if duration_events:
            durations = [e['game_duration'] for e in duration_events]
            max_duration = max(durations)
            avg_duration = sum(durations) / len(durations)
            total_time = sum(durations)
            report += f"\n⏱️ TIEMPO DE JUEGO:\n• Sesión más larga: {max_duration:.1f} segundos\n• Duración promedio: {avg_duration:.1f} segundos\n• Tiempo total jugado: {total_time:.1f} segundos\n"
        
        # Análisis de errores
        if error_events:
            error_types = {}
            for e in error_events:
                et = e['event_type']
                error_types[et] = error_types.get(et, 0) + 1
            
            report += f"\n❌ ANÁLISIS DE ERRORES:\n"
            for error_type, count in error_types.items():
                report += f"• {error_type}: {count} veces\n"
        
        # Recomendaciones
        report += f"\n💡 RECOMENDACIONES:\n"
        
        if len(error_events) / total_events > 0.1:
            report += "• Alta tasa de errores: practica más para mejorar la precisión\n"
        else:
            report += "• Excelente control de errores: ¡sigue así!\n"
        
        if duration_events:
            avg_duration = sum([e['game_duration'] for e in duration_events]) / len(duration_events)
            if avg_duration < 30:
                report += "• Sesiones cortas: intenta jugar por más tiempo para mejorar\n"
            elif avg_duration > 120:
                report += "• Excelente resistencia: sesiones largas indican buen compromiso\n"
        
        if score_events:
            scores = [e['score'] for e in score_events]
            if len(set(scores)) > len(scores) * 0.7:
                report += "• Scores muy variables: trabaja en la consistencia\n"
        
        return report
    
    def export_data_to_csv(self, game_name: str, output_path: str = None):
        """Exportar datos a CSV para análisis externo"""
        if game_name not in self.games_data:
            print(f"❌ No hay datos para el juego: {game_name}")
            return
        
        events = self.games_data[game_name]
        
        # Convertir a DataFrame
        df_data = []
        for e in events:
            row = {
                'timestamp': e['timestamp'],
                'level': e['level'],
                'event_type': e['event_type'],
                'message': e['message'],
                'score': e.get('score', ''),
                'x_pos': e.get('x_pos', ''),
                'y_pos': e.get('y_pos', ''),
                'speed': e.get('speed', ''),
                'game_duration': e.get('game_duration', ''),
                'is_death': e.get('is_death', False),
                'is_success': e.get('is_success', False)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        if output_path is None:
            output_path = f"{game_name.lower().replace(' ', '_')}_analysis.csv"
        
        df.to_csv(output_path, index=False)
        print(f"✅ Datos exportados a: {output_path}")
    
    def list_available_games(self) -> List[str]:
        """Listar juegos disponibles para análisis"""
        return list(self.games_data.keys())
    
    def get_game_summary(self, game_name: str) -> Dict:
        """Obtener resumen rápido de un juego"""
        if game_name not in self.games_data:
            return {}
        
        events = self.games_data[game_name]
        
        return {
            'total_events': len(events),
            'errors': len([e for e in events if e['level'] == 'ERROR']),
            'deaths': len([e for e in events if e.get('is_death', False)]),
            'max_score': max([e.get('score', 0) for e in events]),
            'total_duration': sum([e.get('game_duration', 0) for e in events]),
            'first_event': events[0]['timestamp'] if events else None,
            'last_event': events[-1]['timestamp'] if events else None
        }


def main():
    """Función principal para ejecutar análisis independiente"""
    print("🎮 Game Analytics - Analizador de Logs")
    print("="*50)
    
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
