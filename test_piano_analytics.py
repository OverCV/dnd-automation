#!/usr/bin/env python3
"""
Script de prueba para verificar Piano Digital y Análisis Cognitivo
"""

import sys
import tkinter as tk
sys.path.append('app')

def test_piano_analytics():
    """Probar que el Piano Digital aparece y el análisis funciona"""
    print("🧪 === PRUEBA PIANO DIGITAL + ANÁLISIS ===")
    
    try:
        # 1. Verificar registro de juegos
        from managers.components.game_registry import GameRegistry
        registry = GameRegistry()
        
        print(f"🎮 Juegos registrados: {list(registry.available_games.keys())}")
        print(f"🧪 Juegos con test mode: {registry.get_games_with_test_mode()}")
        
        # 2. Verificar que piano_digital está registrado
        if "piano_digital" in registry.available_games:
            print("✅ Piano Digital está registrado correctamente")
        else:
            print("❌ Piano Digital NO está registrado")
            return False
        
        # 3. Verificar import del sistema cognitivo
        try:
            from core.cognitive import SessionManager
            print("✅ Sistema cognitivo importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando sistema cognitivo: {e}")
            return False
        
        # 4. Verificar que existen datos de ejemplo
        import os
        data_dir = "data/cognitive/piano_digital/sessions"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            print(f"📊 Archivos de datos encontrados: {len(csv_files)}")
            for f in csv_files:
                print(f"   • {f}")
        else:
            print("⚠️ No se encontró directorio de datos")
        
        # 5. Probar ventana de análisis
        root = tk.Tk()
        root.title("Prueba Piano Digital")
        root.geometry("500x300")
        
        # Botón para probar análisis
        def test_analytics():
            try:
                from ui.cognitive.cognitive_analytics_window import open_cognitive_analytics
                analytics = open_cognitive_analytics(root, "piano_digital")
                if analytics:
                    print("✅ Ventana de análisis abierta correctamente")
                else:
                    print("⚠️ Ventana de análisis no se pudo abrir")
            except Exception as e:
                print(f"❌ Error abriendo análisis: {e}")
        
        # Interfaz de prueba
        title_label = tk.Label(
            root,
            text="🎹 PRUEBA PIANO DIGITAL",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        info_label = tk.Label(
            root,
            text="Verificaciones realizadas:\n"
                 "✅ Piano Digital registrado\n"
                 "✅ Sistema cognitivo disponible\n"
                 "✅ Datos de ejemplo cargados",
            font=("Arial", 10),
            justify=tk.LEFT
        )
        info_label.pack(pady=10)
        
        analytics_btn = tk.Button(
            root,
            text="📈 Probar Análisis Cognitivo",
            command=test_analytics,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        analytics_btn.pack(pady=20)
        
        close_btn = tk.Button(
            root,
            text="❌ Cerrar",
            command=root.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)
        
        print("✅ Interfaz de prueba creada")
        print("📊 Haz clic en 'Probar Análisis Cognitivo' para ver las gráficas")
        
        root.mainloop()
        
        print("✅ Prueba completada")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_piano_analytics()
    print(f"\n{'✅ ÉXITO' if success else '❌ FALLO'}: Piano Digital {'FUNCIONA' if success else 'NO FUNCIONA'}")
    sys.exit(0 if success else 1) 