#!/usr/bin/env python3
"""
PRUEBA COMPLETA DEL SISTEMA COGNITIVO
Script para probar todas las funcionalidades - SÚPER SIMPLE
"""

import sys
import os
import random
import time

# Añadir path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cognitive_logger():
    """Probar el logger cognitivo directamente"""
    print("\n🧪 PROBANDO COGNITIVE LOGGER DIRECTO")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager
        
        # Crear session manager
        session_manager = SessionManager()
        print("✅ SessionManager creado")
        
        # Iniciar sesión
        logger = session_manager.start_session("piano_simon", "TEST_P001")
        print("✅ Sesión iniciada")
        
        # Simular algunos eventos
        for i in range(10):
            level = min(i // 2 + 1, 5)
            sequence_length = level + 2
            
            sequence_shown = [random.randint(0, 7) for _ in range(sequence_length)]
            
            # Simular respuesta (80% correctas)
            if random.random() < 0.8:
                sequence_input = sequence_shown.copy()
                response_time = random.randint(1200, 3000)
            else:
                sequence_input = sequence_shown.copy()
                if len(sequence_input) > 1:
                    sequence_input[random.randint(0, len(sequence_input)-1)] = random.randint(0, 7)
                response_time = random.randint(2500, 5000)
            
            presentation_time = sequence_length * 750
            
            logger.log_piano_event(
                level=level,
                sequence_shown=sequence_shown,
                sequence_input=sequence_input,
                presentation_time=presentation_time,
                response_time=response_time
            )
            
            is_correct = sequence_shown == sequence_input
            print(f"   📝 Evento {i+1}: Nivel {level}, {'✅' if is_correct else '❌'}")
        
        # Terminar sesión
        session_manager.end_session()
        print("✅ Sesión terminada y guardada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test logger: {e}")
        return False

def test_visual_analyzer():
    """Probar el analizador visual"""
    print("\n📊 PROBANDO VISUAL ANALYZER")
    print("=" * 50)
    
    try:
        from core.cognitive import SessionManager, CognitiveVisualAnalyzer
        
        # Buscar archivos CSV existentes
        session_manager = SessionManager()
        files = session_manager.list_session_files()
        
        if not files:
            print("❌ No hay archivos CSV para analizar")
            return False
        
        # Tomar el archivo más reciente
        latest_file = files[0]
        info = session_manager.get_session_info(latest_file)
        print(f"📁 Analizando: {info['patient_id']} ({info['event_count']} eventos)")
        
        # Crear visualizador
        analyzer = CognitiveVisualAnalyzer()
        
        # Generar dashboard
        result = analyzer.create_piano_performance_dashboard(info['filepath'])
        print(f"📈 Dashboard: {result}")
        
        # Generar análisis de fatiga
        result_fatigue = analyzer.create_fatigue_analysis(info['filepath'])
        print(f"🧠 Análisis fatiga: {result_fatigue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test visual: {e}")
        return False

def test_data_cleaner():
    """Probar el limpiador de datos"""
    print("\n🗑️ PROBANDO DATA CLEANER")
    print("=" * 50)
    
    try:
        from core.cognitive import CognitiveDataCleaner
        
        cleaner = CognitiveDataCleaner()
        
        # Obtener resumen
        summary = cleaner.get_storage_summary()
        print(summary)
        
        # Listar archivos
        files = cleaner.list_all_files()
        print(f"📁 {len(files)} archivos encontrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test cleaner: {e}")
        return False

def test_game_integration():
    """Probar integración con el juego"""
    print("\n🎮 PROBANDO INTEGRACIÓN CON PIANO-SIMON")
    print("=" * 50)
    
    try:
        from games.piano.game_logic import PianoGameLogic
        
        # Crear game logic con logging
        game_logic = PianoGameLogic(
            enable_cognitive_logging=True,
            patient_id="TEST_INTEGRATION"
        )
        
        print("✅ PianoGameLogic creado con logging")
        
        # Reset game (debería inicializar logger)
        game_logic.reset_game()
        
        if game_logic.current_logger:
            print("✅ Logger cognitivo disponible")
            
            # Simular algunos eventos de juego
            for i in range(5):
                level = i + 1
                sequence = [random.randint(0, 7) for _ in range(level + 2)]
                
                game_logic.current_logger.log_piano_event(
                    level=level,
                    sequence_shown=sequence,
                    sequence_input=sequence,  # Respuesta correcta
                    presentation_time=len(sequence) * 750,
                    response_time=random.randint(1200, 2500)
                )
                
                print(f"   📝 Evento simulado {i+1}: Nivel {level}")
            
            # Terminar sesión
            if game_logic.session_manager:
                game_logic.session_manager.end_session()
                print("✅ Sesión de juego terminada")
            
            return True
        else:
            print("❌ Logger cognitivo no disponible")
            return False
        
    except Exception as e:
        print(f"❌ Error en test game integration: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA COGNITIVO")
    print("=" * 60)
    
    tests = [
        ("Logger Cognitivo", test_cognitive_logger),
        ("Integración Juego", test_game_integration),
        ("Analizador Visual", test_visual_analyzer),
        ("Limpiador de Datos", test_data_cleaner)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 EJECUTANDO: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"💥 FALLO CRÍTICO en {test_name}: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Pausa entre tests
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"  {test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
    else:
        print("⚠️ Hay problemas que resolver")
    
    return passed == total

if __name__ == "__main__":
    main() 