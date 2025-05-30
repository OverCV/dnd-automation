"""
Lógica del Piano-Simon - RESPONSABILIDAD ÚNICA
Maneja reglas, estados y progresión del juego con MELODÍAS FAMOSAS
"""

import time
import random
from enum import Enum
from typing import List, Dict, Any, Callable, Optional, Tuple
from core.cognitive.cognitive_logger import CognitiveLogger


class GameState(Enum):
    WAITING_TO_START = 0
    SHOWING_SEQUENCE = 1
    PLAYER_INPUT = 2
    GAME_OVER = 3
    GAME_WON = 4
    LEVEL_COMPLETE = 5


class MelodyLibrary:
    """Biblioteca de melodías famosas adaptadas a 8 notas - DO RE MI FA SOL LA SI DO8"""
    
    def __init__(self):
        # Mapeo de notas: 0=Do, 1=Re, 2=Mi, 3=Fa, 4=Sol, 5=La, 6=Si, 7=Do8
        self.melodies = {
            1: {
                "name": "Frère Jacques",
                "sequence": [0, 1, 2, 0]  # Do Re Mi Do
            },
            2: {
                "name": "Himno de la Alegría",
                "sequence": [2, 2, 3, 4, 4]  # Mi Mi Fa Sol Sol
            },
            3: {
                "name": "Cumpleaños Feliz",
                "sequence": [0, 0, 1, 0, 3, 2]  # Do Do Re Do Fa Mi
            },
            4: {
                "name": "Mary Had a Little Lamb",
                "sequence": [2, 1, 0, 1, 2, 2, 2]  # Mi Re Do Re Mi Mi Mi
            },
            5: {
                "name": "Twinkle Twinkle",
                "sequence": [0, 0, 4, 4, 5, 5, 4]  # Do Do Sol Sol La La Sol
            },
            6: {
                "name": "Happy Birthday",
                "sequence": [0, 0, 7, 5, 3, 2]  # Do Do Do8 La Fa Mi
            },
            7: {
                "name": "Jingle Bells",
                "sequence": [2, 2, 2, 2, 2, 3, 4, 1]  # Mi Mi Mi Mi Mi Fa Sol Re
            },
            8: {
                "name": "London Bridge",
                "sequence": [4, 3, 2, 3, 4, 4, 4]  # Sol Fa Mi Fa Sol Sol Sol
            },
            9: {
                "name": "Old MacDonald",
                "sequence": [0, 0, 0, 4, 5, 5, 4]  # Do Do Do Sol La La Sol
            },
            10: {
                "name": "Final Challenge",
                "sequence": [0, 2, 4, 5, 7, 5, 4, 2, 0]  # Do Mi Sol La Do8 La Sol Mi Do
            }
        }
    
    def get_melody_for_level(self, level: int) -> Tuple[str, List[int]]:
        """Obtener melodía para un nivel específico"""
        if level in self.melodies:
            melody = self.melodies[level]
            return melody["name"], melody["sequence"]
        else:
            # Fallback para niveles no definidos
            return "Random Sequence", self._generate_random_sequence(level)
    
    def _generate_random_sequence(self, length: int) -> List[int]:
        """Generar secuencia aleatoria como fallback"""
        return [random.randint(0, 7) for _ in range(min(length, 8))]


class PianoGameLogic:
    """Lógica principal del Piano Simon con melodías famosas"""
    
    def __init__(self, enable_cognitive_logging: bool = True, patient_id: str = "default"):
        # Estado del juego
        self.game_state = GameState.WAITING_TO_START
        self.player_level = 1
        self.max_level = 10  # REDUCIDO de 20 a 10
        
        # Biblioteca de melodías
        self.melody_library = MelodyLibrary()
        
        # Secuencia actual
        self.game_sequence = []
        self.current_melody_name = ""
        self.player_input = []
        self.input_progress = 0
        
        # Timing
        self.sequence_start_time = 0
        self.input_start_time = 0
        self.current_note_start = 0
        self.note_display_duration = 800  # ms por nota
        self.note_gap_duration = 200     # ms entre notas
        
        # Estadísticas
        self.total_games = 0
        self.best_level = 0
        self.perfect_games = 0
        
        # Callbacks
        self.on_play_note: Optional[Callable] = None
        self.on_highlight_note: Optional[Callable] = None
        self.on_clear_highlight: Optional[Callable] = None
        self.on_game_over: Optional[Callable] = None
        self.on_victory: Optional[Callable] = None
        
        # Logging cognitivo
        self.cognitive_logger = None
        if enable_cognitive_logging:
            self.cognitive_logger = CognitiveLogger("piano_simon", patient_id)
        
        # Mensaje del juego
        self.game_message = "🎹 Presiona cualquier tecla para empezar"
        
        print(f"🎵 Piano Simon inicializado: max {self.max_level} niveles con melodías famosas")
    
    def set_callbacks(self, on_play_note=None, on_highlight_note=None, 
                     on_clear_highlight=None, on_game_over=None, on_victory=None):
        """Configurar callbacks de audio y visuales"""
        self.on_play_note = on_play_note
        self.on_highlight_note = on_highlight_note
        self.on_clear_highlight = on_clear_highlight
        self.on_game_over = on_game_over
        self.on_victory = on_victory
    
    def start_game_with_button(self, button_index: int):
        """Iniciar juego con botón presionado"""
        if self.game_state == GameState.WAITING_TO_START:
            print(f"🎮 Iniciando juego con tecla {button_index}")
            self.reset_game()
            self.start_level()
    
    def start_level(self):
        """Iniciar nuevo nivel con melodía específica"""
        # Obtener melodía para este nivel
        self.current_melody_name, self.game_sequence = self.melody_library.get_melody_for_level(self.player_level)
        
        # Resetear progreso del jugador
        self.player_input = []
        self.input_progress = 0
        
        # Cambiar estado y mostrar secuencia
        self.game_state = GameState.SHOWING_SEQUENCE
        self.sequence_start_time = time.time() * 1000
        self.current_note_start = self.sequence_start_time
        
        self.game_message = f"🎵 Nivel {self.player_level}: {self.current_melody_name}"
        
        print(f"🎵 Nivel {self.player_level}: {self.current_melody_name} - {self.game_sequence}")
    
    def update_sequence_display(self, current_time: float):
        """Actualizar display de secuencia durante SHOWING_SEQUENCE"""
        if self.game_state != GameState.SHOWING_SEQUENCE:
            return
        
        time_since_start = current_time - self.sequence_start_time
        note_cycle_time = self.note_display_duration + self.note_gap_duration
        
        # Calcular qué nota mostrar
        current_note_index = int(time_since_start // note_cycle_time)
        time_in_note_cycle = time_since_start % note_cycle_time
        
        if current_note_index < len(self.game_sequence):
            # Mostrar nota actual
            if time_in_note_cycle < self.note_display_duration:
                note_to_show = self.game_sequence[current_note_index]
                
                # Activar highlight y sonido
                if self.on_highlight_note:
                    self.on_highlight_note(note_to_show)
                
                if self.on_play_note and time_in_note_cycle < 50:  # Solo tocar al inicio
                    self.on_play_note(note_to_show, 0.6)
            else:
                # Gap entre notas
                if self.on_clear_highlight:
                    for i in range(8):
                        self.on_clear_highlight(i)
        else:
            # Secuencia completa - permitir input del jugador
            self.game_state = GameState.PLAYER_INPUT
            self.input_start_time = current_time
            self.game_message = f"🎯 Tu turno: repite '{self.current_melody_name}'"
            
            # Limpiar highlights
            if self.on_clear_highlight:
                for i in range(8):
                    self.on_clear_highlight(i)
    
    def process_player_input(self, button_index: int):
        """Procesar input del jugador"""
        if self.game_state != GameState.PLAYER_INPUT:
            return
        
        current_time = time.time() * 1000
        response_time = current_time - self.input_start_time
        
        # Añadir a secuencia del jugador
        self.player_input.append(button_index)
        expected_note = self.game_sequence[self.input_progress]
        is_correct = (button_index == expected_note)
        
        print(f"🎹 Input: {button_index}, Esperado: {expected_note}, Correcto: {is_correct}")
        
        # Log cognitivo del evento
        if self.cognitive_logger:
            self.cognitive_logger.log_event({
                'level': self.player_level,
                'sequence_length': len(self.game_sequence),
                'presentation_time_ms': self.note_display_duration * len(self.game_sequence),
                'response_time_ms': response_time,
                'accuracy': 1.0 if is_correct else 0.0,
                'is_correct': is_correct,
                'error_type': 'correct' if is_correct else 'wrong_note',
                'sequence_shown': '|'.join(map(str, self.game_sequence)),
                'sequence_input': '|'.join(map(str, self.player_input)),
                'reaction_latency_ms': response_time,
                'error_position': self.input_progress if not is_correct else -1,
                'melody_name': self.current_melody_name
            })
        
        if is_correct:
            self.input_progress += 1
            
            # Verificar si completó la secuencia
            if self.input_progress >= len(self.game_sequence):
                self.handle_level_complete()
        else:
            # Error - game over
            self.game_state = GameState.GAME_OVER
            self.game_message = f"❌ Error en '{self.current_melody_name}'. ¡Intenta de nuevo!"
            
            if self.on_game_over:
                self.on_game_over()
    
    def handle_level_complete(self):
        """Manejar nivel completado"""
        if self.game_state == GameState.PLAYER_INPUT and self.input_progress >= len(self.game_sequence):
            print(f"✅ Nivel {self.player_level} completado!")
            
            # Actualizar estadísticas
            if self.player_level > self.best_level:
                self.best_level = self.player_level
            
            # Verificar si ganó el juego completo
            if self.player_level >= self.max_level:
                self.game_state = GameState.GAME_WON
                self.game_message = f"🎉 ¡FELICIDADES! Completaste todas las melodías"
                self.perfect_games += 1
                
                if self.on_victory:
                    self.on_victory()
            else:
                # Avanzar al siguiente nivel
                self.game_state = GameState.LEVEL_COMPLETE
                self.player_level += 1
                self.game_message = f"🎵 ¡Excelente! Siguiente: Nivel {self.player_level}"
                
                # Después de 2 segundos, iniciar siguiente nivel
                time.sleep(0.1)  # Pequeña pausa para feedback visual
    
    def handle_game_over(self):
        """Manejar game over con opción de reiniciar"""
        if self.game_state == GameState.GAME_OVER:
            self.game_message = f"💀 Game Over en Nivel {self.player_level}. Presiona tecla para reiniciar"
    
    def handle_game_won(self):
        """Manejar victoria completa"""
        if self.game_state == GameState.GAME_WON:
            self.game_message = f"👑 ¡MAESTRO DE MELODÍAS! Presiona tecla para nuevo juego"
    
    def check_player_timeout(self, current_time: float):
        """Verificar timeout del jugador"""
        if self.game_state == GameState.PLAYER_INPUT:
            time_since_input_start = current_time - self.input_start_time
            timeout_limit = 10000  # 10 segundos
            
            if time_since_input_start > timeout_limit:
                print("⏰ Timeout del jugador")
                self.game_state = GameState.GAME_OVER
                self.game_message = f"⏰ Tiempo agotado en '{self.current_melody_name}'"
                
                if self.on_game_over:
                    self.on_game_over()
    
    def reset_game(self):
        """Resetear juego para nueva partida"""
        self.game_state = GameState.WAITING_TO_START
        self.player_level = 1
        self.game_sequence = []
        self.current_melody_name = ""
        self.player_input = []
        self.input_progress = 0
        self.total_games += 1
        
        self.game_message = "🎹 Presiona cualquier tecla para empezar"
        print(f"🔄 Juego reseteado (partida #{self.total_games})")
    
    def is_waiting_to_start(self) -> bool:
        """¿Está esperando a empezar?"""
        return self.game_state == GameState.WAITING_TO_START
    
    def is_waiting_for_input(self) -> bool:
        """¿Está esperando input del jugador?"""
        return self.game_state == GameState.PLAYER_INPUT
    
    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado completo del juego"""
        return {
            "game_state": self.game_state,
            "player_level": self.player_level,
            "max_level": self.max_level,
            "sequence_length": len(self.game_sequence),
            "input_progress": self.input_progress,
            "current_sequence": self.game_sequence.copy(),
            "current_melody": self.current_melody_name,
            "game_message": self.game_message,
            "total_games": self.total_games,
            "best_level": self.best_level,
            "perfect_games": self.perfect_games
        } 