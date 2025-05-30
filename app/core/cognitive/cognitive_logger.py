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
    
    def _initialize_csv(self):
        """Inicializar archivo CSV con headers específicos del juego"""
        try:
            # Headers comunes para todos los juegos
            common_headers = [
                'timestamp',
                'session_id', 
                'game_type',
                'level',
                'response_time_ms',
                'accuracy',
                'is_correct'
            ]
            
            # Headers específicos por tipo de juego
            game_specific_headers = self._get_game_specific_headers()
            
            headers = common_headers + game_specific_headers
            
            with open(self.log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
            print(f"📊 Archivo CSV inicializado: {self.log_file}")
            
        except Exception as e:
            print(f"❌ Error inicializando CSV: {e}")
    
    def _get_game_specific_headers(self) -> list:
        """Obtener headers específicos según el tipo de juego"""
        if self.game_type == "piano_simon":
            return [
                'sequence_length',
                'presentation_time_ms', 
                'error_type',
                'sequence_shown',
                'sequence_input',
                'reaction_latency_ms',
                'error_position',
                'melody_name'
            ]
        elif self.game_type == "ping_pong":
            return [
                'ball_speed',
                'paddle_position',
                'hit_accuracy',
                'reaction_zone'
            ]
        elif self.game_type == "two_lanes":
            return [
                'lane_changed',
                'obstacle_type',
                'distance_to_obstacle',
                'decision_time_ms'
            ]
        else:
            # Headers genéricos para juegos no definidos
            return [
                'game_specific_data',
                'extra_info'
            ]
    
    def log_event(self, event_data: Dict[str, Any]) -> bool:
        """Registrar evento cognitivo"""
        if not self.enable_logging:
            return True
            
        try:
            # Datos comunes
            common_data = {
                'timestamp': datetime.now().isoformat(),
                'session_id': self.session_id,
                'game_type': self.game_type,
                'level': event_data.get('level', 1),
                'response_time_ms': event_data.get('response_time_ms', 0),
                'accuracy': event_data.get('accuracy', 0.0),
                'is_correct': event_data.get('is_correct', False)
            }
            
            # Combinar con datos específicos del juego
            full_data = {**common_data, **event_data}
            
            # Escribir al CSV
            with open(self.log_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self._get_all_headers())
                writer.writerow(full_data)
            
            self.events_logged += 1
            return True
            
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