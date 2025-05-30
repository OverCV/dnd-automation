"""
Utilidad para limpiar archivos de datos cognitivos - Súper simple
"""

import os
import glob
from typing import List, Dict
from datetime import datetime, timedelta


class CognitiveDataCleaner:
    """Utilidad súper simple para manejo de archivos cognitivos"""
    
    def __init__(self):
        self.data_dir = "data/cognitive"
        self.backup_dir = "data/cognitive/backup"
    
    def list_all_files(self) -> List[Dict]:
        """Listar todos los archivos CSV cognitivos"""
        if not os.path.exists(self.data_dir):
            return []
        
        files_info = []
        csv_files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        
        for filepath in csv_files:
            try:
                filename = os.path.basename(filepath)
                file_size = os.path.getsize(filepath)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # Extraer info del nombre si es posible
                name_parts = filename.replace('.csv', '').split('_')
                patient_id = name_parts[0] if name_parts else "unknown"
                game_type = name_parts[1] if len(name_parts) > 1 else "unknown"
                
                files_info.append({
                    'filename': filename,
                    'filepath': filepath,
                    'patient_id': patient_id,
                    'game_type': game_type,
                    'size_bytes': file_size,
                    'size_kb': file_size / 1024,
                    'modified_date': modified_time,
                    'age_days': (datetime.now() - modified_time).days
                })
            except Exception as e:
                print(f"⚠️ Error procesando archivo {filepath}: {e}")
        
        # Ordenar por fecha de modificación (más recientes primero)
        files_info.sort(key=lambda x: x['modified_date'], reverse=True)
        return files_info
    
    def delete_all_files(self, confirm: bool = False) -> str:
        """Eliminar TODOS los archivos CSV cognitivos"""
        if not confirm:
            return "❌ Debes confirmar explícitamente para eliminar todos los archivos"
        
        files = self.list_all_files()
        if not files:
            return "✅ No hay archivos para eliminar"
        
        deleted_count = 0
        errors = []
        
        for file_info in files:
            try:
                os.remove(file_info['filepath'])
                deleted_count += 1
                print(f"🗑️ Eliminado: {file_info['filename']}")
            except Exception as e:
                errors.append(f"Error eliminando {file_info['filename']}: {e}")
        
        result = f"✅ Eliminados {deleted_count} archivos"
        if errors:
            result += f"\n❌ {len(errors)} errores:\n" + "\n".join(errors)
        
        return result
    
    def delete_files_by_patient(self, patient_id: str) -> str:
        """Eliminar archivos de un paciente específico"""
        files = self.list_all_files()
        patient_files = [f for f in files if f['patient_id'] == patient_id]
        
        if not patient_files:
            return f"❌ No se encontraron archivos para el paciente: {patient_id}"
        
        deleted_count = 0
        errors = []
        
        for file_info in patient_files:
            try:
                os.remove(file_info['filepath'])
                deleted_count += 1
                print(f"🗑️ Eliminado: {file_info['filename']}")
            except Exception as e:
                errors.append(f"Error eliminando {file_info['filename']}: {e}")
        
        result = f"✅ Eliminados {deleted_count} archivos del paciente {patient_id}"
        if errors:
            result += f"\n❌ {len(errors)} errores:\n" + "\n".join(errors)
        
        return result
    
    def delete_old_files(self, days_old: int = 30) -> str:
        """Eliminar archivos más antiguos que X días"""
        files = self.list_all_files()
        old_files = [f for f in files if f['age_days'] > days_old]
        
        if not old_files:
            return f"✅ No hay archivos más antiguos que {days_old} días"
        
        deleted_count = 0
        errors = []
        
        for file_info in old_files:
            try:
                os.remove(file_info['filepath'])
                deleted_count += 1
                print(f"🗑️ Eliminado (viejo): {file_info['filename']}")
            except Exception as e:
                errors.append(f"Error eliminando {file_info['filename']}: {e}")
        
        result = f"✅ Eliminados {deleted_count} archivos antiguos (>{days_old} días)"
        if errors:
            result += f"\n❌ {len(errors)} errores:\n" + "\n".join(errors)
        
        return result
    
    def backup_all_files(self) -> str:
        """Hacer backup de todos los archivos antes de eliminar"""
        files = self.list_all_files()
        if not files:
            return "❌ No hay archivos para hacer backup"
        
        # Crear directorio de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        backed_up = 0
        errors = []
        
        for file_info in files:
            try:
                import shutil
                backup_path = os.path.join(backup_folder, file_info['filename'])
                shutil.copy2(file_info['filepath'], backup_path)
                backed_up += 1
                print(f"💾 Backup: {file_info['filename']}")
            except Exception as e:
                errors.append(f"Error en backup {file_info['filename']}: {e}")
        
        result = f"✅ Backup completado: {backed_up} archivos en {backup_folder}"
        if errors:
            result += f"\n❌ {len(errors)} errores:\n" + "\n".join(errors)
        
        return result
    
    def get_storage_summary(self) -> str:
        """Obtener resumen de almacenamiento"""
        files = self.list_all_files()
        
        if not files:
            return "📊 No hay archivos cognitivos almacenados"
        
        total_size_kb = sum(f['size_kb'] for f in files)
        total_size_mb = total_size_kb / 1024
        
        # Agrupar por paciente
        patients = {}
        for file_info in files:
            patient_id = file_info['patient_id']
            if patient_id not in patients:
                patients[patient_id] = {'count': 0, 'size_kb': 0}
            patients[patient_id]['count'] += 1
            patients[patient_id]['size_kb'] += file_info['size_kb']
        
        # Agrupar por antigüedad
        recent_files = len([f for f in files if f['age_days'] <= 7])
        old_files = len([f for f in files if f['age_days'] > 30])
        
        summary = f"""📊 RESUMEN DE ALMACENAMIENTO COGNITIVO
{"=" * 50}

📁 ARCHIVOS TOTALES: {len(files)}
💾 TAMAÑO TOTAL: {total_size_mb:.2f} MB ({total_size_kb:.1f} KB)

👥 POR PACIENTE:
"""
        
        for patient_id, info in patients.items():
            summary += f"   • {patient_id}: {info['count']} archivos ({info['size_kb']:.1f} KB)\n"
        
        summary += f"""
📅 POR ANTIGÜEDAD:
   • Recientes (≤7 días): {recent_files} archivos
   • Antiguos (>30 días): {old_files} archivos

💡 RECOMENDACIONES:
"""
        
        if old_files > 10:
            summary += "   • Considera eliminar archivos antiguos (>30 días)\n"
        if total_size_mb > 10:
            summary += "   • Tamaño considerable - considera hacer backup\n"
        if len(patients) > 20:
            summary += "   • Muchos pacientes - organizar por fecha\n"
        
        return summary
    
    def selective_delete_menu(self) -> str:
        """Menú interactivo para eliminación selectiva"""
        files = self.list_all_files()
        
        if not files:
            return "❌ No hay archivos para eliminar"
        
        summary = "🗑️ ELIMINACIÓN SELECTIVA\n" + "=" * 30 + "\n\n"
        summary += f"Total de archivos: {len(files)}\n\n"
        
        # Mostrar primeros 10 archivos
        summary += "📋 ARCHIVOS DISPONIBLES (10 más recientes):\n"
        for i, file_info in enumerate(files[:10]):
            age_str = f"{file_info['age_days']}d" if file_info['age_days'] > 0 else "hoy"
            summary += f"  {i+1:2d}. {file_info['filename']} ({file_info['size_kb']:.1f}KB, {age_str})\n"
        
        if len(files) > 10:
            summary += f"     ... y {len(files) - 10} archivos más\n"
        
        summary += "\n💡 OPCIONES RÁPIDAS:\n"
        summary += "   • delete_old_files(30) - Eliminar archivos >30 días\n"
        summary += "   • delete_all_files(confirm=True) - Eliminar TODO\n"
        summary += "   • backup_all_files() - Hacer backup primero\n"
        
        return summary 