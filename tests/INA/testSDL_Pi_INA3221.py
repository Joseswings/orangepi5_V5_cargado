#!/usr/bin/env python
#
# Test SDL_Pi_INA3221
# John C. Shovic, SwitchDoc Labs
# 03/05/2015
#
#

# imports

import sys
import time
import datetime
import random
import SDL_Pi_INA3221

# Main Program

ina3221 = SDL_Pi_INA3221.SDL_Pi_INA3221(addr=0x40) #INA3221 - 1
ina3221_2 = SDL_Pi_INA3221.SDL_Pi_INA3221_2(addr=0x41) #INA3221 - 2

# the three channels of the INA3221 named for SunAirPlus Solar Power Controller channels (www.switchdoc.com)
LIPO_BATTERY_CHANNEL = 1
SOLAR_CELL_CHANNEL = 2
OUTPUT_CHANNEL = 3

LIPO_BATTERY_CHANNEL_1 = 1
SOLAR_CELL_CHANNEL_1 = 2
OUTPUT_CHANNEL_1 = 3
#--------------------------------------------------------------------------------------------------------------
while True:

    #CH1 DEL INA3221 - 1
    shuntvoltage1 = 0 
    busvoltage1 = 0
    current_mA1 = 0
    loadvoltage1 = 0
    
    #CH1 DEL INA3221 - 2
    shuntvoltage_1 = 0
    busvoltage_1 = 0
    current_mA_1 = 0
    loadvoltage_1 = 0

    #CH2 DEL INA3221 - 1
    shuntvoltage2 = 0
    busvoltage2 = 0
    current_mA2 = 0
    loadvoltage2 = 0
    
    #CH2 DEL INA3221 - 2
    shuntvoltage_2 = 0
    busvoltage_2 = 0
    current_mA_2 = 0
    loadvoltage_2 = 0

    #CH3 DEL INA3221 - 1
    shuntvoltage3 = 0
    busvoltage3 = 0
    current_mA3 = 0
    loadvoltage3 = 0

    #CH3 DEL INA3221 - 2
    shuntvoltage_3 = 0
    busvoltage_3 = 0
    current_mA_3 = 0
    loadvoltage_3 = 0
#----------------------------------------Canal 1----------------------------------------------------------------------    
    busvoltage1 = ina3221.getBusVoltage_V(LIPO_BATTERY_CHANNEL)
    busvoltage_1 = ina3221_2.getBusVoltage_V(LIPO_BATTERY_CHANNEL_1)

    shuntvoltage1 = ina3221.getShuntVoltage_mV(LIPO_BATTERY_CHANNEL)
    shuntvoltage_1 = ina3221_2.getShuntVoltage_mV(LIPO_BATTERY_CHANNEL_1)

    # minus is to get the "sense" right.   - means the battery is charging, + that it is discharging
    current_mA1 = ina3221.getCurrent_mA(LIPO_BATTERY_CHANNEL)
    current_mA_1 = ina3221_2.getCurrent_mA(LIPO_BATTERY_CHANNEL_1)

    loadvoltage1 = busvoltage1 + (shuntvoltage1 / 1000)
    loadvoltage_1 = busvoltage_1 + (shuntvoltage_1 / 1000)
#----------------------------------------------Canal 2----------------------------------------------------------------
    busvoltage2 = ina3221.getBusVoltage_V(SOLAR_CELL_CHANNEL)
    busvoltage_2 = ina3221_2.getBusVoltage_V(SOLAR_CELL_CHANNEL_1)

    shuntvoltage2 = ina3221.getShuntVoltage_mV(SOLAR_CELL_CHANNEL)
    shuntvoltage_2 = ina3221_2.getShuntVoltage_mV(SOLAR_CELL_CHANNEL_1)

    current_mA2 = -ina3221.getCurrent_mA(SOLAR_CELL_CHANNEL)
    current_mA_2 = -ina3221_2.getCurrent_mA(SOLAR_CELL_CHANNEL_1)

    loadvoltage2 = busvoltage2 + (shuntvoltage2 / 1000)
    loadvoltage_2 = busvoltage_2 + (shuntvoltage_2 / 1000)
#-------------------------------------------------Canal 3-------------------------------------------------------------
    busvoltage3 = ina3221.getBusVoltage_V(OUTPUT_CHANNEL)
    busvoltage_3 = ina3221_2.getBusVoltage_V(OUTPUT_CHANNEL_1)

    shuntvoltage3 = ina3221.getShuntVoltage_mV(OUTPUT_CHANNEL)
    shuntvoltage_3 = ina3221_2.getShuntVoltage_mV(OUTPUT_CHANNEL_1)

    current_mA3 = ina3221.getCurrent_mA(OUTPUT_CHANNEL)
    current_mA_3 = ina3221_2.getCurrent_mA(OUTPUT_CHANNEL_1)

    loadvoltage3 = busvoltage3 + (shuntvoltage3 / 1000)
    loadvoltage_3 = busvoltage_3 + (shuntvoltage_3 / 1000)
    
    print("-------------CANAL 1 DEL INA 1 (0X40)-----------------")
    print("SALIDA S48V - Entrega 12V/100W Bus Voltage: %3.2f V " % busvoltage1) #Canal 1 del INA1 (0X40)
    print("SALIDA S48V - Entrega 12V/100W Shunt Voltage: %3.2f mV " % shuntvoltage1)
    print("SALIDA S48V - Entrega 12V/100W Load Voltage:  %3.2f V" % loadvoltage1)
    print("SALIDA S48V - Entrega 12V/100W Current 1:  %3.2f mA" % current_mA1)
    print("-------------CANAL 2 DEL INA 1 (0X40)-----------------")
    print("SALIDA PEPLINK 2.5A Bus Voltage:  %3.2f V " % busvoltage2) #Canal 2 del INA1 (0X40)
    print("SALIDA PEPLINK 2.5A Shunt Voltage: %3.2f mV " % shuntvoltage2)
    print("SALIDA PEPLINK 2.5A Load Voltage:  %3.2f V" % loadvoltage2)
    print("SALIDA PEPLINK 2.5A Current:  %3.2f mA" % current_mA2)
    print("-------------CANAL 3 DEL INA 1 (0X40)-----------------")
    print("SALIDA REFRI 8.33A Bus Voltage:  %3.2f V " % busvoltage3) #Canal 3 del INA1 (0X40)
    print("SALIDA REFRI 8.33A Shunt Voltage: %3.2f mV " % shuntvoltage3)
    print("SALIDA REFRI 8.33A Load Voltage:  %3.2f V" % loadvoltage3)
    print("SALIDA REFRI 8.33A Current:  %3.2f mA" % current_mA3)
    print("-------------CANAL 1 DEL INA 2 (0X41)-----------------")
    print("SALIDA AUXILIAR Bus Voltage: %3.2f V " % busvoltage_1) #Canal 1 del INA2 (0X41)
    print("SALIDA AUXILIAR Shunt Voltage: %3.2f mV " % shuntvoltage_1)
    print("SALIDA AUXILIAR Load Voltage:  %3.2f V" % loadvoltage_1)
    print("SALIDA AUXILIAR Current 1:  %3.2f mA" % current_mA_1)
    print("-------------CANAL 2 DEL INA 2 (0X41)-----------------")
    print("SALIDA AUXILIAR FRIDGE 2 Bus Voltage:  %3.2f V " % busvoltage_2) #Canal 2 del INA2 (0X41)
    print("SALIDA AUXILIAR FRIDGE 2 Shunt Voltage: %3.2f mV " % shuntvoltage_2)
    print("SALIDA AUXILIAR FRIDGE 2 Load Voltage:  %3.2f V" % loadvoltage_2)
    print("SALIDA AUXILIAR FRIDGE 2 Current:  %3.2f mA" % current_mA_2)
    print("-------------CANAL 3 DEL INA 2 (0X41)-----------------")
    print("SALIDA DE 2 VENTILADORES DE 1A Bus Voltage:  %3.2f V " % busvoltage_3) #Canal 3 del INA2 (0X41)
    print("SALIDA DE 2 VENTILADORES DE 1A Shunt Voltage: %3.2f mV " % shuntvoltage_3)
    print("SALIDA DE 2 VENTILADORES DE 1A Load Voltage:  %3.2f V" % loadvoltage_3)
    print("SALIDA DE 2 VENTILADORES DE 1A Current:  %3.2f mA" % current_mA_3)
    print("------------------------------------------------------")
    
    time.sleep(2.0)
