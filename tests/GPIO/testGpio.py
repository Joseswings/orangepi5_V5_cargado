from services.gpio_controller import GPIOController
from time import sleep

controller = GPIOController()

GREEN_LED = 11 # Port PH 7
RED_LED = 12 # Port PH 8
BLUE_LED = 13 # Port PC 7

CHASIS = 9 # Port PC 15
SOFTWARE_BUTTON = 10 # Port PC 14
HARDWARE_BUTTON = 8 # Port PC 8

while True:
    chasis_v = controller.read_pin(CHASIS)
    print("Chasis: ",chasis_v)
    software = controller.read_pin(SOFTWARE_BUTTON) 
    print("Software: ",software)
    hardware = controller.read_pin(HARDWARE_BUTTON)
    print("Hardware: ",hardware)
    sleep(4)
    