"""
Manejo visual para el juego Osu! - Renderizado de círculos, cursor y efectos
"""

import time
import math
from typing import List, Tuple, Optional, Dict, Any
from .game_logic import GameState, Circle, HitResult


class OsuVisualManager:
    """Maneja toda la visualización del juego Osu"""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Inicialización de pygame
        self.pygame = None
        self.screen = None
        self.clock = None
        self.font_small = None
        self.font_medium = None
        self.font_large = None

        # Estados visuales
        self.cursor_trail = []
        self.hit_effects = []
        self.background_particles = []

        # Configuración visual
        self.cursor_size = 15
        self.cursor_color = (255, 255, 255)
        self.trail_length = 10
        self.show_timing_circles = True

        # Colores del tema
        self.colors = {
            "background": (20, 20, 30),
            "ui_primary": (255, 255, 255),
            "ui_secondary": (180, 180, 180),
            "cursor": (255, 255, 255),
            "cursor_trail": (255, 255, 255, 100),
            "perfect": (255, 215, 0),  # Dorado
            "good": (50, 255, 50),  # Verde
            "normal": (100, 150, 255),  # Azul
            "miss": (255, 50, 50),  # Rojo
            "combo_text": (255, 255, 100),
        }

        self.initialized = False

    def initialize_pygame(self) -> bool:
        """Inicializar pygame y crear ventana"""
        print("[DEBUG OsuVisualManager] Intentando initialize_pygame...")
        if self.initialized:
            print("[DEBUG OsuVisualManager] Ya inicializado.")
            return True
            
        try:
            import pygame

            self.pygame = pygame

            # Inicializar pygame
            pygame.init()

            # Crear ventana
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            pygame.display.set_caption("🎯 Osu! - Rhythm Game")

            # Clock para FPS
            self.clock = pygame.time.Clock()

            # Fuentes
            self.font_small = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_large = pygame.font.Font(None, 48)

            self.initialized = True
            print("✅ Visual manager Osu inicializado (desde initialize_pygame)")
            return True

        except ImportError:
            print("⚠️ Pygame no disponible - Visual deshabilitado")
            return False
        except Exception as e:
            print(f"❌ Error inicializando visual: {e}")
            return False

    def update_cursor_position(self, x: int, y: int):
        """Actualizar posición del cursor y su trail"""
        # Agregar posición actual al trail
        self.cursor_trail.append((x, y, time.time()))

        # Mantener longitud del trail
        if len(self.cursor_trail) > self.trail_length:
            self.cursor_trail.pop(0)

    def add_hit_effect(self, x: int, y: int, hit_result: HitResult, points: int):
        """Agregar efecto visual de hit"""
        effect = {
            "x": x,
            "y": y,
            "result": hit_result,
            "points": points,
            "start_time": time.time(),
            "duration": 0.5,
        }
        self.hit_effects.append(effect)

    def render_frame(
        self,
        game_state: GameState,
        circles: List[Circle],
        cursor_x: int,
        cursor_y: int,
        game_status: Dict[str, Any],
    ):
        """Renderizar frame completo del juego"""
        # print("[DEBUG OsuVisualManager] render_frame llamado") # Comentado para no inundar consola
        if not self.initialized:
            # print("[DEBUG OsuVisualManager] render_frame - no inicializado, retornando.")
            return

        # Limpiar pantalla
        self.screen.fill(self.colors["background"])

        # Actualizar cursor
        self.update_cursor_position(cursor_x, cursor_y)

        # Renderizar elementos según el estado
        if game_state == GameState.MENU:
            self._render_menu()
        elif game_state == GameState.PLAYING:
            self._render_game(circles, cursor_x, cursor_y, game_status)
        elif game_state == GameState.PAUSED:
            self._render_game(circles, cursor_x, cursor_y, game_status)
            self._render_pause_overlay()
        elif game_state == GameState.RESULTS:
            self._render_results(game_status)

        # Actualizar efectos
        self._update_effects()

        # Actualizar display
        self.pygame.display.flip()
        self.clock.tick(60)  # 60 FPS

    def _render_menu(self):
        """Renderizar menú principal"""
        print("[DEBUG OsuVisualManager] _render_menu llamado")
        # Título
        title_text = self.font_large.render(
            "🎯 OSU! RHYTHM", True, self.colors["ui_primary"]
        )
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title_text, title_rect)

        # Instrucciones
        instructions = [
            "Mueve el cursor con el joystick",
            "Presiona el botón para hacer click",
            "Clickea los círculos cuando aparezcan",
            "¡Precision y timing son clave!",
            "",
            "Conexiones del Joystick KY-023:",
            "VCC -> 5V | GND -> GND",
            "VRx -> A0 | VRy -> A1 | SW -> D2",
        ]

        y_offset = 250
        for instruction in instructions:
            if instruction == "":
                y_offset += 20
                continue

            color = (
                self.colors["ui_secondary"]
                if "Conexiones" in instruction
                else self.colors["ui_primary"]
            )
            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

        # Presiona para empezar
        start_text = self.font_medium.render(
            "Presiona el botón del joystick para empezar", True, self.colors["perfect"]
        )
        start_rect = start_text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 80)
        )
        self.screen.blit(start_text, start_rect)

    def _render_game(
        self,
        circles: List[Circle],
        cursor_x: int,
        cursor_y: int,
        game_status: Dict[str, Any],
    ):
        """Renderizar juego activo"""
        # Renderizar círculos
        self._render_circles(circles)

        # Renderizar cursor y trail
        self._render_cursor(cursor_x, cursor_y)

        # Renderizar UI del juego
        self._render_game_ui(game_status)

        # Renderizar efectos de hit
        self._render_hit_effects()

    def _render_circles(self, circles: List[Circle]):
        """Renderizar círculos del juego"""
        current_time = time.time() * 1000

        for circle in circles:
            if circle.is_hit and circle.hit_result != HitResult.MISS:
                continue  # No renderizar círculos ya golpeados (excepto miss)

            # Calcular alpha basado en tiempo de vida
            time_left = circle.hit_time - current_time
            alpha = max(0, min(255, int(255 * (time_left / 2000))))

            if alpha <= 0:
                continue

            # Color del círculo con transparencia
            color = list(circle.color) + [alpha]

            # Crear superficie con alpha
            circle_surface = self.pygame.Surface(
                (circle.radius * 2, circle.radius * 2), self.pygame.SRCALPHA
            )

            # Círculo principal
            self.pygame.draw.circle(
                circle_surface, color, (circle.radius, circle.radius), circle.radius
            )

            # Borde
            border_color = [min(255, c + 50) for c in color[:3]] + [alpha]
            self.pygame.draw.circle(
                circle_surface,
                border_color,
                (circle.radius, circle.radius),
                circle.radius,
                3,
            )

            # Círculo de timing (se encoge con el tiempo)
            if self.show_timing_circles and time_left > 0:
                timing_radius = int(circle.radius * 1.5 * (time_left / 2000))
                if timing_radius > circle.radius:
                    timing_color = [255, 255, 255, alpha // 3]
                    self.pygame.draw.circle(
                        circle_surface,
                        timing_color,
                        (circle.radius, circle.radius),
                        timing_radius,
                        2,
                    )

            # Dibujar en pantalla
            self.screen.blit(
                circle_surface, (circle.x - circle.radius, circle.y - circle.radius)
            )

            # Renderizar miss visual
            if circle.is_hit and circle.hit_result == HitResult.MISS:
                miss_text = self.font_small.render("MISS", True, self.colors["miss"])
                miss_rect = miss_text.get_rect(center=(circle.x, circle.y))
                self.screen.blit(miss_text, miss_rect)

    def _render_cursor(self, cursor_x: int, cursor_y: int):
        """Renderizar cursor y su trail"""
        current_time = time.time()

        # Renderizar trail del cursor
        for i, (trail_x, trail_y, trail_time) in enumerate(self.cursor_trail):
            age = current_time - trail_time
            if age > 0.5:
                continue

            # Alpha basado en edad y posición en el trail
            alpha = int(255 * (1 - age / 0.5) * (i + 1) / len(self.cursor_trail))

            if alpha > 10:
                trail_color = list(self.colors["cursor_trail"][:3]) + [alpha]
                trail_size = int(self.cursor_size * (1 - age / 0.5) * 0.5)

                # Crear superficie con alpha para el trail
                trail_surface = self.pygame.Surface(
                    (trail_size * 2, trail_size * 2), self.pygame.SRCALPHA
                )
                self.pygame.draw.circle(
                    trail_surface, trail_color, (trail_size, trail_size), trail_size
                )
                self.screen.blit(
                    trail_surface, (trail_x - trail_size, trail_y - trail_size)
                )

        # Cursor principal
        self.pygame.draw.circle(
            self.screen, self.colors["cursor"], (cursor_x, cursor_y), self.cursor_size
        )
        self.pygame.draw.circle(
            self.screen, (100, 100, 100), (cursor_x, cursor_y), self.cursor_size, 2
        )

        # Punto central del cursor
        self.pygame.draw.circle(self.screen, (255, 255, 255), (cursor_x, cursor_y), 2)

    def _render_game_ui(self, game_status: Dict[str, Any]):
        """Renderizar UI del juego (puntuación, combo, etc.)"""
        # Puntuación
        score_text = self.font_medium.render(
            f"Score: {game_status['score']:,}", True, self.colors["ui_primary"]
        )
        self.screen.blit(score_text, (20, 20))

        # Combo
        combo = game_status["combo"]
        if combo > 0:
            combo_color = (
                self.colors["combo_text"] if combo >= 10 else self.colors["ui_primary"]
            )
            combo_text = self.font_medium.render(f"Combo: {combo}x", True, combo_color)
            self.screen.blit(combo_text, (20, 60))

        # Precisión
        accuracy = game_status["accuracy"]
        accuracy_text = self.font_small.render(
            f"Accuracy: {accuracy:.1f}%", True, self.colors["ui_secondary"]
        )
        self.screen.blit(accuracy_text, (20, 100))

        # Nivel de dificultad
        difficulty_text = self.font_small.render(
            f"Level: {game_status['difficulty_level']}",
            True,
            self.colors["ui_secondary"],
        )
        self.screen.blit(difficulty_text, (20, 130))

        # Información en la esquina superior derecha
        # Círculos restantes
        active_circles = game_status["active_circles"]
        circles_text = self.font_small.render(
            f"Active: {active_circles}", True, self.colors["ui_secondary"]
        )
        circles_rect = circles_text.get_rect(topright=(self.screen_width - 20, 20))
        self.screen.blit(circles_text, circles_rect)

        # Tiempo de juego
        game_time = game_status["game_duration"]
        time_text = self.font_small.render(
            f"Time: {game_time:.1f}s", True, self.colors["ui_secondary"]
        )
        time_rect = time_text.get_rect(topright=(self.screen_width - 20, 50))
        self.screen.blit(time_text, time_rect)

        # Estadísticas de hits
        perfect_hits = game_status["perfect_hits"]
        good_hits = game_status["good_hits"]
        normal_hits = game_status["normal_hits"]
        missed = game_status["circles_missed"]

        stats_y = self.screen_height - 120
        perfect_text = self.font_small.render(
            f"Perfect: {perfect_hits}", True, self.colors["perfect"]
        )
        self.screen.blit(perfect_text, (20, stats_y))

        good_text = self.font_small.render(
            f"Good: {good_hits}", True, self.colors["good"]
        )
        self.screen.blit(good_text, (20, stats_y + 25))

        normal_text = self.font_small.render(
            f"Normal: {normal_hits}", True, self.colors["normal"]
        )
        self.screen.blit(normal_text, (20, stats_y + 50))

        miss_text = self.font_small.render(f"Miss: {missed}", True, self.colors["miss"])
        self.screen.blit(miss_text, (20, stats_y + 75))

    def _render_hit_effects(self):
        """Renderizar efectos de hit"""
        current_time = time.time()
        effects_to_remove = []

        for effect in self.hit_effects:
            age = current_time - effect["start_time"]
            if age > effect["duration"]:
                effects_to_remove.append(effect)
                continue

            # Calcular alpha y escala basado en edad
            progress = age / effect["duration"]
            alpha = int(255 * (1 - progress))
            scale = 1 + progress * 2

            # Color basado en resultado
            color_map = {
                HitResult.PERFECT: self.colors["perfect"],
                HitResult.GOOD: self.colors["good"],
                HitResult.NORMAL: self.colors["normal"],
                HitResult.MISS: self.colors["miss"],
            }

            color = list(color_map[effect["result"]]) + [alpha]

            # Texto del resultado
            result_text = effect["result"].name
            if effect["points"] > 0:
                result_text += f" +{effect['points']}"

            # Renderizar texto con efecto
            font_size = int(24 * scale)
            font = self.pygame.font.Font(None, font_size)
            text_surface = font.render(result_text, True, color[:3])

            # Posición con movimiento hacia arriba
            effect_y = effect["y"] - int(30 * progress)
            text_rect = text_surface.get_rect(center=(effect["x"], effect_y))

            # Crear superficie con alpha
            effect_surface = self.pygame.Surface(
                text_surface.get_size(), self.pygame.SRCALPHA
            )
            effect_surface.set_alpha(alpha)
            effect_surface.blit(text_surface, (0, 0))

            self.screen.blit(effect_surface, text_rect)

        # Remover efectos expirados
        for effect in effects_to_remove:
            self.hit_effects.remove(effect)

    def _render_pause_overlay(self):
        """Renderizar overlay de pausa"""
        # Overlay semi-transparente
        overlay = self.pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Texto de pausa
        pause_text = self.font_large.render("PAUSED", True, self.colors["ui_primary"])
        pause_rect = pause_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        self.screen.blit(pause_text, pause_rect)

        # Instrucciones
        resume_text = self.font_small.render(
            "Presiona botón para continuar", True, self.colors["ui_secondary"]
        )
        resume_rect = resume_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 50)
        )
        self.screen.blit(resume_text, resume_rect)

    def _render_results(self, game_status: Dict[str, Any]):
        """Renderizar pantalla de resultados"""
        # Título
        results_text = self.font_large.render(
            "GAME RESULTS", True, self.colors["ui_primary"]
        )
        results_rect = results_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(results_text, results_rect)

        # Puntuación final
        final_score = self.font_medium.render(
            f"Final Score: {game_status['score']:,}", True, self.colors["perfect"]
        )
        score_rect = final_score.get_rect(center=(self.screen_width // 2, 180))
        self.screen.blit(final_score, score_rect)

        # Estadísticas
        stats = [
            f"Max Combo: {game_status['max_combo']}x",
            f"Accuracy: {game_status['accuracy']:.1f}%",
            f"Perfect Hits: {game_status['perfect_hits']}",
            f"Good Hits: {game_status['good_hits']}",
            f"Normal Hits: {game_status['normal_hits']}",
            f"Missed: {game_status['circles_missed']}",
            f"Total Circles: {game_status['total_circles']}",
            f"Time Played: {game_status['game_duration']:.1f}s",
        ]

        y_offset = 250
        for stat in stats:
            stat_text = self.font_small.render(stat, True, self.colors["ui_secondary"])
            stat_rect = stat_text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(stat_text, stat_rect)
            y_offset += 30

        # Instrucciones para reiniciar
        restart_text = self.font_small.render(
            "Presiona botón para nuevo juego", True, self.colors["ui_primary"]
        )
        restart_rect = restart_text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)
        )
        self.screen.blit(restart_text, restart_rect)

    def _update_effects(self):
        """Actualizar efectos visuales"""
        # Limpiar trail antiguo
        current_time = time.time()
        self.cursor_trail = [
            (x, y, t) for x, y, t in self.cursor_trail if current_time - t < 0.5
        ]

    def mostrar_animacion_inicio(self, audio_manager=None):
        """Mostrar animación de inicio del juego Osu"""
        print("[DEBUG OsuVisualManager] Intentando mostrar_animacion_inicio...")
        if not self.initialize_pygame():
            print("⚠️ No se puede mostrar animación - pygame no disponible (desde mostrar_animacion_inicio)")
            return
        
        print("🎯 Mostrando animación de inicio Osu... (desde mostrar_animacion_inicio)")
        
        # Animación de 2 segundos
        for frame in range(120):  # 2 segundos a 60 FPS
            # Limpiar pantalla
            self.screen.fill(self.colors["background"])
            
            # Calcular progreso de animación
            progress = frame / 120.0
            
            # Texto principal con efecto de aparición
            if frame > 30:
                alpha = min(255, int(255 * (frame - 30) / 30))
                title_text = self.font_large.render("🎯 OSU! RHYTHM", True, self.colors["ui_primary"])
                title_rect = title_text.get_rect(center=(self.screen_width // 2, 200))
                
                # Crear superficie con alpha
                title_surface = self.pygame.Surface(title_text.get_size(), self.pygame.SRCALPHA)
                title_surface.set_alpha(alpha)
                title_surface.blit(title_text, (0, 0))
                self.screen.blit(title_surface, title_rect)
            
            # Texto de instrucciones
            if frame > 60:
                alpha = min(255, int(255 * (frame - 60) / 30))
                instruction_text = self.font_medium.render("Usa el joystick para mover el cursor", True, self.colors["ui_secondary"])
                instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, 300))
                
                instruction_surface = self.pygame.Surface(instruction_text.get_size(), self.pygame.SRCALPHA)
                instruction_surface.set_alpha(alpha)
                instruction_surface.blit(instruction_text, (0, 0))
                self.screen.blit(instruction_surface, instruction_rect)
            
            # Indicador de "Presiona para empezar"
            if frame > 90:
                alpha = int(255 * (0.5 + 0.5 * math.sin(frame * 0.2)))
                start_text = self.font_small.render("Presiona el botón del joystick para empezar", True, self.colors["perfect"])
                start_rect = start_text.get_rect(center=(self.screen_width // 2, 400))
                
                start_surface = self.pygame.Surface(start_text.get_size(), self.pygame.SRCALPHA)
                start_surface.set_alpha(alpha)
                start_surface.blit(start_text, (0, 0))
                self.screen.blit(start_surface, start_rect)
            
            # Círculos decorativos animados
            for i in range(5):
                angle = frame * 0.05 + i * 1.2
                x = self.screen_width // 2 + int(150 * math.cos(angle))
                y = self.screen_height // 2 + int(100 * math.sin(angle))
                radius = int(20 + 10 * math.sin(frame * 0.1 + i))
                color = [int(c * (0.3 + 0.3 * math.sin(frame * 0.03 + i))) for c in self.colors["perfect"]]
                
                self.pygame.draw.circle(self.screen, color, (x, y), radius, 2)
            
            # Actualizar pantalla
            self.pygame.display.flip()
            self.clock.tick(60)
            
            # Procesar eventos para evitar que se cuelgue
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    return
        
        print("✅ Animación de inicio completada")

    def process_events(self) -> Dict[str, bool]:
        """Procesar eventos de pygame"""
        events = {
            "quit": False,
            "key_escape": False,
            "key_r": False,
            "key_p": False,
            "key_space": False,
        }

        if not self.initialized:
            return events

        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                events["quit"] = True
            elif event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_ESCAPE:
                    events["key_escape"] = True
                elif event.key == self.pygame.K_r:
                    events["key_r"] = True
                elif event.key == self.pygame.K_p:
                    events["key_p"] = True
                elif event.key == self.pygame.K_SPACE:
                    events["key_space"] = True

        return events

    def cleanup(self):
        """Limpiar recursos visuales"""
        try:
            if self.pygame:
                self.pygame.quit()
            print("🧹 Visual manager Osu limpiado")
        except Exception as e:
            print(f"⚠️ Error limpiando visual: {e}")

    def get_visual_info(self) -> Dict[str, Any]:
        """Obtener información del sistema visual"""
        return {
            "initialized": self.initialized,
            "screen_size": (self.screen_width, self.screen_height),
            "cursor_trail_length": len(self.cursor_trail),
            "active_hit_effects": len(self.hit_effects),
            "show_timing_circles": self.show_timing_circles,
        }
