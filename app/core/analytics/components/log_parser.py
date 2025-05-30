"""
Parser especializado para carga y procesamiento de logs de juegos
"""

import os
import re
from datetime import datetime
from typing import Dict, List


class LogParser:
    """Especialista en carga y parseo de archivos de log de juegos"""
    
    def __init__(self, log_dir: str = "app/data"):
        self.log_dir = log_dir
        self.games_data: Dict[str, List[Dict]] = {}
    
    def load_all_logs(self) -> Dict[str, List[Dict]]:
        """Cargar todos los archivos de log disponibles"""
        if not os.path.exists(self.log_dir):
            print(f"❌ Directorio de logs no encontrado: {self.log_dir}")
            return {}

        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".log")]

        for log_file in log_files:
            game_name = self._extract_game_name(log_file)
            log_path = os.path.join(self.log_dir, log_file)

            try:
                self.games_data[game_name] = self.parse_log_file(log_path)
                print(f"✅ Log cargado: {game_name} ({len(self.games_data[game_name])} eventos)")
            except Exception as e:
                print(f"❌ Error cargando {log_file}: {e}")

        return self.games_data
    
    def _extract_game_name(self, log_file: str) -> str:
        """Extraer nombre del juego desde el archivo de log"""
        return log_file.replace(".log", "").replace("_", " ").title()
    
    def parse_log_file(self, log_path: str) -> List[Dict]:
        """Parsear archivo de log y extraer eventos estructurados"""
        events = []

        with open(log_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                try:
                    event = self._parse_log_line(line.strip(), line_num)
                    if event:
                        events.append(event)
                except Exception as e:
                    print(f"⚠️ Error parseando línea {line_num}: {e}")
                    continue

        return events
    
    def _parse_log_line(self, line: str, line_num: int) -> Dict:
        """Parsear una línea individual del log"""
        # Patrón: 2025-05-25 22:57:24 | INFO | [EVENT_TYPE] message
        pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+) \| \[([A-Z_]+)\] (.+)"
        match = re.match(pattern, line)

        if not match:
            return None

        timestamp_str, level, event_type, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        event = {
            "timestamp": timestamp,
            "level": level,
            "event_type": event_type,
            "message": message,
            "line_number": line_num,
        }

        # Extraer información específica según el tipo de evento
        self._extract_specific_data(event)
        return event
    
    def _extract_specific_data(self, event: Dict):
        """Extraer datos específicos según el tipo de evento"""
        message = event["message"]

        # Extraer scores usando regex
        score_match = re.search(r"Score:?\s*(\d+)", message)
        if score_match:
            event["score"] = int(score_match.group(1))

        # Extraer posiciones de pelota/jugador
        pos_match = re.search(r"\((\d+),\s*(\d+)\)", message)
        if pos_match:
            event["x_pos"] = int(pos_match.group(1))
            event["y_pos"] = int(pos_match.group(2))

        # Extraer velocidad
        speed_match = re.search(r"Speed:?\s*([\d.]+)s?", message)
        if speed_match:
            event["speed"] = float(speed_match.group(1))

        # Extraer duración de juego
        duration_match = re.search(r"Duration:?\s*([\d.]+)s", message)
        if duration_match:
            event["game_duration"] = float(duration_match.group(1))

        # Detectar eventos especiales
        self._detect_special_events(event, message)
    
    def _detect_special_events(self, event: Dict, message: str):
        """Detectar eventos especiales como muertes, hits exitosos, etc."""
        # Detectar muertes/game over
        if "PLAYER DEATH" in message or "GAME OVER" in message:
            event["is_death"] = True

        # Detectar hits exitosos
        if "GOLPE EXITOSO" in message or "esquivado" in message:
            event["is_success"] = True

        # Detectar pausas
        if "PAUSADO" in message or "PAUSED" in message:
            event["is_pause"] = True

        # Detectar inicios de juego
        if "JUEGO INICIADO" in message or "GAME STARTED" in message:
            event["is_game_start"] = True
    
    def get_games_data(self) -> Dict[str, List[Dict]]:
        """Obtener datos de juegos cargados"""
        return self.games_data
    
    def get_game_data(self, game_name: str) -> List[Dict]:
        """Obtener datos de un juego específico"""
        return self.games_data.get(game_name, [])
    
    def list_available_games(self) -> List[str]:
        """Listar juegos disponibles"""
        return list(self.games_data.keys())
    
    def get_events_by_type(self, game_name: str, event_type: str) -> List[Dict]:
        """Filtrar eventos por tipo específico"""
        game_data = self.get_game_data(game_name)
        return [e for e in game_data if e["event_type"] == event_type]
    
    def get_events_by_level(self, game_name: str, level: str) -> List[Dict]:
        """Filtrar eventos por nivel (INFO, WARNING, ERROR)"""
        game_data = self.get_game_data(game_name)
        return [e for e in game_data if e["level"] == level]
    
    def get_game_summary(self, game_name: str) -> Dict:
        """Obtener resumen rápido de un juego"""
        events = self.get_game_data(game_name)
        
        if not events:
            return {}

        return {
            "total_events": len(events),
            "errors": len([e for e in events if e["level"] == "ERROR"]),
            "deaths": len([e for e in events if e.get("is_death", False)]),
            "max_score": max([e.get("score", 0) for e in events]),
            "total_duration": sum([e.get("game_duration", 0) for e in events]),
            "first_event": events[0]["timestamp"] if events else None,
            "last_event": events[-1]["timestamp"] if events else None,
        } 