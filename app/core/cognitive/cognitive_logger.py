"""
Logger cognitivo simple - Solo CSV, nada complicado
"""

import csv
import os
from datetime import datetime
from typing import Dict, Any


class CognitiveLogger:
    """Logger súper simple para métricas cognitivas - Solo CSV"""
    
    def __init__(self, game_type: str, patient_id: str = "default"):
        self.game_type = game_type
        self.patient_id = patient_id
        self.session_id = self._generate_session_id()
        self.data_dir = "data/cognitive"
        
        # Asegurar que existe el directorio ANTES de crear el archivo
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.csv_file = self._create_csv_file()
        
        print(f"🧠 Logger cognitivo iniciado: {self.csv_file}")
    
    def _generate_session_id(self) -> str:
        """Generar ID de sesión simple"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.patient_id}_{self.game_type}_{timestamp}"
    
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
            print(f"❌ Error escribiendo CSV: {e}")
    
    def _calculate_accuracy(self, shown: list, input_seq: list) -> float:
        """Calcular precisión simple"""
        if not shown or not input_seq:
            return 0.0
        
        min_length = min(len(shown), len(input_seq))
        correct = sum(1 for i in range(min_length) if shown[i] == input_seq[i])
        return correct / len(shown)
    
    def _detect_error_type(self, shown: list, input_seq: list) -> str:
        """Detectar tipo de error simple"""
        if not input_seq:
            return "no_response"
        
        if len(input_seq) < len(shown):
            return "incomplete"
        elif len(input_seq) > len(shown):
            return "extra_input"
        elif shown != input_seq:
            return "sequence_error"
        else:
            return "correct"
    
    def _find_error_position(self, shown: list, input_seq: list) -> int:
        """Encontrar posición del primer error"""
        if not shown or not input_seq:
            return -1
        
        for i, (expected, actual) in enumerate(zip(shown, input_seq)):
            if expected != actual:
                return i
        
        return -1  # No hay errores en la parte común
    
    def close_session(self):
        """Cerrar sesión y mostrar resumen"""
        if os.path.exists(self.csv_file):
            # Contar líneas (eventos)
            with open(self.csv_file, 'r') as file:
                line_count = len(file.readlines()) - 1  # -1 por header
            
            print(f"✅ Sesión cognitiva completada: {line_count} eventos guardados")
            print(f"📄 Archivo: {self.csv_file}")
            return self.csv_file
        else:
            print("⚠️ No se encontró archivo de sesión")
            return None 