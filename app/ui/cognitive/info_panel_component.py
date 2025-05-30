"""
Componente de Panel de Información - RESPONSABILIDAD ÚNICA
Solo muestra información detallada de la sesión seleccionada
"""

import pygame
import os


class InfoPanelComponent:
    """Componente pequeño - solo info de sesión"""
    
    def __init__(self):
        # Configuración visual
        self.rect = pygame.Rect(650, 450, 520, 250)
        self.colors = {
            'card': (45, 55, 75),
            'accent': (100, 200, 255),
            'text': (255, 255, 255),
            'text_gray': (180, 180, 180)
        }
    
    def draw(self, screen, selected_session):
        """Dibujar panel de información"""
        if not selected_session:
            self._draw_empty_panel(screen)
            return
        
        # Marco principal
        pygame.draw.rect(screen, self.colors['card'], self.rect)
        pygame.draw.rect(screen, self.colors['accent'], self.rect, 2)
        
        # Título
        font_heading = pygame.font.Font(None, 36)
        font_normal = pygame.font.Font(None, 24)
        
        title = font_heading.render("📊 Información Detallada", True, self.colors['text'])
        screen.blit(title, (660, 460))
        
        # Detalles de la sesión
        details = [
            f"Paciente: {selected_session['patient_id']}",
            f"Tipo: {selected_session['game_type']}",
            f"Fecha: {selected_session['date']} {selected_session['time']}",
            f"Eventos: {selected_session['event_count']}",
            f"Archivo: {os.path.basename(selected_session['filepath'])}"
        ]
        
        # Renderizar detalles
        y_pos = 500
        for detail in details:
            detail_surface = font_normal.render(detail, True, self.colors['text_gray'])
            screen.blit(detail_surface, (670, y_pos))
            y_pos += 25
    
    def _draw_empty_panel(self, screen):
        """Dibujar panel vacío cuando no hay sesión seleccionada"""
        # Marco
        pygame.draw.rect(screen, self.colors['card'], self.rect)
        pygame.draw.rect(screen, self.colors['accent'], self.rect, 2)
        
        # Mensaje
        font_heading = pygame.font.Font(None, 36)
        font_normal = pygame.font.Font(None, 24)
        
        title = font_heading.render("📊 Información", True, self.colors['text'])
        screen.blit(title, (660, 460))
        
        empty_msg = font_normal.render("Selecciona una sesión para ver detalles", True, self.colors['text_gray'])
        screen.blit(empty_msg, (670, 500)) 