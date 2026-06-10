import smbus

from math import exp, log

from services.ads_controller import ADS
from services.loggers import logger


ADDRESS = 0x2e  # EMC2302 address
BUS_NUMBER = 3  # I2C bus number



#### Realizar curva de velocidad en base a la temperatura desde 21-30


class EMC2302FanController:
    """ Singleton class for controlling the EMC2302 fan controller. """
    
    # Name of the file for log specific errors
    MODULE="fans"
    
    bus = None
    _apply_config = True

    def __new__(cls):
        if cls._apply_config:
            cls.bus = smbus.SMBus(BUS_NUMBER)
            cls._apply_config = False
        return cls

    @classmethod
    def set_fan_speed(cls, fan, speed):
        try:
            """ Sets the speed (in RPM) for the given fan in the EMC2302 controller. """
            fan_register = None

            match fan:
                case 'FAN_ONE': fan_register = 0x30
                case 'FAN_TWO': fan_register = 0x40
                case _: raise ValueError(f'Invalid fan: {fan}. Allowed values: FAN_ONE, FAN_TWO')

            # Convert the speed to a register value
            setpoint_value = int((speed * 255) / 100)

            # Write the register value to the EMC2302
            cls.bus.write_word_data(ADDRESS, fan_register, setpoint_value)
            return True
        except Exception as error:
            logger.log({"Set fan speed":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False

    @classmethod
    def get_automatic_fans_speed(cls):
        """ Returns the speed (in porcentage) for the fans based on the given temperature. """
        ads = ADS()
        temperature = ads.get_ADS_Temperature(log_action=False)
            
        match temperature:
            case _ if temperature < 0: return 50 # If temperature is wrong due to resistor, set default fan speed
            case _ if temperature >= 30: return 100 # If the temperature is very high (>= 35°C), set the fans to 100%
            case _ if temperature <= 21: return 30  # If the temperature is very low (<= 24°C, about room temperature), set the fans to 10%  
            case _: return 50 # Temperature is between 21°C and 30°C, set the fans to 50%


    @classmethod
    def update_fans_speed(cls, automatic_mode):
        try:
            """ Updates the fans speed based on the current temperature. """
            fan_one_speed = None
            fan_two_speed = None

            if automatic_mode:
                fan_one_speed = cls.get_automatic_fans_speed()
                fan_two_speed = fan_one_speed

            if fan_one_speed is None or fan_two_speed is None:
                return

            cls.set_fan_speed('FAN_ONE', fan_one_speed)
            cls.set_fan_speed('FAN_TWO', fan_two_speed)

            logger.log(f'Fans speed updated. Fan 1: {fan_one_speed}%. Fan 2: {fan_two_speed}%.')
        
        except Exception as error: logger.log({"Update fan speed":str(error)}, logger.level.ERROR, cls.MODULE, True)
