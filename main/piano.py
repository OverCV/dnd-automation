import pyfirmata
import time

# Configura la placa Arduino
puerto = "COM5"
placa = pyfirmata.Arduino(puerto)
print("Conexión establecida con Arduino")

# Configura los pines de entrada para los botones
boton1 = placa.get_pin("d:2:i")  # Pin digital 2 como entrada
boton2 = placa.get_pin("d:3:i")  # Pin digital 3 como entrada

# Inicia el iterador para leer entradas
it = pyfirmata.util.Iterator(placa)
it.start()

# Variables para almacenar estados anteriores
estado_anterior_boton1 = True
estado_anterior_boton2 = True

try:
    while True:
        # Lee el estado actual de los botones (True cuando no está presionado debido al pull-up)
        estado_boton1 = boton1.read()
        estado_boton2 = boton2.read()

        # Detecta cambio de estado en botón 1 (de no presionado a presionado)
        if estado_boton1 is not None and estado_boton1 != estado_anterior_boton1:
            if not estado_boton1:  # False significa botón presionado
                print("¡Botón 1 pulsado!")
            estado_anterior_boton1 = estado_boton1

        # Detecta cambio de estado en botón 2
        if estado_boton2 is not None and estado_boton2 != estado_anterior_boton2:
            if not estado_boton2:
                print("¡Botón 2 pulsado!")
            estado_anterior_boton2 = estado_boton2

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Programa terminado")
    placa.exit()
