#This light bar needs 220 Ohm Resistors between 3.3V and GPIO pins
#it also, inconvieniently, only works one direction and is labeled randomly so turn it around if no worky
#works by making an array of lights and changing modes based on a button press
import threading
from time import sleep
from gpiozero import LED
from gpiozero import Button
from signal import pause

lightPins = [17,18,27,22,23,24,25,2,3,20]
button = Button(21)
lights = []
loop = False #Used to loop modes that are functional

#Initializes Pins for light bar based on light pins array
for pin in lightPins:
    try:
        lights.append(LED(pin=pin))
    except Exception as e:
        print(f"Error initializing LED on GPIO pin {pin}: {e}")

#Error handling for lights[] not being created
if not lights:
    raise RuntimeError("No valid GPIO pins available for LEDs.")

#reference counter - starts at -1 cuz im stupid and this is the easiest way to fix the first single light not turning off.
# it needs a way to turn off the led
ref = -1

#increment method for selecting method needed and pin needed in some methods
def incrementRef():
    global ref
    ref += 1
    if ref > 11:
        ref = -1
    print(f"Button pressed. Current ref value: {ref}")
    execute_mode()


#Makes the light bar look like water i geuss?
def waterfall():
    global loop
    loop = True
    while loop:
        for index in range(0,len(lightPins),1): # make led(on) move from left to right
            lights[index].off()
            sleep(0.1)
            lights[index].on()
        for index in range(len(lightPins) - 1,-1,-1): #move led(on) from right to left
            lights[index].off()
            sleep(0.1)
            lights[index].on() 
        if button.is_pressed:
            break


#Steps through the lights one at a time constantly
def step():
    global loop
    loop = True
    while loop:
        for index in range(0,len(lightPins),1):
            lights[index].on()
            sleep (0.1)
            lights[index].off()
        for index in range(len(lightPins) - 1,-1,-1):
            lights[index].on()
            sleep (0.1)
            lights[index].off()
        if button.is_pressed:
            break

#Iterates through lights individually on button press
def singlesOff():
    lights[ref].on()
    if ref >= 0:  # Turn off the previous LED
        lights[ref - 1].off()   


#Turns all lights on. when you deactivate the pin the light is on. therefore .off() is actually turning the light on.
def turnAllOn():
    for index in range(0,len(lightPins),1):
        lights[index].off()
    print(f"Lights ON!")

#Turns all lights off. vice versa from above
def turnAllOff():
    for index in range(0,len(lightPins),1):
        lights[index].on()
    print(f"Lights OFF!")


# Cleanup GPIO on exit
def cleanup():
    print("Cleaning up GPIO pins...")
    for light in lights:
        light.close()
    button.close()

#Decides which mode we need based on ref
def execute_mode():
    if ref == -1: #handles use case for initial startup so all lights are on.
        turnAllOn()
    elif (ref >= 0 and ref < len(lights)):  # Single light mode
        singlesOff()
        print(f"Single Mode!")
    elif ref == len(lights):  # Step mode
        step()
        print(f"Step Mode!") #Made them print for easier debugging
    elif ref == len(lights) + 1:  # Waterfall mode
        waterfall()
        print(f"Waterfall Mode!")



# Button press handler to exit the loop
def stopLoop():
    global loop
    loop = False #set loop false

#Button press handler
def buttonPressed():
    global loop
    sleep(.1)
    if loop:
        incrementRef()
        stopLoop()
        print(f"Mode Stopped")
    else:
        incrementRef()

if __name__ == "__main__":
    try:
        button.when_pressed = buttonPressed

        print("Program running. Press the button to switch modes.")

        # Wait for events
        pause()

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        cleanup()
        

