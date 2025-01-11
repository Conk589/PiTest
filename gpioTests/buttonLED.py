from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button
from time import sleep

light = PWMLED(17)
button = Button(2)


while True:
    light.pulse
