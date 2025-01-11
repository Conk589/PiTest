from gpiozero import PWMLED
from gpiozero import Button
from signal import pause

light = PWMLED(17)
button = Button(2)

light.source = button

pause()