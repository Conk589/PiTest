#This light bar needs 220 Ohm Resistors between 3.3V and GPIO pins
#it also, inconvieniently, only works one direction and is labeled randomly so turn it around if no worky
#works by making an array of lights and changing modes based on a button press
from time import sleep
from gpiozero import LED
from gpiozero import Button
from signal import pause

lightPins = [17,18,27,22,23,24,25,2,3,8]
lights = [LED(pin=pin) for pin in lightPins]
button = Button(21)

ref = 0

def incrementRef():
    global ref
    ref += 1
    if (ref > 12):
        ref = 0

def waterfall():
    while True:
        for index in range(0,len(lightPins),1): # make led(on) move from left to right
            lights[index].off()
            sleep(0.1)
            lights[index].on()
        for index in range(len(lightPins)-1,-1,-1): #move led(on) from right to left
            lights[index].off()
            sleep(0.1)
            lights[index].on() 


def step():
    while True:
        for index in range(0,len(lightPins),1):
            lights[index].on()
            sleep (0.1)
            lights[index].off()

def singles():
    
    lights[ref].on()
    button.when_activated = lights[ref - 1].off
    pause()

    


if __name__ == "__main__":

    button.when_activated = incrementRef

    if (ref >= 10):
        singles()
    elif (ref == 11):
        step()
    elif (ref == 12):
        waterfall()
    
    pause()



#button.when_pressed = incrementRef

