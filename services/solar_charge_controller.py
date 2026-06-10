from math import log as logarithm

from services.ina_sensors import INA_Sensors
from services.ads_controller import ADS
from services.loggers import logger


class SolarChargeController:
    """ Singleton to get data from Solar Charge Controller hardware or fake data used only for test """
    charger_workstate = None
    pv_voltage = None
    battery_voltage = None
    battery_voltage_ads1015 = None
    charger_current = None
    charger_power = None
    radiator_temperature = None
    external_temperature = None
    external_temperature_ads1015 = None
    accumulated_pv_power_high = None
    accumulated_pv_power_low = None
    accumulated_day = None
    _charge_mode = 'normal'
    _charge_modes = {
        'normal': 'NORMAL CHARGE',
        'low': 'LOW CHARGE',
        'critical': 'CRITICAL CHARGE',
        'no_charge': 'NO CHARGE AVAILABLE'
    }

    # The INA sensors' values are stored as tuples where the first element is the voltage and the second, the current
    ina_fans = None
    ina_fridge_1 = None
    ina_fridge_2 = None
    ina_peplink = None
    ina_power_supply = None
    ina_aux = None

    def __new__(cls):
        return cls

    @classmethod
    def get(cls, phase='1', ina=False):
        """
        :return: dict representation of every value but for the given phase
        """
        if ina:
            # Return only the values from the INA sensors and the ADS1015
            ina_vals = {
                'battery_voltage_ads1015': cls.battery_voltage_ads1015,
                'ina_fans_voltage': cls.ina_fans[0],
                'ina_fans_current': cls.ina_fans[1],
                'ina_fridge_1_voltage': cls.ina_fridge_1[0],
                'ina_fridge_1_current': cls.ina_fridge_1[1],
                'ina_fridge_2_voltage': cls.ina_fridge_2[0],
                'ina_fridge_2_current': cls.ina_fridge_2[1],
                'ina_peplink_voltage': cls.ina_peplink[0],
                'ina_peplink_current': cls.ina_peplink[1],
                'ina_power_supply_voltage': cls.ina_power_supply[0],
                'ina_power_supply_current': cls.ina_power_supply[1],
                'ina_aux_voltage': cls.ina_aux[0],
                'ina_aux_current': cls.ina_aux[1],
            }

            # If the external_temperature_ads1015 value is -1, there was an error reading the sensor
            if cls.external_temperature_ads1015 != -1:
                ina_vals['external_temperature_ads1015'] = cls.external_temperature_ads1015

            return ina_vals

        if phase == '1':
            new_acc_pv_power_low = check_accumulated_pv_power_low(cls.accumulated_pv_power_low)

            # These values are for phase 1 (reported every 5 minutes)
            phase_1_vals = {
                'charger_workstate': cls.charger_workstate,
                'pv_voltage': cls.pv_voltage,
                'battery_voltage': cls.battery_voltage,
                'battery_voltage_ads1015': cls.battery_voltage_ads1015,
                'charger_current': cls.charger_current,
                'charger_power': cls.charger_power,
                'radiator_temperature': cls.radiator_temperature,
                'external_temperature': cls.external_temperature,
                'state_of_charge': cls.get_state_of_charge(),
                'accumulated_pv_power_low': new_acc_pv_power_low,
                'ina_fans_voltage': cls.ina_fans[0],
                'ina_fans_current': cls.ina_fans[1],
                'ina_fridge_1_voltage': cls.ina_fridge_1[0],
                'ina_fridge_1_current': cls.ina_fridge_1[1],
                'ina_fridge_2_voltage': cls.ina_fridge_2[0],
                'ina_fridge_2_current': cls.ina_fridge_2[1],
                'ina_peplink_voltage': cls.ina_peplink[0],
                'ina_peplink_current': cls.ina_peplink[1],
                'ina_power_supply_voltage': cls.ina_power_supply[0],
                'ina_power_supply_current': cls.ina_power_supply[1],
                'ina_aux_voltage': cls.ina_aux[0],
                'ina_aux_current': cls.ina_aux[1],
            }

            if cls.external_temperature_ads1015 != -1:
                phase_1_vals['external_temperature_ads1015'] = cls.external_temperature_ads1015

            return phase_1_vals
        elif phase == '2':
            new_acc_pv_power_low = check_accumulated_pv_power_low(cls.accumulated_pv_power_low)

            # These values are for phase 2 (reported every 30 minutes)
            return {
                'accumulated_day': cls.accumulated_day,
                'accumulated_pv_power_high': cls.accumulated_pv_power_high,
                'accumulated_pv_power_low': new_acc_pv_power_low,
            }
        return {}

    @classmethod
    def get_ads1015_battery_voltage(cls):
        """ Get the battery voltage from the ADS1015 """
        voltage_divider_value =  ADS.get_channel_reading(0)
        battery_voltage = (voltage_divider_value * (10 + 39)) / 10

        return battery_voltage

    @classmethod
    def get_ads1015_external_temperature(cls):
        """ Get the external temperature from the ADS1015 """
        # Voltage divider values
        voltage_in = 3.3
        voltage_out = ADS.get_channel_reading(2)
        fixed_resistor = 30e3  # 33kOhm

        # Datasheet values for the NTC thermistor
        beta = 3380
        nominal_resistor = 10e3  # 10kOhm

        # First, we calculate the resistance of the thermistor
        ntc_resistance = (fixed_resistor * voltage_out) / \
            (voltage_in - voltage_out)

        log.debug('NTC resistance: %s', ntc_resistance)
        log.debug('Nominal resistance: %s', nominal_resistor)

        # Then, we calculate the temperature
        t_0 = 273.15     # 0 degrees Celsius in Kelvin
        t_25 = t_0 + 25  # 25 degrees Celsius in Kelvin (nominal thermistor temperature)
        t = 0

        try:
            t = 1 / (((logarithm(ntc_resistance / nominal_resistor) / beta)) + (1 / t_25))
        except ValueError:
            log.error('Error calculating temperature')
            return -1

        # The previous calculation was derived from the Steinhart-Hart equation

        # Convert from Kelvin to Celsius
        t -= t_0

        return t

    @classmethod
    def update(cls):
        """
        Read data from serial port to update class values
        """
        # ADS1015 readings
        cls.battery_voltage_ads1015 = cls.get_ads1015_battery_voltage()
        try:
            cls.external_temperature_ads1015 = cls.get_ads1015_external_temperature()
        except ValueError:
            log.error('Error calculating temperature')
            cls.external_temperature_ads1015 = -1

        # INA sensors
        cls.ina_fans = INA_Sensors.get_fans()
        cls.ina_fridge_1 = INA_Sensors.get_fridge_1()
        cls.ina_fridge_2 = INA_Sensors.get_fridge_2()
        cls.ina_peplink = INA_Sensors.get_peplink()
        cls.ina_power_supply = INA_Sensors.get_power_supply()
        cls.ina_aux = INA_Sensors.get_aux()

        serial_data = SerialConnector().read()
        log.info(f'MUST serial data {serial_data}')

        if len(serial_data) != 24:
            log.warning('Expected 24 elements in serial data')
            return False

        cls.charger_workstate = serial_data[0]
        cls.pv_voltage = int(serial_data[4]) / 10.0
        cls.battery_voltage = int(serial_data[5]) / 10.0
        cls.charger_current = int(serial_data[6]) / 10.0
        cls.charger_power = serial_data[7]
        cls.radiator_temperature = float(serial_data[8])
        cls.external_temperature = float(serial_data[9])
        cls.accumulated_pv_power_high = serial_data[16]
        cls.accumulated_pv_power_low = serial_data[17]
        cls.accumulated_day = serial_data[18]
        cls.set_charge_mode()

        return True

    @classmethod
    def set_charge_mode(cls):
        """ Update the value of cls._charge_mode """
        cls._charge_mode = 'normal'
        # TODO: this will be enable later when Victor indicates
        # if 12.5 <= cls.battery_voltage <= 13.0:
        #     cls._charge_mode = 'low'
        # elif cls.battery_voltage < 12.5:
        #     cls._charge_mode = 'critical'
        # elif cls.battery_voltage < 12:
        #     cls._charge_mode = 'no_charge'
        # else:
        #     cls._charge_mode = 'normal'
        return cls._charge_mode

    @classmethod
    def get_charge_mode(cls):
        """ Get charge mode value """
        return cls._charge_mode

    @classmethod
    def get_state_of_charge(cls):
        if cls.battery_voltage < 12:
            return '0'
        elif 13 <= cls.battery_voltage <= 13.15:
            return '25'
        elif 13.15 <= cls.battery_voltage <= 13.2:
            return '50'
        elif 13.3 <= cls.battery_voltage <= 13.33:
            return '75'
        elif 13.33 <= cls.battery_voltage:
            return '100'
        return '0'

    @classmethod
    def get_charger_workstate(cls):
        """
        This function will check what mode is in the charger workstate base on this table

        0: Initialization Mode
        1: Selftest Mode
        2: Work Mode
        3: Stop Mode

        :return: str
        """
        if cls.charger_workstate == '0':
            return 'initialization_mode'
        elif cls.charger_workstate == '1':
            return 'selftest_mode'
        elif cls.charger_workstate == '2':
            return 'work_mode'
        elif cls.charger_workstate == '3':
            return 'stop_mode'
        return ''

    @classmethod
    def is_any_ina_on(cls):
        # Update the INA sensors values
        cls.ina_fans = INA_Sensors.get_fans()
        cls.ina_fridge_1 = INA_Sensors.get_fridge_1()
        cls.ina_fridge_2 = INA_Sensors.get_fridge_2()
        cls.ina_peplink = INA_Sensors.get_peplink()
        cls.ina_power_supply = INA_Sensors.get_power_supply()
        cls.ina_aux = INA_Sensors.get_aux()

        # Check if any of the INA sensors is ON
        if cls.ina_fans[0] > 0 or cls.ina_fans[1] > 0:
            return True
        if cls.ina_fridge_1[0] > 0 or cls.ina_fridge_1[1] > 0:
            return True
        if cls.ina_fridge_2[0] > 0 or cls.ina_fridge_2[1] > 0:
            return True
        if cls.ina_peplink[0] > 0 or cls.ina_peplink[1] > 0:
            return True
        if cls.ina_power_supply[0] > 0 or cls.ina_power_supply[1] > 0:
            return True
        if cls.ina_aux[0] > 0 or cls.ina_aux[1] > 0:
            return True
        return False

    @classmethod
    def get_battery_voltage(cls):
        battery_voltage = cls.battery_voltage

        if cls.battery_voltage is None:
            battery_voltage = ( ADS.get_channel_reading(0) * (10 + 39)) / 10

        return battery_voltage

    @classmethod
    def get_ina_sensors_current(cls):
        fans = INA_Sensors.get_fans()[1]
        ina_frige_1 = INA_Sensors.get_fridge_1()[1]
        ina_frige_2 = INA_Sensors.get_fridge_2()[1]
        ina_peplink = INA_Sensors.get_peplink()[1]
        ina_power_supply = INA_Sensors.get_power_supply()[1]
        ina_aux = INA_Sensors.get_aux()[1]

        return [fans, ina_frige_1, ina_frige_2, ina_peplink, ina_power_supply, ina_aux]


def check_accumulated_pv_power_low(new_val):
    """ Check if the accumulated pv power low value is correct """
    old_val = get_ubidots_variable('accumulated_pv_power_low')

    # Return the greater value to prevent the value to decrease
    if new_val > old_val:
        return new_val
    return old_val
