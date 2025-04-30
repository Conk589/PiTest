from machine import Pin, SPI
from lib.xpt2046 import Touch
import time

# Setup SPI and touchscreen
spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
cs = Pin(5, Pin.OUT)
touch = Touch(spi, cs)

while True:
    pos = touch.get_touch()
    if pos:
        print("Touch at:", pos)
    time.sleep(0.1)
