from smbus import SMBus
from services.loggers import logger

# constants
# /*=========================================================================
#    I2C ADDRESS/BITS
#    -----------------------------------------------------------------------*/
INA3221_ADDRESS_1 = (0x40)    # 1000000 (A0+A1=GND)
INA3221_ADDRESS_2 = (0x41)
INA3221_ADDRESS_3 = (0x42)
INA3221_READ = (0x01)
# /*=========================================================================*/

# /*=========================================================================
#    CONFIG REGISTER (R/W)
#    -----------------------------------------------------------------------*/
INA3221_REG_CONFIG = (0x00)
#    /*---------------------------------------------------------------------*/
INA3221_CONFIG_RESET = (0x8000)  # Reset Bit

INA3221_CONFIG_ENABLE_CHAN1 = (0x4000)  # Enable Channel 1
INA3221_CONFIG_ENABLE_CHAN2 = (0x2000)  # Enable Channel 2
INA3221_CONFIG_ENABLE_CHAN3 = (0x1000)  # Enable Channel 3

INA3221_CONFIG_AVG2 = (0x0800)  # AVG Samples Bit 2 - See table 3 spec
INA3221_CONFIG_AVG1 = (0x0400)  # AVG Samples Bit 1 - See table 3 spec
INA3221_CONFIG_AVG0 = (0x0200)  # AVG Samples Bit 0 - See table 3 spec

# VBUS bit 2 Conversion time - See table 4 spec
INA3221_CONFIG_VBUS_CT2 = (0x0100)
# VBUS bit 1 Conversion time - See table 4 spec
INA3221_CONFIG_VBUS_CT1 = (0x0080)
# VBUS bit 0 Conversion time - See table 4 spec
INA3221_CONFIG_VBUS_CT0 = (0x0040)

# Vshunt bit 2 Conversion time - See table 5 spec
INA3221_CONFIG_VSH_CT2 = (0x0020)
# Vshunt bit 1 Conversion time - See table 5 spec
INA3221_CONFIG_VSH_CT1 = (0x0010)
# Vshunt bit 0 Conversion time - See table 5 spec
INA3221_CONFIG_VSH_CT0 = (0x0008)

INA3221_CONFIG_MODE_2 = (0x0004)  # Operating Mode bit 2 - See table 6 spec
INA3221_CONFIG_MODE_1 = (0x0002)  # Operating Mode bit 1 - See table 6 spec
INA3221_CONFIG_MODE_0 = (0x0001)  # Operating Mode bit 0 - See table 6 spec
# /*=========================================================================*/

# /*=========================================================================
#    SHUNT VOLTAGE REGISTER (R)
#    -----------------------------------------------------------------------*/
INA3221_REG_SHUNTVOLTAGE_1 = (0x01)
# /*=========================================================================*/

# /*=========================================================================
#    BUS VOLTAGE REGISTER (R)
#    -----------------------------------------------------------------------*/
INA3221_REG_BUSVOLTAGE_1 = (0x02)
# /*=========================================================================*/

SHUNT_RESISTOR_VALUE = (0.01)   # default shunt resistor value of 0.01 Ohm
SHUNT_RESISTOR_VALUE_2 = (0.01)   # default shunt resistor value of 0.01 Ohm


class SDL_PI_INA3221():
    # Class state variables
    _apply_config_ina_1 = True
    _apply_config_ina_2 = True
    _apply_config_ina_3 = True

    ###########################
    # INA3221 Code
    ###########################
    """ Singleton to get data from INA sensors """
    def __init__(cls, addr, shunt_resistor, twi=0):
        # twi = nanopi's I2C number

        if cls._apply_config_ina_1 or cls._apply_config_ina_2 or cls._apply_config_ina_3:
            cls._bus = SMBus(twi)
            cls._addr = addr
            cls._shunt_resistor = shunt_resistor
            config = INA3221_CONFIG_ENABLE_CHAN1 | \
                INA3221_CONFIG_ENABLE_CHAN2 | \
                INA3221_CONFIG_ENABLE_CHAN3 | \
                INA3221_CONFIG_AVG1 | \
                INA3221_CONFIG_VBUS_CT2 | \
                INA3221_CONFIG_VSH_CT2 | \
                INA3221_CONFIG_MODE_2 | \
                INA3221_CONFIG_MODE_1 | \
                INA3221_CONFIG_MODE_0

            cls._write_register_little_endian(INA3221_REG_CONFIG, config)

        if addr == INA3221_ADDRESS_1:
            cls._apply_config_ina_1 = False
        elif addr == INA3221_ADDRESS_2:
            cls._apply_config_ina_2 = False
        else:
            cls._apply_config_ina_3 = False

    # Private functions
    def _write(cls, register, data):
        """ Write data to the INA controller """
        # print "addr =0x%x register = 0x%x data = 0x%x " % (cls._addr, register, data)
        cls._bus.write_byte_data(cls._addr, register, data)

    def _read(cls, data):
        """ Read data from the INA controller """
        returndata = cls._bus.read_byte_data(cls._addr, data)
        # print "addr = 0x%x data = 0x%x %i returndata = 0x%x " % (cls._addr, data, data, returndata)

        return returndata

    def _read_register_little_endian(cls, register):
        """ Read the data from the given register from the INA controller """
        try:
            result = cls._bus.read_word_data(cls._addr, register) & 0xFFFF
            lowbyte = (result & 0xFF00) >> 8
            highbyte = (result & 0x00FF) << 8
            switchresult = lowbyte + highbyte
            # print "Read 16 bit Word addr =0x%x register = 0x%x switchresult = 0x%x " % (cls._addr, register, switchresult)

            return switchresult

        except BlockingIOError:
            logger.log({"INA read register": f"The resource for register {register} is busy"}, log_level=logger.level.ERROR)
            return False

        except IOError:
            logger.log({"INA read register": f"IOError on register {register}"}, log_level=logger.level.ERROR)
            return False

        except Exception as e:
            logger.log({"INA read register": f"Exception on register {register}: {e}"}, log_level=logger.level.ERROR)
            return False

    def _write_register_little_endian(cls, register, data):
        """ Write data to the given register from the INA controller """
        data = data & 0xFFFF
        # reverse configure byte for little endian
        lowbyte = data >> 8
        highbyte = (data & 0x00FF) << 8
        switchdata = lowbyte + highbyte
        cls._bus.write_word_data(cls._addr, register, switchdata)
        # print "Write  16 bit Word addr =0x%x register = 0x%x data = 0x%x " % (cls._addr, register, data)

    def _getBusVoltage_raw(cls, channel):
        """ Gets the raw bus voltage (16-bit signed integer, so +-32767) """
        value = cls._read_register_little_endian(
            INA3221_REG_BUSVOLTAGE_1 + (channel - 1) * 2)

        if value > 32767:
            value -= 65536

        return value

    def _getShuntVoltage_raw(cls, channel):
        """ Gets the raw shunt voltage (16-bit signed integer, so +-32767) """
        value = cls._read_register_little_endian(
            INA3221_REG_SHUNTVOLTAGE_1 + (channel - 1) * 2)

        if value > 32767:
            value -= 65536

        return value

    # Public functions
    def getBusVoltage_V(cls, channel):
        """ Gets the Bus voltage in volts """
        value = cls._getBusVoltage_raw(channel)

        return  round(number=(value * 0.001), ndigits=2)

    def getShuntVoltage_mV(cls, channel):
        """ Gets the shunt voltage in mV (so +-168.3mV) """
        value = cls._getShuntVoltage_raw(channel)

        return value * 0.005

    def getCurrent_mA(cls, channel):
        """ Gets the current value in mA, taking into account the config settings and current LSB """
        valueDec = round((cls.getShuntVoltage_mV(channel) / cls._shunt_resistor), ndigits=2)

        return valueDec
    
    def ping_channel(cls, channel):
        """ Ping the channel to see if it is alive """
        try:
            channel_reading = cls._read_register_little_endian(
                INA3221_REG_BUSVOLTAGE_1 + (channel - 1) * 2)
            return channel_reading is not False
        except:
            logger.log({"INA ping Channel": f"INA3221 channel {channel} is not responding"}, log_level=logger.level.ERROR)
            return False


class INA_Sensors():

    MODULE = "ina"

    _apply_config = True
    _INA3221_1_sensors = None
    _INA3221_2_sensors = None
    _INA3221_3_sensors = None

    sensors = {
        "Inversor": {"ina":1,"channel":3},
        "Mikrotik": {"ina":1,"channel":2},
        "48V":      {"ina":1,"channel":1},
        "AUX1":     {"ina":2,"channel":1},
        "Fridge":   {"ina":2,"channel":2},
        "Fans":     {"ina":2,"channel":3},
        "AUX2":     {"ina":3,"channel":1},
        "AUX3":     {"ina":3,"channel":2},
    }

    def __new__(cls, twi=3):
        if cls._apply_config:
            
            # INA 1 sensors:
            # - Channel 1: 48V 
            # - Channel 2: Mikrotik
            # - Channel 3: Inversor
            cls._INA3221_1_sensors = SDL_PI_INA3221(INA3221_ADDRESS_1, SHUNT_RESISTOR_VALUE, twi)

            # INA 2 sensors:
            # - Channel 1: AUX1
            # - Channel 2: Fridge
            # - Channel 3: Fans
            cls._INA3221_2_sensors = SDL_PI_INA3221(INA3221_ADDRESS_2, SHUNT_RESISTOR_VALUE, twi)
            
            # INA 3 sensors:
            # - Channel 1: AUX2
            # - Channel 2: AUX3
            cls._INA3221_3_sensors = SDL_PI_INA3221(INA3221_ADDRESS_3, SHUNT_RESISTOR_VALUE, twi)

            cls._apply_config = False

        return cls
    
    @classmethod
    def get_sensor(cls,sensor:str)->tuple[int,int]:
        """ Get values from INA using the id of the sensor"""

        try:
            sensor = cls.sensors[sensor]
            ina, channel = sensor["ina"], sensor["channel"]

            match ina:
                case 1: return cls._INA3221_1_sensors.getBusVoltage_V(channel), cls._INA3221_1_sensors.getCurrent_mA(channel)
                case 2: return cls._INA3221_2_sensors.getBusVoltage_V(channel), cls._INA3221_2_sensors.getCurrent_mA(channel)
                case 3: return cls._INA3221_3_sensors.getBusVoltage_V(channel), cls._INA3221_3_sensors.getCurrent_mA(channel)
                case _: raise Exception("Invalid INA id")

        except Exception as error:
            logger.log({"INA get sensor":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return 0, 0
    
    @classmethod
    def get_all(cls)->dict:
        """ Get values from all INA sensors and return a Json"""
        try:
            json = {}

            for sensor in cls.sensors.keys():
                voltage, current = cls.get_sensor(sensor)
                if voltage != 0 and current != 0: 
                    key_voltage = "".join(["INA Voltage - ",sensor])
                    key_current = "".join(["INA Current - ",sensor])

                    json[key_voltage] = voltage
                    json[key_current] = current
    
            return json
        except Exception as error: 
            logger.log({"Get all INA data":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None


    # Helper functions to get the voltages and currents for each sensor
    @classmethod
    def get_fans(cls):
        """ Get the fans voltage and current """
        cls()
        return cls._INA3221_2_sensors.getBusVoltage_V(3), cls._INA3221_2_sensors.getCurrent_mA(3)

    @classmethod
    def get_fridge_1(cls):
        """ Get fridge 1 voltage and current """
        cls()
        return cls._INA3221_1_sensors.getBusVoltage_V(3), cls._INA3221_1_sensors.getCurrent_mA(3)

    @classmethod
    def get_fridge_2(cls):
        """ Get fridge 2 voltage and current """
        cls()
        return cls._INA3221_2_sensors.getBusVoltage_V(2), cls._INA3221_2_sensors.getCurrent_mA(2)

    @classmethod
    def get_peplink(cls):
        """ Get Peplink voltage and current """
        cls()
        return cls._INA3221_1_sensors.getBusVoltage_V(2), cls._INA3221_1_sensors.getCurrent_mA(2)

    @classmethod
    def get_power_supply(cls):
        """ Get power supply voltage and current """
        cls()
        return cls._INA3221_1_sensors.getBusVoltage_V(1), cls._INA3221_1_sensors.getCurrent_mA(1)

    @classmethod
    def get_aux(cls):
        """ Get aux voltage and current """
        cls()
        return cls._INA3221_2_sensors.getBusVoltage_V(1), cls._INA3221_2_sensors.getCurrent_mA(1)
    
    @classmethod
    def ping_channels(cls):
        """ Ping all channels to see if they are alive """
        cls()
        power_supply = cls._INA3221_1_sensors.ping_channel(1)
        peplink = cls._INA3221_1_sensors.ping_channel(2)
        fridge_1 = cls._INA3221_1_sensors.ping_channel(3)
        aux = cls._INA3221_2_sensors.ping_channel(1)
        fridge_2 = cls._INA3221_2_sensors.ping_channel(2)
        fans = cls._INA3221_2_sensors.ping_channel(3)

        return power_supply, peplink, fridge_1, aux, fridge_2, fans
