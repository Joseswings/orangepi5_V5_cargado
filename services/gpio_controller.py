import time
import wiringpi # type: ignore
import constants


from services.loggers import logger


class GPIOController:
    """
    Singleton to get access to GPIO ports and some useful functions to turn on and off some devices
    """
    INPUT, OUTPUT = 0, 1
    LOW, HIGH = 0, 1

    RX = constants.RX # Port PC6
    TX = constants.TX # Port PC5

    ALERT_ESP = constants.ALERT_ESP # Port PC 11
    RESET_EXPANDER = constants.RESET_EXPANDER # Port PC 9 
    CABINET = constants.CABINET       # Port PH 9
    INTERRUPT1 = constants.INTERRUPT1 # Port PC 10 Interrupt Expander
    INTERRUPT2 = constants.INTERRUPT2 # Port PH 6 Interrupt Expander

    # Side panel
    GREEN_LED = constants.GREEN_LED # Port PH 7
    RED_LED =   constants.RED_LED   # Port PH 8
    BLUE_LED =  constants.BLUE_LED  # Port PC 7
    CHASIS =    constants.CHASIS    # Port PC 15
    SOFTWARE_BUTTON = constants.SOFTWARE_BUTTON # Port PC 14
    HARDWARE_BUTTON = constants.HARDWARE_BUTTON # Port PC 8

    chasis_button_pressed = False
    _apply_config = True

    def __new__(cls):
        """ Apply config only the first time this class is used """
        if cls._apply_config:
            wiringpi.wiringPiSetup() 

            wiringpi.pinMode(cls.RX, cls.INPUT)
            wiringpi.pinMode(cls.TX, cls.OUTPUT)

            wiringpi.pinMode(cls.ALERT_ESP, cls.OUTPUT)
            wiringpi.pinMode(cls.RESET_EXPANDER, cls.OUTPUT)
            wiringpi.pinMode(cls.CABINET, cls.OUTPUT)
            wiringpi.pinMode(cls.INTERRUPT1, cls.OUTPUT)
            wiringpi.pinMode(cls.INTERRUPT2, cls.OUTPUT)

            # Side panel
            wiringpi.pinMode(cls.GREEN_LED, cls.OUTPUT)
            wiringpi.pinMode(cls.RED_LED, cls.OUTPUT)
            wiringpi.pinMode(cls.BLUE_LED, cls.OUTPUT)
            wiringpi.pinMode(cls.CHASIS, cls.INPUT)
            wiringpi.pinMode(cls.SOFTWARE_BUTTON, cls.INPUT)
            wiringpi.pinMode(cls.HARDWARE_BUTTON, cls.INPUT)
            cls._apply_config = False
        return cls

    @classmethod
    def read_pin(cls,gpio_number):
        """ Read value from input """
        value = wiringpi.digitalRead(gpio_number)
        return value

    @classmethod
    def led_turn_on(cls, gpio_number):
        """ Turn ON leds using gpio.LOW on GPIO ports """
        wiringpi.digitalWrite(gpio_number, cls.LOW)

    @classmethod
    def led_turn_off(cls, gpio_number):
        """ Turn ON leds using gpio.HIGH on GPIO ports """
        wiringpi.digitalWrite(gpio_number, cls.HIGH)

    @classmethod
    def channel_turn_on(cls, gpio_number):
        """ Use this to turn ON GPIO connected to channels """
        wiringpi.digitalWrite(gpio_number, cls.HIGH)

    @classmethod
    def channel_turn_off(cls, gpio_number):
        """ Use this to turn OFF GPIO connected to channels """
        wiringpi.digitalWrite(gpio_number, cls.LOW)

    @classmethod
    def is_chassis_open(cls):
        """Check if the chasis button is open or close and based on that determine if the chasis is open"""
        if wiringpi.digitalRead(cls.CHASIS_BUTTON_GPIO) == 1 and cls.chasis_button_pressed is False:
            cls.chasis_button_pressed = True
            return False
        if wiringpi.digitalRead(cls.CHASIS_BUTTON_GPIO) == 0 and cls.chasis_button_pressed is True:
            cls.chasis_button_pressed = False
            return True
        return False

    @classmethod
    def fan_turn(cls, action):
        """ Turn ON/OFF the fan """
        if action == 'ON':
            cls.channel_turn_on(cls.FAN_GPIO)
        if action == 'OFF':
            cls.channel_turn_off(cls.FAN_GPIO)

    @classmethod
    def power_source_turn(cls, action):
        """ Turn ON/OFF the power source """
        if action == 'ON':
            cls.channel_turn_on(cls.POWER_SOURCE_GPIO_ONE)
            cls.channel_turn_on(cls.POWER_SOURCE_GPIO_TWO)

        if action == 'OFF':
            cls.channel_turn_off(cls.POWER_SOURCE_GPIO_ONE)
            cls.channel_turn_off(cls.POWER_SOURCE_GPIO_TWO)

    @classmethod
    def network_switch_turn(cls, action):
        """ Turn ON/OFF the network switch """
        if action == 'ON':
            cls.channel_turn_on(cls.NETWORK_SWITCH_GPIO)
        if action == 'OFF':
            cls.channel_turn_off(cls.NETWORK_SWITCH_GPIO)

    @classmethod
    def mqtt_connected_turn(cls, action):
        """ Turn ON/OFF the MQTT led indicator """
        if action == 'ON':
            cls.led_turn_on(cls.MQTT_CONNECTED_GPIO)
        if action == 'OFF':
            cls.led_turn_off(cls.MQTT_CONNECTED_GPIO)

    @classmethod
    def critical_indicator_turn(cls, action):
        """ Turn ON/OFF the LED used to show 'critical' state """
        if action == 'ON':
            cls.led_turn_on(cls.CRITICAL_INDICATOR_GPIO)
        if action == 'OFF':
            cls.led_turn_off(cls.CRITICAL_INDICATOR_GPIO)

    @classmethod
    def normal_indicator_turn(cls, action):
        """ Turn ON/OFF the LED use to show 'normal' indicator """
        if action == 'ON':
            cls.led_turn_on(cls.NORMAL_INDICATOR_GPIO)
        if action == 'OFF':
            cls.led_turn_off(cls.NORMAL_INDICATOR_GPIO)

    @classmethod
    def work_mode_indicator_turn(cls, action):
        """ Turn ON/OFF the LED use to show 'work mode' indicator """
        if action == 'ON':
            cls.led_turn_on(cls.WORK_MODE_INDICATOR_GPIO)
        if action == 'OFF':
            cls.led_turn_off(cls.WORK_MODE_INDICATOR_GPIO)

    @classmethod
    def working_normal_indicator_turn(cls, action):
        """ Turn ON/OFF the LED use to show 'working normal' indicator """
        if action == 'ON':
            cls.led_turn_on(cls.WORKING_NORMAL)
        if action == 'OFF':
            cls.led_turn_off(cls.WORKING_NORMAL)

    @classmethod
    def toggle_solenoid(cls):
        """ Set the solenoid to HIGH for 5 seconds and then turn it OFF """
        cls.channel_turn_on(cls.SOLENOID_GPIO)
        time.sleep(5)
        cls.channel_turn_off(cls.SOLENOID_GPIO)
        post_request({'solenoid_toggle': 0.0})
        log('Solenoid turned OFF')

    @classmethod
    def turn_all_off(cls):
        """ Turn OFF all GPIO ports """
        # Subsystems
        cls.channel_turn_off(cls.POWER_SOURCE_GPIO_ONE)
        cls.channel_turn_off(cls.POWER_SOURCE_GPIO_TWO)
        cls.channel_turn_off(cls.NETWORK_SWITCH_GPIO)
        cls.channel_turn_off(cls.FAN_GPIO)

        # LEDs
        cls.channel_turn_off(cls.MQTT_CONNECTED_GPIO)
        cls.channel_turn_off(cls.CRITICAL_INDICATOR_GPIO)
        cls.channel_turn_off(cls.NORMAL_INDICATOR_GPIO)
        cls.channel_turn_off(cls.WORK_MODE_INDICATOR_GPIO)
        cls.channel_turn_off(cls.WORKING_NORMAL)
    
    @classmethod
    def turn_all_on(cls):
        """ Turn OFF all GPIO ports """
        # Subsystems
        cls.channel_turn_on(cls.POWER_SOURCE_GPIO_ONE)
        cls.channel_turn_on(cls.POWER_SOURCE_GPIO_TWO)
        cls.channel_turn_on(cls.NETWORK_SWITCH_GPIO)
        cls.channel_turn_on(cls.FAN_GPIO)

        # LEDs
        cls.channel_turn_on(cls.MQTT_CONNECTED_GPIO)
        cls.channel_turn_on(cls.CRITICAL_INDICATOR_GPIO)
        cls.channel_turn_on(cls.NORMAL_INDICATOR_GPIO)
        cls.channel_turn_on(cls.WORK_MODE_INDICATOR_GPIO)
        cls.channel_turn_on(cls.WORKING_NORMAL)
