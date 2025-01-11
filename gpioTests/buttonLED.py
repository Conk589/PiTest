from gpiozero import LED
from gpiozero import Button
from time import sleep

light = LED(17)
button = Button(2)


while True:
    light.on
    sleep(1)
    light.off
    sleep(1)
