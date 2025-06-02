"""
Ventana de Análisis Cognitivo - Gráficas de Evaluación Neurocognitiva
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


class CognitiveAnalyticsWindow:
    """Ventana especializada para mostrar análisis cognitivos con gráficas"""
    
    def __init__(self, parent_window, game_id: str = "piano_digital"):
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
        self.window.title(f"📈 Análisis Neurocognitivo - {self.game_id.title()}")
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
            # Buscar archivos de sesiones - CORREGIDO: usar piano_digital
            sessions_dir = f"data/cognitive/{self.game_id}/sessions"
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir, exist_ok=True)
                return
            
            # Cargar todos los archivos CSV
            csv_files = glob.glob(os.path.join(sessions_dir, "*.csv"))
            
            if not csv_files:
                print(f"⚠️ No se encontraron datos de sesiones en {sessions_dir}")
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
                print(f"✅ Cargados {len(all_sessions)} archivos con {len(self.session_data)} registros")
            
        except Exception as e:
            print(f"❌ Error cargando datos cognitivos: {e}")
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
            text="📊 ANÁLISIS NEUROCOGNITIVO",
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
        
        # Notebook para las pestañas de gráficas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Crear pestañas con diferentes análisis
        self.create_performance_tab()
        self.create_reaction_time_tab()
        self.create_error_analysis_tab()
        self.create_progress_tab()
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def show_no_data_message(self, parent):
        """Mostrar mensaje cuando no hay datos"""
        no_data_frame = tk.Frame(parent, bg="#f0f0f0")
        no_data_frame.pack(expand=True)
        
        message_label = tk.Label(
            no_data_frame,
            text="📊 No se encontraron datos de sesiones\n\n"
                 "Para ver análisis cognitivos:\n"
                 "1. Ejecuta algunas sesiones del Piano Simon\n"
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
        total_events = len(self.session_data)
        date_range = f"{self.session_data['session_date'].min().strftime('%d/%m/%Y')} - {self.session_data['session_date'].max().strftime('%d/%m/%Y')}"
        
        info_text = f"📋 Sesiones: {total_sessions} | 📊 Eventos: {total_events} | 📅 Período: {date_range}"
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            pady=10
        )
        info_label.pack()
    
    def create_performance_tab(self):
        """Crear pestaña de análisis de rendimiento"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🎯 Rendimiento")
        
        # Crear figura de matplotlib
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Análisis de Rendimiento Cognitivo', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Progreso de nivel por sesión
            if 'player_level' in self.session_data.columns:
                session_levels = self.session_data.groupby('session_file')['player_level'].max()
                ax1.plot(range(len(session_levels)), session_levels.values, 'bo-', linewidth=2, markersize=6)
                ax1.set_title('Progreso de Nivel por Sesión')
                ax1.set_xlabel('Sesión')
                ax1.set_ylabel('Nivel Máximo Alcanzado')
                ax1.grid(True, alpha=0.3)
            
            # Gráfica 2: Distribución de eventos por tipo
            if 'event_type' in self.session_data.columns:
                event_counts = self.session_data['event_type'].value_counts().head(8)
                colors = plt.cm.Set3(np.linspace(0, 1, len(event_counts)))
                ax2.pie(event_counts.values, labels=event_counts.index, autopct='%1.1f%%', colors=colors)
                ax2.set_title('Distribución de Tipos de Eventos')
            
            # Gráfica 3: Tendencia de errores
            if 'level' in self.session_data.columns:
                errors_by_session = self.session_data[self.session_data['level'] == 'ERROR'].groupby('session_file').size()
                if len(errors_by_session) > 0:
                    ax3.bar(range(len(errors_by_session)), errors_by_session.values, color='lightcoral', alpha=0.7)
                    ax3.set_title('Errores por Sesión')
                    ax3.set_xlabel('Sesión')
                    ax3.set_ylabel('Número de Errores')
                else:
                    ax3.text(0.5, 0.5, 'No se encontraron errores', ha='center', va='center', transform=ax3.transAxes)
                    ax3.set_title('Análisis de Errores')
            
            # Gráfica 4: Tiempo de sesión
            if 'session_date' in self.session_data.columns:
                session_durations = self.session_data.groupby('session_file')['session_date'].agg(['min', 'max'])
                durations = (session_durations['max'] - session_durations['min']).dt.total_seconds() / 60
                ax4.hist(durations.dropna(), bins=10, color='lightblue', alpha=0.7, edgecolor='black')
                ax4.set_title('Distribución de Duración de Sesiones')
                ax4.set_xlabel('Duración (minutos)')
                ax4.set_ylabel('Frecuencia')
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de rendimiento: {e}")
            ax1.text(0.5, 0.5, f'Error generando gráficas:\n{e}', ha='center', va='center', transform=ax1.transAxes)
        
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
            # Simular datos de tiempo de reacción (en un juego real vendrían de los logs)
            if 'timestamp' in self.session_data.columns:
                # Calcular tiempos entre eventos como proxy de tiempo de reacción
                self.session_data['timestamp'] = pd.to_datetime(self.session_data['timestamp'])
                reaction_times = []
                
                for session in self.session_data['session_file'].unique():
                    session_data = self.session_data[self.session_data['session_file'] == session].sort_values('timestamp')
                    if len(session_data) > 1:
                        time_diffs = session_data['timestamp'].diff().dt.total_seconds()
                        # Filtrar tiempos razonables (entre 0.1 y 10 segundos)
                        valid_times = time_diffs[(time_diffs > 0.1) & (time_diffs < 10)]
                        reaction_times.extend(valid_times.dropna().tolist())
                
                if reaction_times:
                    # Gráfica 1: Distribución de tiempos de reacción
                    ax1.hist(reaction_times, bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
                    ax1.set_title('Distribución de Tiempos de Reacción')
                    ax1.set_xlabel('Tiempo (segundos)')
                    ax1.set_ylabel('Frecuencia')
                    ax1.axvline(np.mean(reaction_times), color='red', linestyle='--', label=f'Media: {np.mean(reaction_times):.2f}s')
                    ax1.legend()
                    
                    # Gráfica 2: Evolución de tiempos por sesión
                    session_means = []
                    session_labels = []
                    for i, session in enumerate(self.session_data['session_file'].unique()):
                        session_data = self.session_data[self.session_data['session_file'] == session]
                        if len(session_data) > 1:
                            time_diffs = session_data.sort_values('timestamp')['timestamp'].diff().dt.total_seconds()
                            valid_times = time_diffs[(time_diffs > 0.1) & (time_diffs < 10)]
                            if len(valid_times) > 0:
                                session_means.append(valid_times.mean())
                                session_labels.append(f'S{i+1}')
                    
                    if session_means:
                        ax2.plot(range(len(session_means)), session_means, 'ro-', linewidth=2, markersize=6)
                        ax2.set_title('Evolución del Tiempo de Reacción Promedio')
                        ax2.set_xlabel('Sesión')
                        ax2.set_ylabel('Tiempo Promedio (segundos)')
                        ax2.set_xticks(range(len(session_labels)))
                        ax2.set_xticklabels(session_labels)
                        ax2.grid(True, alpha=0.3)
                else:
                    ax1.text(0.5, 0.5, 'Datos insuficientes\npara calcular tiempos', ha='center', va='center', transform=ax1.transAxes)
                    ax2.text(0.5, 0.5, 'Datos insuficientes\npara análisis temporal', ha='center', va='center', transform=ax2.transAxes)
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de tiempo de reacción: {e}")
            ax1.text(0.5, 0.5, f'Error:\n{e}', ha='center', va='center', transform=ax1.transAxes)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_error_analysis_tab(self):
        """Crear pestaña de análisis de errores"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="❌ Análisis de Errores")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Análisis Detallado de Errores', fontsize=14, fontweight='bold')
        
        try:
            error_data = self.session_data[self.session_data['level'] == 'ERROR'] if 'level' in self.session_data.columns else pd.DataFrame()
            
            if len(error_data) > 0:
                # Gráfica 1: Tipos de errores
                error_types = error_data['event_type'].value_counts().head(10)
                ax1.barh(range(len(error_types)), error_types.values, color='lightcoral')
                ax1.set_yticks(range(len(error_types)))
                ax1.set_yticklabels(error_types.index)
                ax1.set_title('Tipos de Errores Más Frecuentes')
                ax1.set_xlabel('Frecuencia')
                
                # Gráfica 2: Errores por sesión
                errors_by_session = error_data.groupby('session_file').size()
                ax2.plot(range(len(errors_by_session)), errors_by_session.values, 'ro-', linewidth=2)
                ax2.set_title('Evolución de Errores por Sesión')
                ax2.set_xlabel('Sesión')
                ax2.set_ylabel('Número de Errores')
                ax2.grid(True, alpha=0.3)
                
                # Gráfica 3: Patrón temporal de errores
                if 'timestamp' in error_data.columns:
                    error_data['hour'] = pd.to_datetime(error_data['timestamp']).dt.hour
                    errors_by_hour = error_data['hour'].value_counts().sort_index()
                    ax3.bar(errors_by_hour.index, errors_by_hour.values, color='orange', alpha=0.7)
                    ax3.set_title('Errores por Hora del Día')
                    ax3.set_xlabel('Hora')
                    ax3.set_ylabel('Número de Errores')
                
                # Gráfica 4: Distribución de severidad
                ax4.pie([len(error_data), len(self.session_data) - len(error_data)], 
                       labels=['Errores', 'Eventos Exitosos'], 
                       autopct='%1.1f%%', 
                       colors=['lightcoral', 'lightgreen'])
                ax4.set_title('Proporción de Errores vs Éxitos')
            else:
                for ax in [ax1, ax2, ax3, ax4]:
                    ax.text(0.5, 0.5, '¡Excelente!\nNo se encontraron errores', 
                           ha='center', va='center', transform=ax.transAxes, 
                           fontsize=12, color='green', fontweight='bold')
                    ax.set_title('Sin Errores Detectados')
        
        except Exception as e:
            print(f"⚠️ Error creando gráficas de errores: {e}")
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_progress_tab(self):
        """Crear pestaña de análisis de progreso"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📈 Progreso")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('Análisis de Progreso Cognitivo', fontsize=14, fontweight='bold')
        
        try:
            # Gráfica 1: Evolución temporal de todas las métricas
            sessions = self.session_data['session_file'].unique()
            
            metrics = {
                'Eventos por Sesión': [],
                'Errores por Sesión': [],
                'Eficiencia': []  # (eventos exitosos / total eventos) * 100
            }
            
            for session in sessions:
                session_data = self.session_data[self.session_data['session_file'] == session]
                total_events = len(session_data)
                error_events = len(session_data[session_data['level'] == 'ERROR']) if 'level' in session_data.columns else 0
                efficiency = ((total_events - error_events) / total_events * 100) if total_events > 0 else 0
                
                metrics['Eventos por Sesión'].append(total_events)
                metrics['Errores por Sesión'].append(error_events)
                metrics['Eficiencia'].append(efficiency)
            
            x = range(len(sessions))
            
            # Normalizar los datos para mostrar tendencias
            ax1_twin = ax1.twinx()
            
            line1 = ax1.plot(x, metrics['Eventos por Sesión'], 'b-o', label='Eventos por Sesión', linewidth=2)
            line2 = ax1.plot(x, metrics['Errores por Sesión'], 'r-s', label='Errores por Sesión', linewidth=2)
            line3 = ax1_twin.plot(x, metrics['Eficiencia'], 'g-^', label='Eficiencia (%)', linewidth=2)
            
            ax1.set_xlabel('Sesión')
            ax1.set_ylabel('Número de Eventos', color='b')
            ax1_twin.set_ylabel('Eficiencia (%)', color='g')
            ax1.set_title('Evolución de Métricas por Sesión')
            ax1.grid(True, alpha=0.3)
            
            # Combinar leyendas
            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
            
            # Gráfica 2: Análisis de tendencias
            if len(sessions) > 2:
                # Calcular tendencias lineales
                efficiency_trend = np.polyfit(x, metrics['Eficiencia'], 1)
                events_trend = np.polyfit(x, metrics['Eventos por Sesión'], 1)
                
                ax2.scatter(x, metrics['Eficiencia'], color='green', s=50, alpha=0.7, label='Eficiencia Real')
                ax2.plot(x, np.poly1d(efficiency_trend)(x), 'g--', linewidth=2, label=f'Tendencia Eficiencia (pendiente: {efficiency_trend[0]:.2f})')
                
                ax2_twin = ax2.twinx()
                ax2_twin.scatter(x, metrics['Eventos por Sesión'], color='blue', s=50, alpha=0.7, label='Eventos Real')
                ax2_twin.plot(x, np.poly1d(events_trend)(x), 'b--', linewidth=2, label=f'Tendencia Eventos (pendiente: {events_trend[0]:.2f})')
                
                ax2.set_xlabel('Sesión')
                ax2.set_ylabel('Eficiencia (%)', color='g')
                ax2_twin.set_ylabel('Número de Eventos', color='b')
                ax2.set_title('Análisis de Tendencias de Mejora')
                ax2.grid(True, alpha=0.3)
                
                # Mostrar interpretación
                if efficiency_trend[0] > 0:
                    interpretation = "📈 MEJORA POSITIVA"
                    color = 'green'
                elif efficiency_trend[0] < -0.5:
                    interpretation = "📉 NECESITA ATENCIÓN"
                    color = 'red'
                else:
                    interpretation = "📊 ESTABLE"
                    color = 'orange'
                
                ax2.text(0.02, 0.98, f"Interpretación: {interpretation}", 
                        transform=ax2.transAxes, fontsize=12, fontweight='bold', 
                        color=color, verticalalignment='top')
            
        except Exception as e:
            print(f"⚠️ Error creando gráficas de progreso: {e}")
        
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
        
        # NUEVO: Botón para limpiar datos del paciente
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
            
            filename = f"analisis_cognitivo_{self.game_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self.session_data.to_excel(filename, index=False)
            messagebox.showinfo("Exportado", f"Datos exportados a: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando datos: {e}")
    
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
                f"• {len(self.session_data)} eventos registrados\n\n"
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
    
    def generate_report(self):
        """Generar reporte textual"""
        try:
            if not self.data_loaded:
                messagebox.showwarning("Sin Datos", "No hay datos para generar reporte")
                return
            
            # Crear ventana de reporte
            report_window = tk.Toplevel(self.window)
            report_window.title("📋 Reporte Neurocognitivo")
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
        total_events = len(self.session_data)
        error_count = len(self.session_data[self.session_data['level'] == 'ERROR']) if 'level' in self.session_data.columns else 0
        efficiency = ((total_events - error_count) / total_events * 100) if total_events > 0 else 0
        
        report = f"""
📊 REPORTE DE EVALUACIÓN NEUROCOGNITIVA
{'=' * 50}

📅 Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🎮 Juego: {self.game_id.title()}

📈 RESUMEN EJECUTIVO:
• Total de sesiones analizadas: {total_sessions}
• Total de eventos registrados: {total_events}
• Errores detectados: {error_count}
• Eficiencia general: {efficiency:.1f}%

🧠 ANÁLISIS COGNITIVO:
• Capacidad de atención: {'EXCELENTE' if efficiency > 85 else 'BUENA' if efficiency > 70 else 'NECESITA MEJORA'}
• Velocidad de procesamiento: {'RÁPIDA' if total_events/total_sessions > 50 else 'MODERADA' if total_events/total_sessions > 20 else 'LENTA'}
• Control de errores: {'EXCELENTE' if error_count/total_events < 0.1 else 'BUENO' if error_count/total_events < 0.2 else 'MEJORABLE'}

💡 RECOMENDACIONES:
"""
        
        if efficiency > 85:
            report += "• Excelente rendimiento cognitivo. Mantener nivel de práctica actual.\n"
        elif efficiency > 70:
            report += "• Buen rendimiento con espacio para mejora. Incrementar frecuencia de práctica.\n"
        else:
            report += "• Rendimiento que requiere atención. Considerar sesiones más frecuentes y estructuradas.\n"
        
        if error_count/total_events > 0.2:
            report += "• Alta tasa de errores. Enfocar en ejercicios de precisión y concentración.\n"
        
        report += "\n🔬 DATOS TÉCNICOS:\n"
        report += f"• Promedio de eventos por sesión: {total_events/total_sessions:.1f}\n"
        report += f"• Tasa de error: {(error_count/total_events)*100:.1f}%\n"
        
        return report
    
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


def open_cognitive_analytics(parent_window, game_id: str = "piano_digital"):
    """Función para abrir la ventana de análisis cognitivo"""
    try:
        analytics_window = CognitiveAnalyticsWindow(parent_window, game_id)
        analytics_window.show()
        return analytics_window
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el análisis cognitivo: {e}")
        return None 