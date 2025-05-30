import pygame
from typing import Optional, Tuple

class PingPongPygameRenderer:
    """Manejador de visualización con Pygame"""

    def __init__(self, screen_width: int = 800, screen_height: int = 600,
                 lcd_width: int = 16, lcd_height: int = 2):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.LCD_WIDTH = lcd_width
        self.LCD_HEIGHT = lcd_height

        self.screen = None
        self.clock = None
        self.initialized = False

        # Fuentes
        self.font_large = None
        self.font_medium = None
        self.font_small = None

        # Colores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 100, 100)
        self.YELLOW = (255, 255, 0)

    def initialize(self):
        """Inicializar Pygame"""
        if not self.initialized:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Ping Pong - Arduino + Python")

            # Inicializar fuentes
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)

            self.clock = pygame.time.Clock()
            self.initialized = True

    def quit(self):
        """Cerrar Pygame de forma segura"""
        try:
            if self.initialized:
                pygame.display.quit()
                pygame.quit()
                self.initialized = False
                print("✅ Pygame cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error cerrando Pygame: {e}")
            # Forzar cierre si hay problemas
            try:
                pygame.quit()
                self.initialized = False
            except:
                pass

    def draw_game(self, ball_x: int, ball_y: int, left_paddle_active: bool,
                  right_paddle_active: bool, score: int, game_over: bool,
                  game_paused: bool, total_hits: int, left_hits: int, right_hits: int):
        """Dibujar el estado completo del juego"""
        if not self.initialized:
            return

        self.screen.fill(self.BLACK)

        # Título
        title = self.font_large.render("Ping Pong - Arduino + Python", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # Simulación del LCD
        lcd_width = 640
        lcd_height = 160
        lcd_x = (self.screen_width - lcd_width) // 2
        lcd_y = 120

        # Marco del LCD
        pygame.draw.rect(self.screen, self.GREEN,
                        (lcd_x - 5, lcd_y - 5, lcd_width + 10, lcd_height + 10), 3)
        pygame.draw.rect(self.screen, self.BLACK, (lcd_x, lcd_y, lcd_width, lcd_height))

        # Grid del LCD
        char_width = lcd_width // self.LCD_WIDTH
        char_height = lcd_height // self.LCD_HEIGHT

        # Dibujar caracteres
        for y in range(self.LCD_HEIGHT):
            for x in range(self.LCD_WIDTH):
                char_x = lcd_x + x * char_width
                char_y = lcd_y + y * char_height

                # Pelota
                if x == ball_x and y == ball_y:
                    pygame.draw.circle(self.screen, self.WHITE,
                                     (char_x + char_width//2, char_y + char_height//2),
                                     min(char_width, char_height)//3)

                # Palas
                if x == 0 and left_paddle_active:
                    pygame.draw.rect(self.screen, self.BLUE,
                                   (char_x, char_y, char_width//3, char_height))
                elif x == self.LCD_WIDTH - 1 and right_paddle_active:
                    pygame.draw.rect(self.screen, self.BLUE,
                                   (char_x + 2*char_width//3, char_y, char_width//3, char_height))

        # Información del juego
        info_y = 320
        score_text = self.font_medium.render(f"Puntuación: {score}", True, self.YELLOW)
        self.screen.blit(score_text, (50, info_y))

        # Mostrar estadísticas de hits
        hits_text = self.font_small.render(
            f"Total Hits: {total_hits} | Left: {left_hits} | Right: {right_hits}",
            True, self.WHITE
        )
        self.screen.blit(hits_text, (50, info_y + 30))

        # Estado del juego
        if game_over:
            status = "GAME OVER - Presiona SELECT para reiniciar"
            color = self.RED
        elif game_paused:
            status = "PAUSADO - Presiona SELECT para continuar"
            color = self.YELLOW
        else:
            status = "JUGANDO - LEFT/RIGHT para palas, SELECT para pausar"
            color = self.GREEN

        status_text = self.font_medium.render(status, True, color)
        status_rect = status_text.get_rect(center=(self.screen_width // 2, info_y + 70))
        self.screen.blit(status_text, status_rect)

        # Estado de palas
        left_status = "ACTIVA" if left_paddle_active else "INACTIVA"
        right_status = "ACTIVA" if right_paddle_active else "INACTIVA"

        left_color = self.GREEN if left_paddle_active else self.RED
        right_color = self.GREEN if right_paddle_active else self.RED

        left_text = self.font_small.render(f"Pala Izq: {left_status}", True, left_color)
        right_text = self.font_small.render(f"Pala Der: {right_status}", True, right_color)

        self.screen.blit(left_text, (50, info_y + 110))
        self.screen.blit(right_text, (50, info_y + 140))

        # Información de conexión y logging
        conn_text = self.font_small.render(
            "✅ Arduino conectado con Firmata | 📝 Logs: data/pingpong.log",
            True, self.GREEN
        )
        self.screen.blit(conn_text, (50, info_y + 180))

    def update_display(self):
        """Actualizar la pantalla"""
        if self.initialized:
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self) -> Tuple[bool, Optional[str]]:
        """
        Manejar eventos de Pygame
        Retorna: (continuar_juego, accion)
        """
        if not self.initialized:
            return True, None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, "QUIT"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, "ESCAPE"
                elif event.key == pygame.K_r:
                    return True, "RESET"
                elif event.key == pygame.K_p:
                    return True, "PAUSE"

        return True, None
