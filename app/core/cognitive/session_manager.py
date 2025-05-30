"""
Gestor de Sesiones Cognitivas - RESPONSABILIDAD ÚNICA
Maneja listado y metadatos de sesiones organizadas por juego
"""

import os
import csv
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional


class SessionManager:
    """Gestor simple de sesiones cognitivas - ORGANIZADO POR JUEGO"""
    
    def __init__(self, base_dir: str = "data/cognitive"):
        self.base_dir = base_dir
        
        # Asegurar que existe el directorio
        os.makedirs(self.base_dir, exist_ok=True)
    
    def list_session_files(self, game_type: Optional[str] = None) -> List[str]:
        """Listar archivos de sesión, opcionalmente filtrados por juego"""
        session_files = []
        
        if game_type:
            # Buscar solo en el directorio específico del juego
            pattern = f"{self.base_dir}/{game_type}/sessions/*.csv"
            session_files = glob.glob(pattern)
        else:
            # Buscar en todos los directorios de juegos
            pattern = f"{self.base_dir}/*/sessions/*.csv"
            session_files = glob.glob(pattern)
        
        # Ordenar por fecha de modificación (más reciente primero)
        session_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return session_files
    
    def get_session_info(self, file_path: str) -> Dict[str, Any]:
        """Obtener información detallada de una sesión"""
        try:
            # Información básica del archivo
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            mod_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Extraer información del nombre del archivo
            filename = os.path.basename(file_path)
            session_id = filename.replace('.csv', '')
            
            # Determinar tipo de juego desde la ruta
            path_parts = file_path.replace('\\', '/').split('/')
            game_type = "unknown"
            for i, part in enumerate(path_parts):
                if part == "cognitive" and i + 1 < len(path_parts):
                    game_type = path_parts[i + 1]
                    break
            
            # Extraer patient_id del session_id
            patient_id = "unknown"
            if '_' in session_id:
                parts = session_id.split('_')
                if len(parts) >= 3:
                    patient_id = parts[0]
            
            # Contar eventos en el archivo
            event_count = self._count_events_in_file(file_path)
            
            return {
                'filepath': file_path,
                'session_id': session_id,
                'patient_id': patient_id,
                'game_type': game_type,
                'date': mod_time.strftime('%Y-%m-%d'),
                'time': mod_time.strftime('%H:%M:%S'),
                'file_size': file_size,
                'event_count': event_count
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo info de sesión {file_path}: {e}")
            return {
                'filepath': file_path,
                'session_id': 'error',
                'patient_id': 'unknown',
                'game_type': 'unknown',
                'date': 'unknown',
                'time': 'unknown',
                'file_size': 0,
                'event_count': 0
            }
    
    def _count_events_in_file(self, file_path: str) -> int:
        """Contar número de eventos en archivo CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Saltar header y contar filas
                next(reader, None)  # Skip header
                return sum(1 for _ in reader)
        except Exception as e:
            print(f"⚠️ Error contando eventos en {file_path}: {e}")
            return 0
    
    def get_sessions_by_game(self, game_type: str) -> List[Dict[str, Any]]:
        """Obtener sesiones específicas de un juego"""
        files = self.list_session_files(game_type)
        return [self.get_session_info(f) for f in files]
    
    def get_sessions_by_patient(self, patient_id: str) -> List[Dict[str, Any]]:
        """Obtener todas las sesiones de un paciente específico"""
        all_files = self.list_session_files()
        patient_sessions = []
        
        for file_path in all_files:
            session_info = self.get_session_info(file_path)
            if session_info['patient_id'] == patient_id:
                patient_sessions.append(session_info)
        
        return patient_sessions
    
    def get_available_games(self) -> List[str]:
        """Obtener lista de juegos que tienen datos"""
        games = set()
        
        # Buscar directorios en data/cognitive
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path) and item != "shared":
                    # Verificar si tiene sesiones
                    sessions_dir = os.path.join(item_path, "sessions")
                    if os.path.exists(sessions_dir) and os.listdir(sessions_dir):
                        games.add(item)
        
        return sorted(list(games))
    
    def get_available_patients(self) -> List[str]:
        """Obtener lista de pacientes que tienen datos"""
        patients = set()
        
        all_files = self.list_session_files()
        for file_path in all_files:
            session_info = self.get_session_info(file_path)
            if session_info['patient_id'] != 'unknown':
                patients.add(session_info['patient_id'])
        
        return sorted(list(patients))
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales"""
        all_files = self.list_session_files()
        games = self.get_available_games()
        patients = self.get_available_patients()
        
        total_events = 0
        for file_path in all_files:
            session_info = self.get_session_info(file_path)
            total_events += session_info['event_count']
        
        return {
            'total_sessions': len(all_files),
            'total_games': len(games),
            'total_patients': len(patients),
            'total_events': total_events,
            'available_games': games,
            'available_patients': patients
        }
    
    def delete_session(self, file_path: str) -> bool:
        """Eliminar sesión específica"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Sesión eliminada: {file_path}")
                return True
            else:
                print(f"❌ Archivo no encontrado: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Error eliminando sesión: {e}")
            return False
    
    def cleanup_empty_directories(self):
        """Limpiar directorios vacíos"""
        try:
            for game_dir in glob.glob(f"{self.base_dir}/*"):
                if os.path.isdir(game_dir):
                    sessions_dir = os.path.join(game_dir, "sessions")
                    if os.path.exists(sessions_dir) and not os.listdir(sessions_dir):
                        os.rmdir(sessions_dir)
                        print(f"🧹 Directorio vacío eliminado: {sessions_dir}")
                    
                    if os.path.exists(game_dir) and not os.listdir(game_dir):
                        os.rmdir(game_dir)
                        print(f"🧹 Directorio de juego vacío eliminado: {game_dir}")
        except Exception as e:
            print(f"⚠️ Error limpiando directorios: {e}") 