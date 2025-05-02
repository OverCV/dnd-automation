from pyfirmata import Port, Arduino

comport = "COM3"

board = Arduino(comport)

num_pines = 8, 9, 10, 11, 12
num_str = "uno", "dos", "tres", "cuatro", "cinco"
mapeo_mano_a_leds = {
    (0, 0, 0, 0, 0): (0, 0, 0, 0, 0),
    (0, 0, 0, 1, 0): (1, 0, 0, 0, 0),
    (0, 0, 1, 1, 0): (1, 1, 0, 0, 0),
    (0, 1, 1, 1, 0): (1, 1, 1, 0, 0),
    (1, 1, 1, 1, 0): (1, 1, 1, 1, 0),
    (1, 1, 1, 1, 1): (1, 1, 1, 1, 1),
}

data_outputs = (f"d:{idx}:o" for idx in num_pines)

leds: list[Port] = [board.get_pin(output) for output in data_outputs]


def set_leds(dedo_mano):
    leds = mapeo_mano_a_leds[dedo_mano]
    for led in leds:
        led.write(1) if led else led.write(0)
"""  """""" """  """ """