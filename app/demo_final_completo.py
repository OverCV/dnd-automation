#!/usr/bin/env python3
"""
DEMOSTRACIÓN FINAL COMPLETA - Sistema Cognitivo
Todo el sistema funcionando de extremo a extremo
"""

import sys
import os
import random
import time

# Añadir path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generar_datos_de_prueba():
    """Generar datos de prueba realistas"""
    print("🧠 GENERANDO DATOS DE PRUEBA COGNITIVOS")
    print("=" * 50)
    
    from core.cognitive import SessionManager
    
    # Generar 3 pacientes con diferentes perfiles cognitivos
    patients_data = [
        {"id": "PACIENTE_SANO", "degradation": 0.0, "base_accuracy": 0.92},
        {"id": "PACIENTE_LEVE", "degradation": 0.3, "base_accuracy": 0.78},
        {"id": "PACIENTE_MODERADO", "degradation": 0.6, "base_accuracy": 0.65}
    ]
    
    session_files = []
    
    for patient in patients_data:
        print(f"\n👤 Generando datos para: {patient['id']}")
        
        # Crear sesión
        session_manager = SessionManager()
        logger = session_manager.start_session("piano_simon", patient['id'])
        
        # Generar 20 eventos con patrón específico
        for i in range(20):
            level = min(i // 4 + 1, 5)
            sequence_length = level + 2
            
            # Calcular fatiga y degradación
            fatigue_factor = 1.0 - (i / 25)  # Fatiga gradual
            degradation_factor = 1.0 - patient['degradation']
            
            # Probabilidad de éxito considerando todos los factores
            success_prob = patient['base_accuracy'] * fatigue_factor * degradation_factor
            
            # Generar secuencia
            sequence_shown = [random.randint(0, 7) for _ in range(sequence_length)]
            
            # Respuesta del paciente
            if random.random() < success_prob:
                sequence_input = sequence_shown.copy()
                base_time = 1200 + (level * 200)
                response_time = base_time + random.randint(-200, 400) + (i * 30)  # Tiempo aumenta con fatiga
            else:
                # Error - cambiar uno o más elementos
                sequence_input = sequence_shown.copy()
                if len(sequence_input) > 1:
                    error_count = random.choice([1, 2]) if level > 3 else 1
                    for _ in range(error_count):
                        error_pos = random.randint(0, len(sequence_input)-1)
                        sequence_input[error_pos] = random.randint(0, 7)
                
                base_time = 1800 + (level * 300)
                response_time = base_time + random.randint(0, 1000) + (i * 50)
            
            presentation_time = sequence_length * 750
            
            # Log del evento
            logger.log_piano_event(
                level=level,
                sequence_shown=sequence_shown,
                sequence_input=sequence_input,
                presentation_time=presentation_time,
                response_time=response_time
            )
            
            is_correct = sequence_shown == sequence_input
            print(f"   └─ Evento {i+1:2d}: Nivel {level}, {'✅' if is_correct else '❌'}, {response_time}ms")
        
        # Finalizar sesión
        session_manager.end_session()
        session_info = session_manager.list_session_files()[0]  # Más reciente
        session_files.append(session_manager.get_session_info(session_info))
        
        print(f"✅ {patient['id']}: 20 eventos generados")
    
    return session_files

def analizar_datos_generados(session_files):
    """Analizar los datos generados con métricas"""
    print("\n📊 ANÁLISIS COGNITIVO AUTOMÁTICO")
    print("=" * 50)
    
    from core.cognitive import MetricsCalculator
    
    for session_info in session_files:
        print(f"\n🧑‍⚕️ ANALIZANDO: {session_info['patient_id']}")
        print("-" * 40)
        
        calculator = MetricsCalculator(session_info['filepath'])
        report = calculator.generate_summary_report()
        print(report)

def generar_todas_las_graficas(session_files):
    """Generar todas las gráficas posibles"""
    print("\n📈 GENERACIÓN DE GRÁFICAS COGNITIVAS")
    print("=" * 50)
    
    from core.cognitive import CognitiveVisualAnalyzer
    
    analyzer = CognitiveVisualAnalyzer()
    
    # Dashboard individual para cada paciente
    for session_info in session_files:
        patient_id = session_info['patient_id']
        print(f"\n🎨 Generando dashboard para: {patient_id}")
        
        result = analyzer.create_piano_performance_dashboard(session_info['filepath'])
        print(f"   {result}")
        
        # Análisis de fatiga individual
        result_fatigue = analyzer.create_fatigue_analysis(session_info['filepath'])
        print(f"   {result_fatigue.split(chr(10))[0]}")  # Solo primera línea
    
    # Gráfica de comparación entre todos los pacientes
    print(f"\n🔄 Generando comparación entre {len(session_files)} pacientes...")
    
    file_paths = [info['filepath'] for info in session_files]
    patient_labels = [info['patient_id'] for info in session_files]
    
    result_comparison = analyzer.create_comparison_chart(file_paths, patient_labels)
    print(f"   {result_comparison}")

def mostrar_utilidades_limpieza():
    """Mostrar utilidades de limpieza"""
    print("\n🗑️ UTILIDADES DE LIMPIEZA DE DATOS")
    print("=" * 50)
    
    from core.cognitive import CognitiveDataCleaner
    
    cleaner = CognitiveDataCleaner()
    
    # Mostrar resumen completo
    summary = cleaner.get_storage_summary()
    print(summary)
    
    # Mostrar menú de limpieza selectiva
    menu = cleaner.selective_delete_menu()
    print("\n" + menu)

def main():
    """Demostración completa del sistema"""
    print("🚀 DEMOSTRACIÓN FINAL COMPLETA - SISTEMA COGNITIVO")
    print("=" * 60)
    print()
    print("🎯 Objetivos de la demostración:")
    print("   • Generar datos cognitivos realistas")
    print("   • Análisis automático de métricas")
    print("   • Gráficas profesionales de rendimiento")
    print("   • Comparaciones entre pacientes")
    print("   • Utilidades de gestión de datos")
    print()
    
    try:
        # PASO 1: Generar datos de prueba
        print("🔄 PASO 1: Generación de datos de prueba")
        session_files = generar_datos_de_prueba()
        
        input("\n⏸️  Presione Enter para continuar al análisis...")
        
        # PASO 2: Análisis de métricas
        print("\n🔄 PASO 2: Análisis cognitivo automático")
        analizar_datos_generados(session_files)
        
        input("\n⏸️  Presione Enter para continuar a las gráficas...")
        
        # PASO 3: Generar gráficas
        print("\n🔄 PASO 3: Generación de gráficas")
        generar_todas_las_graficas(session_files)
        
        input("\n⏸️  Presione Enter para ver utilidades de limpieza...")
        
        # PASO 4: Mostrar utilidades
        print("\n🔄 PASO 4: Utilidades de gestión")
        mostrar_utilidades_limpieza()
        
        # RESUMEN FINAL
        print("\n" + "=" * 60)
        print("🎉 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print()
        print("✅ FUNCIONALIDADES DEMOSTRADAS:")
        print("   • Logging cognitivo automático con CSV")
        print("   • Análisis de métricas neurodegenerativas")
        print("   • Dashboard visual con 4 gráficas simultáneas")
        print("   • Análisis específico de fatiga cognitiva")
        print("   • Comparación entre múltiples pacientes")
        print("   • Gestión y limpieza de archivos de datos")
        print()
        print("📁 ARCHIVOS GENERADOS:")
        print("   • Datos CSV: data/cognitive/*.csv")
        print("   • Dashboards: data/cognitive/dashboard_*.png")
        print("   • Análisis fatiga: data/cognitive/fatiga_analysis_*.png")
        print("   • Comparaciones: data/cognitive/comparison_*.png")
        print()
        print("🧠 APLICACIÓN MÉDICA:")
        print("   • Sistema listo para evaluación neurodegenerativa")
        print("   • Métricas objetivas para diagnóstico")
        print("   • Seguimiento de progresión de pacientes")
        print("   • Reportes visuales para equipos médicos")
        print()
        print("🚀 El sistema está completamente funcional!")
        
    except Exception as e:
        print(f"\n❌ Error en la demostración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 