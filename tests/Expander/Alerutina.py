import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.gpio_expander import GPIOExpander
import time


GPA0, GPA1, GPA2, GPA3, GPA4, GPA5, GPA6, GPA7 = 0, 1, 2, 3, 4, 5, 6, 7

GPB0, GPB1, GPB2, GPB3, GPB4, GPB5, GPB6, GPB7 = 8, 9, 10, 11, 12, 13, 14, 15

"""
GPA7 = GPIO 10 FRIDGE  # Output
GPA6 = GPIO 14 PEPL    # Output
GPA5 = GPIO 13 S48V    # Output

GPA4 = WARNING_INA_1   # Input
GPA3 = CRITICAL_INA_1  # Input

GPA2 = GPIO 16 FAN     # Output
GPA1 = GPIO FRIDGE 2   # Output
GPA0 = GPIO 6 AXU1     # Output

GPB6 = WARNING_INA_2   # Input
GPB7 = CRITICAL_INA_2  # Input

GPB3 = GPIO 15 AUX3    # Output
GPB4 = GPIO 0 AUX 2    # Output

GPB5 = WARNING_INA_3   # Input
GPB2 = CRITICAL_INA_3  # Input

GPB0 = A+_COM          # Output
GPB1 = B-_COM          # Output

"""

expander = GPIOExpander()

expander.setPinOff(GPA7)
expander.setPinOff(GPA5)
expander.setPinOff(GPA2)
expander.setPinOff(GPA6)
time.sleep(2)

while True:

    expander.setPinOn(GPA7)
    expander.setPinOn(GPA5)
    expander.setPinOn(GPA2)
    expander.setPinOn(GPA6)
    time.sleep(60)

    expander.setPinOff(GPA7)
    expander.setPinOff(GPA5)
    expander.setPinOff(GPA2)
    expander.setPinOff(GPA6)
    time.sleep(60)