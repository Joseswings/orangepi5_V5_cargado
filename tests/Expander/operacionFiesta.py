import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import random
from time import sleep

from services.gpio_expander import GPIOExpander

expander = GPIOExpander()

while True:

    action = random.randint(0,1)
    #print("Action: ",action)
    pin = random.randint(0,15)
    #print("Pin: ", pin)
    timer = random.random() / 20
    #print("Timer: ",timer)

    if action == 1:
        try:
            expander.setPinOn(pin)
        except:
            pass
    else:
        try:
            expander.setPinOff(pin)
        except:
            pass

    sleep(timer)

