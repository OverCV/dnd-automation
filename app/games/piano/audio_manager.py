import pygame
import numpy as np
import time
from typing import Dict, List, Tuple


class PianoAudioManager:
    """Maneja todo lo relacionado con audio y generación de sonidos del piano"""
    
    def __init__(self):
        # Configuración de audio
        self.SAMPLE_RATE = 44100
        self.DURACION_NOTA = 0.8
        self.VOLUMEN = 0.4
        
        # Notas musicales (frecuencias en Hz)
        self.NOTAS = [
            ("Do", 262, "white"),   # Botón 0 - Pin 2
            ("Re", 294, "white"),   # Botón 1 - Pin 3
            ("Mi", 330, "white"),   # Botón 2 - Pin 4
            ("Fa", 349, "white"),   # Botón 3 - Pin 5
            ("Sol", 392, "white"),  # Botón 4 - Pin 6
            ("La", 440, "white"),   # Botón 5 - Pin 7
            ("Si", 494, "white"),   # Botón 6 - Pin 8
            ("Do8", 523, "white"),  # Botón 7 - Pin 9
        ]
        
        # Estado de audio
        self.audio_initialized = False
        self.sounds_playing = {}
        self.last_note_played = None
        self.total_notes_played = 0
        
        # Inicializar audio
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Inicializar sistema de audio"""
        try:
            pygame.mixer.pre_init(
                frequency=self.SAMPLE_RATE, size=-16, channels=2, buffer=512
            )
            pygame.mixer.init()
            self.audio_initialized = True
            print("✅ Audio inicializado correctamente")
        except Exception as e:
            print(f"❌ Error inicializando audio: {e}")
            self.audio_initialized = False
    
    def reproducir_nota(self, note_index: int, duration: float = None):
        """Reproducir una nota específica"""
        if not (0 <= note_index < len(self.NOTAS)):
            print(f"❌ Índice de nota inválido: {note_index}")
            return False
            
        if duration is None:
            duration = self.DURACION_NOTA
            
        nombre, frecuencia, _ = self.NOTAS[note_index]
        
        try:
            if self.audio_initialized:
                # Generar audio
                audio_data = self._generate_sine_wave(frecuencia, duration)
                
                # Crear array estéreo
                stereo_data = np.column_stack((audio_data, audio_data))
                stereo_data = np.ascontiguousarray(stereo_data, dtype=np.int16)
                
                # Reproducir sonido
                sound = pygame.sndarray.make_sound(stereo_data)
                sound.play()
                
                # Guardar referencia del sonido
                self.sounds_playing[note_index] = sound
                
            # Actualizar estado
            self.last_note_played = nombre
            self.total_notes_played += 1
            
            print(f"🎵 Reproduciendo: {nombre} ({frecuencia} Hz)")
            return True
            
        except Exception as e:
            print(f"❌ Error reproduciendo nota {nombre}: {e}")
            return False
    
    def _generate_sine_wave(self, frequency: float, duration: float) -> np.ndarray:
        """Generar onda seno con envelope suave"""
        frames = int(duration * self.SAMPLE_RATE)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = float(i) / self.SAMPLE_RATE
            
            # Envelope ADSR simplificado
            envelope = 1.0
            attack_time = 0.05
            release_time = min(0.2, duration * 0.3)
            
            if t < attack_time:
                envelope = t / attack_time
            elif t > duration - release_time:
                envelope = (duration - t) / release_time
            
            # Onda seno con armónicos para sonido más rico
            fundamental = np.sin(2 * np.pi * frequency * t)
            harmonic2 = 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
            harmonic3 = 0.1 * np.sin(2 * np.pi * frequency * 3 * t)
            
            arr[i] = envelope * (fundamental + harmonic2 + harmonic3)
        
        return (arr * self.VOLUMEN * 32767).astype(np.int16)
    
    def reproducir_secuencia_game_over(self):
        """Reproducir secuencia de game over"""
        if not self.audio_initialized:
            return
            
        print("🔊 Reproduciendo secuencia de game over")
        
        # Sonido descendente disonante
        for i in range(4):
            # Reproducir acorde disonante
            self.reproducir_nota(0, 0.3)  # Do
            time.sleep(0.1)
            self.reproducir_nota(1, 0.3)  # Re (disonante)
            time.sleep(0.25)
    
    def reproducir_secuencia_victoria(self):
        """Reproducir secuencia de victoria"""
        if not self.audio_initialized:
            return
            
        print("🔊 Reproduciendo secuencia de victoria")
        
        # Secuencia ascendente celebratoria
        for wave in range(3):
            for i in range(8):
                self.reproducir_nota(i, 0.2)
                time.sleep(0.1)
        
        # Acorde final
        time.sleep(0.2)
        for i in [0, 2, 4, 7]:  # Do, Mi, Sol, Do8
            self.reproducir_nota(i, 1.0)
    
    def probar_todas_notas(self):
        """Reproducir todas las notas en secuencia para prueba"""
        print("🧪 Probando todas las notas...")
        
        for i in range(8):
            print(f"🎵 Probando nota {i+1}: {self.NOTAS[i][0]}")
            self.reproducir_nota(i, 0.5)
            time.sleep(0.6)
        
        print("✅ Prueba de notas completada")
    
    def detener_todos_sonidos(self):
        """Detener todos los sonidos"""
        if self.audio_initialized:
            pygame.mixer.stop()
            self.sounds_playing.clear()
    
    def obtener_info_nota(self, note_index: int) -> Tuple[str, int, str]:
        """Obtener información de una nota específica"""
        if 0 <= note_index < len(self.NOTAS):
            return self.NOTAS[note_index]
        return ("", 0, "")
    
    def obtener_todas_notas(self) -> List[Tuple[str, int, str]]:
        """Obtener información de todas las notas"""
        return self.NOTAS.copy()
    
    def reiniciar_estadisticas(self):
        """Reiniciar estadísticas de audio"""
        self.last_note_played = None
        self.total_notes_played = 0
        self.sounds_playing.clear() 