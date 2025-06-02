"""
Manejo de audio para el juego Osu! - Efectos de sonido y feedback auditivo
"""

import time
import threading
import math
from typing import Optional, Dict, Any


class OsuAudioManager:
    """Maneja todos los efectos de sonido del juego Osu"""
    
    def __init__(self, enable_audio: bool = True):
        self.enable_audio = enable_audio
        self.pygame = None
        self.mixer = None
        self.sounds = {}
        self.music_playing = False
        
        if self.enable_audio:
            self._lazy_import_pygame()
    
    def _lazy_import_pygame(self):
        """Importar pygame solo cuando se necesite"""
        try:
            import pygame
            self.pygame = pygame
            
            # Inicializar mixer de pygame
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            
            # Crear sonidos sintéticos
            self._create_synthetic_sounds()
            
            print("✅ Audio Osu inicializado correctamente")
            
        except ImportError:
            print("⚠️ Pygame no disponible - Audio deshabilitado")
            self.enable_audio = False
        except Exception as e:
            print(f"⚠️ Error inicializando audio: {e}")
            self.enable_audio = False
    
    def _create_synthetic_sounds(self):
        """Crear efectos de sonido sintéticos"""
        if not self.enable_audio or not self.pygame:
            return
            
        try:
            import numpy as np
            
            sample_rate = 22050
            
            # Sonido de hit perfecto (nota alta y brillante)
            perfect_freq = 800
            perfect_duration = 0.15
            perfect_samples = int(sample_rate * perfect_duration)
            perfect_wave = np.sin(2 * np.pi * perfect_freq * np.linspace(0, perfect_duration, perfect_samples))
            # Envelope de decaimiento
            perfect_envelope = np.exp(-np.linspace(0, 8, perfect_samples))
            perfect_wave = (perfect_wave * perfect_envelope * 16383).astype(np.int16)
            # Hacer array contíguo
            perfect_stereo = np.ascontiguousarray(np.array([perfect_wave, perfect_wave]).T)
            self.sounds['perfect'] = self.pygame.sndarray.make_sound(perfect_stereo)
            
            # Sonido de hit bueno (nota media)
            good_freq = 600
            good_duration = 0.12
            good_samples = int(sample_rate * good_duration)
            good_wave = np.sin(2 * np.pi * good_freq * np.linspace(0, good_duration, good_samples))
            good_envelope = np.exp(-np.linspace(0, 6, good_samples))
            good_wave = (good_wave * good_envelope * 12287).astype(np.int16)
            good_stereo = np.ascontiguousarray(np.array([good_wave, good_wave]).T)
            self.sounds['good'] = self.pygame.sndarray.make_sound(good_stereo)
            
            # Sonido de hit normal (nota baja)
            normal_freq = 400
            normal_duration = 0.1
            normal_samples = int(sample_rate * normal_duration)
            normal_wave = np.sin(2 * np.pi * normal_freq * np.linspace(0, normal_duration, normal_samples))
            normal_envelope = np.exp(-np.linspace(0, 4, normal_samples))
            normal_wave = (normal_wave * normal_envelope * 8191).astype(np.int16)
            normal_stereo = np.ascontiguousarray(np.array([normal_wave, normal_wave]).T)
            self.sounds['normal'] = self.pygame.sndarray.make_sound(normal_stereo)
            
            # Sonido de miss (ruido grave)
            miss_freq = 150
            miss_duration = 0.2
            miss_samples = int(sample_rate * miss_duration)
            miss_wave = np.sin(2 * np.pi * miss_freq * np.linspace(0, miss_duration, miss_samples))
            # Agregar algo de ruido
            noise = np.random.normal(0, 0.1, miss_samples)
            miss_wave = miss_wave + noise
            miss_envelope = np.exp(-np.linspace(0, 3, miss_samples))
            miss_wave = (miss_wave * miss_envelope * 6143).astype(np.int16)
            miss_stereo = np.ascontiguousarray(np.array([miss_wave, miss_wave]).T)
            self.sounds['miss'] = self.pygame.sndarray.make_sound(miss_stereo)
            
            # Sonido de aparición de círculo (tick suave)
            spawn_freq = 1000
            spawn_duration = 0.05
            spawn_samples = int(sample_rate * spawn_duration)
            spawn_wave = np.sin(2 * np.pi * spawn_freq * np.linspace(0, spawn_duration, spawn_samples))
            spawn_envelope = np.exp(-np.linspace(0, 10, spawn_samples))
            spawn_wave = (spawn_wave * spawn_envelope * 4095).astype(np.int16)
            spawn_stereo = np.ascontiguousarray(np.array([spawn_wave, spawn_wave]).T)
            self.sounds['spawn'] = self.pygame.sndarray.make_sound(spawn_stereo)
            
            # Sonido de combo (escalas ascendentes)
            combo_freqs = [400, 500, 600, 700, 800]
            combo_duration = 0.3
            combo_samples = int(sample_rate * combo_duration)
            combo_wave = np.zeros(combo_samples)
            
            for i, freq in enumerate(combo_freqs):
                start_idx = int(i * combo_samples / len(combo_freqs))
                end_idx = int((i + 1) * combo_samples / len(combo_freqs))
                segment_length = end_idx - start_idx
                segment_wave = np.sin(2 * np.pi * freq * np.linspace(0, combo_duration/len(combo_freqs), segment_length))
                combo_wave[start_idx:end_idx] = segment_wave
            
            combo_envelope = np.exp(-np.linspace(0, 2, combo_samples))
            combo_wave = (combo_wave * combo_envelope * 10239).astype(np.int16)
            combo_stereo = np.ascontiguousarray(np.array([combo_wave, combo_wave]).T)
            self.sounds['combo'] = self.pygame.sndarray.make_sound(combo_stereo)
            
            print("🔊 Efectos de sonido Osu creados")
            
        except ImportError:
            print("⚠️ NumPy no disponible - Sonidos básicos solamente")
            self._create_basic_sounds()
        except Exception as e:
            print(f"⚠️ Error creando sonidos sintéticos: {e}")
            self._create_basic_sounds()
    
    def _create_basic_sounds(self):
        """Crear sonidos básicos sin NumPy"""
        if not self.enable_audio or not self.pygame:
            return
            
        try:
            # Crear tonos simples usando pygame
            sample_rate = 22050
            
            # Función helper para crear tonos
            def create_tone(frequency: int, duration: float, volume: float = 0.5):
                frames = int(duration * sample_rate)
                arr = []
                for i in range(frames):
                    wave = 4096 * volume * math.sin(2 * math.pi * frequency * i / sample_rate)
                    arr.append([int(wave), int(wave)])
                return self.pygame.sndarray.make_sound(self.pygame.array.array('i', arr))
            
            self.sounds['perfect'] = create_tone(800, 0.15, 0.6)
            self.sounds['good'] = create_tone(600, 0.12, 0.5)
            self.sounds['normal'] = create_tone(400, 0.1, 0.4)
            self.sounds['miss'] = create_tone(150, 0.2, 0.3)
            self.sounds['spawn'] = create_tone(1000, 0.05, 0.2)
            self.sounds['combo'] = create_tone(500, 0.3, 0.4)
            
            print("🔊 Efectos de sonido básicos creados")
            
        except Exception as e:
            print(f"⚠️ Error creando sonidos básicos: {e}")
    
    def play_hit_sound(self, accuracy_score: int):
        """Reproducir sonido según la precisión del hit"""
        if not self.enable_audio:
            return
            
        try:
            if accuracy_score >= 90:
                sound_key = 'perfect'
            elif accuracy_score >= 70:
                sound_key = 'good'
            elif accuracy_score >= 50:
                sound_key = 'normal'
            else:
                sound_key = 'miss'
            
            if sound_key in self.sounds:
                self.sounds[sound_key].play()
                
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido de hit: {e}")
    
    def play_miss_sound(self):
        """Reproducir sonido de miss"""
        if not self.enable_audio:
            return
            
        try:
            if 'miss' in self.sounds:
                self.sounds['miss'].play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido de miss: {e}")
    
    def play_spawn_sound(self):
        """Reproducir sonido de aparición de círculo"""
        if not self.enable_audio:
            return
            
        try:
            if 'spawn' in self.sounds:
                self.sounds['spawn'].play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido de spawn: {e}")
    
    def play_combo_sound(self, combo_count: int):
        """Reproducir sonido de combo"""
        if not self.enable_audio or combo_count < 5:
            return
            
        try:
            if 'combo' in self.sounds and combo_count % 10 == 0:
                self.sounds['combo'].play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido de combo: {e}")
    
    def play_perfect_sound(self):
        """Reproducir sonido de hit perfecto"""
        if not self.enable_audio:
            return
            
        try:
            if 'perfect' in self.sounds:
                self.sounds['perfect'].play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido perfecto: {e}")
    
    def play_click_sound(self):
        """Reproducir sonido de click genérico"""
        if not self.enable_audio:
            return
            
        try:
            if 'spawn' in self.sounds:
                self.sounds['spawn'].play()
        except Exception as e:
            print(f"⚠️ Error reproduciendo sonido de click: {e}")
    
    def start_background_rhythm(self, bpm: int = 120):
        """Iniciar ritmo de fondo (metrónomo simple)"""
        if not self.enable_audio:
            return
            
        def metronome_loop():
            beat_interval = 60.0 / bpm
            while self.music_playing:
                try:
                    if 'spawn' in self.sounds:
                        self.sounds['spawn'].play()
                    time.sleep(beat_interval)
                except:
                    break
        
        self.music_playing = True
        threading.Thread(target=metronome_loop, daemon=True).start()
        print(f"🎵 Ritmo de fondo iniciado - {bpm} BPM")
    
    def stop_background_rhythm(self):
        """Detener ritmo de fondo"""
        self.music_playing = False
        print("🔇 Ritmo de fondo detenido")
    
    def stop_all_sounds(self):
        """Detener todos los sonidos"""
        if not self.enable_audio:
            return
            
        try:
            if self.pygame:
                self.pygame.mixer.stop()
            self.stop_background_rhythm()
        except Exception as e:
            print(f"⚠️ Error deteniendo sonidos: {e}")
    
    def set_volume(self, volume: float):
        """Ajustar volumen global (0.0 a 1.0)"""
        if not self.enable_audio:
            return
            
        try:
            volume = max(0.0, min(1.0, volume))
            for sound in self.sounds.values():
                sound.set_volume(volume)
            print(f"🔊 Volumen ajustado a {volume * 100}%")
        except Exception as e:
            print(f"⚠️ Error ajustando volumen: {e}")
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Obtener información del sistema de audio"""
        return {
            "audio_enabled": self.enable_audio,
            "pygame_available": self.pygame is not None,
            "sounds_loaded": len(self.sounds),
            "sound_effects": list(self.sounds.keys()),
            "music_playing": self.music_playing
        }
    
    def cleanup(self):
        """Limpiar recursos de audio"""
        try:
            self.stop_all_sounds()
            if self.pygame:
                self.pygame.mixer.quit()
            print("🧹 Audio Osu limpiado")
        except Exception as e:
            print(f"⚠️ Error limpiando audio: {e}") 