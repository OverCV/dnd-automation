"""
Componente de Gestión de Pacientes - RESPONSABILIDAD ÚNICA
Solo maneja identificación y selección de pacientes
"""

import pygame
import os
import json
from datetime import datetime


class PatientManagerComponent:
    """Componente para gestión de pacientes con JSON separado por juego"""
    
    def __init__(self, game_type: str = "piano_simon"):
        self.game_type = game_type.lower().replace(" ", "_")
        self.screen = None
        self.font_medium = None
        self.font_small = None
        
        # Archivos específicos por juego
        self.game_data_dir = f"data/cognitive/{self.game_type}"
        self.patients_file = f"{self.game_data_dir}/patients.json"
        
        # Asegurar directorios
        os.makedirs(self.game_data_dir, exist_ok=True)
        
        # Estado del componente
        self.patients = self._load_patients()
        self.current_patient_id = None
        self.message = ""
        self.message_timer = 0
        
        # Estados de entrada
        self.entering_name = False
        self.entering_age = False
        self.temp_name = ""
        self.temp_age = ""
        
        # Posiciones de UI
        self.box_x = 50
        self.box_y = 50
        self.box_width = 400
        self.box_height = 300
        
        # Colores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 150, 255)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        
        # Configuración visual
        self.rect = pygame.Rect(650, 460, 520, 140)
        self.colors = {
            'card': (45, 55, 75),
            'accent': (100, 200, 255),
            'success': (100, 255, 100),
            'text': (255, 255, 255),
            'text_gray': (180, 180, 180)
        }
        
        # Botones
        self.new_patient_btn = pygame.Rect(660, 520, 150, 30)
        self.select_patient_btn = pygame.Rect(820, 520, 150, 30)
        
        # Estados
        self.showing_input = False
        self.input_text = ""
    
    def _load_patients(self):
        """Cargar lista de pacientes del archivo"""
        try:
            if os.path.exists(self.patients_file):
                with open(self.patients_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"❌ Error cargando pacientes: {e}")
            return {}
    
    def save_patients(self):
        """Guardar lista de pacientes"""
        try:
            with open(self.patients_file, 'w', encoding='utf-8') as f:
                json.dump(self.patients, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando pacientes: {e}")
    
    def add_patient(self, patient_name: str) -> str:
        """Añadir nuevo paciente y retornar su ID"""
        if not patient_name.strip():
            return None
            
        # Generar ID único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_id = f"P_{len(self.patients) + 1:03d}_{timestamp}"
        
        # Guardar paciente
        self.patients[patient_id] = {
            'name': patient_name.strip(),
            'created': datetime.now().isoformat(),
            'sessions_count': 0
        }
        
        self.save_patients()
        self.current_patient_id = patient_id
        return patient_id
    
    def get_current_patient_id(self) -> str:
        """Obtener ID del paciente actual para logging"""
        if self.current_patient_id:
            return self.current_patient_id
        
        # Si no hay paciente, crear uno por defecto
        return self.add_patient("Paciente Anónimo")
    
    def handle_click(self, mouse_pos, message_manager):
        """Manejar clics en botones"""
        if self.new_patient_btn.collidepoint(mouse_pos):
            self.showing_input = True
            self.input_text = ""
            
        elif self.select_patient_btn.collidepoint(mouse_pos):
            self._show_patient_selection(message_manager)
    
    def handle_keydown(self, event, message_manager):
        """Manejar entrada de texto para nuevo paciente"""
        if not self.showing_input:
            return False
            
        if event.key == pygame.K_RETURN:
            if self.input_text.strip():
                patient_id = self.add_patient(self.input_text)
                message_manager.show_message(f"✅ Paciente creado: {patient_id}", self.GREEN)
                self.showing_input = False
                self.input_text = ""
                return True
        
        elif event.key == pygame.K_ESCAPE:
            self.showing_input = False
            self.input_text = ""
            return True
            
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return True
            
        else:
            # Añadir carácter
            if event.unicode and len(self.input_text) < 30:
                self.input_text += event.unicode
                return True
        
        return False
    
    def _show_patient_selection(self, message_manager):
        """Mostrar selección de pacientes (simplificado)"""
        if not self.patients:
            message_manager.show_message("❌ No hay pacientes registrados", self.GRAY)
            return
            
        # Por simplicidad, rotar entre pacientes existentes
        patient_ids = list(self.patients.keys())
        if self.current_patient_id in patient_ids:
            current_index = patient_ids.index(self.current_patient_id)
            next_index = (current_index + 1) % len(patient_ids)
        else:
            next_index = 0
            
        self.current_patient_id = patient_ids[next_index]
        patient_name = self.patients[self.current_patient_id]['name']
        message_manager.show_message(f"👤 Paciente: {patient_name}", self.GREEN)
    
    def draw(self, screen, mouse_pos):
        """Dibujar panel de gestión de pacientes"""
        # Marco principal
        pygame.draw.rect(screen, self.colors['card'], self.rect)
        pygame.draw.rect(screen, self.colors['accent'], self.rect, 2)
        
        # Título
        font_heading = pygame.font.Font(None, 28)
        font_normal = pygame.font.Font(None, 20)
        font_small = pygame.font.Font(None, 16)
        
        title = font_heading.render("👤 Gestión de Pacientes", True, self.colors['text'])
        screen.blit(title, (660, 470))
        
        # Info paciente actual
        if self.current_patient_id and self.current_patient_id in self.patients:
            patient_name = self.patients[self.current_patient_id]['name']
            current_text = f"Actual: {patient_name} ({self.current_patient_id})"
        else:
            current_text = "No hay paciente seleccionado"
            
        current_surface = font_normal.render(current_text, True, self.colors['text_gray'])
        screen.blit(current_surface, (670, 495))
        
        # Entrada de texto para nuevo paciente
        if self.showing_input:
            input_rect = pygame.Rect(660, 555, 310, 25)
            pygame.draw.rect(screen, self.WHITE, input_rect)
            pygame.draw.rect(screen, self.colors['accent'], input_rect, 2)
            
            input_surface = font_normal.render(self.input_text + "|", True, self.BLACK)
            screen.blit(input_surface, (665, 560))
            
            # Instrucción
            instruction = font_small.render("Escribe nombre y presiona Enter", True, self.colors['text_gray'])
            screen.blit(instruction, (660, 575))
        
        # Botones
        self._draw_button(screen, self.new_patient_btn, "➕ Nuevo", mouse_pos, font_small)
        self._draw_button(screen, self.select_patient_btn, "🔄 Cambiar", mouse_pos, font_small)
    
    def _draw_button(self, screen, button_rect, text, mouse_pos, font):
        """Dibujar un botón"""
        color = self.colors['card']
        if button_rect.collidepoint(mouse_pos):
            color = tuple(min(255, c + 30) for c in color)
            
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, self.colors['text'], button_rect, 1)
        
        text_surface = font.render(text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect) 