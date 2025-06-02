"""
Ventana de Análisis Cognitivo para Osu! - Métricas de precisión y coordinación
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from typing import Dict, List, Optional


class OsuCognitiveAnalyticsWindow:
    """Ventana especializada para análisis cognitivo del juego Osu"""
    
    def __init__(self, parent_window, game_id: str = "osu_rhythm"):
        self.parent = parent_window
        self.game_id = game_id
        self.window = None
        self.data_loaded = False
        self.session_data = []
        
        # Configuración de matplotlib en español
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        
        self.create_window()
        self.load_cognitive_data()
        self.setup_analytics_interface()
    
    def create_window(self):
        """Crear ventana principal de análisis"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎯 Análisis Cognitivo Osu! - {self.game_id.title()}")
        self.window.geometry("1200x800")
        self.window.configure(bg="#f0f0f0")
        
        # Hacer que la ventana sea modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_cognitive_data(self):
        """Cargar datos de sesiones cognitivas desde archivos CSV"""
        try:
            # Buscar archivos de sesiones Osu
            sessions_dir = f"data/cognitive/{self.game_id}/sessions"
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir, exist_ok=True)
                return
            
            # Cargar todos los archivos CSV
            csv_files = glob.glob(os.path.join(sessions_dir, "*.csv"))
            
            if not csv_files:
                print(f"⚠️ No se encontraron datos de sesiones Osu en {sessions_dir}")
                return
            
            all_sessions = []
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    # Agregar información del archivo
                    df['session_file'] = os.path.basename(csv_file)
                    df['session_date'] = self.extract_date_from_filename(csv_file)
                    all_sessions.append(df)
                except Exception as e:
                    print(f"⚠️ Error cargando {csv_file}: {e}")
            
            if all_sessions:
                self.session_data = pd.concat(all_sessions, ignore_index=True)
                self.data_loaded = True
                print(f"✅ Cargados {len(all_sessions)} archivos Osu con {len(self.session_data)} registros")
            
        except Exception as e:
            print(f"❌ Error cargando datos cognitivos Osu: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
    
    def extract_date_from_filename(self, filepath: str) -> datetime:
        """Extraer fecha del nombre del archivo"""
        try:
            filename = os.path.basename(filepath)
            # Buscar patrón de fecha en el nombre del archivo
            parts = filename.split('_')
            for part in parts:
                if len(part) >= 8 and part.isdigit():
                    # Formato: YYYYMMDD
                    if len(part) == 8:
                        return datetime.strptime(part, "%Y%m%d")
                    # Formato: YYYYMMDDHHMMSS
                    elif len(part) == 14:
                        return datetime.strptime(part, "%Y%m%d%H%M%S")
            # Si no encuentra fecha, usar fecha de modificación del archivo
            return datetime.fromtimestamp(os.path.getmtime(filepath))
        except:
            return datetime.now()
    
    def setup_analytics_interface(self):
        """Configurar la interfaz de análisis"""
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🎯 ANÁLISIS COGNITIVO OSU! RHYTHM",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        if not self.data_loaded or len(self.session_data) == 0:
            self.show_no_data_message(main_frame)
            return
        
        # Información de sesiones
        self.create_session_info(main_frame)
        
        # Notebook para las pestañas de análisis
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Crear pestañas específicas para Osu
        self.create_precision_tab()
        self.create_reaction_time_tab()
        self.create_coordination_tab()
        self.create_performance_tab()
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def show_no_data_message(self, parent):
        """Mostrar mensaje cuando no hay datos"""
        no_data_frame = tk.Frame(parent, bg="#f0f0f0")
        no_data_frame.pack(expand=True)
        
        message_label = tk.Label(
            no_data_frame,
            text="🎯 No se encontraron datos de sesiones Osu\n\n"
                 "Para ver análisis cognitivos:\n"
                 "1. Ejecuta algunas sesiones del juego Osu\n"
                 "2. Los datos se guardarán automáticamente\n"
                 "3. Vuelve a abrir esta ventana",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#7f8c8d",
            justify=tk.CENTER
        )
        message_label.pack(expand=True)
    
    def create_session_info(self, parent):
        """Crear información resumida de las sesiones"""
        info_frame = tk.Frame(parent, bg="#ecf0f1", relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Estadísticas rápidas
        total_sessions = len(self.session_data['session_file'].unique())
        total_hits = len(self.session_data)
        avg_spatial_accuracy = self.session_data['spatial_accuracy'].mean()
        avg_temporal_accuracy = self.session_data['temporal_accuracy'].mean()
        
        info_text = f"🎯 Sesiones: {total_sessions} | 🎪 Hits totales: {total_hits} | 📍 Precisión espacial: {avg_spatial_accuracy:.1f}% | ⏱️ Precisión temporal: {avg_temporal_accuracy:.1f}%"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            pady=10
        )
        info_label.pack()
    
    def create_precision_tab(self):
        """Crear pestaña de análisis de precisión espacial"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📍 Precisión Espacial")
        
        # Crear figura de matplotlib
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Análisis de Precisión Espacial', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Distribución de precisión espacial
            spatial_accuracy = self.session_data['spatial_accuracy'].dropna()
            ax1.hist(spatial_accuracy, bins=20, color='lightblue', alpha=0.7, edgecolor='black')
            ax1.axvline(spatial_accuracy.mean(), color='red', linestyle='--', 
                       label=f'Media: {spatial_accuracy.mean():.1f}%')
            ax1.set_title('Distribución de Precisión Espacial')
            ax1.set_xlabel('Precisión (%)')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Gráfica 2: Evolución de precisión por sesión
            session_spatial = self.session_data.groupby('session_file')['spatial_accuracy'].mean()
            ax2.plot(range(len(session_spatial)), session_spatial.values, 'bo-', linewidth=2, markersize=6)
            ax2.set_title('Evolución de Precisión Espacial por Sesión')
            ax2.set_xlabel('Sesión')
            ax2.set_ylabel('Precisión Espacial (%)')
            ax2.grid(True, alpha=0.3)
            
            # Gráfica 3: Precisión por tipo de hit
            hit_results = self.session_data['hit_result'].value_counts()
            colors = ['gold', 'lightgreen', 'lightblue', 'lightcoral']
            ax3.pie(hit_results.values, labels=hit_results.index, autopct='%1.1f%%', 
                   colors=colors[:len(hit_results)])
            ax3.set_title('Distribución de Tipos de Hit')
            
            # Gráfica 4: Mapa de calor de precisión por posición
            if len(self.session_data) > 10:
                # Crear bins para posiciones X e Y
                x_bins = np.linspace(0, 800, 10)
                y_bins = np.linspace(0, 600, 10)
                
                # Calcular precisión promedio por región
                heatmap_data = np.zeros((len(y_bins)-1, len(x_bins)-1))
                
                for i in range(len(y_bins)-1):
                    for j in range(len(x_bins)-1):
                        mask = ((self.session_data['cursor_x'] >= x_bins[j]) & 
                               (self.session_data['cursor_x'] < x_bins[j+1]) &
                               (self.session_data['cursor_y'] >= y_bins[i]) & 
                               (self.session_data['cursor_y'] < y_bins[i+1]))
                        
                        if mask.sum() > 0:
                            heatmap_data[i, j] = self.session_data.loc[mask, 'spatial_accuracy'].mean()
                
                im = ax4.imshow(heatmap_data, cmap='viridis', aspect='auto')
                ax4.set_title('Mapa de Calor - Precisión por Región')
                ax4.set_xlabel('Región X')
                ax4.set_ylabel('Región Y')
                plt.colorbar(im, ax=ax4, label='Precisión (%)')
            else:
                ax4.text(0.5, 0.5, 'Datos insuficientes\npara mapa de calor', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Mapa de Calor - Precisión')
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de precisión: {e}")
            ax1.text(0.5, 0.5, f'Error:\n{e}', ha='center', va='center', transform=ax1.transAxes)
        
        plt.tight_layout()
        
        # Integrar matplotlib en tkinter
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_reaction_time_tab(self):
        """Crear pestaña de análisis de tiempos de reacción"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚡ Tiempos de Reacción")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle('Análisis de Tiempos de Reacción', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Distribución de tiempos de reacción
            reaction_times = self.session_data['reaction_time_ms'].dropna()
            ax1.hist(reaction_times, bins=25, color='lightgreen', alpha=0.7, edgecolor='black')
            ax1.axvline(reaction_times.mean(), color='red', linestyle='--', 
                       label=f'Media: {reaction_times.mean():.0f}ms')
            ax1.axvline(reaction_times.median(), color='orange', linestyle='--', 
                       label=f'Mediana: {reaction_times.median():.0f}ms')
            ax1.set_title('Distribución de Tiempos de Reacción')
            ax1.set_xlabel('Tiempo de Reacción (ms)')
            ax1.set_ylabel('Frecuencia')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Gráfica 2: Evolución temporal de tiempos de reacción
            session_reaction = self.session_data.groupby('session_file')['reaction_time_ms'].agg(['mean', 'std'])
            x_pos = range(len(session_reaction))
            
            ax2.errorbar(x_pos, session_reaction['mean'], yerr=session_reaction['std'], 
                        fmt='o-', linewidth=2, markersize=6, capsize=5)
            ax2.set_title('Evolución de Tiempos de Reacción')
            ax2.set_xlabel('Sesión')
            ax2.set_ylabel('Tiempo de Reacción (ms)')
            ax2.grid(True, alpha=0.3)
            
            # Agregar línea de tendencia
            if len(x_pos) > 2:
                z = np.polyfit(x_pos, session_reaction['mean'], 1)
                p = np.poly1d(z)
                ax2.plot(x_pos, p(x_pos), "r--", alpha=0.8, 
                        label=f'Tendencia: {z[0]:.1f}ms/sesión')
                ax2.legend()
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de tiempo de reacción: {e}")
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_coordination_tab(self):
        """Crear pestaña de análisis de coordinación ojo-mano"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🎯 Coordinación")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Análisis de Coordinación Ojo-Mano', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Correlación entre precisión espacial y temporal
            spatial = self.session_data['spatial_accuracy'].dropna()
            temporal = self.session_data['temporal_accuracy'].dropna()
            
            if len(spatial) > 0 and len(temporal) > 0:
                # Asegurar que ambas series tengan la misma longitud
                min_len = min(len(spatial), len(temporal))
                spatial = spatial.iloc[:min_len]
                temporal = temporal.iloc[:min_len]
                
                ax1.scatter(spatial, temporal, alpha=0.6, c='blue')
                
                # Línea de tendencia
                if len(spatial) > 1:
                    z = np.polyfit(spatial, temporal, 1)
                    p = np.poly1d(z)
                    ax1.plot(spatial, p(spatial), "r--", alpha=0.8)
                    
                    # Calcular correlación
                    correlation = np.corrcoef(spatial, temporal)[0, 1]
                    ax1.text(0.05, 0.95, f'r = {correlation:.3f}', 
                            transform=ax1.transAxes, fontsize=12, 
                            bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
                
                ax1.set_title('Correlación Precisión Espacial vs Temporal')
                ax1.set_xlabel('Precisión Espacial (%)')
                ax1.set_ylabel('Precisión Temporal (%)')
                ax1.grid(True, alpha=0.3)
            
            # Gráfica 2: Evolución del score por sesión
            session_scores = self.session_data.groupby('session_file')['score'].sum()
            ax2.bar(range(len(session_scores)), session_scores.values, color='gold', alpha=0.7)
            ax2.set_title('Puntuación Total por Sesión')
            ax2.set_xlabel('Sesión')
            ax2.set_ylabel('Puntuación')
            ax2.grid(True, alpha=0.3)
            
            # Gráfica 3: Análisis de combos
            combo_data = self.session_data['combo'].dropna()
            max_combos = self.session_data.groupby('session_file')['combo'].max()
            
            ax3.plot(range(len(max_combos)), max_combos.values, 'go-', linewidth=2, markersize=6)
            ax3.set_title('Máximo Combo por Sesión')
            ax3.set_xlabel('Sesión')
            ax3.set_ylabel('Máximo Combo')
            ax3.grid(True, alpha=0.3)
            
            # Gráfica 4: Progreso de dificultad
            difficulty_progress = self.session_data.groupby('session_file')['difficulty_level'].max()
            ax4.plot(range(len(difficulty_progress)), difficulty_progress.values, 'ro-', linewidth=2, markersize=6)
            ax4.set_title('Progreso de Nivel de Dificultad')
            ax4.set_xlabel('Sesión')
            ax4.set_ylabel('Nivel Máximo Alcanzado')
            ax4.grid(True, alpha=0.3)
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de coordinación: {e}")
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_performance_tab(self):
        """Crear pestaña de análisis de rendimiento general"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📈 Rendimiento")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Análisis de Rendimiento General', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Métricas consolidadas por sesión
            sessions = self.session_data['session_file'].unique()
            
            metrics = {
                'Precisión Espacial': [],
                'Precisión Temporal': [],
                'Tiempo Reacción': [],
                'Score Promedio': []
            }
            
            for session in sessions:
                session_data = self.session_data[self.session_data['session_file'] == session]
                
                metrics['Precisión Espacial'].append(session_data['spatial_accuracy'].mean())
                metrics['Precisión Temporal'].append(session_data['temporal_accuracy'].mean())
                metrics['Tiempo Reacción'].append(session_data['reaction_time_ms'].mean())
                metrics['Score Promedio'].append(session_data['score'].mean())
            
            # Normalizar métricas para comparación
            x = range(len(sessions))
            
            # Subplot 1: Precisiones
            ax1.plot(x, metrics['Precisión Espacial'], 'b-o', label='Precisión Espacial', linewidth=2)
            ax1.plot(x, metrics['Precisión Temporal'], 'g-s', label='Precisión Temporal', linewidth=2)
            ax1.set_title('Evolución de Precisiones')
            ax1.set_xlabel('Sesión')
            ax1.set_ylabel('Precisión (%)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Subplot 2: Interpretación automática
            if len(sessions) >= 3:
                # Calcular tendencias
                spatial_trend = np.polyfit(x, metrics['Precisión Espacial'], 1)[0]
                temporal_trend = np.polyfit(x, metrics['Precisión Temporal'], 1)[0]
                reaction_trend = np.polyfit(x, metrics['Tiempo Reacción'], 1)[0]
                
                # Generar interpretación
                interpretation = []
                
                if spatial_trend > 0.5:
                    interpretation.append("📈 MEJORA en precisión espacial")
                elif spatial_trend < -0.5:
                    interpretation.append("📉 Decline en precisión espacial")
                else:
                    interpretation.append("📊 Precisión espacial estable")
                
                if temporal_trend > 0.5:
                    interpretation.append("📈 MEJORA en timing")
                elif temporal_trend < -0.5:
                    interpretation.append("📉 Decline en timing")
                else:
                    interpretation.append("📊 Timing estable")
                
                if reaction_trend < -10:
                    interpretation.append("⚡ Mejora en tiempo de reacción")
                elif reaction_trend > 10:
                    interpretation.append("🐌 Aumento en tiempo de reacción")
                else:
                    interpretation.append("⏱️ Tiempo de reacción estable")
                
                # Mostrar interpretación
                interpretation_text = "\n".join(interpretation)
                ax2.text(0.1, 0.7, "INTERPRETACIÓN AUTOMÁTICA:", 
                        transform=ax2.transAxes, fontsize=14, fontweight='bold')
                ax2.text(0.1, 0.3, interpretation_text, 
                        transform=ax2.transAxes, fontsize=12)
                ax2.set_xlim(0, 1)
                ax2.set_ylim(0, 1)
                ax2.axis('off')
            else:
                ax2.text(0.5, 0.5, 'Necesitas al menos 3 sesiones\npara análisis de tendencias', 
                        ha='center', va='center', transform=ax2.transAxes, fontsize=12)
                ax2.axis('off')
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de rendimiento: {e}")
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = tk.Frame(parent, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón para exportar datos
        export_btn = tk.Button(
            button_frame,
            text="📊 Exportar Datos",
            command=self.export_data,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para generar reporte
        report_btn = tk.Button(
            button_frame,
            text="📋 Generar Reporte",
            command=self.generate_report,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para limpiar datos
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Limpiar Datos",
            command=self.clear_patient_data,
            bg="#e67e22",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para actualizar datos
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Actualizar",
            command=self.refresh_data,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para cerrar
        close_btn = tk.Button(
            button_frame,
            text="❌ Cerrar",
            command=self.close_window,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT)
    
    def export_data(self):
        """Exportar datos a Excel"""
        try:
            if not self.data_loaded:
                messagebox.showwarning("Sin Datos", "No hay datos para exportar")
                return
            
            filename = f"analisis_osu_{self.game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self.session_data.to_excel(filename, index=False)
            messagebox.showinfo("Exportado", f"Datos exportados a: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando datos: {e}")
    
    def generate_report(self):
        """Generar reporte textual"""
        try:
            if not self.data_loaded:
                messagebox.showwarning("Sin Datos", "No hay datos para generar reporte")
                return
            
            # Crear ventana de reporte
            report_window = tk.Toplevel(self.window)
            report_window.title("📋 Reporte Osu Cognitivo")
            report_window.geometry("600x400")
            
            # Generar contenido del reporte
            report_text = self.create_detailed_report()
            
            # Widget de texto para mostrar el reporte
            text_widget = tk.Text(report_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', report_text)
            text_widget.config(state=tk.DISABLED)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(report_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def create_detailed_report(self) -> str:
        """Crear reporte detallado en texto"""
        if not self.data_loaded:
            return "No hay datos disponibles para generar el reporte."
        
        total_sessions = len(self.session_data['session_file'].unique())
        total_hits = len(self.session_data)
        avg_spatial = self.session_data['spatial_accuracy'].mean()
        avg_temporal = self.session_data['temporal_accuracy'].mean()
        avg_reaction = self.session_data['reaction_time_ms'].mean()
        total_score = self.session_data['score'].sum()
        
        perfect_hits = len(self.session_data[self.session_data['hit_result'] == 'PERFECT'])
        good_hits = len(self.session_data[self.session_data['hit_result'] == 'GOOD'])
        normal_hits = len(self.session_data[self.session_data['hit_result'] == 'NORMAL'])
        miss_hits = len(self.session_data[self.session_data['hit_result'] == 'MISS'])
        
        report = f"""
🎯 REPORTE DE EVALUACIÓN COGNITIVA OSU!
{'=' * 50}

📅 Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🎮 Juego: Osu! Rhythm Game

📈 RESUMEN EJECUTIVO:
• Total de sesiones analizadas: {total_sessions}
• Total de hits registrados: {total_hits}
• Precisión espacial promedio: {avg_spatial:.1f}%
• Precisión temporal promedio: {avg_temporal:.1f}%
• Tiempo de reacción promedio: {avg_reaction:.1f}ms
• Puntuación total acumulada: {total_score:,}

🧠 ANÁLISIS COGNITIVO:
• Coordinación ojo-mano: {'EXCELENTE' if avg_spatial > 85 else 'BUENA' if avg_spatial > 70 else 'NECESITA MEJORA'}
• Precisión temporal: {'EXCELENTE' if avg_temporal > 85 else 'BUENA' if avg_temporal > 70 else 'NECESITA MEJORA'}
• Velocidad de reacción: {'RÁPIDA' if avg_reaction < 400 else 'MODERADA' if avg_reaction < 600 else 'LENTA'}

🎯 DISTRIBUCIÓN DE HITS:
• Perfect: {perfect_hits} ({(perfect_hits/total_hits)*100:.1f}%)
• Good: {good_hits} ({(good_hits/total_hits)*100:.1f}%)
• Normal: {normal_hits} ({(normal_hits/total_hits)*100:.1f}%)
• Miss: {miss_hits} ({(miss_hits/total_hits)*100:.1f}%)

💡 RECOMENDACIONES:
"""
        
        if avg_spatial > 85:
            report += "• Excelente precisión espacial. Mantener nivel de práctica actual.\n"
        elif avg_spatial > 70:
            report += "• Buena precisión espacial con espacio para mejora. Enfocar en ejercicios de puntería.\n"
        else:
            report += "• Precisión espacial que requiere atención. Practicar movimientos más lentos y precisos.\n"
        
        if avg_temporal > 85:
            report += "• Excelente timing. Mantener ritmo de práctica.\n"
        elif avg_temporal > 70:
            report += "• Buen timing con margen de mejora. Practicar con metrónomo.\n"
        else:
            report += "• Timing que necesita trabajo. Enfocarse en ejercicios de ritmo.\n"
        
        if avg_reaction < 400:
            report += "• Tiempo de reacción excelente. Considerar incrementar dificultad.\n"
        elif avg_reaction > 600:
            report += "• Tiempo de reacción lento. Practicar ejercicios de velocidad.\n"
        
        report += "\n🔬 DATOS TÉCNICOS:\n"
        report += f"• Hits por sesión promedio: {total_hits/total_sessions:.1f}\n"
        report += f"• Rango de precisión espacial: {self.session_data['spatial_accuracy'].min():.1f}% - {self.session_data['spatial_accuracy'].max():.1f}%\n"
        report += f"• Rango de precisión temporal: {self.session_data['temporal_accuracy'].min():.1f}% - {self.session_data['temporal_accuracy'].max():.1f}%\n"
        
        return report
    
    def clear_patient_data(self):
        """Limpiar todos los datos del paciente actual"""
        try:
            if not self.data_loaded or len(self.session_data) == 0:
                messagebox.showinfo("Sin Datos", "No hay datos para limpiar")
                return
            
            # Confirmar acción
            result = messagebox.askyesno(
                "Confirmar Limpieza",
                f"¿Estás seguro de que quieres eliminar TODOS los datos del paciente?\n\n"
                f"Se eliminarán:\n"
                f"• {len(self.session_data['session_file'].unique())} sesiones\n"
                f"• {len(self.session_data)} hits registrados\n\n"
                f"⚠️ Esta acción NO se puede deshacer"
            )
            
            if result:
                # Eliminar archivos CSV
                sessions_dir = f"data/cognitive/{self.game_id}/sessions"
                csv_files = glob.glob(os.path.join(sessions_dir, "*.csv"))
                
                deleted_count = 0
                for csv_file in csv_files:
                    try:
                        os.remove(csv_file)
                        deleted_count += 1
                        print(f"🗑️ Eliminado: {os.path.basename(csv_file)}")
                    except Exception as e:
                        print(f"❌ Error eliminando {csv_file}: {e}")
                
                # Limpiar datos en memoria
                self.session_data = []
                self.data_loaded = False
                
                # Mostrar resultado
                messagebox.showinfo(
                    "Datos Eliminados",
                    f"✅ Se eliminaron {deleted_count} archivos de sesión\n\n"
                    f"El paciente puede comenzar con datos limpios.\n"
                    f"Las nuevas sesiones se guardarán automáticamente."
                )
                
                # Actualizar interfaz
                self.refresh_data()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error limpiando datos: {e}")
    
    def refresh_data(self):
        """Actualizar datos y regenerar gráficas"""
        try:
            self.session_data = []
            self.data_loaded = False
            self.load_cognitive_data()
            
            # Cerrar ventana actual y recrear
            self.window.destroy()
            self.__init__(self.parent, self.game_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando datos: {e}")
    
    def close_window(self):
        """Cerrar ventana"""
        try:
            plt.close('all')  # Cerrar todas las figuras de matplotlib
            self.window.destroy()
        except:
            pass
    
    def show(self):
        """Mostrar la ventana"""
        if self.window:
            self.window.focus_set()
            self.window.lift()


def open_osu_cognitive_analytics(parent_window, game_id: str = "osu_rhythm"):
    """Función para abrir la ventana de análisis cognitivo de Osu"""
    try:
        analytics_window = OsuCognitiveAnalyticsWindow(parent_window, game_id)
        analytics_window.show()
        return analytics_window
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el análisis cognitivo de Osu: {e}")
        return None 