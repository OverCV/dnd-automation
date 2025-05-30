"""
Componente de Panel de Botones - RESPONSABILIDAD ÚNICA
Solo maneja botones de acción y sus callbacks
"""

import pygame
import subprocess
import platform
import os


class ButtonPanelComponent:
    """Componente pequeño - solo botones de acción"""
    
    def __init__(self, visual_analyzer, session_list, exit_callback):
        self.visual_analyzer = visual_analyzer
        self.session_list = session_list
        self.exit_callback = exit_callback
        
        # Configuración visual
        self.colors = {
            'accent': (100, 200, 255),
            'success': (100, 255, 100),
            'warning': (255, 200, 100),
            'error': (255, 100, 100),
            'card': (45, 55, 75),
            'text': (255, 255, 255)
        }
        
        # Crear botones
        self._create_buttons()
    
    def _create_buttons(self):
        """Crear definiciones de botones"""
        button_width = 200
        button_height = 40
        start_x = 980  # A la derecha
        start_y = 100
        
        self.buttons = [
            {
                'rect': pygame.Rect(start_x, start_y, button_width, button_height),
                'text': '📊 Dashboard',
                'action': 'dashboard',
                'color': self.colors['accent']
            },
            {
                'rect': pygame.Rect(start_x, start_y + 60, button_width, button_height),
                'text': '🧠 Análisis Fatiga',
                'action': 'fatigue',
                'color': self.colors['warning']
            },
            {
                'rect': pygame.Rect(start_x, start_y + 120, button_width, button_height),
                'text': '🔄 Comparar',
                'action': 'compare',
                'color': self.colors['success']
            },
            {
                'rect': pygame.Rect(start_x, start_y + 200, button_width, button_height),
                'text': '📁 Abrir Carpeta',
                'action': 'folder',
                'color': self.colors['card']
            },
            {
                'rect': pygame.Rect(start_x, start_y + 260, button_width, button_height),
                'text': '🔄 Actualizar',
                'action': 'refresh',
                'color': self.colors['card']
            },
            {
                'rect': pygame.Rect(start_x, start_y + 340, button_width, button_height),
                'text': '🚪 Volver',
                'action': 'exit',
                'color': self.colors['error']
            }
        ]
    
    def handle_click(self, mouse_pos, message_manager) -> bool:
        """Manejar clics en botones"""
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                self._execute_action(button['action'], message_manager)
                return True
        return False
    
    def _execute_action(self, action: str, message_manager):
        """Ejecutar acción del botón"""
        if action == 'exit':
            self.exit_callback()
        
        elif action == 'refresh':
            self.session_list.refresh_sessions()
            message_manager.show_message("🔄 Sesiones actualizadas", self.colors['success'])
        
        elif action == 'folder':
            self._open_folder(message_manager)
        
        elif action == 'dashboard':
            self._generate_dashboard(message_manager)
        
        elif action == 'fatigue':
            self._generate_fatigue(message_manager)
        
        elif action == 'compare':
            self._compare_sessions(message_manager)
    
    def _open_folder(self, message_manager):
        """Abrir carpeta de datos"""
        try:
            folder_path = "data/cognitive"
            
            if platform.system() == "Windows":
                subprocess.run(f'explorer "{os.path.abspath(folder_path)}"', shell=True)
            elif platform.system() == "Darwin":
                subprocess.run(f'open "{os.path.abspath(folder_path)}"', shell=True)
            else:
                subprocess.run(f'xdg-open "{os.path.abspath(folder_path)}"', shell=True)
            
            message_manager.show_message("📁 Carpeta abierta", self.colors['success'])
            
        except Exception as e:
            message_manager.show_message("❌ Error abriendo carpeta", self.colors['error'])
    
    def _generate_dashboard(self, message_manager):
        """Generar dashboard para sesión seleccionada"""
        session = self.session_list.get_selected_session()
        if not session:
            message_manager.show_message("❌ No hay sesión seleccionada", self.colors['error'])
            return
        
        try:
            result = self.visual_analyzer.create_piano_performance_dashboard(session['filepath'])
            
            if "✅" in result:
                message_manager.show_message("✅ Dashboard generado", self.colors['success'])
            else:
                message_manager.show_message("❌ Error en dashboard", self.colors['error'])
                
        except Exception as e:
            message_manager.show_message(f"❌ Error: {str(e)[:30]}", self.colors['error'])
    
    def _generate_fatigue(self, message_manager):
        """Generar análisis de fatiga"""
        session = self.session_list.get_selected_session()
        if not session:
            message_manager.show_message("❌ No hay sesión seleccionada", self.colors['error'])
            return
        
        if session['event_count'] < 6:
            message_manager.show_message("❌ Necesita mín. 6 eventos", self.colors['warning'])
            return
        
        try:
            result = self.visual_analyzer.create_fatigue_analysis(session['filepath'])
            
            if "✅" in result:
                message_manager.show_message("✅ Análisis fatiga generado", self.colors['success'])
            else:
                message_manager.show_message("❌ Error en fatiga", self.colors['error'])
                
        except Exception as e:
            message_manager.show_message(f"❌ Error: {str(e)[:30]}", self.colors['error'])
    
    def _compare_sessions(self, message_manager):
        """Comparar todas las sesiones"""
        if len(self.session_list.sessions) < 2:
            message_manager.show_message("❌ Necesita mín. 2 sesiones", self.colors['warning'])
            return
        
        try:
            file_paths = [s['filepath'] for s in self.session_list.sessions]
            labels = [f"{s['patient_id']}_{s['date']}" for s in self.session_list.sessions]
            
            result = self.visual_analyzer.create_comparison_chart(file_paths, labels)
            
            if "✅" in result:
                message_manager.show_message("✅ Comparación generada", self.colors['success'])
            else:
                message_manager.show_message("❌ Error comparando", self.colors['error'])
                
        except Exception as e:
            message_manager.show_message(f"❌ Error: {str(e)[:30]}", self.colors['error'])
    
    def draw(self, screen, mouse_pos):
        """Dibujar botones"""
        font = pygame.font.Font(None, 24)
        
        for button in self.buttons:
            # Color con hover effect
            color = button['color']
            if button['rect'].collidepoint(mouse_pos):
                color = tuple(min(255, c + 30) for c in color)
            
            # Dibujar botón
            pygame.draw.rect(screen, color, button['rect'])
            pygame.draw.rect(screen, self.colors['text'], button['rect'], 2)
            
            # Texto centrado
            text_surface = font.render(button['text'], True, self.colors['text'])
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect) 