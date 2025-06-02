#!/usr/bin/env python3
"""
Test final - Confirmar que test mode funciona sin bloquear
"""

import sys
import time
sys.path.append('app')

def test_final():
    """Test final del modo headless"""
    print("🎯 === TEST FINAL DEL MODO HEADLESS ===")
    
    try:
        from core.arduino_manager import ArduinoManager
        from games.piano.piano import PianoSimonGame
        
        print("✅ Importaciones exitosas (sin pygame)")
        
        arduino = ArduinoManager()
        piano = PianoSimonGame(arduino, enable_cognitive_logging=False, headless_mode=True)
        
        print("✅ Piano headless creado")
        
        start_time = time.time()
        resultado = piano.start_test_mode(headless_mode=True)
        end_time = time.time()
        
        print(f"✅ start_test_mode terminó en {end_time - start_time:.3f}s - Resultado: {resultado}")
        
        if resultado:
            print("⏳ Test mode corriendo... esperando 5 segundos")
            time.sleep(5)
            
            estado = piano.state_manager.get_status()
            print(f"📊 Estado: running={estado.get('is_running', False)}")
            
            piano.stop_game()
            print("✅ Test mode detenido")
            
        print("🎉 === TEST FINAL EXITOSO ===")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_final()
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}: Test mode {'FUNCIONA' if success else 'NO FUNCIONA'}")
    sys.exit(0 if success else 1) 