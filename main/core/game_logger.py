import logging
import os
from datetime import datetime
from typing import Optional

class GameLogger:
    """Manejador de logging para el juego"""

    def __init__(self, game_name: str = "PingPongGame", log_dir: str = "main/data"):
        self.clean_logs()
        self.game_name = game_name
        self.log_dir = log_dir
        self.logger = None
        self._setup_logging()

    def clean_logs(self):
        """Eliminar logs antiguos de la carpeta"""
        for filename in os.listdir(self.log_dir):
            if filename.endswith(".log"):
                os.remove(os.path.join(self.log_dir, filename))

    def _setup_logging(self):
        """Configurar el sistema de logging"""
        # Crear carpeta data si no existe
        os.makedirs(self.log_dir, exist_ok=True)

        # Configurar el logger
        self.logger = logging.getLogger(self.game_name)
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar handlers si ya existen
        if not self.logger.handlers:
            # Handler para archivo
            log_file = os.path.join(self.log_dir, 'pingpong.log')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            # Formato personalizado con fecha y hora
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

            # También mostrar logs importantes en consola
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_game_event(self, event_type: str, message: str, level: str = "INFO",
                      score: Optional[int] = None, ball_pos: Optional[tuple] = None):
        """Registrar evento del juego"""
        log_parts = [f"[{event_type}] {message}"]

        if score is not None:
            log_parts.append(f"Score: {score}")

        if ball_pos is not None:
            log_parts.append(f"Ball: {ball_pos}")

        log_message = " | ".join(log_parts)

        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def log_player_death_ping_pong(self, death_reason: str, side: str, final_score: int,
                        total_hits: int, left_hits: int, right_hits: int,
                        game_duration: float, game_speed: float):
        """Registrar muerte/error especial del jugador"""
        death_message = (
            f"💀 PLAYER DEATH 💀 | Reason: {death_reason} | Side: {side} | "
            f"Final Score: {final_score} | Total Hits: {total_hits} | "
            f"Left Hits: {left_hits} | Right Hits: {right_hits} | "
            f"Game Duration: {game_duration:.2f}s | Speed: {game_speed:.2f}s"
        )

        self.logger.error(death_message)
        print(f"🎮 {death_message}")  # También mostrar en consola para eventos críticos
