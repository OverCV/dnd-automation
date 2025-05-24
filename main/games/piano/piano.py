
"""
Piano Digital Arduino + Python
Recibe datos del Arduino por puerto serial y reproduce sonidos
"""

import serial
import pygame
import numpy as np
import time
import threading
from typing import Optional
import serial.tools.list_ports

class PianoArduino:
    """Clase para manejar el piano digital con Arduino"""

    # Configuración de audio
    SAMPLE_RATE = 44100
    DURACION_NOTA = 0.5
    VOLUMEN = 0.3

    # Notas musicales (frecuencias en Hz)
    NOTAS = [
        ('Do', 262),    # Botón 0
        ('Re', 294),    # Botón 1
        ('Mi', 330),    # Botón 2
        ('Fa', 349),    # Botón 3
        ('Sol', 392),   # Botón 4
        ('La', 440),    # Botón 5
        ('Si', 494),    # Botón 6
        ('Do8', 523),   # Botón 7
    ]

    def __init__(self):
        """Inicializar el piano con Arduino"""
        self.arduino: Optional[serial.Serial] = None
        self.ejecutando = True
        self.inicializar_audio()

    def inicializar_audio(self) -> None:
        """Inicializar pygame para audio"""
        try:
            pygame.mixer.pre_init(
                frequency=self.SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=512
            )
            pygame.mixer.init()
            print("✅ Audio inicializado")
        except Exception as e:
            print(f"❌ Error en audio: {e}")
            raise

    def buscar_arduino(self) -> Optional[str]:
        """Buscar puerto del Arduino automáticamente"""
        print("🔍 Buscando Arduino...")

        puertos = serial.tools.list_ports.comports()
        for puerto in puertos:
            if 'Arduino' in puerto.description or 'CH340' in puerto.description or 'USB' in puerto.description:
                print(f"✅ Arduino encontrado en: {puerto.device}")
                return puerto.device

        # Si no encuentra automáticamente, mostrar puertos disponibles
        print("⚠️  Arduino no encontrado automáticamente")
        print("Puertos disponibles:")
        for i, puerto in enumerate(puertos):
            print(f"  {i}: {puerto.device} - {puerto.description}")

        return None

    def conectar_arduino(self, puerto: Optional[str] = None) -> bool:
        """Conectar con el Arduino"""
        try:
            if not puerto:
                puerto = self.buscar_arduino()

            if not puerto:
                # Solicitar puerto manualmente
                print("\n📝 Ingresa el puerto manualmente (ej: COM3, /dev/ttyUSB0):")
                puerto = input("Puerto: ").strip()

            print(f"🔌 Conectando a {puerto}...")
            self.arduino = serial.Serial(puerto, 9600, timeout=1)
            time.sleep(2)  # Esperar reset del Arduino

            # Verificar conexión
            if self.arduino.is_open:
                print("✅ Conexión establecida")
                return True
            else:
                print("❌ No se pudo abrir el puerto")
                return False

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def generar_onda_seno(self, frecuencia: float, duracion: float) -> np.ndarray:
        """Generar onda seno para una frecuencia"""
        frames = int(duracion * self.SAMPLE_RATE)
        arr = np.zeros(frames)

        for i in range(frames):
            tiempo = float(i) / self.SAMPLE_RATE
            # Envelope suave
            envelope = 1.0
            if tiempo < 0.01:
                envelope = tiempo / 0.01
            elif tiempo > duracion - 0.01:
                envelope = (duracion - tiempo) / 0.01

            arr[i] = envelope * np.sin(2 * np.pi * frecuencia * tiempo)

        return (arr * self.VOLUMEN * 32767).astype(np.int16)

    def tocar_nota(self, indice: int) -> None:
        """Tocar nota según índice del botón"""
        if 0 <= indice < len(self.NOTAS):
            nombre, frecuencia = self.NOTAS[indice]

            try:
                # Generar audio
                audio_data = self.generar_onda_seno(frecuencia, self.DURACION_NOTA)

                # Crear array estéreo contiguous
                stereo_data = np.column_stack((audio_data, audio_data))
                stereo_data = np.ascontiguousarray(stereo_data, dtype=np.int16)

                # Reproducir
                sound = pygame.sndarray.make_sound(stereo_data)
                sound.play()

                print(f"🎵 Botón {indice + 1}: {nombre} ({frecuencia} Hz)")

            except Exception as e:
                print(f"❌ Error reproduciendo nota: {e}")

    def leer_arduino(self) -> None:
        """Leer datos del Arduino en hilo separado"""
        while self.ejecutando and self.arduino and self.arduino.is_open:
            try:
                if self.arduino.in_waiting > 0:
                    linea = self.arduino.readline().decode('utf-8').strip()

                    if linea == "PIANO_READY":
                        print("🎹 Piano Arduino listo")
                    elif linea.startswith("NOTA:"):
                        indice = int(linea.split(":")[1])
                        # Tocar nota en hilo separado
                        hilo_nota = threading.Thread(
                            target=self.tocar_nota,
                            args=(indice,)
                        )
                        hilo_nota.daemon = True
                        hilo_nota.start()

            except Exception as e:
                print(f"❌ Error leyendo Arduino: {e}")
                time.sleep(0.1)

    def mostrar_info(self) -> None:
        """Mostrar información del piano"""
        print("\n" + "="*50)
        print("🎹 PIANO DIGITAL ARDUINO + PYTHON 🎹")
        print("="*50)
        print("\n🔧 CONEXIONES ARDUINO:")
        print("   Botones 1-8: Pines 2-9 a GND")
        print("   (Sin resistencias - usa pull-up interno)")
        print("\n🎵 NOTAS:")
        for i, (nombre, freq) in enumerate(self.NOTAS):
            print(f"   Botón {i+1}: {nombre} ({freq} Hz)")
        print("\n🎮 Presiona Ctrl+C para salir")
        print("-"*50)

    def ejecutar(self) -> None:
        """Ejecutar el piano"""
        self.mostrar_info()

        # Conectar Arduino
        if not self.conectar_arduino():
            print("❌ No se pudo conectar con Arduino")
            return

        # Iniciar hilo de lectura
        hilo_lectura = threading.Thread(target=self.leer_arduino)
        hilo_lectura.daemon = True
        hilo_lectura.start()

        print("🎵 Piano funcionando. Presiona los botones en el Arduino!")

        try:
            while self.ejecutando:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⚠️  Cerrando piano...")
        finally:
            self.cerrar()

    def cerrar(self) -> None:
        """Cerrar conexiones"""
        self.ejecutando = False
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        pygame.mixer.quit()
        print("✅ Piano cerrado correctamente")


def main():
    """Función principal"""
    try:
        piano = PianoArduino()
        piano.ejecutar()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        print("👋 ¡Gracias por usar el Piano Digital!")


if __name__ == "__main__":
    # Verificar dependencias
    try:
        import serial
        import pygame
        import numpy as np
        main()
    except ImportError as e:
        print("❌ Instala las dependencias:")
        print("   pip install pyserial pygame numpy")
        print(f"   Error: {e}")
