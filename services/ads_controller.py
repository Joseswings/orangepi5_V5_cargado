# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import busio

import adafruit_ads1x15.ads1115 as ADS1115 # type: ignore
from adafruit_ads1x15.analog_in import AnalogIn # type: ignore
from math import log as logarithm

from services.loggers import logger

class ADS:

    def __new__(cls): return cls

    MODULE = "ads"

    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the ADC object using the I2C bus
    ads = ADS1115.ADS1115(i2c)

    # Canales 0,1,2,3
    chan0 = AnalogIn(ads, ADS1115.P0)  # 12V channel
    chan1 = AnalogIn(ads, ADS1115.P1)  # Remote termocouple
    chan2 = AnalogIn(ads, ADS1115.P2)  # Local temperature resistance
    chan3 = AnalogIn(ads, ADS1115.P3)

    @classmethod
    def get_channel_reading(cls, channel):
        match channel:
            case 0: return cls.chan0.voltage
            case 1: return cls.chan1.voltage
            case 2: return cls.chan2.voltage
            case 3: return cls.chan3.voltage
            case _: return None

    @classmethod
    def get_ADS_Voltage(cls)->float|None:
        """Function to get voltage from ADS

        Returns:
            float : Final voltage value
        """
        try:
            # Calculate V_Out using the formula
            # V_In * (R1 + R2)/(R2) = V_In * ((82K ohms + 10K ohms)/ 10K ohms)
            ads_voltage = cls.get_channel_reading(0)
            voltage = ads_voltage * ((82+10)/10)

            return round(voltage,2)
        except Exception as error:
            logger.log({"Get ADS voltage":str(error)}, logger.level.INFO, cls.MODULE, True)
            return None
        
    @classmethod
    def get_ADS_Temperature(cls, log_action=True)->float:
        """Get the external temperature from the ADS115

        Returns:
            float : Temperature in celsius
        """
        try:
            # Voltage divider values
            voltage_in = 3.3
            voltage_out = cls.get_channel_reading(2)
            fixed_resistor = 30e3  # 33kOhm

            # Datasheet values for the NTC thermistor
            beta = 3380
            nominal_resistor = 10e3  # 10kOhm

            # First, we calculate the resistance of the thermistor
            ntc_resistance = (fixed_resistor * voltage_out) / \
                (voltage_in - voltage_out)

            # Then, we calculate the temperature
            t_0 = 273.15     # 0 degrees Celsius in Kelvin
            t_25 = t_0 + 25  # 25 degrees Celsius in Kelvin (nominal thermistor temperature)
            t = 0

            try:
                t = 1 / ((logarithm(ntc_resistance / nominal_resistor) / beta) + (1 / t_25))
            except ValueError:
                if log_action: logger.log("Calculating ADS temperature failed, check resistors", logger.level.WARNING)
                return -1

            # The previous calculation was derived from the Steinhart-Hart equation
            # Convert from Kelvin to Celsius
            t -= t_0

            return round(t,2)
        except Exception as error:
            logger.log({"Get ADS temperature":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return -1
    
    @classmethod
    def get_ADS_data(cls)->tuple[dict|None,bool]:
        """Function to get ADS data and save it into a Json
        
        Raises:
            Exception: ADS not detected

        Returns:
            dict: Return a Json object if Voltage value is exists
        """
        try:
            voltage_ads = cls.get_ADS_Voltage()
            temp_ads    = cls.get_ADS_Temperature()
            
            json = {
                "Voltage - ADS": voltage_ads,
                "Temperature - ADS": temp_ads,
            }
        
            if voltage_ads is not None: return json, True
            return None, False
        
        except Exception as error:
            logger.log({"Get ADS data":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None, False