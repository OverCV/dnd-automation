"""
Componente de Manejo de Mensajes - RESPONSABILIDAD ÚNICA
Solo maneja mensajes temporales en pantalla
"""

import pygame


class MessageManager:
    """Componente pequeño - solo mensajes temporales"""
    
    def __init__(self):
        self.message = ""
        self.message_color = (255, 255, 255)
        self.message_time = 0
        self.message_duration = 3000  # 3 segundos
    
    def show_message(self, text: str, color: tuple):
        """Mostrar mensaje temporal"""
        self.message = text
        self.message_color = color
        self.message_time = pygame.time.get_ticks()
    
    def update(self, dt: float):
        """Actualizar estado de mensajes"""
        # Limpiar mensaje después del tiempo
        if self.message and pygame.time.get_ticks() - self.message_time > self.message_duration:
            self.message = ""
    
    def draw(self, screen, screen_width: int):
        """Dibujar mensaje si existe"""
        if not self.message:
            return
        
        font = pygame.font.Font(None, 24)
        
        # Renderizar texto
        text_surface = font.render(self.message, True, self.message_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.y = screen.get_height() - 60
        
        # Fondo semi-transparente
        bg_rect = text_rect.copy()
        bg_rect.inflate_ip(20, 10)
        
        # Crear superficie con alpha
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(180)
        bg_surface.fill((0, 0, 0))
        
        # Dibujar fondo y texto
        screen.blit(bg_surface, bg_rect)
        screen.blit(text_surface, text_rect) 