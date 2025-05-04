# firmdata\hand_ctrl.py
from pyfirmata import Port, Arduino

puerto = "COM5"
placa = Arduino(puerto)

num_pines = 8, 9, 10, 11, 12

salidas_led = [f"d:{idx}:o" for idx in num_pines]
puertos_led: list[Port] = [placa.get_pin(salida) for salida in salidas_led]


def switch_leds(estado_dedos: list[int]):
    for led, port_led in zip(estado_dedos, puertos_led):
        port_led.write(led)
