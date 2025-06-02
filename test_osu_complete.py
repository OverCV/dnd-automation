#!/usr/bin/env python3
"""
Script de prueba completo para el juego Osu! Rhythm Game
Verifica todos los componentes del sistema
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_osu_imports():
    """Probar importaciones del juego Osu"""
    print("🧪 Probando importaciones del juego Osu...")
    
    try:
        # Probar importaciones principales
        from games.osu.hardware_manager import OsuHardwareManager
        print("✅ OsuHardwareManager importado correctamente")
        
        from games.osu.audio_manager import OsuAudioManager
        print("✅ OsuAudioManager importado correctamente")
        
        from games.osu.visual_manager import OsuVisualManager
        print("✅ OsuVisualManager importado correctamente")
        
        from games.osu.game_logic import OsuGameLogic, GameState, HitResult
        print("✅ OsuGameLogic importado correctamente")
        
        from games.osu.osu import OsuGame, create_osu_game
        print("✅ OsuGame importado correctamente")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando componentes Osu: {e}")
        return False

def test_game_registry():
    """Probar registro de juegos"""
    print("\n🧪 Probando registro de juegos...")
    
    try:
        from managers.components.game_registry import GameRegistry
        
        registry = GameRegistry()
        
        # Verificar que Osu está registrado
        if "osu_rhythm" in registry.available_games:
            print("✅ Osu Rhythm registrado en el sistema")
        else:
            print("❌ Osu Rhythm NO encontrado en el registro")
            return False
        
        # Verificar soporte cognitivo
        if registry.supports_cognitive_logging("osu_rhythm"):
            print("✅ Osu Rhythm soporta logging cognitivo")
        else:
            print("❌ Osu Rhythm NO soporta logging cognitivo")
            return False
        
        # Verificar modo de prueba
        if "osu_rhythm" in registry.get_games_with_test_mode():
            print("✅ Osu Rhythm tiene modo de prueba")
        else:
            print("❌ Osu Rhythm NO tiene modo de prueba")
            return False
        
        # Información técnica
        tech_info = registry.get_tech_info("osu_rhythm")
        print(f"📋 Info técnica: {tech_info}")
        
        # Icono
        icon = registry.get_game_icon("osu_rhythm")
        print(f"🎯 Icono: {icon}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando registro: {e}")
        return False

def test_cognitive_logging():
    """Probar sistema de logging cognitivo"""
    print("\n🧪 Probando sistema cognitivo Osu...")
    
    try:
        from core.cognitive.cognitive_logger import CognitiveLogger
        
        # Crear logger para Osu
        logger = CognitiveLogger("osu_rhythm", "test_paciente")
        print("✅ CognitiveLogger creado para Osu")
        
        # Probar log de evento Osu
        logger.log_osu_event(
            circle_x=400,
            circle_y=300,
            cursor_x=395,
            cursor_y=305,
            spawn_time=1000.0,
            hit_time=1300.0,
            reaction_time=300.0,
            spatial_accuracy=92.5,
            temporal_accuracy=88.7,
            hit_result="PERFECT",
            score=300,
            combo=5,
            difficulty_level=3
        )
        print("✅ Evento Osu loggeado correctamente")
        
        # Cerrar sesión
        session_file = logger.close_session()
        print(f"✅ Sesión cerrada: {session_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando logging cognitivo: {e}")
        return False

def test_data_structure():
    """Probar estructura de datos"""
    print("\n🧪 Probando estructura de datos...")
    
    try:
        import glob
        
        # Verificar directorio de datos
        data_dir = "data/cognitive/osu_rhythm/sessions"
        if os.path.exists(data_dir):
            print(f"✅ Directorio de datos existe: {data_dir}")
        else:
            print(f"❌ Directorio de datos NO existe: {data_dir}")
            return False
        
        # Verificar archivos CSV de ejemplo
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if csv_files:
            print(f"✅ Encontrados {len(csv_files)} archivos CSV de ejemplo")
            for csv_file in csv_files:
                print(f"   📄 {os.path.basename(csv_file)}")
        else:
            print("⚠️ No se encontraron archivos CSV de ejemplo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando estructura de datos: {e}")
        return False

def test_analytics_window():
    """Probar ventana de análisis"""
    print("\n🧪 Probando ventana de análisis Osu...")
    
    try:
        # Importar sin crear ventana (no tenemos GUI en el test)
        from ui.cognitive.osu_analytics_window import OsuCognitiveAnalyticsWindow
        print("✅ OsuCognitiveAnalyticsWindow importado correctamente")
        
        # Verificar que se puede importar la función de apertura
        from ui.cognitive.osu_analytics_window import open_osu_cognitive_analytics
        print("✅ Función open_osu_cognitive_analytics disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando ventana de análisis: {e}")
        return False

def test_game_creation():
    """Probar creación del juego (sin Arduino)"""
    print("\n🧪 Probando creación del juego Osu...")
    
    try:
        # Crear mock de ArduinoManager para prueba
        class MockArduinoManager:
            def __init__(self):
                self.connected = False
            
            def is_connected(self):
                return self.connected
        
        mock_arduino = MockArduinoManager()
        
        # Probar creación del juego
        from games.osu.osu import create_osu_game
        
        osu_game = create_osu_game(mock_arduino)
        print("✅ Juego Osu creado correctamente")
        
        # Verificar propiedades
        if hasattr(osu_game, 'name'):
            print(f"📋 Nombre: {osu_game.name}")
        
        if hasattr(osu_game, 'description'):
            print(f"📋 Descripción: {osu_game.description}")
        
        # Verificar managers
        if hasattr(osu_game, 'hardware_manager'):
            print("✅ Hardware manager presente")
        
        if hasattr(osu_game, 'audio_manager'):
            print("✅ Audio manager presente")
        
        if hasattr(osu_game, 'visual_manager'):
            print("✅ Visual manager presente")
        
        if hasattr(osu_game, 'game_logic'):
            print("✅ Game logic presente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando juego: {e}")
        return False

def test_hardware_info():
    """Probar información de hardware"""
    print("\n🧪 Probando información de hardware...")
    
    try:
        from games.osu.osu import get_osu_info
        
        info = get_osu_info()
        print("✅ Información de Osu obtenida")
        
        print(f"📋 Nombre: {info['name']}")
        print(f"📋 Descripción: {info['description']}")
        
        print("🔧 Requisitos de hardware:")
        for req in info['hardware_requirements']:
            print(f"   • {req}")
        
        print("⚡ Características:")
        for feature in info['features']:
            print(f"   • {feature}")
        
        print("🧠 Métricas cognitivas:")
        for metric in info['cognitive_metrics']:
            print(f"   • {metric}")
        
        print("🎮 Controles:")
        for control, description in info['controls'].items():
            print(f"   • {control}: {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error obteniendo información: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🎯 PRUEBA COMPLETA DEL SISTEMA OSU! RHYTHM GAME")
    print("=" * 55)
    
    tests = [
        ("Importaciones", test_osu_imports),
        ("Registro de juegos", test_game_registry),
        ("Logging cognitivo", test_cognitive_logging),
        ("Estructura de datos", test_data_structure),
        ("Ventana de análisis", test_analytics_window),
        ("Creación del juego", test_game_creation),
        ("Información de hardware", test_hardware_info),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error en prueba '{test_name}': {e}")
            results[test_name] = False
    
    # Resumen final
    print("\n" + "=" * 55)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 55)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema Osu está listo.")
        print("\n🚀 Próximos pasos:")
        print("1. Conecta el joystick KY-023 según las especificaciones")
        print("2. Ejecuta el juego desde la interfaz principal")
        print("3. Prueba el modo de prueba del joystick")
        print("4. Juega algunas sesiones para generar datos cognitivos")
        print("5. Revisa los análisis cognitivos con gráficas detalladas")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 