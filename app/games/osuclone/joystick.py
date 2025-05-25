import pygame
import math
import random
import time
import json
from datetime import datetime
from pyfirmata import Arduino, util
import threading


class JoystickCoordinationGame:
    def __init__(self, arduino_port="COM5", difficulty="medio"):
        # Configuración de pygame
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Juego de Coordinación Visuomotora")

        # Colores Arduino
        self.COLORS = {
            "white": (255, 255, 255),
            "light_blue": (79, 204, 243),
            "medium_blue": (49, 134, 160),
            "purple": (74, 35, 112),
            "dark_blue": (29, 32, 135),
            "black": (0, 0, 0),
            "green": (0, 255, 0),
            "red": (255, 0, 0),
            "yellow": (255, 255, 0),
        }

        # Configuración de dificultad
        self.difficulty_settings = {
            "facil": {"num_points": 5, "point_radius": 30, "tolerance_radius": 40},
            "medio": {"num_points": 7, "point_radius": 25, "tolerance_radius": 35},
            "dificil": {"num_points": 11, "point_radius": 20, "tolerance_radius": 30},
        }

        self.difficulty = difficulty
        self.settings = self.difficulty_settings[difficulty]

        # Variables del juego
        self.points = []
        self.current_point_index = 0
        self.cursor_pos = [self.screen_width // 2, self.screen_height // 2]
        self.game_state = "waiting"  # 'waiting', 'showing', 'playing', 'finished'
        self.show_time = 3000  # 3 segundos para mostrar puntos
        self.start_time = None
        self.results = []
        self.session_data = []

        # Arduino setup
        self.arduino_port = arduino_port
        self.board = None
        self.joystick_x = None
        self.joystick_y = None
        self.joystick_button = None
        self.button_pressed = False
        self.last_button_state = False

        # Fuentes
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Clock para FPS
        self.clock = pygame.time.Clock()

        self.setup_arduino()

    def setup_arduino(self):
        """Configurar conexión con Arduino"""
        try:
            self.board = Arduino(self.arduino_port)
            # Configurar iterator para lectura continua
            it = util.Iterator(self.board)
            it.start()

            # Configurar pines del joystick
            self.joystick_x = self.board.get_pin("a:0:i")  # Pin analógico A0
            self.joystick_y = self.board.get_pin("a:1:i")  # Pin analógico A1
            self.joystick_button = self.board.get_pin("d:2:i")  # Pin digital 2

            print(f"Arduino conectado en {self.arduino_port}")
            time.sleep(2)  # Dar tiempo para estabilizar la conexión

        except Exception as e:
            print(f"Error conectando Arduino: {e}")
            self.board = None

    def generate_points(self):
        """Generar puntos aleatorios en la pantalla"""
        self.points = []
        margin = 100

        for i in range(self.settings["num_points"]):
            while True:
                x = random.randint(margin, self.screen_width - margin)
                y = random.randint(margin, self.screen_height - margin)

                # Verificar que no esté muy cerca de otros puntos
                valid = True
                for existing_point in self.points:
                    distance = math.sqrt(
                        (x - existing_point[0]) ** 2 + (y - existing_point[1]) ** 2
                    )
                    if distance < 80:  # Distancia mínima entre puntos
                        valid = False
                        break

                if valid:
                    self.points.append((x, y))
                    break

    def read_joystick(self):
        """Leer valores del joystick de Arduino"""
        if not self.board:
            return

        try:
            # Leer valores analógicos (0.0 a 1.0)
            x_val = self.joystick_x.read()
            y_val = self.joystick_y.read()
            button_val = self.joystick_button.read()

            if x_val is not None and y_val is not None:
                # Convertir a coordenadas de pantalla
                # Centrar en 0.5 y escalar
                x_offset = (x_val - 0.5) * 400  # Sensibilidad ajustable
                y_offset = (y_val - 0.5) * 300

                # Actualizar posición del cursor
                self.cursor_pos[0] = max(
                    0, min(self.screen_width, self.screen_width // 2 + x_offset)
                )
                self.cursor_pos[1] = max(
                    0, min(self.screen_height, self.screen_height // 2 + y_offset)
                )

            # Detectar presión del botón (flanco ascendente)
            if button_val is not None:
                if button_val and not self.last_button_state:
                    self.button_pressed = True
                self.last_button_state = button_val

        except Exception as e:
            print(f"Error leyendo joystick: {e}")

    def handle_button_press(self):
        """Manejar presión del botón del joystick"""
        if not self.button_pressed:
            return

        self.button_pressed = False

        if self.game_state == "playing":
            # Registrar intento
            target_point = self.points[self.current_point_index]
            distance = math.sqrt(
                (self.cursor_pos[0] - target_point[0]) ** 2
                + (self.cursor_pos[1] - target_point[1]) ** 2
            )

            # Verificar si acertó
            hit = distance <= self.settings["tolerance_radius"]

            # Guardar resultado
            result = {
                "point_index": self.current_point_index,
                "target_pos": target_point,
                "cursor_pos": tuple(self.cursor_pos),
                "distance": distance,
                "hit": hit,
                "timestamp": time.time(),
                "reaction_time": time.time() - self.start_time
                if self.start_time
                else 0,
            }

            self.results.append(result)
            self.session_data.append(result)

            # Avanzar al siguiente punto
            self.current_point_index += 1

            if self.current_point_index >= len(self.points):
                self.game_state = "finished"
                self.save_session_data()
            else:
                self.start_time = time.time()

    def save_session_data(self):
        """Guardar datos de la sesión en archivo log"""
        session_summary = {
            "timestamp": datetime.now().isoformat(),
            "difficulty": self.difficulty,
            "total_points": len(self.points),
            "hits": sum(1 for r in self.results if r["hit"]),
            "accuracy": sum(1 for r in self.results if r["hit"])
            / len(self.results)
            * 100,
            "average_distance": sum(r["distance"] for r in self.results)
            / len(self.results),
            "average_reaction_time": sum(r["reaction_time"] for r in self.results)
            / len(self.results),
            "detailed_results": self.results,
        }

        try:
            # Leer datos existentes
            try:
                with open("joystick.log", "r") as f:
                    all_sessions = json.load(f)
            except FileNotFoundError:
                all_sessions = []

            # Agregar nueva sesión
            all_sessions.append(session_summary)

            # Guardar todo
            with open("joystick.log", "w") as f:
                json.dump(all_sessions, f, indent=2)

            print(f"Sesión guardada. Precisión: {session_summary['accuracy']:.1f}%")

        except Exception as e:
            print(f"Error guardando datos: {e}")

    def draw_game(self):
        """Dibujar el estado actual del juego"""
        self.screen.fill(self.WHITE)

        if self.game_state == "waiting":
            # Pantalla de inicio
            title = self.font.render(
                "Juego de Coordinación Visuomotora", True, self.BLACK
            )
            self.screen.blit(
                title, (self.screen_width // 2 - title.get_width() // 2, 200)
            )

            diff_text = self.small_font.render(
                f"Dificultad: {self.difficulty.capitalize()}", True, self.BLACK
            )
            self.screen.blit(
                diff_text, (self.screen_width // 2 - diff_text.get_width() // 2, 250)
            )

            points_text = self.small_font.render(
                f"Puntos a recordar: {self.settings['num_points']}", True, self.BLACK
            )
            self.screen.blit(
                points_text,
                (self.screen_width // 2 - points_text.get_width() // 2, 280),
            )

            start_text = self.small_font.render(
                "Presiona el botón del joystick para comenzar", True, self.BLUE
            )
            self.screen.blit(
                start_text, (self.screen_width // 2 - start_text.get_width() // 2, 350)
            )

        elif self.game_state == "showing":
            # Mostrar todos los puntos numerados
            for i, point in enumerate(self.points):
                # Dibujar círculo del punto
                pygame.draw.circle(
                    self.screen, self.BLUE, point, self.settings["point_radius"]
                )
                pygame.draw.circle(
                    self.screen, self.BLACK, point, self.settings["point_radius"], 2
                )

                # Dibujar número
                num_text = self.font.render(str(i + 1), True, self.WHITE)
                text_rect = num_text.get_rect(center=point)
                self.screen.blit(num_text, text_rect)

            # Mostrar tiempo restante
            remaining_time = max(
                0, self.show_time - (pygame.time.get_ticks() - self.show_start_time)
            )
            time_text = self.font.render(
                f"Memoriza los puntos: {remaining_time // 1000 + 1}", True, self.RED
            )
            self.screen.blit(time_text, (10, 10))

        elif self.game_state == "playing":
            # Mostrar punto actual objetivo
            current_target = self.points[self.current_point_index]
            pygame.draw.circle(
                self.screen,
                self.GREEN,
                current_target,
                self.settings["tolerance_radius"],
                3,
            )
            pygame.draw.circle(
                self.screen, self.RED, current_target, self.settings["point_radius"]
            )

            # Número del punto actual
            num_text = self.font.render(
                str(self.current_point_index + 1), True, self.WHITE
            )
            text_rect = num_text.get_rect(center=current_target)
            self.screen.blit(num_text, text_rect)

            # Mostrar progreso
            progress_text = self.small_font.render(
                f"Punto {self.current_point_index + 1} de {len(self.points)}",
                True,
                self.BLACK,
            )
            self.screen.blit(progress_text, (10, 10))

            # Mostrar puntos ya completados (más pequeños)
            for i in range(self.current_point_index):
                point = self.points[i]
                result = self.results[i]
                color = self.GREEN if result["hit"] else self.RED
                pygame.draw.circle(self.screen, color, point, 10)
                pygame.draw.circle(self.screen, self.BLACK, point, 10, 1)

        elif self.game_state == "finished":
            # Mostrar resultados
            hits = sum(1 for r in self.results if r["hit"])
            accuracy = hits / len(self.results) * 100
            avg_distance = sum(r["distance"] for r in self.results) / len(self.results)

            title = self.font.render("¡Juego Completado!", True, self.BLACK)
            self.screen.blit(
                title, (self.screen_width // 2 - title.get_width() // 2, 200)
            )

            accuracy_text = self.font.render(
                f"Precisión: {accuracy:.1f}%", True, self.BLACK
            )
            self.screen.blit(
                accuracy_text,
                (self.screen_width // 2 - accuracy_text.get_width() // 2, 250),
            )

            hits_text = self.small_font.render(
                f"Aciertos: {hits}/{len(self.results)}", True, self.BLACK
            )
            self.screen.blit(
                hits_text, (self.screen_width // 2 - hits_text.get_width() // 2, 280)
            )

            distance_text = self.small_font.render(
                f"Distancia promedio: {avg_distance:.1f} píxeles", True, self.BLACK
            )
            self.screen.blit(
                distance_text,
                (self.screen_width // 2 - distance_text.get_width() // 2, 310),
            )

            restart_text = self.small_font.render(
                "Presiona ESC para salir o ESPACIO para jugar de nuevo", True, self.BLUE
            )
            self.screen.blit(
                restart_text,
                (self.screen_width // 2 - restart_text.get_width() // 2, 400),
            )

        # Dibujar cursor del joystick
        if self.game_state in ["playing", "showing"]:
            pygame.draw.circle(
                self.screen,
                self.YELLOW,
                (int(self.cursor_pos[0]), int(self.cursor_pos[1])),
                8,
            )
            pygame.draw.circle(
                self.screen,
                self.BLACK,
                (int(self.cursor_pos[0]), int(self.cursor_pos[1])),
                8,
                2,
            )

    def run(self):
        """Bucle principal del juego"""
        running = True

        while running:
            # Leer joystick
            self.read_joystick()

            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.game_state == "finished":
                        self.restart_game()

            # Lógica del juego
            if self.game_state == "waiting":
                if self.button_pressed:
                    self.button_pressed = False
                    self.start_game()

            elif self.game_state == "showing":
                if pygame.time.get_ticks() - self.show_start_time >= self.show_time:
                    self.game_state = "playing"
                    self.current_point_index = 0
                    self.start_time = time.time()

            elif self.game_state == "playing":
                self.handle_button_press()

            # Dibujar
            self.draw_game()
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup
        if self.board:
            self.board.exit()
        pygame.quit()

    def start_game(self):
        """Iniciar nuevo juego"""
        self.generate_points()
        self.game_state = "showing"
        self.show_start_time = pygame.time.get_ticks()
        self.results = []
        self.current_point_index = 0

    def restart_game(self):
        """Reiniciar juego"""
        self.game_state = "waiting"
        self.results = []
        self.current_point_index = 0


# Función para integrar con tu interfaz existente
def start_joystick_game(arduino_port="COM3", difficulty="medio"):
    """Función para llamar desde tu interfaz principal"""
    game = JoystickCoordinationGame(arduino_port, difficulty)
    game.run()


if __name__ == "__main__":
    # Prueba del juego
    start_joystick_game()
