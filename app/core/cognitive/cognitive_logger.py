"""
Logger Cognitivo - RESPONSABILIDAD ÚNICA
Registra eventos cognitivos con estructura de carpetas organizada por juego
"""

import csv
import os
from datetime import datetime
from typing import Dict, Any, Optional


class CognitiveLogger:
    """Logger súper simple para eventos cognitivos - ORGANIZADO POR JUEGO"""
    
    def __init__(self, game_type: str, patient_id: str, enable_logging: bool = True):
        self.game_type = game_type.lower().replace(" ", "_")
        self.patient_id = patient_id
        self.enable_logging = enable_logging
        
        # Estructura organizada: data/cognitive/{game_type}/sessions/
        self.base_dir = f"data/cognitive/{self.game_type}"
        self.sessions_dir = f"{self.base_dir}/sessions"
        
        # Archivo de sesión con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{patient_id}_{self.game_type}_{timestamp}"
        self.log_file = f"{self.sessions_dir}/{self.session_id}.csv"
        
        self.events_logged = 0
        
        if self.enable_logging:
            self._ensure_directories()
            self._initialize_csv()
    
    def _ensure_directories(self):
        """Crear estructura de directorios si no existe"""
        os.makedirs(self.sessions_dir, exist_ok=True)
        print(f"📁 Directorio creado: {self.sessions_dir}")
    
    def _create_csv_file(self) -> str:
        """Crear archivo CSV con headers apropiados"""
        filename = f"{self.session_id}.csv"
        filepath = os.path.join(self.data_dir, filename)
        
        # Headers específicos por tipo de juego
        if self.game_type == "piano_simon" or self.game_type == "piano_digital":
            headers = [
                "timestamp", "session_id", "level", "sequence_length", 
                "presentation_time_ms", "response_time_ms", "accuracy",
                "error_type", "sequence_shown", "sequence_input", 
                "reaction_latency_ms", "is_correct", "error_position"
            ]
        elif self.game_type == "two_lane_runner":
            headers = [
                "timestamp", "session_id", "obstacle_position", 
                "reaction_time_ms", "success", "lane_change_accuracy",
                "speed_level", "decision_time_ms"
            ]
        elif self.game_type == "osu_rhythm":
            headers = [
                "timestamp", "session_id", "circle_x", "circle_y", 
                "cursor_x", "cursor_y", "spawn_time", "hit_time",
                "reaction_time_ms", "spatial_accuracy", "temporal_accuracy",
                "hit_result", "score", "combo", "difficulty_level"
            ]
        else:
            # Headers genéricos para otros juegos
            headers = [
                "timestamp", "session_id", "event_type", "value", 
                "reaction_time_ms", "accuracy", "success"
            ]
        
        # Crear archivo con headers
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
        
        return filepath
    
    def log_piano_event(self, level: int, sequence_shown: list, sequence_input: list,
                       presentation_time: float, response_time: float, **kwargs):
        """Log específico para Piano-Simon - Súper directo"""
        
        # Calcular métricas básicas
        accuracy = self._calculate_accuracy(sequence_shown, sequence_input)
        error_type = self._detect_error_type(sequence_shown, sequence_input)
        error_position = self._find_error_position(sequence_shown, sequence_input)
        is_correct = accuracy == 1.0
        
        # Datos para CSV
        row_data = [
            datetime.now().isoformat(),
            self.session_id,
            level,
            len(sequence_shown),
            presentation_time,
            response_time,
            accuracy,
            error_type,
            '|'.join(map(str, sequence_shown)),  # Simple: separar con |
            '|'.join(map(str, sequence_input)),
            kwargs.get('reaction_latency', 0),
            is_correct,
            error_position
        ]
        
        self._write_row(row_data)
        print(f"📊 Piano event logged: L{level}, Acc:{accuracy:.2f}")
    
    def log_runner_event(self, obstacle_position: str, reaction_time: float,
                        success: bool, lane_accuracy: float, speed_level: int, **kwargs):
        """Log específico para Two-Lane Runner"""
        
        row_data = [
            datetime.now().isoformat(),
            self.session_id,
            obstacle_position,
            reaction_time,
            success,
            lane_accuracy,
            speed_level,
            kwargs.get('decision_time', 0)
        ]
        
        self._write_row(row_data)
        print(f"🏃 Runner event logged: {obstacle_position}, Success:{success}")
    
    def log_generic_event(self, event_type: str, value: Any, 
                         reaction_time: float = 0, accuracy: float = 0, 
                         success: bool = False):
        """Log genérico para otros juegos"""
        
        row_data = [
            datetime.now().isoformat(),
            self.session_id,
            event_type,
            str(value),
            reaction_time,
            accuracy,
            success
        ]
        
        self._write_row(row_data)
        print(f"🎮 Generic event logged: {event_type}")
    
    def log_osu_event(self, circle_x: int, circle_y: int, cursor_x: int, cursor_y: int,
                     spawn_time: float, hit_time: float, reaction_time: float,
                     spatial_accuracy: float, temporal_accuracy: float, hit_result: str,
                     score: int, combo: int, difficulty_level: int):
        """Log específico para juego Osu - Precisión espacial y temporal"""
        
        row_data = [
            datetime.now().isoformat(),
            self.session_id,
            circle_x,
            circle_y,
            cursor_x,
            cursor_y,
            spawn_time,
            hit_time,
            reaction_time,
            spatial_accuracy,
            temporal_accuracy,
            hit_result,
            score,
            combo,
            difficulty_level
        ]
        
        self._write_row(row_data)
        print(f"🎯 Osu event logged: {hit_result}, Spatial:{spatial_accuracy:.1f}%, Temporal:{temporal_accuracy:.1f}%")
    
    def _write_row(self, row_data: list):
        """Escribir fila al CSV - Súper simple"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(row_data)
        except Exception as e:
            print(f"❌ Error logging evento: {e}")
            return False
    
    def _get_all_headers(self) -> list:
        """Obtener todos los headers (comunes + específicos)"""
        common = [
            'timestamp', 'session_id', 'game_type', 'level',
            'response_time_ms', 'accuracy', 'is_correct'
        ]
        return common + self._get_game_specific_headers()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Obtener información de la sesión actual"""
        return {
            'session_id': self.session_id,
            'game_type': self.game_type,
            'patient_id': self.patient_id,
            'log_file': self.log_file,
            'events_logged': self.events_logged,
            'enable_logging': self.enable_logging
        }
    
    def finalize_session(self) -> Dict[str, Any]:
        """Finalizar sesión y retornar resumen"""
        if not self.enable_logging:
            return {'status': 'logging_disabled'}
            
        try:
            session_summary = {
                'session_id': self.session_id,
                'game_type': self.game_type,
                'patient_id': self.patient_id,
                'total_events': self.events_logged,
                'file_path': self.log_file,
                'status': 'completed'
            }
            
            print(f"✅ Sesión finalizada: {self.events_logged} eventos registrados")
            return session_summary
            
        except Exception as e:
            print(f"❌ Error finalizando sesión: {e}")
            return {'status': 'error', 'error': str(e)} 