"""
Generador de reportes especializado para análisis de juegos
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime


class ReportGenerator:
    """Especialista en generación de reportes textuales y exportación de datos"""

    def __init__(self):
        self.report_templates = {
            "basic": self._generate_basic_report,
            "detailed": self._generate_detailed_report,
            "performance": self.generate_performance_report,
            "errors": self._generate_error_report,
        }

    def generate_performance_report(self, game_name: str, events: List[Dict]) -> str:
        """Generar reporte textual de rendimiento completo"""
        if not events:
            return f"❌ No hay datos para el juego: {game_name}"

        # Estadísticas básicas
        total_events = len(events)
        error_events = [e for e in events if e["level"] == "ERROR"]
        death_events = [e for e in events if e.get("is_death", False)]
        score_events = [e for e in events if "score" in e]
        duration_events = [e for e in events if "game_duration" in e]

        report = f"""🎮 REPORTE DE RENDIMIENTO: {game_name.upper()}
{"=" * 60}

📊 ESTADÍSTICAS GENERALES:
• Total de eventos registrados: {total_events}
• Errores totales: {len(error_events)}
• Partidas completadas: {len(death_events)}
• Eventos con score: {len(score_events)}
"""

        # Sección de puntuaciones
        if score_events:
            report += self._add_scores_section(score_events)

        # Sección de duraciones
        if duration_events:
            report += self._add_durations_section(duration_events)

        # Análisis de errores
        if error_events:
            report += self._add_errors_section(error_events)

        # Recomendaciones
        report += self._add_recommendations_section(
            events, error_events, duration_events, score_events
        )

        return report

    def _add_scores_section(self, score_events: List[Dict]) -> str:
        """Agregar sección de puntuaciones al reporte"""
        scores = [e["score"] for e in score_events]
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)

        return f"""
🎯 PUNTUACIONES:
• Score máximo alcanzado: {max_score}
• Score promedio: {avg_score:.1f}
• Score mínimo: {min_score}
• Total de puntuaciones registradas: {len(scores)}
"""

    def _add_durations_section(self, duration_events: List[Dict]) -> str:
        """Agregar sección de duraciones al reporte"""
        durations = [e["game_duration"] for e in duration_events]
        max_duration = max(durations)
        avg_duration = sum(durations) / len(durations)
        total_time = sum(durations)

        return f"""
⏱️ TIEMPO DE JUEGO:
• Sesión más larga: {max_duration:.1f} segundos ({max_duration / 60:.1f} minutos)
• Duración promedio: {avg_duration:.1f} segundos
• Tiempo total jugado: {total_time:.1f} segundos ({total_time / 60:.1f} minutos)
• Número de sesiones: {len(durations)}
"""

    def _add_errors_section(self, error_events: List[Dict]) -> str:
        """Agregar sección de análisis de errores"""
        error_types = {}
        for e in error_events:
            et = e["event_type"]
            error_types[et] = error_types.get(et, 0) + 1

        error_section = "\n❌ ANÁLISIS DE ERRORES:\n"
        for error_type, count in error_types.items():
            percentage = (count / len(error_events)) * 100
            error_section += f"• {error_type}: {count} veces ({percentage:.1f}%)\n"

        return error_section

    def _add_recommendations_section(
        self,
        all_events: List[Dict],
        error_events: List[Dict],
        duration_events: List[Dict],
        score_events: List[Dict],
    ) -> str:
        """Agregar sección de recomendaciones inteligentes"""
        recommendations = "\n💡 RECOMENDACIONES:\n"

        # Análisis de tasa de errores
        error_rate = len(error_events) / len(all_events)
        if error_rate > 0.1:
            recommendations += "• Alta tasa de errores (>10%): practica más para mejorar la precisión\n"
        elif error_rate < 0.05:
            recommendations += "• Excelente control de errores (<5%): ¡sigue así!\n"
        else:
            recommendations += "• Tasa de errores moderada: hay espacio para mejorar\n"

        # Análisis de duración de sesiones
        if duration_events:
            avg_duration = sum([e["game_duration"] for e in duration_events]) / len(
                duration_events
            )
            if avg_duration < 30:
                recommendations += "• Sesiones cortas (<30s): intenta jugar por más tiempo para mejorar\n"
            elif avg_duration > 120:
                recommendations += "• Excelente resistencia (>2min): sesiones largas indican buen compromiso\n"

        # Análisis de consistencia en scores
        if score_events and len(score_events) > 3:
            scores = [e["score"] for e in score_events]
            score_variance = len(set(scores)) / len(scores)
            if score_variance > 0.7:
                recommendations += (
                    "• Scores muy variables: trabaja en la consistencia\n"
                )
            elif score_variance < 0.3:
                recommendations += "• Rendimiento muy consistente: ¡excelente!\n"

        # Análisis temporal
        if len(all_events) > 10:
            timestamps = [e["timestamp"] for e in all_events]
            time_span = (
                max(timestamps) - min(timestamps)
            ).total_seconds() / 3600  # horas
            if time_span > 1:
                recommendations += (
                    f"• Sesión de {time_span:.1f} horas: toma descansos regulares\n"
                )

        return recommendations

    def generate_summary_report(self, games_data: Dict[str, List[Dict]]) -> str:
        """Generar reporte resumen de todos los juegos"""
        if not games_data:
            return "❌ No hay datos de juegos disponibles"

        report = f"""📊 REPORTE RESUMEN MULTI-JUEGO
{"=" * 50}
🕒 Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🎮 JUEGOS ANALIZADOS: {len(games_data)}
"""

        for game_name, events in games_data.items():
            report += f"\n🔹 {game_name}:\n"
            report += f"   • Eventos totales: {len(events)}\n"

            error_count = len([e for e in events if e["level"] == "ERROR"])
            report += f"   • Errores: {error_count}\n"

            scores = [e.get("score", 0) for e in events if "score" in e]
            if scores:
                report += f"   • Score máximo: {max(scores)}\n"

            durations = [
                e.get("game_duration", 0) for e in events if "game_duration" in e
            ]
            if durations:
                total_time = sum(durations)
                report += f"   • Tiempo total: {total_time / 60:.1f} minutos\n"

        return report

    def export_data_to_csv(
        self, game_name: str, events: List[Dict], output_path: str = None
    ) -> str:
        """Exportar datos a CSV para análisis externo"""
        if not events:
            return f"❌ No hay datos para el juego: {game_name}"

        # Convertir a DataFrame
        df_data = []
        for e in events:
            row = {
                "timestamp": e["timestamp"],
                "level": e["level"],
                "event_type": e["event_type"],
                "message": e["message"],
                "score": e.get("score", ""),
                "x_pos": e.get("x_pos", ""),
                "y_pos": e.get("y_pos", ""),
                "speed": e.get("speed", ""),
                "game_duration": e.get("game_duration", ""),
                "is_death": e.get("is_death", False),
                "is_success": e.get("is_success", False),
                "is_pause": e.get("is_pause", False),
                "is_game_start": e.get("is_game_start", False),
            }
            df_data.append(row)

        df = pd.DataFrame(df_data)

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{game_name.lower().replace(' ', '_')}_{timestamp}.csv"

        try:
            df.to_csv(output_path, index=False)
            return f"✅ Datos exportados a: {output_path}"
        except Exception as e:
            return f"❌ Error exportando datos: {e}"

    def export_multiple_games_to_excel(
        self, games_data: Dict[str, List[Dict]], output_path: str = None
    ) -> str:
        """Exportar múltiples juegos a un archivo Excel con hojas separadas"""
        if not games_data:
            return "❌ No hay datos de juegos para exportar"

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"game_analytics_export_{timestamp}.xlsx"

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for game_name, events in games_data.items():
                    if events:
                        # Convertir eventos a DataFrame
                        df_data = []
                        for e in events:
                            row = {
                                "timestamp": e["timestamp"],
                                "level": e["level"],
                                "event_type": e["event_type"],
                                "message": e["message"],
                                "score": e.get("score", ""),
                                "x_pos": e.get("x_pos", ""),
                                "y_pos": e.get("y_pos", ""),
                                "speed": e.get("speed", ""),
                                "game_duration": e.get("game_duration", ""),
                                "is_death": e.get("is_death", False),
                                "is_success": e.get("is_success", False),
                            }
                            df_data.append(row)

                        df = pd.DataFrame(df_data)
                        # Limpiar nombre de hoja para Excel
                        sheet_name = game_name.replace(" ", "_")[:31]  # Excel limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            return f"✅ Datos de {len(games_data)} juegos exportados a: {output_path}"

        except Exception as e:
            return f"❌ Error exportando a Excel: {e}"

    def generate_custom_report(
        self, game_name: str, events: List[Dict], report_type: str = "basic", **kwargs
    ) -> str:
        """Generar reporte personalizado según tipo"""
        if report_type in self.report_templates:
            return self.report_templates[report_type](game_name, events, **kwargs)
        else:
            return f"❌ Tipo de reporte no soportado: {report_type}"

    def _generate_basic_report(
        self, game_name: str, events: List[Dict], **kwargs
    ) -> str:
        """Generar reporte básico"""
        if not events:
            return f"❌ No hay datos para {game_name}"

        total_events = len(events)
        error_count = len([e for e in events if e["level"] == "ERROR"])

        return f"""📋 REPORTE BÁSICO: {game_name}
• Total eventos: {total_events}
• Errores: {error_count}
• Primera actividad: {events[0]["timestamp"]}
• Última actividad: {events[-1]["timestamp"]}
"""

    def _generate_detailed_report(
        self, game_name: str, events: List[Dict], **kwargs
    ) -> str:
        """Generar reporte detallado"""
        return self.generate_performance_report(game_name, events)

    def _generate_error_report(
        self, game_name: str, events: List[Dict], **kwargs
    ) -> str:
        """Generar reporte enfocado en errores"""
        error_events = [e for e in events if e["level"] == "ERROR"]

        if not error_events:
            return f"✅ {game_name}: No se encontraron errores"

        error_types = {}
        for e in error_events:
            et = e["event_type"]
            error_types[et] = error_types.get(et, 0) + 1

        report = f"""❌ REPORTE DE ERRORES: {game_name}
Total de errores: {len(error_events)}

DISTRIBUCIÓN POR TIPO:
"""
        for error_type, count in error_types.items():
            report += f"• {error_type}: {count} veces\n"

        return report
