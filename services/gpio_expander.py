import board
import busio
import digitalio

from time import sleep
from adafruit_mcp230xx.mcp23017 import MCP23017

from services.loggers import logger

OUTPUT = digitalio.Direction.OUTPUT
INPUT = digitalio.Direction.INPUT

"""
GPA7 = GPIO 10 INVERSOR  # Output
GPA6 = GPIO 14 MIKROTIK  # Output
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

class GPIOExpander:

    MODULE = "expander"

    # Initialize the I2C bus:
    i2c = busio.I2C(board.SCL, board.SDA)
    mcp = MCP23017(i2c, address=0x20) 


    
    gpioPin = []
    _apply_config = True


    ALL_GPIO = {

        # Main outputs 
        "GPA7": {"pin_id":7 , "pin":None, "mode":OUTPUT, "name":"Inversor" },
        "GPA6": {"pin_id":6 , "pin":None, "mode":OUTPUT, "name":"Mirkotik" },
        "GPA2": {"pin_id":2 , "pin":None, "mode":OUTPUT, "name":"Fans" },
        "GPA5": {"pin_id":5 , "pin":None, "mode":OUTPUT, "name":"48V" },
        "GPA1": {"pin_id":1 , "pin":None, "mode":OUTPUT, "name":"Fridge_2" },   

        # INA alerts
        "GPA4": {"pin_id":4 , "pin":None, "mode":INPUT,  "name":"WARNING_INA_1" },
        "GPA3": {"pin_id":3 , "pin":None, "mode":INPUT,  "name":"CRITICAL_INA_1" },

        "GPB6": {"pin_id":14, "pin":None, "mode":INPUT,  "name":"WARNING_INA_2"},
        "GPB7": {"pin_id":15, "pin":None, "mode":INPUT,  "name":"CRITICAL_INA_2"}, 

        "GPB5": {"pin_id":13, "pin":None, "mode":INPUT,  "name":"WARNING_INA_3"},
        "GPB2": {"pin_id":10, "pin":None, "mode":INPUT,  "name":"CRITICAL_INA_3"},

        # Multiplexing COM pins
        "GPB0": {"pin_id":8 , "pin":None, "mode":OUTPUT, "name":"A+_COM" },
        "GPB1": {"pin_id":9 , "pin":None, "mode":OUTPUT, "name":"B-_COM"},

        # AUX
        "GPA0": {"pin_id":0 , "pin":None, "mode":OUTPUT, "name":"Aux_1" },
        "GPB3": {"pin_id":11, "pin":None, "mode":OUTPUT, "name":"Aux_3"},
        "GPB4": {"pin_id":12, "pin":None, "mode":OUTPUT, "name":"Aux_2"},
            
    }

    CONFIG_GPIO = [ "OUTPUT", "OUTPUT", "OUTPUT", "INPUT",  "INPUT",  "OUTPUT", "OUTPUT", "OUTPUT",     # Pin GPA0 -> GPA7
                    "OUTPUT",  "OUTPUT",  "INPUT",  "OUTPUT", "OUTPUT", "INPUT",  "INPUT",  "OUTPUT"]     # Pin GPB0 -> GPB7

    def __new__(cls):
        if not cls._apply_config: return cls

        for gpio in cls.ALL_GPIO.keys():
            try:
                pin_id, pin_mode   = cls.ALL_GPIO[gpio]["pin_id"], cls.ALL_GPIO[gpio]["mode"]
                cls.ALL_GPIO[gpio]["pin"] = cls.mcp.get_pin(pin_id)
                cls.ALL_GPIO[gpio]["pin"].direction = pin_mode

            except Exception as error: logger.log({"Expander config":str(error)}, logger.level.ERROR, cls.MODULE, True)

        cls._apply_config = False
        return cls
    
    @classmethod
    def get_name_GPIO(cls, gpio:str):
        return cls.ALL_GPIO[gpio]["name"]  
    

    @classmethod
    def setPinOn(cls, gpio:str)->bool:
        """Function to turn on a GPIO pin of the expander

        Args:
            gpio (str): ID of the GPIO 

        Returns:
            bool: Indicates if an action was performed
        """
        try:
            cls.ALL_GPIO[gpio]["pin"].value = True
            return True
        except Exception as error:
            logger.log({"Expander turn on pin":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False
        
    @classmethod
    def setPinOff(cls, gpio:str)->bool:
        """Function to turn off a GPIO pin of the expander

        Args:
            gpio (str): ID of the GPIO 

        Returns:
            bool: Indicates if an action was performed
        """
        try:
            cls.ALL_GPIO[gpio]["pin"].value = False
            return True
        except Exception as error:
            logger.log({"Expander turn off pin":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False


    @classmethod
    def readValue(cls, gpio):
        # If button is pressed = True
        # If button is not pressed = False
        value = cls.ALL_GPIO.gpioPin[gpio]["pin"].value
        return value
    
    @classmethod
    def turnAllPinsOff(cls):
        cls.setPinOff("GPA7")
        cls.setPinOff("GPA5")
        cls.setPinOff("GPA2")
    
    @classmethod
    def turnAllPinsOn(cls):
        cls.setPinOn("GPA6")
        cls.setPinOn("GPA7")
        cls.setPinOn("GPA5")
        cls.setPinOn("GPA2")

    @classmethod
    def hardReset(cls,port:str):
        cls.setPinOff(port)
        sleep(5)
        cls.setPinOn(port)

    @classmethod
    def hardResetStarlink(cls,port1:str, port2:str):
        cls.setPinOff(port1)
        cls.setPinOff(port2)
        sleep(5)
        cls.setPinOn(port1)
        cls.setPinOn(port2)

    