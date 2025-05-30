"""
Visualizador de datos especializado para gráficos matplotlib de analytics
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class DataVisualizer:
    """Especialista en visualizaciones matplotlib para análisis de juegos"""
    
    def __init__(self):
        self.color_schemes = {
            "primary": {"INFO": "blue", "WARNING": "orange", "ERROR": "red"},
            "pastel": {"INFO": "#a8e6cf", "WARNING": "#ffd3a5", "ERROR": "#fd9ada"},
            "dark": {"INFO": "#2c3e50", "WARNING": "#f39c12", "ERROR": "#e74c3c"}
        }
    
    def show_performance_dashboard(self, games_data: Dict[str, List[Dict]], game_name: Optional[str] = None):
        """Mostrar dashboard completo de rendimiento"""
        if not games_data:
            print("❌ No hay datos de logs disponibles")
            return

        # Si no se especifica juego, mostrar todos
        games_to_show = (
            [game_name] if game_name and game_name in games_data else list(games_data.keys())
        )

        # Crear subplots dinámicamente
        fig_rows = len(games_to_show)
        fig, axes = plt.subplots(fig_rows, 3, figsize=(18, 6 * fig_rows))
        if fig_rows == 1:
            axes = axes.reshape(1, -1)

        fig.suptitle("🎮 Game Performance Dashboard", fontsize=16, fontweight="bold")

        for idx, game in enumerate(games_to_show):
            events = games_data[game]

            # Gráfico 1: Eventos por tiempo
            self.plot_events_timeline(events, axes[idx, 0], f"{game} - Timeline de Eventos")

            # Gráfico 2: Distribución de errores
            self.plot_error_distribution(events, axes[idx, 1], f"{game} - Distribución de Errores")

            # Gráfico 3: Rendimiento por sesión
            self.plot_performance_trends(events, axes[idx, 2], f"{game} - Tendencias de Rendimiento")

        plt.tight_layout()
        plt.show()
    
    def show_detailed_game_analysis(self, game_name: str, events: List[Dict]):
        """Análisis detallado de un juego específico"""
        if not events:
            print(f"❌ No hay datos para el juego: {game_name}")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"📊 Análisis Detallado: {game_name}", fontsize=16, fontweight="bold")

        # 1. Heatmap de actividad por hora
        self.plot_activity_heatmap(events, axes[0, 0], "Actividad por Hora del Día")

        # 2. Duración de sesiones
        self.plot_session_durations(events, axes[0, 1], "Duración de Sesiones")

        # 3. Velocidad vs Rendimiento
        self.plot_speed_performance(events, axes[1, 0], "Velocidad vs Rendimiento")

        # 4. Progresión de habilidad
        self.plot_skill_progression(events, axes[1, 1], "Progresión de Habilidad")

        plt.tight_layout()
        plt.show()
    
    def plot_events_timeline(self, events: List[Dict], ax, title: str):
        """Gráfico de timeline de eventos"""
        if not events:
            self._show_no_data_message(ax, title)
            return

        # Separar eventos por tipo
        timestamps = [e["timestamp"] for e in events]
        event_types = [e["event_type"] for e in events]
        levels = [e["level"] for e in events]

        # Crear colores por nivel
        colors = [self.color_schemes["primary"].get(level, "gray") for level in levels]

        # Convertir tipos de evento a números para scatter plot
        unique_types = list(set(event_types))
        type_to_num = {t: i for i, t in enumerate(unique_types)}
        y_positions = [type_to_num[et] for et in event_types]

        ax.scatter(timestamps, y_positions, c=colors, alpha=0.6, s=30)
        ax.set_yticks(range(len(unique_types)))
        ax.set_yticklabels(unique_types, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Tiempo")

        # Formatear eje x
        if timestamps:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def plot_error_distribution(self, events: List[Dict], ax, title: str):
        """Gráfico de distribución de errores por tipo"""
        error_events = [e for e in events if e["level"] == "ERROR"]

        if not error_events:
            ax.text(0.5, 0.5, "No hay errores registrados\n✅ ¡Excelente!",
                   ha="center", va="center", transform=ax.transAxes,
                   fontsize=12, color="green")
            ax.set_title(title)
            return

        # Contar errores por tipo
        error_types = [e["event_type"] for e in error_events]
        error_counts = pd.Series(error_types).value_counts()

        # Gráfico de barras
        bars = ax.bar(range(len(error_counts)), error_counts.values, 
                     color="red", alpha=0.7)
        ax.set_xticks(range(len(error_counts)))
        ax.set_xticklabels(error_counts.index, rotation=45, ha="right")
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("Cantidad de Errores")

        # Agregar números en las barras
        for bar, count in zip(bars, error_counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                   str(count), ha="center", va="bottom")
    
    def plot_performance_trends(self, events: List[Dict], ax, title: str):
        """Gráfico de tendencias de rendimiento"""
        # Extraer eventos con score
        score_events = [e for e in events if "score" in e]
        death_events = [e for e in events if e.get("is_death", False)]

        if not score_events and not death_events:
            self._show_no_data_message(ax, title, "No hay datos de rendimiento")
            return

        # Línea de scores a lo largo del tiempo
        if score_events:
            score_times = [e["timestamp"] for e in score_events]
            scores = [e["score"] for e in score_events]
            ax.plot(score_times, scores, "b-", linewidth=2, label="Score",
                   marker="o", markersize=4)

        # Marcar muertes
        if death_events:
            death_times = [e["timestamp"] for e in death_events]
            max_score = max([e.get("score", 0) for e in events]) if score_events else 10
            death_y = [max_score * 1.1] * len(death_times)
            ax.scatter(death_times, death_y, c="red", s=100, marker="X",
                      label="Game Over", zorder=5)

        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Score")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Formatear eje x
        self._format_time_axis(ax, score_events, death_events)
    
    def plot_activity_heatmap(self, events: List[Dict], ax, title: str):
        """Heatmap de actividad por hora"""
        if not events:
            self._show_no_data_message(ax, title)
            return

        # Crear matriz de horas (24h) x días
        hours = [e["timestamp"].hour for e in events]
        activity_by_hour = pd.Series(hours).value_counts().sort_index()

        # Rellenar horas faltantes con 0
        all_hours = pd.Series(0, index=range(24))
        all_hours.update(activity_by_hour)

        # Crear heatmap simple
        ax.bar(range(24), all_hours.values, color="skyblue", alpha=0.7)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Hora del Día")
        ax.set_ylabel("Número de Eventos")
        ax.grid(True, alpha=0.3)
    
    def plot_session_durations(self, events: List[Dict], ax, title: str):
        """Duración de sesiones de juego"""
        duration_events = [e for e in events if "game_duration" in e]

        if not duration_events:
            self._show_no_data_message(ax, title, "No hay datos de duración")
            return

        durations = [e["game_duration"] for e in duration_events]

        ax.hist(durations, bins=10, color="lightgreen", alpha=0.7, edgecolor="black")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Duración (segundos)")
        ax.set_ylabel("Frecuencia")
        ax.grid(True, alpha=0.3)

        # Estadísticas
        avg_duration = np.mean(durations)
        ax.axvline(avg_duration, color="red", linestyle="--",
                  label=f"Promedio: {avg_duration:.1f}s")
        ax.legend()
    
    def plot_speed_performance(self, events: List[Dict], ax, title: str):
        """Relación entre velocidad y rendimiento"""
        speed_events = [e for e in events if "speed" in e and "score" in e]

        if not speed_events:
            self._show_no_data_message(ax, title, "No hay datos de velocidad")
            return

        speeds = [e["speed"] for e in speed_events]
        scores = [e["score"] for e in speed_events]

        ax.scatter(speeds, scores, alpha=0.6, color="purple")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Velocidad (segundos)")
        ax.set_ylabel("Score")
        ax.grid(True, alpha=0.3)

        # Línea de tendencia
        if len(speeds) > 1:
            z = np.polyfit(speeds, scores, 1)
            p = np.poly1d(z)
            ax.plot(speeds, p(speeds), "r--", alpha=0.8, label="Tendencia")
            ax.legend()
    
    def plot_skill_progression(self, events: List[Dict], ax, title: str):
        """Progresión de habilidad a lo largo del tiempo"""
        death_events = [e for e in events if e.get("is_death", False) and "score" in e]

        if not death_events:
            self._show_no_data_message(ax, title, "No hay datos de progresión")
            return

        # Ordenar por tiempo
        death_events.sort(key=lambda x: x["timestamp"])

        times = [e["timestamp"] for e in death_events]
        final_scores = [e["score"] for e in death_events]

        ax.plot(times, final_scores, "o-", color="darkblue", 
               linewidth=2, markersize=6)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Score Final por Partida")
        ax.grid(True, alpha=0.3)

        # Formatear eje x
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # Tendencia
        if len(final_scores) > 2:
            z = np.polyfit(range(len(final_scores)), final_scores, 1)
            trend_line = np.poly1d(z)
            ax.plot(times, trend_line(range(len(final_scores))), "r--",
                   alpha=0.8, label="Tendencia")
            ax.legend()
    
    def _show_no_data_message(self, ax, title: str, message: str = "No hay datos"):
        """Mostrar mensaje cuando no hay datos"""
        ax.text(0.5, 0.5, message, ha="center", va="center", 
               transform=ax.transAxes)
        ax.set_title(title)
    
    def _format_time_axis(self, ax, *event_lists):
        """Formatear eje de tiempo"""
        all_times = []
        for events in event_lists:
            if events:
                all_times.extend([e["timestamp"] for e in events])
        
        if all_times:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def create_custom_plot(self, events: List[Dict], plot_type: str, **kwargs):
        """Crear gráfico personalizado según tipo"""
        plot_methods = {
            "timeline": self.plot_events_timeline,
            "errors": self.plot_error_distribution,
            "performance": self.plot_performance_trends,
            "activity": self.plot_activity_heatmap,
            "durations": self.plot_session_durations,
            "speed": self.plot_speed_performance,
            "progression": self.plot_skill_progression
        }
        
        if plot_type in plot_methods:
            fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 6)))
            plot_methods[plot_type](events, ax, kwargs.get("title", f"{plot_type.title()} Plot"))
            plt.tight_layout()
            plt.show()
        else:
            print(f"❌ Tipo de gráfico no soportado: {plot_type}")
            print(f"Tipos disponibles: {list(plot_methods.keys())}") 