import constants
from services.gpio_controller import GPIOController
from time import sleep

controller = GPIOController()
controller.channel_turn_on(constants.CABINET)
sleep(10)
controller.channel_turn_off(constants.CABINET)