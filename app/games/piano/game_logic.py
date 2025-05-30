import time
import random
import threading
from typing import List, Dict, Any
from enum import Enum


class GameState(Enum):
    WAITING_TO_START = 0
    SHOWING_SEQUENCE = 1
    PLAYER_INPUT = 2
    GAME_OVER = 3
    GAME_WON = 4
    LEVEL_COMPLETE = 5


class PianoGameLogic:
    """Maneja exclusivamente la lógica del juego Simon Says"""
    
    def __init__(self):
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
        
        print(f"🔄 Juego reiniciado - Secuencia generada para {self.MAX_LEVEL} niveles")
    
    def start_game_with_button(self, button_index: int):
        """Iniciar juego cuando se presiona un botón"""
        if self.game_state == GameState.WAITING_TO_START:
            print(f"🎮 Juego iniciado con botón {button_index + 1}")
            self.game_message = f"Nivel {self.player_level} - Observa la secuencia"
            self.game_state = GameState.SHOWING_SEQUENCE
            self.sequence_index = 0
            self.last_sequence_time = time.time() * 1000
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
            
        expected_note = self.game_sequence[self.input_count]
        
        # Reproducir nota presionada
        if self.on_play_note:
            self.on_play_note(note_index, 0.4)
        
        if note_index == expected_note:
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