"""
Calculador de métricas cognitivas - Solo lo esencial
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class MetricsCalculator:
    """Calcula métricas cognitivas básicas de archivos CSV"""
    
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.data = self._load_data()
        self.game_type = self._detect_game_type()
    
    def _load_data(self) -> Optional[pd.DataFrame]:
        """Cargar datos del CSV"""
        try:
            return pd.read_csv(self.csv_file)
        except Exception as e:
            print(f"❌ Error cargando CSV: {e}")
            return None
    
    def _detect_game_type(self) -> str:
        """Detectar tipo de juego por columnas"""
        if self.data is None:
            return "unknown"
        
        columns = set(self.data.columns)
        
        if 'sequence_shown' in columns and 'sequence_input' in columns:
            return "piano_simon"
        elif 'obstacle_position' in columns and 'lane_change_accuracy' in columns:
            return "two_lane_runner" 
        else:
            return "generic"
    
    def calculate_piano_metrics(self) -> Dict:
        """Métricas específicas para Piano-Simon"""
        if self.data is None or self.game_type != "piano_simon":
            return {}
        
        try:
            metrics = {
                # Métricas básicas
                'total_attempts': len(self.data),
                'accuracy_mean': self.data['accuracy'].mean(),
                'accuracy_std': self.data['accuracy'].std(),
                
                # Tiempo de reacción
                'reaction_time_mean': self.data['response_time_ms'].mean(),
                'reaction_time_std': self.data['response_time_ms'].std(),
                'reaction_time_median': self.data['response_time_ms'].median(),
                
                # Progresión de nivel
                'max_level_reached': self.data['level'].max(),
                'levels_completed': len(self.data[self.data['is_correct'] == True]['level'].unique()),
                
                # Análisis de errores
                'error_rate': (self.data['is_correct'] == False).mean(),
                'error_types': self.data['error_type'].value_counts().to_dict(),
                
                # Fatiga cognitiva (degradación en el tiempo)
                'fatigue_index': self._calculate_fatigue_index(),
                
                # Curva de aprendizaje
                'learning_trend': self._calculate_learning_trend(),
                
                # Consistencia
                'consistency_score': self._calculate_consistency()
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculando métricas piano: {e}")
            return {}
    
    def calculate_runner_metrics(self) -> Dict:
        """Métricas específicas para Two-Lane Runner"""
        if self.data is None or self.game_type != "two_lane_runner":
            return {}
        
        try:
            metrics = {
                'total_obstacles': len(self.data),
                'success_rate': self.data['success'].mean(),
                'reaction_time_mean': self.data['reaction_time_ms'].mean(),
                'reaction_time_std': self.data['reaction_time_ms'].std(),
                'lane_accuracy_mean': self.data['lane_change_accuracy'].mean(),
                'max_speed_level': self.data['speed_level'].max(),
                'attention_score': self._calculate_attention_score()
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculando métricas runner: {e}")
            return {}
    
    def _calculate_fatigue_index(self) -> float:
        """Calcular índice de fatiga cognitiva"""
        if len(self.data) < 6:  # Necesitamos varios puntos
            return 0.0
        
        # Dividir en primera y segunda mitad
        mid_point = len(self.data) // 2
        first_half = self.data.iloc[:mid_point]['accuracy'].mean()
        second_half = self.data.iloc[mid_point:]['accuracy'].mean()
        
        # Fatiga = degradación del rendimiento
        fatigue = (first_half - second_half) / first_half if first_half > 0 else 0
        return max(0, fatigue)  # Solo valores positivos
    
    def _calculate_learning_trend(self) -> float:
        """Calcular tendencia de aprendizaje"""
        if len(self.data) < 4:
            return 0.0
        
        # Regresión simple sobre la precisión
        x = np.arange(len(self.data))
        y = self.data['accuracy'].values
        
        try:
            slope = np.polyfit(x, y, 1)[0]
            return slope  # Positivo = mejora, negativo = empeora
        except:
            return 0.0
    
    def _calculate_consistency(self) -> float:
        """Calcular score de consistencia"""
        if len(self.data) < 3:
            return 0.0
        
        # Basado en desviación estándar (menos variación = más consistencia)
        accuracy_std = self.data['accuracy'].std()
        consistency = 1.0 - min(accuracy_std, 1.0)  # Invertir para que alto = más consistente
        return consistency
    
    def _calculate_attention_score(self) -> float:
        """Calcular score de atención para runner"""
        if len(self.data) == 0:
            return 0.0
        
        # Combinar success rate y tiempo de reacción
        success_rate = self.data['success'].mean()
        reaction_penalty = min(self.data['reaction_time_ms'].mean() / 1000, 1.0)  # Normalizar
        
        attention_score = success_rate * (1.0 - reaction_penalty * 0.3)
        return max(0, attention_score)
    
    def generate_summary_report(self) -> str:
        """Generar reporte de resumen simple"""
        if self.data is None:
            return "❌ No se pudieron cargar los datos"
        
        if self.game_type == "piano_simon":
            metrics = self.calculate_piano_metrics()
            return self._format_piano_report(metrics)
        elif self.game_type == "two_lane_runner":
            metrics = self.calculate_runner_metrics()
            return self._format_runner_report(metrics)
        else:
            return "📊 Tipo de juego no reconocido para métricas específicas"
    
    def _format_piano_report(self, metrics: Dict) -> str:
        """Formatear reporte para Piano-Simon"""
        if not metrics:
            return "❌ Error generando métricas"
        
        return f"""🧠 EVALUACIÓN COGNITIVA - PIANO SIMON
{"=" * 50}

📊 RENDIMIENTO GENERAL:
• Intentos totales: {metrics.get('total_attempts', 0)}
• Precisión promedio: {metrics.get('accuracy_mean', 0):.2%}
• Nivel máximo alcanzado: {metrics.get('max_level_reached', 0)}
• Tasa de error: {metrics.get('error_rate', 0):.2%}

⏱️ TIEMPO DE REACCIÓN:
• Promedio: {metrics.get('reaction_time_mean', 0):.0f}ms
• Mediana: {metrics.get('reaction_time_median', 0):.0f}ms
• Variabilidad: {metrics.get('reaction_time_std', 0):.0f}ms

🧩 ANÁLISIS COGNITIVO:
• Índice de fatiga: {metrics.get('fatigue_index', 0):.3f} (0=sin fatiga, 1=alta fatiga)
• Tendencia de aprendizaje: {metrics.get('learning_trend', 0):.3f} (pos=mejora)
• Consistencia: {metrics.get('consistency_score', 0):.3f} (0-1, alto=más consistente)

❌ PATRONES DE ERROR:
{self._format_error_types(metrics.get('error_types', {}))}

💡 INTERPRETACIÓN COGNITIVA:
{self._interpret_piano_results(metrics)}
"""
    
    def _format_runner_report(self, metrics: Dict) -> str:
        """Formatear reporte para Two-Lane Runner"""
        if not metrics:
            return "❌ Error generando métricas"
        
        return f"""🏃 EVALUACIÓN COGNITIVA - TWO LANE RUNNER
{"=" * 50}

📊 RENDIMIENTO GENERAL:
• Obstáculos enfrentados: {metrics.get('total_obstacles', 0)}
• Tasa de éxito: {metrics.get('success_rate', 0):.2%}
• Velocidad máxima: Nivel {metrics.get('max_speed_level', 0)}

⚡ ATENCIÓN Y REACCIÓN:
• Tiempo de reacción promedio: {metrics.get('reaction_time_mean', 0):.0f}ms
• Precisión de cambio de carril: {metrics.get('lane_accuracy_mean', 0):.2%}
• Score de atención: {metrics.get('attention_score', 0):.3f}

💡 INTERPRETACIÓN COGNITIVA:
{self._interpret_runner_results(metrics)}
"""
    
    def _format_error_types(self, error_types: Dict) -> str:
        """Formatear tipos de errores"""
        if not error_types:
            return "• No hay errores registrados"
        
        formatted = []
        for error_type, count in error_types.items():
            formatted.append(f"• {error_type}: {count} veces")
        
        return "\n".join(formatted)
    
    def _interpret_piano_results(self, metrics: Dict) -> str:
        """Interpretar resultados cognitivos del piano"""
        interpretations = []
        
        accuracy = metrics.get('accuracy_mean', 0)
        fatigue = metrics.get('fatigue_index', 0)
        consistency = metrics.get('consistency_score', 0)
        learning = metrics.get('learning_trend', 0)
        
        # Interpretación de precisión
        if accuracy >= 0.8:
            interpretations.append("• Excelente capacidad de memoria a corto plazo")
        elif accuracy >= 0.6:
            interpretations.append("• Capacidad de memoria moderada")
        else:
            interpretations.append("• Dificultades en retención de secuencias")
        
        # Interpretación de fatiga
        if fatigue > 0.3:
            interpretations.append("• Alta fatiga cognitiva detectada")
        elif fatigue > 0.1:
            interpretations.append("• Fatiga cognitiva moderada")
        else:
            interpretations.append("• Buena resistencia cognitiva")
        
        # Interpretación de aprendizaje
        if learning > 0.01:
            interpretations.append("• Curva de aprendizaje positiva")
        elif learning < -0.01:
            interpretations.append("• Declive en rendimiento durante sesión")
        
        return "\n".join(interpretations) if interpretations else "• Análisis insuficiente"
    
    def _interpret_runner_results(self, metrics: Dict) -> str:
        """Interpretar resultados cognitivos del runner"""
        interpretations = []
        
        success_rate = metrics.get('success_rate', 0)
        reaction_time = metrics.get('reaction_time_mean', 0)
        attention_score = metrics.get('attention_score', 0)
        
        if success_rate >= 0.8:
            interpretations.append("• Excelente atención sostenida")
        elif success_rate >= 0.6:
            interpretations.append("• Atención moderada")
        else:
            interpretations.append("• Dificultades de atención")
        
        if reaction_time < 500:
            interpretations.append("• Tiempo de reacción excelente")
        elif reaction_time < 800:
            interpretations.append("• Tiempo de reacción normal")
        else:
            interpretations.append("• Tiempo de reacción lento")
        
        return "\n".join(interpretations) if interpretations else "• Análisis insuficiente" 