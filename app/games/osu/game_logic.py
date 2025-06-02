"""
Lógica principal del juego Osu! - Círculos, timing, precisión y puntuación
"""

import time
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# Importar logging cognitivo
try:
    import sys
    import os
    # Agregar el directorio app al path si no está
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(current_dir, "..", "..")
    app_dir = os.path.abspath(app_dir)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    from core.cognitive import SessionManager
    COGNITIVE_LOGGING_AVAILABLE = True
    print("✅ Logging cognitivo Osu habilitado")
except ImportError as e:
    COGNITIVE_LOGGING_AVAILABLE = False
    print(f"⚠️ Logging cognitivo no disponible: {e}")
except Exception as e:
    COGNITIVE_LOGGING_AVAILABLE = False
    print(f"⚠️ Error cargando sistema cognitivo: {e}")


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    RESULTS = 4


class HitResult(Enum):
    MISS = 0
    NORMAL = 1
    GOOD = 2
    PERFECT = 3


@dataclass
class Circle:
    """Representa un círculo en el juego"""
    x: int
    y: int
    spawn_time: float
    hit_time: float
    radius: int
    color: Tuple[int, int, int]
    is_hit: bool = False
    hit_result: Optional[HitResult] = None
    hit_accuracy: float = 0.0


@dataclass
class Hit:
    """Representa un hit del jugador"""
    circle: Circle
    cursor_x: int
    cursor_y: int
    hit_time: float
    distance_from_center: float
    timing_accuracy: float
    result: HitResult
    points: int


class OsuGameLogic:
    """Maneja la lógica principal del juego Osu"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600,
                 enable_cognitive_logging: bool = False, patient_id: str = "default"):
        
        # Configuración de la pantalla
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.safe_margin = 80  # Margen para que los círculos no aparezcan en el borde
        
        # Configuración del juego
        self.circle_radius = 40
        self.hit_window_perfect = 100  # ms para hit perfecto
        self.hit_window_good = 200     # ms para hit bueno
        self.hit_window_normal = 300   # ms para hit normal
        self.circle_lifetime = 2000    # ms que vive un círculo
        self.spawn_interval = 800      # ms entre spawns de círculos
        
        # Estado del juego
        self.game_state = GameState.MENU
        self.circles: List[Circle] = []
        self.hits: List[Hit] = []
        self.last_spawn_time = 0.0
        self.game_start_time = 0.0
        self.game_duration = 0.0
        
        # Estadísticas del juego
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.total_circles = 0
        self.circles_hit = 0
        self.circles_missed = 0
        self.perfect_hits = 0
        self.good_hits = 0
        self.normal_hits = 0
        
        # Niveles de dificultad dinámicos
        self.difficulty_level = 1
        self.circles_per_level = 10
        self.min_spawn_interval = 400
        
        # Colores de los círculos
        self.circle_colors = [
            (255, 100, 100),  # Rojo claro
            (100, 255, 100),  # Verde claro
            (100, 100, 255),  # Azul claro
            (255, 255, 100),  # Amarillo
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cian
            (255, 200, 100),  # Naranja
            (200, 100, 255),  # Púrpura
        ]
        
        # LOGGING COGNITIVO
        self.cognitive_logging = enable_cognitive_logging and COGNITIVE_LOGGING_AVAILABLE
        self.session_manager: Optional[SessionManager] = None
        self.current_logger = None
        self.patient_id = patient_id
        
        if self.cognitive_logging:
            try:
                self.session_manager = SessionManager()
                print("🧠 Logging cognitivo habilitado para Osu")
            except Exception as e:
                print(f"❌ Error iniciando logging cognitivo: {e}")
                self.cognitive_logging = False
        
        # Callbacks para eventos
        self.on_circle_spawn = None
        self.on_circle_hit = None
        self.on_circle_miss = None
        self.on_combo_milestone = None
    
    def set_callbacks(self, on_circle_spawn=None, on_circle_hit=None, 
                     on_circle_miss=None, on_combo_milestone=None):
        """Configurar callbacks para eventos del juego"""
        self.on_circle_spawn = on_circle_spawn
        self.on_circle_hit = on_circle_hit
        self.on_circle_miss = on_circle_miss
        self.on_combo_milestone = on_combo_milestone
    
    def start_game(self):
        """Iniciar nuevo juego"""
        self.game_state = GameState.PLAYING
        self.game_start_time = time.time() * 1000
        
        # Reiniciar estadísticas
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.total_circles = 0
        self.circles_hit = 0
        self.circles_missed = 0
        self.perfect_hits = 0
        self.good_hits = 0
        self.normal_hits = 0
        self.difficulty_level = 1
        
        # Limpiar círculos e hits
        self.circles.clear()
        self.hits.clear()
        
        self.last_spawn_time = self.game_start_time
        
        # COGNITIVE LOGGING: Iniciar nueva sesión
        if self.cognitive_logging and self.session_manager:
            try:
                self.current_logger = self.session_manager.start_session("osu_rhythm", self.patient_id)
                print("🧠 Sesión cognitiva Osu iniciada")
            except Exception as e:
                print(f"❌ Error iniciando sesión cognitiva: {e}")
        
        print("🎮 Juego Osu iniciado")
    
    def update(self, current_time: float, cursor_x: int, cursor_y: int, 
               button_just_pressed: bool) -> bool:
        """Actualizar lógica del juego - devuelve True si hay cambios"""
        if self.game_state != GameState.PLAYING:
            return False
        
        changed = False
        
        # Spawn de nuevos círculos
        if self._should_spawn_circle(current_time):
            self._spawn_circle(current_time)
            changed = True
        
        # Procesar click del jugador
        if button_just_pressed:
            if self._process_player_click(current_time, cursor_x, cursor_y):
                changed = True
        
        # Actualizar círculos existentes
        if self._update_circles(current_time):
            changed = True
        
        # Verificar condiciones de fin de juego
        self._check_game_end_conditions(current_time)
        
        return changed
    
    def _should_spawn_circle(self, current_time: float) -> bool:
        """Verificar si debe spawnearse un nuevo círculo"""
        current_interval = max(self.min_spawn_interval, 
                             self.spawn_interval - (self.difficulty_level * 30))
        return current_time - self.last_spawn_time >= current_interval
    
    def _spawn_circle(self, current_time: float):
        """Crear un nuevo círculo"""
        # Calcular posición aleatoria dentro de los márgenes seguros
        x = random.randint(self.safe_margin, self.screen_width - self.safe_margin)
        y = random.randint(self.safe_margin, self.screen_height - self.safe_margin)
        
        # Evitar solapamiento con círculos existentes
        attempts = 0
        while attempts < 10:
            overlap = False
            for circle in self.circles:
                if not circle.is_hit:
                    distance = math.sqrt((x - circle.x)**2 + (y - circle.y)**2)
                    if distance < (self.circle_radius * 2.5):
                        overlap = True
                        break
            
            if not overlap:
                break
                
            x = random.randint(self.safe_margin, self.screen_width - self.safe_margin)
            y = random.randint(self.safe_margin, self.screen_height - self.safe_margin)
            attempts += 1
        
        # Crear círculo
        color = random.choice(self.circle_colors)
        hit_time = current_time + self.circle_lifetime
        
        circle = Circle(
            x=x, y=y,
            spawn_time=current_time,
            hit_time=hit_time,
            radius=self.circle_radius,
            color=color
        )
        
        self.circles.append(circle)
        self.total_circles += 1
        self.last_spawn_time = current_time
        
        # Callback de spawn
        if self.on_circle_spawn:
            self.on_circle_spawn()
        
        # Incrementar dificultad cada ciertos círculos
        if self.total_circles % self.circles_per_level == 0:
            self.difficulty_level += 1
            print(f"🆙 Nivel de dificultad: {self.difficulty_level}")
    
    def _process_player_click(self, current_time: float, cursor_x: int, cursor_y: int) -> bool:
        """Procesar click del jugador"""
        closest_circle = None
        closest_distance = float('inf')
        
        # Buscar el círculo más cercano al cursor que esté activo
        for circle in self.circles:
            if circle.is_hit:
                continue
                
            distance = math.sqrt((cursor_x - circle.x)**2 + (cursor_y - circle.y)**2)
            
            # Solo considerar círculos dentro del rango de hit
            if distance <= self.circle_radius * 1.2 and distance < closest_distance:
                closest_circle = circle
                closest_distance = distance
        
        if closest_circle is None:
            return False
        
        # Calcular timing accuracy
        optimal_hit_time = closest_circle.hit_time - (self.circle_lifetime / 2)
        timing_diff = abs(current_time - optimal_hit_time)
        
        # Determinar resultado del hit
        hit_result = self._calculate_hit_result(timing_diff, closest_distance)
        
        if hit_result == HitResult.MISS:
            return False
        
        # Marcar círculo como golpeado
        closest_circle.is_hit = True
        closest_circle.hit_result = hit_result
        
        # Calcular puntos
        points = self._calculate_points(hit_result, closest_distance, timing_diff)
        self.score += points
        
        # Actualizar combo
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        
        # Actualizar estadísticas
        self.circles_hit += 1
        if hit_result == HitResult.PERFECT:
            self.perfect_hits += 1
        elif hit_result == HitResult.GOOD:
            self.good_hits += 1
        elif hit_result == HitResult.NORMAL:
            self.normal_hits += 1
        
        # Crear registro del hit
        hit = Hit(
            circle=closest_circle,
            cursor_x=cursor_x,
            cursor_y=cursor_y,
            hit_time=current_time,
            distance_from_center=closest_distance,
            timing_accuracy=timing_diff,
            result=hit_result,
            points=points
        )
        self.hits.append(hit)
        
        # COGNITIVE LOGGING
        if self.cognitive_logging and self.current_logger:
            try:
                reaction_time = current_time - closest_circle.spawn_time
                spatial_accuracy = 100 * (1 - closest_distance / (self.circle_radius * 1.2))
                temporal_accuracy = 100 * (1 - timing_diff / self.hit_window_normal)
                
                self.current_logger.log_osu_event(
                    circle_x=closest_circle.x,
                    circle_y=closest_circle.y,
                    cursor_x=cursor_x,
                    cursor_y=cursor_y,
                    spawn_time=closest_circle.spawn_time,
                    hit_time=current_time,
                    reaction_time=reaction_time,
                    spatial_accuracy=max(0, spatial_accuracy),
                    temporal_accuracy=max(0, temporal_accuracy),
                    hit_result=hit_result.name,
                    score=points,
                    combo=self.combo,
                    difficulty_level=self.difficulty_level
                )
            except Exception as e:
                print(f"❌ Error logging evento cognitivo: {e}")
        
        # Callbacks
        if self.on_circle_hit:
            self.on_circle_hit(hit_result, points)
        
        if self.combo % 10 == 0 and self.on_combo_milestone:
            self.on_combo_milestone(self.combo)
        
        return True
    
    def _calculate_hit_result(self, timing_diff: float, distance: float) -> HitResult:
        """Calcular resultado del hit basado en timing y distancia"""
        # Verificar si está dentro del radio del círculo
        if distance > self.circle_radius * 1.2:
            return HitResult.MISS
        
        # Verificar timing
        if timing_diff > self.hit_window_normal:
            return HitResult.MISS
        elif timing_diff <= self.hit_window_perfect and distance <= self.circle_radius * 0.3:
            return HitResult.PERFECT
        elif timing_diff <= self.hit_window_good and distance <= self.circle_radius * 0.7:
            return HitResult.GOOD
        else:
            return HitResult.NORMAL
    
    def _calculate_points(self, hit_result: HitResult, distance: float, timing_diff: float) -> int:
        """Calcular puntos basado en la precisión"""
        base_points = {
            HitResult.PERFECT: 100,
            HitResult.GOOD: 75,
            HitResult.NORMAL: 50,
            HitResult.MISS: 0
        }
        
        points = base_points[hit_result]
        
        # Bonus por combo
        combo_multiplier = min(1.0 + (self.combo * 0.1), 3.0)
        points = int(points * combo_multiplier)
        
        # Bonus por dificultad
        difficulty_bonus = self.difficulty_level * 5
        points += difficulty_bonus
        
        return points
    
    def _update_circles(self, current_time: float) -> bool:
        """Actualizar estado de los círculos"""
        changed = False
        circles_to_remove = []
        
        for circle in self.circles:
            if circle.is_hit:
                # Remover círculos golpeados después de un tiempo
                if current_time - circle.hit_time > 200:
                    circles_to_remove.append(circle)
                    changed = True
            else:
                # Verificar si el círculo expiró (miss)
                if current_time > circle.hit_time:
                    circle.is_hit = True
                    circle.hit_result = HitResult.MISS
                    
                    self.circles_missed += 1
                    self.combo = 0  # Reset combo en miss
                    
                    if self.on_circle_miss:
                        self.on_circle_miss()
                    
                    circles_to_remove.append(circle)
                    changed = True
        
        # Remover círculos marcados
        for circle in circles_to_remove:
            self.circles.remove(circle)
        
        return changed
    
    def _check_game_end_conditions(self, current_time: float):
        """Verificar condiciones de fin de juego"""
        self.game_duration = current_time - self.game_start_time
        
        # Fin por tiempo (ejemplo: 2 minutos)
        if self.game_duration > 120000:  # 2 minutos en ms
            self.end_game()
    
    def end_game(self):
        """Terminar juego y mostrar resultados"""
        self.game_state = GameState.RESULTS
        
        # COGNITIVE LOGGING: Cerrar sesión
        if self.cognitive_logging and self.session_manager:
            try:
                csv_file = self.session_manager.end_session()
                if csv_file:
                    print(f"🧠 Datos cognitivos Osu guardados: {csv_file}")
            except Exception as e:
                print(f"❌ Error cerrando sesión cognitiva: {e}")
        
        print(f"🏁 Juego terminado - Puntuación final: {self.score}")
    
    def pause_game(self):
        """Pausar juego"""
        if self.game_state == GameState.PLAYING:
            self.game_state = GameState.PAUSED
    
    def resume_game(self):
        """Reanudar juego"""
        if self.game_state == GameState.PAUSED:
            self.game_state = GameState.PLAYING
    
    def get_game_status(self) -> Dict[str, Any]:
        """Obtener estado completo del juego"""
        accuracy = (self.circles_hit / max(1, self.total_circles)) * 100
        
        return {
            "game_state": self.game_state,
            "score": self.score,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "total_circles": self.total_circles,
            "circles_hit": self.circles_hit,
            "circles_missed": self.circles_missed,
            "perfect_hits": self.perfect_hits,
            "good_hits": self.good_hits,
            "normal_hits": self.normal_hits,
            "accuracy": accuracy,
            "difficulty_level": self.difficulty_level,
            "game_duration": self.game_duration / 1000.0,  # en segundos
            "active_circles": len([c for c in self.circles if not c.is_hit]),
            "circles": self.circles,
            "recent_hits": self.hits[-10:] if len(self.hits) > 10 else self.hits
        }
    
    def get_difficulty_info(self) -> Dict[str, Any]:
        """Obtener información de dificultad actual"""
        current_interval = max(self.min_spawn_interval, 
                             self.spawn_interval - (self.difficulty_level * 30))
        
        return {
            "level": self.difficulty_level,
            "spawn_interval": current_interval,
            "circles_per_level": self.circles_per_level,
            "circle_radius": self.circle_radius,
            "hit_windows": {
                "perfect": self.hit_window_perfect,
                "good": self.hit_window_good,
                "normal": self.hit_window_normal
            }
        } 