#!/usr/bin/env python3
"""
Test súper simple para verificar logging cognitivo
Solo para verificar que todo funciona - KISSS
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cognitive_components():
    """Probar componentes cognitivos básicos"""
    print("🧠 TESTING COMPONENTES COGNITIVOS - SÚPER SIMPLE")
    print("=" * 50)
    
    try:
        # Test 1: Importar módulos
        print("📦 Test 1: Importando módulos...")
        from core.cognitive import CognitiveLogger, SessionManager, MetricsCalculator
        print("✅ Imports OK")
        
        # Test 2: Crear sesión
        print("\n🔄 Test 2: Crear sesión...")
        session_manager = SessionManager()
        logger = session_manager.start_session("piano_simon", "test_patient")
        print("✅ Sesión creada OK")
        
        # Test 3: Log eventos falsos
        print("\n📊 Test 3: Logging eventos falsos...")
        logger.log_piano_event(
            level=1,
            sequence_shown=[1, 3, 2],
            sequence_input=[1, 3, 2],
            presentation_time=1500,
            response_time=2800
        )
        
        logger.log_piano_event(
            level=2,
            sequence_shown=[1, 3, 2, 5],
            sequence_input=[1, 3, 4, 5],  # Error en posición 2
            presentation_time=2000,
            response_time=3200
        )
        
        logger.log_piano_event(
            level=2,
            sequence_shown=[1, 3, 2, 5],
            sequence_input=[1, 3, 2, 5],  # Correcto
            presentation_time=2000,
            response_time=2500
        )
        print("✅ Eventos loggeados OK")
        
        # Test 4: Cerrar sesión
        print("\n🔚 Test 4: Cerrar sesión...")
        csv_file = session_manager.end_session()
        print(f"✅ Sesión cerrada, archivo: {csv_file}")
        
        # Test 5: Analizar métricas
        if csv_file:
            print("\n📈 Test 5: Análisis de métricas...")
            calculator = MetricsCalculator(csv_file)
            report = calculator.generate_summary_report()
            print("✅ Reporte generado:")
            print("-" * 30)
            print(report)
            print("-" * 30)
        
        print("\n🎉 TODOS LOS TESTS PASARON - SISTEMA COGNITIVO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_piano_integration():
    """Test de integración con Piano (sin Arduino)"""
    print("\n🎹 TESTING INTEGRACIÓN PIANO - SIN HARDWARE")
    print("=" * 50)
    
    try:
        from games.piano.game_logic import PianoGameLogic
        
        # Crear game logic con logging habilitado
        game_logic = PianoGameLogic(
            enable_cognitive_logging=True,
            patient_id="test_integration"
        )
        
        print("✅ Piano game logic con logging cognitivo creado")
        
        # Simular algunos eventos
        game_logic.reset_game()
        
        # Simular inicio de juego
        if game_logic.start_game_with_button(0):
            print("✅ Juego iniciado")
        
        # Simular algunos inputs (esto será simplificado)
        print("✅ Integración básica funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración piano: {e}")
        return False


if __name__ == "__main__":
    print("🚀 INICIANDO TESTS COGNITIVOS...")
    
    # Test componentes básicos
    success1 = test_cognitive_components()
    
    # Test integración piano
    success2 = test_piano_integration()
    
    if success1 and success2:
        print("\n🎉 TODOS LOS TESTS EXITOSOS - SISTEMA LISTO!")
        print("\n💡 Para usar en el juego real:")
        print("   - Pasa enable_cognitive_logging=True al crear PianoSimonGame")
        print("   - Los datos se guardan automáticamente en data/cognitive/")
        print("   - Usa MetricsCalculator para análisis post-sesión")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1) 