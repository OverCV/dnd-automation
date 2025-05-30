"""
Componente de Lista de Sesiones - RESPONSABILIDAD ÚNICA
Solo maneja la lista y selección de sesiones
"""

import pygame
import os


class SessionListComponent:
    """Componente pequeño - solo lista de sesiones"""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.sessions = []
        self.selected_index = 0
        self.scroll_offset = 0
        
        # Configuración visual
        self.rect = pygame.Rect(20, 100, 600, 600)
        self.colors = {
            'card': (45, 55, 75),
            'card_hover': (60, 70, 90),
            'accent': (100, 200, 255),
            'text': (255, 255, 255),
            'text_gray': (180, 180, 180)
        }
        
        # Cargar sesiones
        self.refresh_sessions()
    
    def refresh_sessions(self):
        """Recargar lista de sesiones"""
        try:
            session_files = self.session_manager.list_session_files()
            self.sessions = []
            
            for file_path in session_files:
                info = self.session_manager.get_session_info(file_path)
                self.sessions.append(info)
                
            print(f"📊 {len(self.sessions)} sesiones cargadas")
            
        except Exception as e:
            print(f"❌ Error cargando sesiones: {e}")
            self.sessions = []
    
    def get_selected_session(self):
        """Obtener sesión seleccionada"""
        if not self.sessions or self.selected_index >= len(self.sessions):
            return None
        return self.sessions[self.selected_index]
    
    def handle_keydown(self, event):
        """Manejar navegación con teclado"""
        if not self.sessions:
            return
            
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.sessions) - 1, self.selected_index + 1)
    
    def handle_click(self, mouse_pos):
        """Manejar clics en la lista"""
        if not self.rect.collidepoint(mouse_pos):
            return
        
        # Calcular sesión clickeada
        relative_y = mouse_pos[1] - 100 + abs(self.scroll_offset)
        session_index = relative_y // 80
        
        if 0 <= session_index < len(self.sessions):
            self.selected_index = session_index
    
    def handle_scroll(self, event):
        """Manejar scroll"""
        self.scroll_offset += event.y * 30
        max_scroll = max(0, len(self.sessions) * 80 - 400)
        self.scroll_offset = max(-max_scroll, min(0, self.scroll_offset))
    
    def draw(self, screen):
        """Dibujar lista de sesiones"""
        # Marco principal
        pygame.draw.rect(screen, self.colors['card'], self.rect)
        pygame.draw.rect(screen, self.colors['accent'], self.rect, 2)
        
        # Título
        font_heading = pygame.font.Font(None, 36)
        font_normal = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        
        title = font_heading.render("📋 Sesiones Guardadas", True, self.colors['text'])
        screen.blit(title, (30, 110))
        
        # Info general
        info_text = f"Total: {len(self.sessions)} sesiones"
        info_surface = font_normal.render(info_text, True, self.colors['text_gray'])
        screen.blit(info_surface, (30, 140))
        
        # Lista de sesiones
        y_offset = 170 + self.scroll_offset
        
        for i, session in enumerate(self.sessions):
            session_rect = pygame.Rect(30, y_offset + i * 80, 580, 70)
            
            # Fondo según selección
            if i == self.selected_index:
                pygame.draw.rect(screen, self.colors['card_hover'], session_rect)
                pygame.draw.rect(screen, self.colors['accent'], session_rect, 2)
            else:
                pygame.draw.rect(screen, (30, 35, 50), session_rect)
            
            # Textos de la sesión
            patient_text = f"👤 {session['patient_id']}"
            date_text = f"📅 {session['date']} {session['time']}"
            events_text = f"📊 {session['event_count']} eventos"
            
            # Renderizar textos
            patient_surface = font_normal.render(patient_text, True, self.colors['text'])
            date_surface = font_small.render(date_text, True, self.colors['text_gray'])
            events_surface = font_small.render(events_text, True, self.colors['accent'])
            
            # Posicionar textos
            screen.blit(patient_surface, (session_rect.x + 10, session_rect.y + 5))
            screen.blit(date_surface, (session_rect.x + 10, session_rect.y + 25))
            screen.blit(events_surface, (session_rect.x + 10, session_rect.y + 45)) 