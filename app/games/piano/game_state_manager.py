"""
Gestor de Estado del Juego - RESPONSABILIDAD ÚNICA
Maneja correctamente el ciclo de vida del juego y evita bugs de threading
"""

import threading
import time
from enum import Enum
from typing import Callable, Optional


class GameLifecycleState(Enum):
    """Estados del ciclo de vida del juego"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class GameStateManager:
    """Gestor robusto del estado del juego - PREVIENE BUGS DE THREADING"""
    
    def __init__(self):
        # Estado del ciclo de vida
        self.lifecycle_state = GameLifecycleState.STOPPED
        self.state_lock = threading.Lock()
        
        # Control de hilos
        self.game_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Callbacks de limpieza
        self.cleanup_callbacks: list[Callable] = []
        
        # Estadísticas
        self.start_time = None
        self.total_runs = 0
        
    def is_running(self) -> bool:
        """¿Está el juego actualmente ejecutándose?"""
        with self.state_lock:
            return self.lifecycle_state == GameLifecycleState.RUNNING
    
    def can_start(self) -> bool:
        """¿Se puede iniciar el juego?"""
        with self.state_lock:
            return self.lifecycle_state in [GameLifecycleState.STOPPED, GameLifecycleState.ERROR]
    
    def start_game(self, game_loop_func: Callable, *args, **kwargs) -> bool:
        """Iniciar juego de forma segura"""
        with self.state_lock:
            if not self.can_start():
                print(f"❌ No se puede iniciar: estado actual {self.lifecycle_state.value}")
                return False
            
            # Limpiar estado previo
            self._cleanup_previous_run()
            
            # Cambiar estado
            self.lifecycle_state = GameLifecycleState.STARTING
            self.stop_event.clear()
            
        try:
            # Crear nuevo hilo
            self.game_thread = threading.Thread(
                target=self._run_game_safely,
                args=(game_loop_func, args, kwargs),
                daemon=True,
                name="GameThread"
            )
            
            self.game_thread.start()
            self.start_time = time.time()
            self.total_runs += 1
            
            # Esperar a que inicie correctamente
            time.sleep(0.1)
            
            with self.state_lock:
                if self.lifecycle_state == GameLifecycleState.STARTING:
                    self.lifecycle_state = GameLifecycleState.RUNNING
                    
            print(f"✅ Juego iniciado correctamente (run #{self.total_runs})")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            with self.state_lock:
                self.lifecycle_state = GameLifecycleState.ERROR
            return False
    
    def stop_game(self, timeout: float = 3.0) -> bool:
        """Detener juego de forma segura"""
        with self.state_lock:
            if self.lifecycle_state == GameLifecycleState.STOPPED:
                return True
                
            print("🛑 Deteniendo juego...")
            self.lifecycle_state = GameLifecycleState.STOPPING
        
        # Señalar parada
        self.stop_event.set()
        
        # Esperar a que termine el hilo
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=timeout)
            
            # Si no terminó, es problemático pero no fatal
            if self.game_thread.is_alive():
                print("⚠️ El hilo del juego no terminó limpiamente")
        
        # Ejecutar limpieza
        self._execute_cleanup()
        
        with self.state_lock:
            self.lifecycle_state = GameLifecycleState.STOPPED
            
        print("✅ Juego detenido correctamente")
        return True
    
    def should_continue(self) -> bool:
        """¿Debería continuar el loop del juego?"""
        return not self.stop_event.is_set() and self.is_running()
    
    def add_cleanup_callback(self, callback: Callable):
        """Añadir función de limpieza"""
        self.cleanup_callbacks.append(callback)
    
    def get_status(self) -> dict:
        """Obtener estado actual del gestor"""
        with self.state_lock:
            return {
                'lifecycle_state': self.lifecycle_state.value,
                'is_running': self.is_running(),
                'can_start': self.can_start(),
                'total_runs': self.total_runs,
                'uptime': time.time() - self.start_time if self.start_time else 0,
                'thread_alive': self.game_thread.is_alive() if self.game_thread else False
            }
    
    def _run_game_safely(self, game_loop_func: Callable, args: tuple, kwargs: dict):
        """Ejecutar el loop del juego con manejo de errores"""
        try:
            print("🎮 Iniciando loop del juego...")
            game_loop_func(*args, **kwargs)
            
        except Exception as e:
            print(f"❌ Error en loop del juego: {e}")
            with self.state_lock:
                self.lifecycle_state = GameLifecycleState.ERROR
                
        finally:
            print("🔄 Loop del juego terminado")
            with self.state_lock:
                if self.lifecycle_state != GameLifecycleState.ERROR:
                    self.lifecycle_state = GameLifecycleState.STOPPED
    
    def _cleanup_previous_run(self):
        """Limpiar estado de ejecución anterior"""
        if self.game_thread and self.game_thread.is_alive():
            print("⚠️ Limpiando hilo anterior...")
            self.stop_event.set()
            self.game_thread.join(timeout=1.0)
        
        self.game_thread = None
        self.start_time = None
    
    def _execute_cleanup(self):
        """Ejecutar todas las funciones de limpieza"""
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"⚠️ Error en limpieza: {e}") 