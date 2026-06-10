import constants

from services.redis_connection import Redis
from services.gpio_controller import GPIOController
from services.solar_charge_controller import SolarChargeController


def get_stored_fan_threshold():
    """ Get the stored value of fan threshold """
    stored_value = Redis.conn().get('fan_threshold')
    if not stored_value:
        return float(constants.FAN_THRESHOLD_DEFAULT_VALUE)
    return float(stored_value)


def handle_fan_activation():
    """ Check the fan threshold and compare with the last value of the MUST radiator_temperature """
    solar_charge_controller = SolarChargeController()
    fan_threshold_value = get_stored_fan_threshold()
    if type(fan_threshold_value) is not float:
        return
    if solar_charge_controller.external_temperature is None:
        return
    if solar_charge_controller.external_temperature >= fan_threshold_value:
        GPIOController().fan_turn('ON')
    else:
        GPIOController().fan_turn('OFF')
