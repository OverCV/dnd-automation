import time
import random
import threading
from typing import List, Dict, Any, Optional
from enum import Enum

# Importar logging cognitivo - SÚPER SIMPLE
try:
    from ...core.cognitive import SessionManager
    COGNITIVE_LOGGING_AVAILABLE = True
except ImportError:
    COGNITIVE_LOGGING_AVAILABLE = False
    print("⚠️ Logging cognitivo no disponible")


class GameState(Enum):
    WAITING_TO_START = 0
    SHOWING_SEQUENCE = 1
    PLAYER_INPUT = 2
    GAME_OVER = 3
    GAME_WON = 4
    LEVEL_COMPLETE = 5


class PianoGameLogic:
    """Maneja exclusivamente la lógica del juego Simon Says"""
    
    def __init__(self, enable_cognitive_logging: bool = False, patient_id: str = "default"):
        # Constantes del juego Simon
        self.MAX_LEVEL = 20
        self.INITIAL_DELAY = 800  # ms entre notas en secuencia
        self.MIN_DELAY = 300
        self.START_DELAY = 1500
        self.PLAYER_TIMEOUT = 5000  # 5 segundos para responder
        
        # Variables del juego Simon
        self.game_sequence = []
        self.player_level = 1
        self.input_count = 0
        self.game_state = GameState.WAITING_TO_START
        self.sequence_index = 0
        self.last_sequence_time = 0
        self.last_input_time = 0
        
        # Estadísticas
        self.total_games = 0
        self.best_level = 0
        self.perfect_games = 0
        
        # Estado del juego
        self.game_message = "Presiona cualquier tecla para empezar"
        
        # LOGGING COGNITIVO - Solo si está habilitado
        self.cognitive_logging = enable_cognitive_logging and COGNITIVE_LOGGING_AVAILABLE
        self.session_manager: Optional[SessionManager] = None
        self.current_logger = None
        self.sequence_start_time = 0
        self.patient_id = patient_id
        
        if self.cognitive_logging:
            try:
                self.session_manager = SessionManager()
                print("🧠 Logging cognitivo habilitado para Piano-Simon")
            except Exception as e:
                print(f"❌ Error iniciando logging cognitivo: {e}")
                self.cognitive_logging = False
        
        # Callbacks para efectos externos
        self.on_play_note = None
        self.on_highlight_note = None
        self.on_clear_highlight = None
        self.on_game_over = None
        self.on_victory = None
    
    def set_callbacks(self, on_play_note=None, on_highlight_note=None, 
                     on_clear_highlight=None, on_game_over=None, on_victory=None):
        """Configurar callbacks para efectos externos"""
        self.on_play_note = on_play_note
        self.on_highlight_note = on_highlight_note
        self.on_clear_highlight = on_clear_highlight
        self.on_game_over = on_game_over
        self.on_victory = on_victory
    
    def reset_game(self):
        """Resetear estado del juego"""
        self.player_level = 1
        self.input_count = 0
        self.sequence_index = 0
        self.game_state = GameState.WAITING_TO_START
        
        # Generar nueva secuencia aleatoria
        self.game_sequence = [random.randint(0, 7) for _ in range(self.MAX_LEVEL)]
        self.game_message = "Presiona cualquier tecla para empezar"
        
        # COGNITIVE LOGGING: Iniciar nueva sesión si está habilitado
        if self.cognitive_logging and self.session_manager:
            try:
                self.current_logger = self.session_manager.start_session("piano_simon", self.patient_id)
            except Exception as e:
                print(f"❌ Error iniciando sesión cognitiva: {e}")
        
        print(f"🔄 Juego reiniciado - Secuencia generada para {self.MAX_LEVEL} niveles")
    
    def start_game_with_button(self, button_index: int):
        """Iniciar juego cuando se presiona un botón"""
        if self.game_state == GameState.WAITING_TO_START:
            print(f"🎮 Juego iniciado con botón {button_index + 1}")
            self.game_message = f"Nivel {self.player_level} - Observa la secuencia"
            self.game_state = GameState.SHOWING_SEQUENCE
            self.sequence_index = 0
            self.last_sequence_time = time.time() * 1000
            
            # COGNITIVE LOGGING: Marcar inicio de secuencia
            self.sequence_start_time = time.time() * 1000
            
            return True
        return False
    
    def update_sequence_display(self, current_time: float) -> bool:
        """Actualizar mostrar secuencia - devuelve True si hay cambios"""
        if self.game_state != GameState.SHOWING_SEQUENCE:
            return False
            
        delay_time = max(self.MIN_DELAY, self.INITIAL_DELAY - (self.player_level * 20))
        
        if current_time - self.last_sequence_time >= delay_time:
            if self.sequence_index < self.player_level:
                # Mostrar siguiente nota de la secuencia
                note_index = self.game_sequence[self.sequence_index]
                
                # Reproducir nota y highlight
                if self.on_play_note:
                    self.on_play_note(note_index, 0.5)
                if self.on_highlight_note:
                    self.on_highlight_note(note_index)
                
                print(f"🎵 Secuencia {self.sequence_index + 1}/{self.player_level}: Nota {note_index + 1}")
                
                self.sequence_index += 1
                self.last_sequence_time = current_time
                
                # Programar apagado del highlight
                if self.on_clear_highlight:
                    threading.Timer(
                        delay_time / 2000.0, 
                        self.on_clear_highlight, 
                        [note_index]
                    ).start()
                
                return True
                
            else:
                # Secuencia completada, turno del jugador
                print("👤 Tu turno - Repite la secuencia")
                self.game_message = f"Tu turno - Repite la secuencia ({self.player_level} notas)"
                self.game_state = GameState.PLAYER_INPUT
                self.input_count = 0
                self.last_input_time = current_time
                return True
        
        return False
    
    def check_player_timeout(self, current_time: float) -> bool:
        """Verificar timeout del jugador"""
        if self.game_state == GameState.PLAYER_INPUT:
            if current_time - self.last_input_time > self.PLAYER_TIMEOUT:
                print("⏰ Timeout - Game Over")
                self.game_message = "Timeout - ¡Demasiado lento!"
                self.game_state = GameState.GAME_OVER
                return True
        return False
    
    def process_player_input(self, note_index: int) -> bool:
        """Procesar entrada del jugador - devuelve True si es correcta"""
        if self.game_state != GameState.PLAYER_INPUT:
            return False
            
        current_time = time.time() * 1000
        expected_note = self.game_sequence[self.input_count]
        
        # Reproducir nota presionada
        if self.on_play_note:
            self.on_play_note(note_index, 0.4)
        
        # COGNITIVE LOGGING: Calcular tiempos para logging
        response_time = current_time - self.sequence_start_time if self.sequence_start_time > 0 else 0
        presentation_time = self.last_input_time - self.sequence_start_time if self.last_input_time > 0 else 0
        
        is_correct = note_index == expected_note
        
        # COGNITIVE LOGGING: Log del evento si está habilitado
        if self.cognitive_logging and self.current_logger:
            try:
                # Preparar secuencias para logging
                sequence_shown = self.game_sequence[:self.player_level]
                sequence_input = self.game_sequence[:self.input_count] + [note_index]
                
                self.current_logger.log_piano_event(
                    level=self.player_level,
                    sequence_shown=sequence_shown,
                    sequence_input=sequence_input,
                    presentation_time=presentation_time,
                    response_time=response_time,
                    reaction_latency=current_time - self.last_input_time
                )
            except Exception as e:
                print(f"❌ Error logging evento cognitivo: {e}")
        
        if is_correct:
            # Respuesta correcta
            self.input_count += 1
            print(f"✅ Correcto: Nota {note_index + 1} ({self.input_count}/{self.player_level})")
            self.game_message = f"¡Correcto! {self.input_count}/{self.player_level}"
            
            if self.input_count >= self.player_level:
                # Nivel completado
                print(f"🎉 Nivel {self.player_level} completado!")
                self.game_state = GameState.LEVEL_COMPLETE
            
            return True
        else:
            # Respuesta incorrecta
            print(f"❌ Error: esperaba nota {expected_note + 1}, tocaste nota {note_index + 1}")
            self.game_message = f"Error: esperaba nota {expected_note + 1}, tocaste nota {note_index + 1}"
            self.game_state = GameState.GAME_OVER
            return False
    
    def handle_level_complete(self):
        """Manejar completar nivel"""
        if self.game_state != GameState.LEVEL_COMPLETE:
            return
            
        if self.player_level >= self.MAX_LEVEL:
            # Juego ganado
            print("🏆 ¡Juego completado! ¡Felicitaciones!")
            self.game_message = "¡FELICITACIONES! ¡Completaste todos los niveles!"
            self.game_state = GameState.GAME_WON
            self.perfect_games += 1
            
            if self.on_victory:
                self.on_victory()
        else:
            # Avanzar al siguiente nivel
            self.player_level += 1
            print(f"⬆️ Avanzando al nivel {self.player_level}")
            self.game_message = f"¡Avanzando al nivel {self.player_level}!"
            self.game_state = GameState.SHOWING_SEQUENCE
            self.sequence_index = 0
            self.last_sequence_time = time.time() * 1000 + self.START_DELAY
    
    def handle_game_over(self):
        """Manejar game over"""
        if self.game_state != GameState.GAME_OVER:
            return
            
        if self.on_game_over:
            self.on_game_over()
        
        # Actualizar estadísticas
        self.total_games += 1
        if self.player_level > self.best_level:
            self.best_level = self.player_level
        
        # COGNITIVE LOGGING: Cerrar sesión si está habilitado
        if self.cognitive_logging and self.session_manager:
            try:
                csv_file = self.session_manager.end_session()
                if csv_file:
                    print(f"🧠 Datos cognitivos guardados: {csv_file}")
            except Exception as e:
                print(f"❌ Error cerrando sesión cognitiva: {e}")
        
        print(f"💀 Game Over - Nivel alcanzado: {self.player_level}")
        print(f"📊 Mejor nivel: {self.best_level}")
        
        # Resetear después de un delay
        threading.Timer(2.0, self.reset_game).start()
    
    def handle_game_won(self):
        """Manejar victoria"""
        if self.game_state != GameState.GAME_WON:
            return
            
        # Actualizar estadísticas
        self.total_games += 1
        self.best_level = self.MAX_LEVEL
        
        # COGNITIVE LOGGING: Cerrar sesión si está habilitado
        if self.cognitive_logging and self.session_manager:
            try:
                csv_file = self.session_manager.end_session()
                if csv_file:
                    print(f"🧠 ¡Sesión perfecta guardada!: {csv_file}")
            except Exception as e:
                print(f"❌ Error cerrando sesión cognitiva: {e}")
        
        print("🏆 ¡VICTORIA TOTAL!")
        
        # Resetear después de un delay
        threading.Timer(3.0, self.reset_game).start()
    
    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado actual del juego"""
        return {
            "game_state": self.game_state,
            "player_level": self.player_level,
            "max_level": self.MAX_LEVEL,
            "sequence_length": len(self.game_sequence),
            "input_progress": self.input_count,
            "total_games": self.total_games,
            "best_level": self.best_level,
            "perfect_games": self.perfect_games,
            "current_sequence": self.game_sequence[: self.player_level] if self.game_sequence else [],
            "game_message": self.game_message
        }
    
    def is_waiting_for_input(self) -> bool:
        """Verificar si está esperando entrada del jugador"""
        return self.game_state == GameState.PLAYER_INPUT
    
    def is_showing_sequence(self) -> bool:
        """Verificar si está mostrando secuencia"""
        return self.game_state == GameState.SHOWING_SEQUENCE
    
    def is_waiting_to_start(self) -> bool:
        """Verificar si está esperando para empezar"""
        return self.game_state == GameState.WAITING_TO_START 