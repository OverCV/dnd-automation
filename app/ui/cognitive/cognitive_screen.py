#!/usr/bin/env python3
"""
Pantalla Principal de Análisis Cognitivo - COORDINADOR SIMPLE
Solo coordina componentes, no hace el trabajo pesado
"""

import pygame
import sys
import os

# Añadir paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .session_list_component import SessionListComponent
from .button_panel_component import ButtonPanelComponent
from .info_panel_component import InfoPanelComponent
from .message_manager import MessageManager

# Verificar disponibilidad cognitiva
try:
    from core.cognitive import SessionManager, CognitiveVisualAnalyzer, CognitiveDataCleaner
    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False


class CognitiveScreen:
    """Pantalla principal - SOLO COORDINA componentes"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        
        # Colores theme
        self.colors = {
            'background': (20, 25, 40),
            'text': (255, 255, 255)
        }
        
        # Componentes
        self.session_list = None
        self.button_panel = None
        self.info_panel = None
        self.message_manager = None
        
        # Managers cognitivos
        self.session_manager = None
        self.visual_analyzer = None
        self.data_cleaner = None
    
    def initialize(self) -> bool:
        """Inicializar pantalla y componentes"""
        if not COGNITIVE_AVAILABLE:
            print("❌ Módulos cognitivos no disponibles")
            return False
        
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("🧠 Análisis Cognitivo")
            
            # Inicializar managers
            self.session_manager = SessionManager()
            self.visual_analyzer = CognitiveVisualAnalyzer()
            self.data_cleaner = CognitiveDataCleaner()
            
            # Crear componentes
            self.session_list = SessionListComponent(self.session_manager)
            self.button_panel = ButtonPanelComponent(
                self.visual_analyzer, 
                self.session_list,
                self._on_exit
            )
            self.info_panel = InfoPanelComponent()
            self.message_manager = MessageManager()
            
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando: {e}")
            return False
    
    def run(self) -> bool:
        """Ejecutar pantalla"""
        if not self.initialize():
            return False
        
        self.running = True
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.session_list.handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event)
                elif event.type == pygame.MOUSEWHEEL:
                    self.session_list.handle_scroll(event)
            
            # Actualizar componentes
            self.message_manager.update(dt)
            
            # Dibujar
            self._draw()
            pygame.display.flip()
        
        pygame.quit()
        return True
    
    def _handle_mouse_click(self, event):
        """Delegar clics a componentes"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Verificar botones primero
        if self.button_panel.handle_click(mouse_pos, self.message_manager):
            return
        
        # Luego lista de sesiones
        self.session_list.handle_click(mouse_pos)
    
    def _draw(self):
        """Coordinar dibujado de todos los componentes"""
        # Fondo
        self.screen.fill(self.colors['background'])
        
        # Título
        font = pygame.font.Font(None, 48)
        title = font.render("🧠 Análisis Cognitivo", True, self.colors['text'])
        self.screen.blit(title, (20, 20))
        
        # Componentes
        self.session_list.draw(self.screen)
        self.button_panel.draw(self.screen, pygame.mouse.get_pos())
        self.info_panel.draw(self.screen, self.session_list.get_selected_session())
        self.message_manager.draw(self.screen, self.width)
    
    def _on_exit(self):
        """Callback de salida"""
        self.running = False


def main():
    """Función principal para testing"""
    screen = CognitiveScreen()
    screen.run()


if __name__ == "__main__":
    main() 