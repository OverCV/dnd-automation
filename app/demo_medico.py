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
    print("  3. 📁 Ver historial de pacientes")
    print("  4. ℹ️  Información del sistema")
    print("  5. 🚪 Salir")
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
    
    # Simular 10 intentos con diferentes patrones
    for i in range(10):
        nivel = min(i // 3 + 1, 5)  # Niveles 1-5
        longitud_secuencia = nivel + 2
        
        # Generar secuencia mostrada
        secuencia_mostrada = [random.randint(0, 7) for _ in range(longitud_secuencia)]
        
        # Simular respuesta del paciente (con algunos errores)
        if random.random() < 0.8:  # 80% de respuestas correctas
            secuencia_respuesta = secuencia_mostrada.copy()
            tiempo_respuesta = random.randint(1500, 4000)  # Tiempo normal
        else:
            # Introducir error
            secuencia_respuesta = secuencia_mostrada.copy()
            if len(secuencia_respuesta) > 1:
                secuencia_respuesta[random.randint(0, len(secuencia_respuesta)-1)] = random.randint(0, 7)
            tiempo_respuesta = random.randint(2500, 6000)  # Tiempo más lento en errores
        
        # Tiempo de presentación
        tiempo_presentacion = longitud_secuencia * 800
        
        # Log del evento
        logger.log_piano_event(
            level=nivel,
            sequence_shown=secuencia_mostrada,
            sequence_input=secuencia_respuesta,
            presentation_time=tiempo_presentacion,
            response_time=tiempo_respuesta
        )
        
        print(f"   └─ Intento {i+1}: Nivel {nivel}, Precisión: {'✅' if secuencia_mostrada == secuencia_respuesta else '❌'}")
        time.sleep(0.1)  # Pausa visual
    
    print("\n✅ Simulación completada")

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

def mostrar_info_sistema():
    """Mostrar información del sistema"""
    print("\n ℹ️ INFORMACIÓN DEL SISTEMA")
    print("=" * 50)
    print()
    print("🧠 SISTEMA DE EVALUACIÓN COGNITIVA")
    print("   Versión: 1.0 - Implementación MVP")
    print("   Desarrollado para evaluación neurodegenerativa")
    print()
    print("🎯 CAPACIDADES ACTUALES:")
    print("   • Piano-Simon: Memoria, secuencias, tiempo de reacción")
    print("   • Análisis automático de fatiga cognitiva")
    print("   • Detección de patrones de error")
    print("   • Exportación a CSV para análisis estadístico")
    print()
    print("📊 MÉTRICAS EVALUADAS:")
    print("   • Precisión promedio y variabilidad")
    print("   • Tiempo de reacción y patrones")
    print("   • Índice de fatiga cognitiva")
    print("   • Tendencia de aprendizaje")
    print("   • Consistencia en respuestas")
    print()
    print("🔬 APLICACIÓN MÉDICA:")
    print("   • Detección temprana de deterioro cognitivo")
    print("   • Seguimiento de progresión")
    print("   • Evaluación objetiva de capacidades")
    print("   • Datos cuantitativos para investigación")

def main():
    """Función principal del demo"""
    print("🚀 Iniciando demo médico...")
    
    while True:
        mostrar_menu_principal()
        
        try:
            opcion = input("👉 Seleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                ejecutar_evaluacion_piano()
            elif opcion == "2":
                analizar_sesion_anterior()
            elif opcion == "3":
                ver_historial_pacientes()
            elif opcion == "4":
                mostrar_info_sistema()
            elif opcion == "5":
                print("\n👋 Saliendo del sistema...")
                print("   Gracias por usar el Sistema de Evaluación Cognitiva")
                break
            else:
                print("❌ Opción inválida. Por favor seleccione 1-5.")
            
            input("\n⏸️  Presione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo del sistema...")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main() 