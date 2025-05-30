#!/usr/bin/env python3
"""
DEMO PARA MÉDICOS - Sistema de Evaluación Cognitiva
Súper simple de usar - Solo seguir instrucciones
"""

import sys
import os
import time
from datetime import datetime

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def mostrar_menu_principal():
    """Menú principal súper simple"""
    print("\n" + "=" * 60)
    print("🧠 SISTEMA DE EVALUACIÓN COGNITIVA - DEMO MÉDICO")
    print("=" * 60)
    print()
    print("📋 OPCIONES DISPONIBLES:")
    print("  1. 🎹 Ejecutar evaluación Piano-Simon (RECOMENDADO)")
    print("  2. 📊 Analizar sesión anterior")
    print("  3. 📈 Generar gráficas de rendimiento")
    print("  4. 🔄 Comparar múltiples sesiones")
    print("  5. 🧠 Análisis de fatiga cognitiva")
    print("  6. 📁 Ver historial de pacientes")
    print("  7. 🗑️  Limpiar archivos de datos")
    print("  8. ℹ️  Información del sistema")
    print("  9. 🚪 Salir")
    print()

def ejecutar_evaluacion_piano():
    """Ejecutar evaluación cognitiva con Piano-Simon"""
    print("\n🎹 EVALUACIÓN COGNITIVA - PIANO SIMON")
    print("=" * 50)
    
    # Solicitar datos del paciente
    patient_id = input("📝 ID del paciente (ej: P001): ").strip()
    if not patient_id:
        patient_id = f"PACIENTE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n🧠 Iniciando evaluación para: {patient_id}")
    print("⚠️  IMPORTANTE: Esta es una SIMULACIÓN sin hardware real")
    print("   En el sistema real, el paciente interactuaría con el piano físico")
    
    try:
        from games.piano.game_logic import PianoGameLogic
        
        # Crear game logic con logging habilitado
        game_logic = PianoGameLogic(
            enable_cognitive_logging=True,
            patient_id=patient_id
        )
        
        print("\n✅ Sistema cognitivo iniciado")
        
        # Resetear y simular sesión
        game_logic.reset_game()
        print("🔄 Juego reiniciado")
        
        # Simular secuencia de evaluación
        print("\n🎯 SIMULANDO EVALUACIÓN COGNITIVA...")
        print("   (En el sistema real, el paciente jugará Piano-Simon)")
        
        # Simular algunos eventos cognitivos
        simular_sesion_cognitiva(game_logic, patient_id)
        
        print("\n✅ Evaluación completada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en evaluación: {e}")
        return False

def simular_sesion_cognitiva(game_logic, patient_id):
    """Simular una sesión cognitiva básica"""
    
    # Simular datos de diferentes niveles de habilidad cognitiva
    print("\n📊 Simulando datos cognitivos...")
    
    import random
    logger = game_logic.current_logger
    
    if not logger:
        print("❌ Logger no disponible")
        return
    
    # Simular 15 intentos con diferentes patrones (más datos para mejores gráficas)
    for i in range(15):
        nivel = min(i // 3 + 1, 5)  # Niveles 1-5
        longitud_secuencia = nivel + 2
        
        # Generar secuencia mostrada
        secuencia_mostrada = [random.randint(0, 7) for _ in range(longitud_secuencia)]
        
        # Simular degradación por fatiga (los últimos intentos son peores)
        fatigue_factor = 1.0 - (i / 20)  # Degradación gradual
        success_rate = 0.85 * fatigue_factor  # Base 85% que baja por fatiga
        
        # Simular respuesta del paciente
        if random.random() < success_rate:
            secuencia_respuesta = secuencia_mostrada.copy()
            tiempo_respuesta = random.randint(1200, 3500) + (i * 50)  # Tiempo aumenta con fatiga
        else:
            # Introducir error
            secuencia_respuesta = secuencia_mostrada.copy()
            if len(secuencia_respuesta) > 1:
                error_pos = random.randint(0, len(secuencia_respuesta)-1)
                secuencia_respuesta[error_pos] = random.randint(0, 7)
            tiempo_respuesta = random.randint(2000, 5000) + (i * 100)  # Más lento en errores
        
        # Tiempo de presentación
        tiempo_presentacion = longitud_secuencia * 750
        
        # Log del evento
        logger.log_piano_event(
            level=nivel,
            sequence_shown=secuencia_mostrada,
            sequence_input=secuencia_respuesta,
            presentation_time=tiempo_presentacion,
            response_time=tiempo_respuesta
        )
        
        es_correcto = secuencia_mostrada == secuencia_respuesta
        print(f"   └─ Intento {i+1:2d}: Nivel {nivel}, {'✅' if es_correcto else '❌'}, {tiempo_respuesta}ms")
        time.sleep(0.05)  # Pausa visual más rápida
    
    print("\n✅ Simulación completada - Patrón de fatiga incluido")

def analizar_sesion_anterior():
    """Analizar una sesión anterior"""
    print("\n📊 ANÁLISIS DE SESIÓN ANTERIOR")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager, MetricsCalculator
        
        session_manager = SessionManager()
        archivos = session_manager.list_session_files()
        
        if not archivos:
            print("❌ No hay sesiones anteriores disponibles")
            return
        
        print("📁 Sesiones disponibles:")
        for i, archivo in enumerate(archivos[:10]):  # Mostrar solo las 10 más recientes
            info = session_manager.get_session_info(archivo)
            print(f"  {i+1}. {info.get('patient_id', 'Unknown')} - {info.get('game_type', 'Unknown')} ({info.get('event_count', 0)} eventos)")
        
        try:
            seleccion = int(input("\n📋 Seleccionar sesión (número): ")) - 1
            if 0 <= seleccion < len(archivos):
                archivo_seleccionado = archivos[seleccion]
                info = session_manager.get_session_info(archivo_seleccionado)
                
                print(f"\n📈 Analizando sesión: {info['patient_id']}")
                
                # Crear calculador de métricas
                calculator = MetricsCalculator(info['filepath'])
                reporte = calculator.generate_summary_report()
                
                print("\n" + "="*60)
                print(reporte)
                print("="*60)
                
            else:
                print("❌ Selección inválida")
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
        
    except Exception as e:
        print(f"❌ Error analizando sesión: {e}")

def ver_historial_pacientes():
    """Ver historial simplificado"""
    print("\n📁 HISTORIAL DE PACIENTES")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager
        
        session_manager = SessionManager()
        archivos = session_manager.list_session_files()
        
        if not archivos:
            print("❌ No hay historial disponible")
            return
        
        # Agrupar por paciente
        pacientes = {}
        for archivo in archivos:
            info = session_manager.get_session_info(archivo)
            patient_id = info.get('patient_id', 'Unknown')
            
            if patient_id not in pacientes:
                pacientes[patient_id] = []
            pacientes[patient_id].append(info)
        
        print(f"👥 {len(pacientes)} pacientes encontrados:")
        print()
        
        for patient_id, sesiones in pacientes.items():
            print(f"🧑‍⚕️ {patient_id}:")
            for sesion in sesiones:
                fecha = sesion.get('date', 'Unknown')
                hora = sesion.get('time', 'Unknown')
                eventos = sesion.get('event_count', 0)
                print(f"   └─ {fecha} {hora}: {eventos} eventos registrados")
            print()
        
    except Exception as e:
        print(f"❌ Error accediendo historial: {e}")

def limpiar_archivos_datos():
    """Menú para limpiar archivos de datos"""
    print("\n🗑️ LIMPIEZA DE ARCHIVOS DE DATOS")
    print("=" * 50)
    
    try:
        from core.cognitive import CognitiveDataCleaner
        
        cleaner = CognitiveDataCleaner()
        
        # Mostrar resumen de almacenamiento
        summary = cleaner.get_storage_summary()
        print(summary)
        
        print("\n📋 OPCIONES DE LIMPIEZA:")
        print("  1. 📊 Ver archivos detallados")
        print("  2. 💾 Hacer backup de todos los archivos")
        print("  3. 🗑️ Eliminar archivos antiguos (>30 días)")
        print("  4. 🗑️ Eliminar archivos de un paciente específico")
        print("  5. 🚨 ELIMINAR TODOS LOS ARCHIVOS")
        print("  6. 🔙 Volver al menú principal")
        
        try:
            opcion = input("\n👉 Seleccione opción de limpieza (1-6): ").strip()
            
            if opcion == "1":
                # Ver archivos detallados
                menu_info = cleaner.selective_delete_menu()
                print("\n" + menu_info)
                
            elif opcion == "2":
                # Hacer backup
                print("\n💾 Haciendo backup de todos los archivos...")
                result = cleaner.backup_all_files()
                print(result)
                
            elif opcion == "3":
                # Eliminar archivos antiguos
                confirmar = input("\n⚠️ ¿Eliminar archivos antiguos (>30 días)? (si/no): ").strip().lower()
                if confirmar in ['si', 'sí', 's', 'yes', 'y']:
                    result = cleaner.delete_old_files(30)
                    print(result)
                else:
                    print("❌ Operación cancelada")
                    
            elif opcion == "4":
                # Eliminar archivos de paciente específico
                patient_id = input("\n📝 ID del paciente a eliminar: ").strip()
                if patient_id:
                    confirmar = input(f"⚠️ ¿Eliminar TODOS los archivos del paciente '{patient_id}'? (si/no): ").strip().lower()
                    if confirmar in ['si', 'sí', 's', 'yes', 'y']:
                        result = cleaner.delete_files_by_patient(patient_id)
                        print(result)
                    else:
                        print("❌ Operación cancelada")
                else:
                    print("❌ ID de paciente vacío")
                    
            elif opcion == "5":
                # Eliminar TODOS los archivos
                print("\n🚨 ADVERTENCIA: Esto eliminará TODOS los archivos de datos cognitivos")
                confirmar1 = input("¿Estás seguro? (ELIMINAR/cancelar): ").strip()
                if confirmar1 == "ELIMINAR":
                    confirmar2 = input("¿Realmente seguro? Escribe 'SI ELIMINAR TODO': ").strip()
                    if confirmar2 == "SI ELIMINAR TODO":
                        result = cleaner.delete_all_files(confirm=True)
                        print(result)
                    else:
                        print("❌ Operación cancelada (confirmación incorrecta)")
                else:
                    print("❌ Operación cancelada")
                    
            elif opcion == "6":
                return
            else:
                print("❌ Opción inválida")
                
        except Exception as e:
            print(f"❌ Error en limpieza: {e}")
        
    except Exception as e:
        print(f"❌ Error accediendo limpiador: {e}")

def mostrar_info_sistema():
    """Mostrar información del sistema"""
    print("\n ℹ️ INFORMACIÓN DEL SISTEMA")
    print("=" * 50)
    print()
    print("🧠 SISTEMA DE EVALUACIÓN COGNITIVA")
    print("   Versión: 2.0 - Con Visualización y Análisis Avanzado")
    print("   Desarrollado para evaluación neurodegenerativa")
    print()
    print("🎯 CAPACIDADES ACTUALES:")
    print("   • Piano-Simon: Memoria, secuencias, tiempo de reacción")
    print("   • Análisis automático de fatiga cognitiva")
    print("   • Detección de patrones de error")
    print("   • Exportación a CSV para análisis estadístico")
    print("   • Gráficas profesionales de rendimiento")
    print("   • Comparación entre múltiples sesiones")
    print("   • Dashboard cognitivo completo")
    print()
    print("📊 MÉTRICAS EVALUADAS:")
    print("   • Precisión promedio y variabilidad")
    print("   • Tiempo de reacción y patrones")
    print("   • Índice de fatiga cognitiva")
    print("   • Tendencia de aprendizaje")
    print("   • Consistencia en respuestas")
    print("   • Progresión por niveles")
    print("   • Distribución de tipos de errores")
    print()
    print("📈 VISUALIZACIONES:")
    print("   • Dashboard de 4 gráficas simultáneas")
    print("   • Análisis de fatiga con tendencias")
    print("   • Comparaciones multi-sesión")
    print("   • Exportación automática PNG de alta calidad")
    print()
    print("🔬 APLICACIÓN MÉDICA:")
    print("   • Detección temprana de deterioro cognitivo")
    print("   • Seguimiento de progresión")
    print("   • Evaluación objetiva de capacidades")
    print("   • Datos cuantitativos para investigación")
    print("   • Reportes visuales para equipos médicos")

def generar_graficas_rendimiento():
    """Generar gráficas de rendimiento"""
    print("\n📈 GENERACIÓN DE GRÁFICAS DE RENDIMIENTO")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager, CognitiveVisualAnalyzer
        
        session_manager = SessionManager()
        archivos = session_manager.list_session_files()
        
        if not archivos:
            print("❌ No hay sesiones disponibles para graficar")
            return
        
        print("📁 Sesiones disponibles:")
        for i, archivo in enumerate(archivos[:10]):
            info = session_manager.get_session_info(archivo)
            print(f"  {i+1}. {info.get('patient_id', 'Unknown')} - {info.get('game_type', 'Unknown')} ({info.get('event_count', 0)} eventos)")
        
        try:
            seleccion = int(input("\n📋 Seleccionar sesión para graficar (número): ")) - 1
            if 0 <= seleccion < len(archivos):
                archivo_seleccionado = archivos[seleccion]
                info = session_manager.get_session_info(archivo_seleccionado)
                
                print(f"\n🎨 Generando gráficas para: {info['patient_id']}")
                
                # Crear visualizador y generar dashboard
                analyzer = CognitiveVisualAnalyzer()
                result = analyzer.create_piano_performance_dashboard(info['filepath'])
                
                print(result)
                
            else:
                print("❌ Selección inválida")
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
        
    except Exception as e:
        print(f"❌ Error generando gráficas: {e}")

def comparar_multiples_sesiones():
    """Comparar múltiples sesiones"""
    print("\n🔄 COMPARACIÓN ENTRE MÚLTIPLES SESIONES")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager, CognitiveVisualAnalyzer
        
        session_manager = SessionManager()
        archivos = session_manager.list_session_files()
        
        if len(archivos) < 2:
            print("❌ Se necesitan al menos 2 sesiones para comparar")
            return
        
        print("📁 Sesiones disponibles:")
        for i, archivo in enumerate(archivos[:10]):
            info = session_manager.get_session_info(archivo)
            print(f"  {i+1}. {info.get('patient_id', 'Unknown')} - {info.get('game_type', 'Unknown')} ({info.get('event_count', 0)} eventos)")
        
        print("\n💡 Ingresa los números de las sesiones a comparar (separados por comas)")
        print("   Ejemplo: 1,3,5")
        
        try:
            selecciones_str = input("📋 Sesiones a comparar: ").strip()
            selecciones = [int(x.strip()) - 1 for x in selecciones_str.split(',')]
            
            # Validar selecciones
            archivos_seleccionados = []
            nombres_pacientes = []
            
            for sel in selecciones:
                if 0 <= sel < len(archivos):
                    archivo = archivos[sel]
                    info = session_manager.get_session_info(archivo)
                    archivos_seleccionados.append(info['filepath'])
                    nombres_pacientes.append(f"{info['patient_id']}_{info['date']}")
                else:
                    print(f"⚠️ Selección inválida: {sel + 1}")
            
            if len(archivos_seleccionados) >= 2:
                print(f"\n🔄 Comparando {len(archivos_seleccionados)} sesiones...")
                
                analyzer = CognitiveVisualAnalyzer()
                result = analyzer.create_comparison_chart(archivos_seleccionados, nombres_pacientes)
                
                print(result)
            else:
                print("❌ Se necesitan al menos 2 sesiones válidas")
                
        except ValueError:
            print("❌ Formato inválido. Usa números separados por comas")
        
    except Exception as e:
        print(f"❌ Error comparando sesiones: {e}")

def analisis_fatiga_cognitiva():
    """Análisis específico de fatiga cognitiva"""
    print("\n🧠 ANÁLISIS DE FATIGA COGNITIVA")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager, CognitiveVisualAnalyzer
        
        session_manager = SessionManager()
        archivos = session_manager.list_session_files()
        
        if not archivos:
            print("❌ No hay sesiones disponibles para analizar")
            return
        
        print("📁 Sesiones disponibles:")
        for i, archivo in enumerate(archivos[:10]):
            info = session_manager.get_session_info(archivo)
            eventos = info.get('event_count', 0)
            if eventos >= 6:  # Mínimo para análisis de fatiga
                print(f"  {i+1}. ✅ {info.get('patient_id', 'Unknown')} - {eventos} eventos")
            else:
                print(f"  {i+1}. ⚠️ {info.get('patient_id', 'Unknown')} - {eventos} eventos (insuficientes)")
        
        try:
            seleccion = int(input("\n📋 Seleccionar sesión para análisis de fatiga (número): ")) - 1
            if 0 <= seleccion < len(archivos):
                archivo_seleccionado = archivos[seleccion]
                info = session_manager.get_session_info(archivo_seleccionado)
                
                print(f"\n🧠 Analizando fatiga cognitiva para: {info['patient_id']}")
                
                analyzer = CognitiveVisualAnalyzer()
                result = analyzer.create_fatigue_analysis(info['filepath'])
                
                print(result)
                
            else:
                print("❌ Selección inválida")
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
        
    except Exception as e:
        print(f"❌ Error en análisis de fatiga: {e}")

def main():
    """Función principal del demo"""
    print("🚀 Iniciando demo médico completo...")
    
    while True:
        mostrar_menu_principal()
        
        try:
            opcion = input("👉 Seleccione una opción (1-9): ").strip()
            
            if opcion == "1":
                ejecutar_evaluacion_piano()
            elif opcion == "2":
                analizar_sesion_anterior()
            elif opcion == "3":
                generar_graficas_rendimiento()
            elif opcion == "4":
                comparar_multiples_sesiones()
            elif opcion == "5":
                analisis_fatiga_cognitiva()
            elif opcion == "6":
                ver_historial_pacientes()
            elif opcion == "7":
                limpiar_archivos_datos()
            elif opcion == "8":
                mostrar_info_sistema()
            elif opcion == "9":
                print("\n👋 Saliendo del sistema...")
                print("   Gracias por usar el Sistema de Evaluación Cognitiva")
                break
            else:
                print("❌ Opción inválida. Por favor seleccione 1-9.")
            
            input("\n⏸️  Presione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo del sistema...")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main() 