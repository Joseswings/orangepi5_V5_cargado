# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

#Canales 0,1,2,3
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)


print("{:>5}\t{:>5}\t{:>5}\t{:>5}".format("CH0","CH1","CH2","CH3"))

while True:
    print("{:>5.3f}\t{:>5.3f}\t{:>5.3f}\t{:>5.3f}".format(chan0.voltage,chan1.voltage,chan2.voltage,chan3.voltage))
    time.sleep(0.5)
