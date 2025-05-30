"""
Componente de Lista de Sesiones - RESPONSABILIDAD ÚNICA
Solo maneja la lista y selección de sesiones
"""

import pygame
import os
from core.cognitive.session_manager import SessionManager


class SessionListComponent:
    """Componente pequeño - solo lista de sesiones"""
    
    def __init__(self):
        # Manager de sesiones con nueva estructura
        self.session_manager = SessionManager()
        
        # Filtro por tipo de juego
        self.current_game_filter = "piano_simon"  # Por defecto mostrar piano simon
        self.available_games = ["piano_simon", "ping_pong", "two_lanes", "all"]  # Futuros juegos
        
        self.sessions = []
        self.selected_session = 0
        self.scroll_offset = 0
        self.visible_sessions = 8
        
        # Colors
        self.colors = {
            'background': (20, 20, 30),
            'list_bg': (40, 40, 50),
            'selected': (70, 130, 180),
            'text': (255, 255, 255),
            'text_secondary': (180, 180, 180),
            'highlight': (100, 150, 200),
            'error': (255, 100, 100),
            'success': (100, 255, 100)
        }
        
        # Configuración visual
        self.rect = pygame.Rect(20, 100, 600, 600)
        
        # Cargar sesiones
        self.load_sessions()
    
    def load_sessions(self):
        """Cargar sesiones usando el manager actualizado"""
        try:
            if self.current_game_filter == "all":
                session_files = self.session_manager.list_session_files()
            else:
                session_files = self.session_manager.list_session_files(self.current_game_filter)
            
            self.sessions = []
            for file_path in session_files:
                session_info = self.session_manager.get_session_info(file_path)
                if session_info:
                    self.sessions.append(session_info)
            
            print(f"📁 Cargadas {len(self.sessions)} sesiones para {self.current_game_filter}")
            
        except Exception as e:
            print(f"❌ Error cargando sesiones: {e}")
            self.sessions = []
    
    def get_selected_session(self):
        """Obtener sesión seleccionada"""
        if not self.sessions or self.selected_session >= len(self.sessions):
            return None
        return self.sessions[self.selected_session]
    
    def handle_keydown(self, event):
        """Manejar navegación con teclado"""
        if not self.sessions:
            return
            
        if event.key == pygame.K_UP:
            self.selected_session = max(0, self.selected_session - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_session = min(len(self.sessions) - 1, self.selected_session + 1)
    
    def handle_click(self, mouse_pos):
        """Manejar clics en la lista"""
        if not self.rect.collidepoint(mouse_pos):
            return
        
        # Calcular sesión clickeada
        relative_y = mouse_pos[1] - 100 + abs(self.scroll_offset)
        session_index = relative_y // 80
        
        if 0 <= session_index < len(self.sessions):
            self.selected_session = session_index
    
    def handle_scroll(self, event):
        """Manejar scroll"""
        self.scroll_offset += event.y * 30
        max_scroll = max(0, len(self.sessions) * 80 - 400)
        self.scroll_offset = max(-max_scroll, min(0, self.scroll_offset))
    
    def draw(self, screen):
        """Dibujar lista de sesiones"""
        # Marco principal
        pygame.draw.rect(screen, self.colors['list_bg'], self.rect)
        pygame.draw.rect(screen, self.colors['highlight'], self.rect, 2)
        
        # Título
        font_heading = pygame.font.Font(None, 36)
        font_normal = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        
        title = font_heading.render("📋 Sesiones Guardadas", True, self.colors['text'])
        screen.blit(title, (30, 110))
        
        # Info general
        info_text = f"Total: {len(self.sessions)} sesiones"
        info_surface = font_normal.render(info_text, True, self.colors['text_secondary'])
        screen.blit(info_surface, (30, 140))
        
        # Lista de sesiones
        y_offset = 170 + self.scroll_offset
        
        for i, session in enumerate(self.sessions):
            session_rect = pygame.Rect(30, y_offset + i * 80, 580, 70)
            
            # Fondo según selección
            if i == self.selected_session:
                pygame.draw.rect(screen, self.colors['selected'], session_rect)
                pygame.draw.rect(screen, self.colors['highlight'], session_rect, 2)
            else:
                pygame.draw.rect(screen, self.colors['background'], session_rect)
            
            # Textos de la sesión
            patient_text = f"👤 {session['patient_id']}"
            date_text = f"📅 {session['date']} {session['time']}"
            events_text = f"📊 {session['event_count']} eventos"
            
            # Renderizar textos
            patient_surface = font_normal.render(patient_text, True, self.colors['text'])
            date_surface = font_small.render(date_text, True, self.colors['text_secondary'])
            events_surface = font_small.render(events_text, True, self.colors['success'])
            
            # Posicionar textos
            screen.blit(patient_surface, (session_rect.x + 10, session_rect.y + 5))
            screen.blit(date_surface, (session_rect.x + 10, session_rect.y + 25))
            screen.blit(events_surface, (session_rect.x + 10, session_rect.y + 45)) 