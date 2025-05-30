# #!/usr/bin/env python3
# """
# Script de prueba para el sistema de análisis de logs
# Ejecuta el analizador de gráficas independientemente
# """

# import sys
# import os

# # Agregar el directorio main al path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from core.game_analytics import GameAnalytics

# def test_analytics():
#     """Probar el sistema de análisis"""
#     print("🎮 Probando Game Analytics")
#     print("="*50)

#     # Cambiar al directorio correcto
#     original_dir = os.getcwd()
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     parent_dir = os.path.dirname(script_dir)
#     os.chdir(parent_dir)

#     try:
#         # Crear instancia del analizador
#         analytics = GameAnalytics()

#         # Listar juegos disponibles
#         available_games = analytics.list_available_games()
#         print(f"📊 Juegos encontrados: {available_games}")

#         if not available_games:
#             print("❌ No se encontraron logs para analizar")
#             print("💡 Ejecuta algunos juegos primero para generar logs")
#             return

#         # Mostrar información de cada juego
#         for game in available_games:
#             summary = analytics.get_game_summary(game)
#             print(f"\n🎯 {game}:")
#             print(f"   • Eventos totales: {summary.get('total_events', 0)}")
#             print(f"   • Errores: {summary.get('errors', 0)}")
#             print(f"   • Partidas: {summary.get('deaths', 0)}")
#             print(f"   • Score máximo: {summary.get('max_score', 0)}")
#             print(f"   • Duración total: {summary.get('total_duration', 0):.1f}s")

#         # Preguntar qué mostrar
#         print("\n" + "="*50)
#         print("¿Qué análisis deseas ver?")
#         print("1. Dashboard general de todos los juegos")
#         print("2. Análisis detallado de un juego específico")
#         print("3. Reporte textual de un juego")
#         print("4. Exportar datos a CSV")
#         print("5. Todo lo anterior (automático)")

#         try:
#             choice = input("\nElige una opción (1-5): ").strip()
#         except KeyboardInterrupt:
#             print("\n👋 Análisis cancelado")
#             return

#         if choice == "1":
#             print("\n📈 Mostrando dashboard general...")
#             analytics.show_performance_dashboard()

#         elif choice == "2":
#             if len(available_games) == 1:
#                 game_to_analyze = available_games[0]
#             else:
#                 print(f"\nJuegos disponibles: {', '.join(available_games)}")
#                 game_to_analyze = input("Ingresa el nombre del juego: ").strip()

#             if game_to_analyze in available_games:
#                 print(f"\n📊 Análisis detallado de {game_to_analyze}...")
#                 analytics.show_detailed_game_analysis(game_to_analyze)
#             else:
#                 print("❌ Juego no encontrado")

#         elif choice == "3":
#             if len(available_games) == 1:
#                 game_to_analyze = available_games[0]
#             else:
#                 print(f"\nJuegos disponibles: {', '.join(available_games)}")
#                 game_to_analyze = input("Ingresa el nombre del juego: ").strip()

#             if game_to_analyze in available_games:
#                 print(f"\n📋 Reporte de {game_to_analyze}:")
#                 print("-" * 60)
#                 print(analytics.generate_performance_report(game_to_analyze))
#             else:
#                 print("❌ Juego no encontrado")

#         elif choice == "4":
#             if len(available_games) == 1:
#                 game_to_analyze = available_games[0]
#             else:
#                 print(f"\nJuegos disponibles: {', '.join(available_games)}")
#                 game_to_analyze = input("Ingresa el nombre del juego: ").strip()

#             if game_to_analyze in available_games:
#                 print(f"\n💾 Exportando datos de {game_to_analyze}...")
#                 analytics.export_data_to_csv(game_to_analyze)
#             else:
#                 print("❌ Juego no encontrado")

#         elif choice == "5":
#             print("\n🚀 Ejecutando análisis completo...")

#             # Dashboard general
#             print("\n📈 1. Dashboard general:")
#             analytics.show_performance_dashboard()

#             # Análisis detallado del primer juego
#             first_game = available_games[0]
#             print(f"\n📊 2. Análisis detallado de {first_game}:")
#             analytics.show_detailed_game_analysis(first_game)

#             # Reporte textual
#             print(f"\n📋 3. Reporte textual de {first_game}:")
#             print("-" * 60)
#             print(analytics.generate_performance_report(first_game))

#             # Exportar CSV
#             print(f"\n💾 4. Exportando datos de {first_game}...")
#             analytics.export_data_to_csv(first_game)

#         else:
#             print("❌ Opción no válida")

#     except Exception as e:
#         print(f"❌ Error durante el análisis: {e}")
#         import traceback
#         traceback.print_exc()

#     finally:
#         # Restaurar directorio original
#         os.chdir(original_dir)

# if __name__ == "__main__":
#     test_analytics()
