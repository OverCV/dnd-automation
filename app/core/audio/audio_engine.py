import pygame
import numpy as np

class AudioEngine:
    """Motor de audio para generar sonidos"""

    def __init__(self):
        self.sample_rate = 44100
        self.volume = 0.3

        # Inicializar pygame audio
        pygame.mixer.pre_init(
            frequency=self.sample_rate,
            size=-16,
            channels=2,
            buffer=512
        )
        pygame.mixer.init()

    def generate_tone(self, frequency: float, duration: float) -> np.ndarray:
        """Generar tono senoidal"""
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)

        for i in range(frames):
            time_val = float(i) / self.sample_rate

            # Envelope para evitar clicks
            envelope = 1.0
            fade_time = 0.02

            if time_val < fade_time:
                envelope = time_val / fade_time
            elif time_val > duration - fade_time:
                envelope = (duration - time_val) / fade_time

            arr[i] = envelope * np.sin(2 * np.pi * frequency * time_val)

        return (arr * self.volume * 32767).astype(np.int16)

    def play_tone(self, frequency: float, duration: float):
        """Reproducir tono"""
        audio_data = self.generate_tone(frequency, duration)
        stereo_data = np.column_stack((audio_data, audio_data))
        stereo_data = np.ascontiguousarray(stereo_data, dtype=np.int16)

        sound = pygame.sndarray.make_sound(stereo_data)
        sound.play()
