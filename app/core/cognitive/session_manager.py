"""
Manejador de sesiones cognitivas - Lo más simple posible
"""

import os
from typing import Optional
from .cognitive_logger import CognitiveLogger


class SessionManager:
    """Maneja sesiones cognitivas de forma súper simple"""
    
    def __init__(self):
        self.current_logger: Optional[CognitiveLogger] = None
        self.data_dir = "data/cognitive"
        
        # Asegurar que existe el directorio
        os.makedirs(self.data_dir, exist_ok=True)
    
    def start_session(self, game_type: str, patient_id: str = "default") -> CognitiveLogger:
        """Iniciar nueva sesión cognitiva"""
        # Si hay una sesión activa, cerrarla primero
        if self.current_logger:
            print("⚠️ Cerrando sesión anterior...")
            self.end_session()
        
        # Crear nuevo logger
        self.current_logger = CognitiveLogger(game_type, patient_id)
        print(f"🧠 Sesión cognitiva iniciada para {game_type}")
        
        return self.current_logger
    
    def get_current_logger(self) -> Optional[CognitiveLogger]:
        """Obtener logger actual"""
        return self.current_logger
    
    def is_session_active(self) -> bool:
        """Verificar si hay sesión activa"""
        return self.current_logger is not None
    
    def end_session(self) -> Optional[str]:
        """Finalizar sesión actual"""
        if self.current_logger:
            csv_file = self.current_logger.close_session()
            self.current_logger = None
            print("✅ Sesión cognitiva finalizada")
            return csv_file
        else:
            print("⚠️ No hay sesión activa para cerrar")
            return None
    
    def list_session_files(self) -> list:
        """Listar archivos de sesiones guardadas"""
        if not os.path.exists(self.data_dir):
            return []
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        return sorted(csv_files, reverse=True)  # Más recientes primero
    
    def get_session_info(self, filename: str) -> dict:
        """Obtener información básica de una sesión"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return {}
        
        try:
            # Extraer info del nombre del archivo
            # Formato: patient_game_YYYYMMDD_HHMMSS.csv
            name_parts = filename.replace('.csv', '').split('_')
            
            if len(name_parts) >= 4:
                patient_id = name_parts[0]
                game_type = name_parts[1]
                date_part = name_parts[2]
                time_part = name_parts[3]
                
                # Contar eventos (líneas - header)
                with open(filepath, 'r') as file:
                    event_count = len(file.readlines()) - 1
                
                return {
                    'filename': filename,
                    'patient_id': patient_id,
                    'game_type': game_type,
                    'date': date_part,
                    'time': time_part,
                    'event_count': event_count,
                    'filepath': filepath
                }
            
        except Exception as e:
            print(f"❌ Error leyendo info de sesión: {e}")
        
        return {'filename': filename, 'error': 'Could not parse'}
    
    def emergency_stop(self):
        """Parada de emergencia - Solo cerrar si existe"""
        if self.current_logger:
            try:
                self.current_logger.close_session()
                print("🚨 Sesión cognitiva cerrada por emergencia")
            except:
                print("🚨 Error en parada de emergencia")
            finally:
                self.current_logger = None 