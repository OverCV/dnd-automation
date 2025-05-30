"""
Visualizador de gráficas cognitivas - Súper simple y efectivo
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import os
from datetime import datetime


class CognitiveVisualAnalyzer:
    """Visualizador súper simple para análisis cognitivos"""
    
    def __init__(self):
        self.fig_size = (12, 8)
        self.colors = {
            'primary': '#2E86C1',
            'success': '#28B463', 
            'warning': '#F39C12',
            'error': '#E74C3C',
            'secondary': '#85929E'
        }
    
    def create_piano_performance_dashboard(self, csv_file: str, save_path: str = None) -> str:
        """Crear dashboard completo de rendimiento Piano-Simon"""
        try:
            # Cargar datos
            data = pd.read_csv(csv_file)
            
            if data.empty:
                return "❌ No hay datos en el archivo CSV"
            
            # Crear figura con subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('🧠 DASHBOARD COGNITIVO - PIANO SIMON', fontsize=16, fontweight='bold')
            
            # Gráfica 1: Precisión por intento
            self._plot_accuracy_trend(data, ax1)
            
            # Gráfica 2: Tiempo de reacción por nivel
            self._plot_reaction_time_by_level(data, ax2)
            
            # Gráfica 3: Tipos de errores
            self._plot_error_types(data, ax3)
            
            # Gráfica 4: Progresión de niveles
            self._plot_level_progression(data, ax4)
            
            plt.tight_layout()
            
            # Guardar o mostrar
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return f"✅ Dashboard guardado: {save_path}"
            else:
                # Generar nombre automático
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_path = f"data/cognitive/dashboard_{timestamp}.png"
                os.makedirs(os.path.dirname(auto_path), exist_ok=True)
                plt.savefig(auto_path, dpi=300, bbox_inches='tight')
                plt.close()
                return f"✅ Dashboard guardado: {auto_path}"
        
        except Exception as e:
            return f"❌ Error creando dashboard: {e}"
    
    def _plot_accuracy_trend(self, data: pd.DataFrame, ax):
        """Gráfica de tendencia de precisión"""
        accuracy_values = data['accuracy'].values
        attempts = range(1, len(accuracy_values) + 1)
        
        ax.plot(attempts, accuracy_values, 'o-', color=self.colors['primary'], linewidth=2, markersize=6)
        ax.set_title('📈 Tendencia de Precisión', fontweight='bold')
        ax.set_xlabel('Intento')
        ax.set_ylabel('Precisión (0-1)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.1)
        
        # Línea de promedio
        mean_accuracy = accuracy_values.mean()
        ax.axhline(y=mean_accuracy, color=self.colors['warning'], linestyle='--', 
                  label=f'Promedio: {mean_accuracy:.2f}')
        ax.legend()
    
    def _plot_reaction_time_by_level(self, data: pd.DataFrame, ax):
        """Gráfica de tiempo de reacción por nivel"""
        levels = data['level'].unique()
        reaction_times = []
        
        for level in sorted(levels):
            level_data = data[data['level'] == level]['response_time_ms']
            reaction_times.append(level_data.mean())
        
        bars = ax.bar(sorted(levels), reaction_times, color=self.colors['success'], alpha=0.7)
        ax.set_title('⏱️ Tiempo de Reacción por Nivel', fontweight='bold')
        ax.set_xlabel('Nivel')
        ax.set_ylabel('Tiempo de Reacción (ms)')
        ax.grid(True, alpha=0.3)
        
        # Añadir valores encima de las barras
        for bar, time in zip(bars, reaction_times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                   f'{time:.0f}ms', ha='center', va='bottom', fontweight='bold')
    
    def _plot_error_types(self, data: pd.DataFrame, ax):
        """Gráfica de tipos de errores"""
        error_counts = data['error_type'].value_counts()
        
        # Colores para diferentes tipos de errores
        colors = [self.colors['success'] if error == 'correct' else self.colors['error'] 
                 for error in error_counts.index]
        
        wedges, texts, autotexts = ax.pie(error_counts.values, labels=error_counts.index, 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('❌ Distribución de Tipos de Respuesta', fontweight='bold')
        
        # Mejorar legibilidad
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _plot_level_progression(self, data: pd.DataFrame, ax):
        """Gráfica de progresión de niveles"""
        level_accuracy = data.groupby('level')['accuracy'].mean()
        level_attempts = data['level'].value_counts().sort_index()
        
        # Gráfica de barras con doble eje
        ax2 = ax.twinx()
        
        bars1 = ax.bar(level_accuracy.index, level_accuracy.values, 
                      alpha=0.7, color=self.colors['primary'], label='Precisión')
        bars2 = ax2.bar([x + 0.4 for x in level_accuracy.index], level_attempts.values,
                       alpha=0.7, color=self.colors['secondary'], width=0.4, label='Intentos')
        
        ax.set_title('📊 Progresión por Nivel', fontweight='bold')
        ax.set_xlabel('Nivel')
        ax.set_ylabel('Precisión', color=self.colors['primary'])
        ax2.set_ylabel('Número de Intentos', color=self.colors['secondary'])
        
        # Leyendas
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        ax.grid(True, alpha=0.3)
    
    def create_comparison_chart(self, csv_files: List[str], patient_names: List[str] = None) -> str:
        """Crear gráfica de comparación entre múltiples sesiones"""
        try:
            if not csv_files:
                return "❌ No hay archivos para comparar"
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle('🔄 COMPARACIÓN ENTRE SESIONES', fontsize=16, fontweight='bold')
            
            metrics_summary = []
            labels = patient_names if patient_names else [f"Sesión {i+1}" for i in range(len(csv_files))]
            
            for i, csv_file in enumerate(csv_files):
                try:
                    data = pd.read_csv(csv_file)
                    if not data.empty:
                        metrics = {
                            'label': labels[i],
                            'avg_accuracy': data['accuracy'].mean(),
                            'avg_reaction': data['response_time_ms'].mean(),
                            'max_level': data['level'].max(),
                            'error_rate': (data['is_correct'] == False).mean()
                        }
                        metrics_summary.append(metrics)
                except Exception as e:
                    print(f"⚠️ Error procesando {csv_file}: {e}")
            
            if not metrics_summary:
                return "❌ No se pudieron procesar los archivos"
            
            # Gráfica 1: Precisión promedio
            labels_list = [m['label'] for m in metrics_summary]
            accuracies = [m['avg_accuracy'] for m in metrics_summary]
            reactions = [m['avg_reaction'] for m in metrics_summary]
            
            bars1 = ax1.bar(labels_list, accuracies, color=self.colors['success'], alpha=0.8)
            ax1.set_title('📊 Precisión Promedio', fontweight='bold')
            ax1.set_ylabel('Precisión (0-1)')
            ax1.set_ylim(0, 1.1)
            
            # Añadir valores
            for bar, acc in zip(bars1, accuracies):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{acc:.2f}', ha='center', va='bottom', fontweight='bold')
            
            # Gráfica 2: Tiempo de reacción promedio
            bars2 = ax2.bar(labels_list, reactions, color=self.colors['warning'], alpha=0.8)
            ax2.set_title('⏱️ Tiempo de Reacción Promedio', fontweight='bold')
            ax2.set_ylabel('Tiempo (ms)')
            
            # Añadir valores
            for bar, react in zip(bars2, reactions):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                        f'{react:.0f}ms', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Guardar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"data/cognitive/comparison_{timestamp}.png"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return f"✅ Comparación guardada: {save_path}"
        
        except Exception as e:
            return f"❌ Error creando comparación: {e}"
    
    def create_fatigue_analysis(self, csv_file: str) -> str:
        """Análisis específico de fatiga cognitiva"""
        try:
            data = pd.read_csv(csv_file)
            
            if len(data) < 6:
                return "❌ Datos insuficientes para análisis de fatiga (min 6 eventos)"
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle('🧠 ANÁLISIS DE FATIGA COGNITIVA', fontsize=16, fontweight='bold')
            
            # Dividir en primera y segunda mitad
            mid_point = len(data) // 2
            first_half = data.iloc[:mid_point]
            second_half = data.iloc[mid_point:]
            
            # Gráfica 1: Precisión a lo largo del tiempo
            attempts = range(1, len(data) + 1)
            accuracies = data['accuracy'].values
            
            ax1.plot(attempts, accuracies, 'o-', color=self.colors['primary'], alpha=0.7)
            ax1.axvline(x=mid_point, color=self.colors['error'], linestyle='--', 
                       label=f'Punto medio (intento {mid_point})')
            
            # Tendencias
            first_avg = first_half['accuracy'].mean()
            second_avg = second_half['accuracy'].mean()
            
            ax1.axhline(y=first_avg, xmin=0, xmax=0.5, color=self.colors['success'], 
                       linewidth=3, label=f'Primera mitad: {first_avg:.2f}')
            ax1.axhline(y=second_avg, xmin=0.5, xmax=1, color=self.colors['warning'], 
                       linewidth=3, label=f'Segunda mitad: {second_avg:.2f}')
            
            ax1.set_title('📉 Tendencia de Precisión (Análisis de Fatiga)', fontweight='bold')
            ax1.set_xlabel('Intento')
            ax1.set_ylabel('Precisión')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Gráfica 2: Tiempo de reacción a lo largo del tiempo
            reaction_times = data['response_time_ms'].values
            
            ax2.plot(attempts, reaction_times, 's-', color=self.colors['warning'], alpha=0.7)
            ax2.axvline(x=mid_point, color=self.colors['error'], linestyle='--')
            
            first_reaction_avg = first_half['response_time_ms'].mean()
            second_reaction_avg = second_half['response_time_ms'].mean()
            
            ax2.axhline(y=first_reaction_avg, xmin=0, xmax=0.5, color=self.colors['success'], 
                       linewidth=3, label=f'Primera mitad: {first_reaction_avg:.0f}ms')
            ax2.axhline(y=second_reaction_avg, xmin=0.5, xmax=1, color=self.colors['error'], 
                       linewidth=3, label=f'Segunda mitad: {second_reaction_avg:.0f}ms')
            
            ax2.set_title('⏱️ Tendencia Tiempo de Reacción', fontweight='bold')
            ax2.set_xlabel('Intento')
            ax2.set_ylabel('Tiempo de Reacción (ms)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Guardar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"data/cognitive/fatiga_analysis_{timestamp}.png"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Calcular índice de fatiga
            fatigue_accuracy = (first_avg - second_avg) / first_avg if first_avg > 0 else 0
            fatigue_reaction = (second_reaction_avg - first_reaction_avg) / first_reaction_avg if first_reaction_avg > 0 else 0
            
            analysis = f"""✅ Análisis de fatiga completado: {save_path}

📊 RESULTADOS:
• Índice de fatiga (precisión): {fatigue_accuracy:.3f}
• Cambio en tiempo de reacción: {fatigue_reaction:.3f}

💡 INTERPRETACIÓN:
"""
            
            if fatigue_accuracy > 0.2:
                analysis += "• 🔴 Alta fatiga cognitiva detectada\n"
            elif fatigue_accuracy > 0.1:
                analysis += "• 🟡 Fatiga cognitiva moderada\n"
            else:
                analysis += "• 🟢 Buena resistencia cognitiva\n"
            
            if fatigue_reaction > 0.2:
                analysis += "• ⏱️ Tiempo de reacción se deterioró significativamente\n"
            elif fatigue_reaction > 0.1:
                analysis += "• ⏱️ Ligero deterioro en tiempo de reacción\n"
            else:
                analysis += "• ⏱️ Tiempo de reacción se mantuvo estable\n"
            
            return analysis
            
        except Exception as e:
            return f"❌ Error en análisis de fatiga: {e}" 