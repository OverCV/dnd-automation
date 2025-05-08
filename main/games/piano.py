import pyfirmata
import time

# Configuración de la placa Arduino
# Reemplaza 'YOUR_PORT_HERE' con el puerto correcto
# Ejemplos: '/dev/ttyACM0' (Linux), 'COM3' (Windows), '/dev/tty.usbmodem11401' (Mac)
board = pyfirmata.Arduino("COM5")
print("Comunicación iniciada con éxito")

# Iniciar iterador para recibir datos de entrada
it = pyfirmata.util.Iterator(board)
it.start()

# Constantes
NUM_BUTTONS = 8
BUTTON_PINS = [2, 3, 4, 5, 6, 7, 8, 9]
BUZZER_PIN = 13

# Frecuencias de notas musicales (en Hz)
NOTE_FREQUENCIES = [
    262,  # Do (C4)
    294,  # Re (D4)
    330,  # Mi (E4)
    349,  # Fa (F4)
    392,  # Sol (G4)
    440,  # La (A4)
    494,  # Si (B4)
    523,  # Do (C5)
]

# Duración de la nota en milisegundos
NOTE_DURATION = 100  # milisegundos
LOOP_DELAY = 0.01  # segundos

# Configuración de pines
# Configurar botones como entradas
buttons = []
for i in range(NUM_BUTTONS):
    button = board.get_pin(f"d:{BUTTON_PINS[i]}:i")
    button.enable_reporting()
    buttons.append(button)

# Configurar buzzer como salida
buzzer = board.get_pin(f"d:{BUZZER_PIN}:o")


# Función para reproducir un tono en la computadora
def play_computer_tone(frequency, duration):
    try:
        import winsound

        winsound.Beep(frequency, duration)
    except ImportError:
        print("Módulo winsound no disponible")


try:
    print("Piano digital con PyFirmata")
    print(
        "NOTA: PyFirmata no puede generar tonos de frecuencias específicas en el Arduino."
    )

    # Estados previos de los botones para detectar cambios
    prev_states = [0] * NUM_BUTTONS

    while True:
        # Verificar el estado de cada botón
        for i in range(NUM_BUTTONS):
            button_state = buttons[i].read()

            # Si el botón está presionado
            if button_state == 1 and prev_states[i] == 0:
                print(f"Nota {i + 1} - {NOTE_FREQUENCIES[i]} Hz")
                buzzer.write(1)  # Activar buzzer
                play_computer_tone(NOTE_FREQUENCIES[i], NOTE_DURATION)
                buzzer.write(0)  # Apagar buzzer

            # Actualizar estado previo
            if button_state is not None:
                prev_states[i] = button_state

        # Pequeña pausa para estabilizar el bucle
        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    board.exit()
    print("\nPrograma terminado")
