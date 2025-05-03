# firmdata\hand_ctrl.py
from pyfirmata import Port, Arduino

comport = "COM5"

board = Arduino(comport)

num_pines = 8, 9, 10, 11, 12
mapeo_mano_a_leds = {
    (0, 0, 0, 0, 0): (0, 0, 0, 0, 0),
    (0, 0, 0, 1, 0): (1, 0, 0, 0, 0),
    (0, 0, 1, 1, 0): (1, 1, 0, 0, 0),
    (0, 1, 1, 1, 0): (1, 1, 1, 0, 0),
    (1, 1, 1, 1, 0): (1, 1, 1, 1, 0),
    (1, 1, 1, 1, 1): (1, 1, 1, 1, 1),
}

data_outputs = [f"d:{idx}:o" for idx in num_pines]
port_leds: list[Port] = [board.get_pin(output) for output in data_outputs]


def set_leds(dedo_mano):
    if tuple(dedo_mano) not in mapeo_mano_a_leds:
        return
    leds = mapeo_mano_a_leds[tuple(dedo_mano)]

    for led, port_led in zip(leds, port_leds):
        port_led.write(led)
