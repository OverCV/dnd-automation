#!/usr/bin/env python3
"""
Test específico del modo prueba del Piano Simon - VERSIÓN ACTUALIZADA
"""

import sys
import time
import threading

sys.path.append("app")

from core.arduino_manager import ArduinoManager
from games.piano.piano import PianoSimonGame


def test_piano_test_mode():
    """Test del modo prueba del piano de forma no bloqueante"""
    print("🎹 === TEST MODO PRUEBA PIANO (NO BLOQUEANTE) ===")

    # Crear Arduino Manager
    print("🔧 Creando Arduino Manager...")
    arduino = ArduinoManager()
    print(f"Arduino conectado: {arduino.connected}")

    # Crear Piano Game en modo HEADLESS
    print("🎹 Creando Piano Game en modo headless...")
    piano = PianoSimonGame(arduino, enable_cognitive_logging=False, headless_mode=True)
    print("Piano creado exitosamente en modo headless")

    # Verificar estado inicial
    print("📊 Estado inicial del state manager:")
    estado = piano.state_manager.get_status()
    for key, value in estado.items():
        print(f"  - {key}: {value}")

    # Test del start_test_mode en modo HEADLESS (NO DEBE BLOQUEAR)
    print("\n🧪 === INICIANDO TEST MODE HEADLESS ===")
    print("📍 Antes de start_test_mode...")

    start_time = time.time()
    resultado = piano.start_test_mode(headless_mode=True)  # MODO HEADLESS
    end_time = time.time()

    print(f"📍 Después de start_test_mode: {resultado}")
    print(f"⏱️ Tiempo transcurrido: {end_time - start_time:.3f} segundos")

    if resultado:
        print("✅ Test mode headless iniciado exitosamente!")

        # Verificar que esté corriendo
        print("📊 Verificando estado después del inicio...")
        for i in range(8):  # 8 segundos de test
            time.sleep(1)
            estado = piano.state_manager.get_status()
            print(
                f"  Estado {i + 1}s: running={estado['is_running']}, lifecycle={estado['lifecycle_state']}"
            )

            if not estado["is_running"]:
                print("⚠️ El test mode se detuvo inesperadamente")
                break

        # Detener test mode
        print("\n🛑 Deteniendo test mode...")
        piano.stop_game()
        time.sleep(1)

        estado_final = piano.state_manager.get_status()
        print(f"📊 Estado final: {estado_final}")

    else:
        print("❌ Test mode NO se pudo iniciar")

    print("\n🎯 === TEST COMPLETO ===")


if __name__ == "__main__":
    test_piano_test_mode()
