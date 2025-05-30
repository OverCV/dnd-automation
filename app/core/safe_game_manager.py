"""
Gestor seguro de juegos para manejar detención sin crashes
"""

import threading
import time
import pygame
from typing import Optional
from core.base_game import BaseGame


class SafeGameManager:
    """Manager que garantiza detención segura de juegos sin crashes"""
    
    def __init__(self):
        self.current_game: Optional[BaseGame] = None
        self.stop_in_progress = False
        self._stop_lock = threading.Lock()
    
    def set_current_game(self, game: BaseGame):
        """Establecer el juego actual"""
        with self._stop_lock:
            self.current_game = game
    
    def stop_current_game_safely(self, timeout: float = 5.0) -> bool:
        """Detener el juego actual de forma completamente segura"""
        with self._stop_lock:
            if not self.current_game or self.stop_in_progress:
                return True
            
            self.stop_in_progress = True
            game = self.current_game
            game_name = getattr(game, 'name', 'Juego Desconocido')
            
            try:
                print(f"🛑 Deteniendo {game_name} de forma segura...")
                
                # Paso 1: Marcar como no ejecutándose
                if hasattr(game, 'running'):
                    game.running = False
                if hasattr(game, 'test_mode'):
                    game.test_mode = False
                
                # Paso 2: Esperar a que los hilos terminen
                self._stop_game_threads(game, timeout)
                
                # Paso 3: Limpiar audio
                self._cleanup_audio(game)
                
                # Paso 4: Limpiar Pygame
                self._cleanup_pygame(game)
                
                # Paso 5: Limpiar hardware
                self._cleanup_hardware(game)
                
                # Paso 6: Llamar al stop_game original si existe
                if hasattr(game, 'stop_game'):
                    try:
                        game.stop_game()
                    except Exception as e:
                        print(f"⚠️ Error en stop_game original: {e}")
                
                print(f"✅ {game_name} detenido completamente")
                self.current_game = None
                return True
                
            except Exception as e:
                print(f"❌ Error deteniendo {game_name}: {e}")
                return False
            finally:
                self.stop_in_progress = False
    
    def _stop_game_threads(self, game: BaseGame, timeout: float):
        """Detener hilos del juego de forma segura"""
        threads_to_wait = []
        
        # Encontrar hilos del juego
        if hasattr(game, 'game_thread') and game.game_thread:
            threads_to_wait.append(('game_thread', game.game_thread))
        
        # Esperar a que terminen los hilos
        for thread_name, thread in threads_to_wait:
            if thread and thread.is_alive():
                print(f"⏳ Esperando que termine {thread_name}...")
                try:
                    thread.join(timeout=timeout/len(threads_to_wait))
                    if thread.is_alive():
                        print(f"⚠️ {thread_name} no terminó en el tiempo esperado")
                    else:
                        print(f"✅ {thread_name} terminado")
                except Exception as e:
                    print(f"⚠️ Error esperando {thread_name}: {e}")
    
    def _cleanup_audio(self, game: BaseGame):
        """Limpiar recursos de audio"""
        try:
            # Piano modular
            if hasattr(game, 'audio_manager'):
                if hasattr(game.audio_manager, 'detener_todos_sonidos'):
                    game.audio_manager.detener_todos_sonidos()
                print("✅ Audio manager limpiado")
            
            # Otros juegos con pygame.mixer
            elif hasattr(game, 'audio_initialized') and game.audio_initialized:
                pygame.mixer.stop()
                print("✅ Pygame mixer detenido")
            
            # Intentar limpiar mixer de forma general
            try:
                pygame.mixer.stop()
                pygame.mixer.quit()
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Error limpiando audio: {e}")
    
    def _cleanup_pygame(self, game: BaseGame):
        """Limpiar Pygame de forma segura"""
        try:
            # Piano modular
            if hasattr(game, 'visual_manager'):
                if hasattr(game.visual_manager, 'cerrar'):
                    game.visual_manager.cerrar()
                print("✅ Visual manager cerrado")
            
            # Otros juegos con pygame
            elif hasattr(game, 'pygame_initialized') and game.pygame_initialized:
                try:
                    pygame.display.quit()
                    pygame.quit()
                    game.pygame_initialized = False
                    print("✅ Pygame cerrado")
                except Exception as e:
                    print(f"⚠️ Error cerrando pygame del juego: {e}")
                    # Intentar cerrar de forma forzada
                    try:
                        pygame.quit()
                        game.pygame_initialized = False
                    except:
                        pass
            
            # Limpiar pygame de forma general si está activo
            try:
                if pygame.get_init():
                    pygame.display.quit()
                    pygame.quit()
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Error limpiando Pygame: {e}")
    
    def _cleanup_hardware(self, game: BaseGame):
        """Limpiar recursos de hardware"""
        try:
            # Piano modular
            if hasattr(game, 'hardware_manager'):
                if hasattr(game.hardware_manager, 'cleanup'):
                    game.hardware_manager.cleanup()
                print("✅ Hardware manager limpiado")
            
            # LCD
            if hasattr(game, 'lcd') and game.lcd:
                try:
                    game.lcd.clear()
                    print("✅ LCD limpiado")
                except:
                    pass
            
            # LEDs (Simon)
            if hasattr(game, 'leds') and game.leds:
                try:
                    for led in game.leds:
                        if led:
                            led.write(0)
                    print("✅ LEDs apagados")
                except:
                    pass
            
            # Buzzer
            if hasattr(game, 'buzzer') and game.buzzer:
                try:
                    game.buzzer.write(0)
                    print("✅ Buzzer apagado")
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error limpiando hardware: {e}")
    
    def emergency_stop_all(self):
        """Parada de emergencia para todos los recursos"""
        print("🚨 PARADA DE EMERGENCIA - Limpiando todos los recursos")
        
        try:
            # Detener todo el audio
            pygame.mixer.stop()
            pygame.mixer.quit()
        except:
            pass
        
        try:
            # Cerrar pygame completamente
            if pygame.get_init():
                pygame.display.quit()
                pygame.quit()
        except:
            pass
        
        # Resetear estado
        self.current_game = None
        self.stop_in_progress = False
        
        print("✅ Parada de emergencia completada")
    
    def is_game_running(self) -> bool:
        """Verificar si hay un juego ejecutándose"""
        return (self.current_game is not None and 
                hasattr(self.current_game, 'running') and 
                self.current_game.running) 