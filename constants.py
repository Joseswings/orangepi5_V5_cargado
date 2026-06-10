FIRST_PHASE_CHECK_INTERVAL = 300    # Time in seconds to wait for the first phase check

SECOND_PHASE_CHECK_INTERVAL = 30    # Time in minutes to wait for the second phase check

CHASSIS_SWITCH_CHECK_INTERVAL = 1   # Time in seconds to wait to check the chassis switch

SOLENOID_CHECK_INTERVAL = 1         # Time in seconds to wait to check the solenoid toggle

REBOOT_CHECK_INTERVAL = 1           # Time in seconds to wait to check the reboot signal

INA_SENSORS_CHECK_INTERVAL = 60     # Time in seconds to wait to check the INA sensors energy consumption

INA_PING_CHECK_INTERVAL = 900       # Time in seconds to wait to ping the INA sensors

EMC2302_FANS_CHECK_INTERVAL = 120     # Time in seconds to wait to check the EMC2302 fans

ORPI_STATUS_CHECK_INTERVAL = 15     # Time in minutes to wait to check the OrPi status

BOTTOM_THRESHOLD_BATTERY_VOLTAGE = 23

TOP_THRESHOLD_BATTERY_VOLTAGE = 24

BOTTOM_TIME_TO_CHECK = 5

TOP_TIME_TO_CHECK = 19

INIT_ACCUMULATED_PV_POWER_LOW_KEY = 'INIT_ACC_PV_PLK'

END_ACCUMULATED_PV_POWER_LOW_KEY = 'END_ACC_PV_PLK'

FAN_THRESHOLD_DEFAULT_VALUE = 30.0

BATTERY_CHARGE_CHECK_INTERVAL = 60

EPEVER_BATTERY_PARAMS_CHECK_INTERVAL = 300

INVERSOR_CHECK_INTERVAL = 300

PING_CHECK_INTERVAL = 60

WIFI_RECONNECT_INTERVAL = 10

# OrangePi Pins

RX = 5 # Port PC6
TX = 7 # Port PC5

ALERT_ESP = 6 # Port PC 11

RESET_EXPANDER = 2 # Port PC 9 
CABINET = 15       # Port PH 9
INTERRUPT1 = 16    # Port PC 10 Interrupt Expander
INTERRUPT2 = 14    # Port PH 6 Interrupt Expander

## Side panel

GREEN_LED = 11 # Port PH 7
RED_LED = 12   # Port PH 8
BLUE_LED = 13  # Port PC 7
CHASIS = 9     # Port PC 15
SOFTWARE_BUTTON = 10 # Port PC 14
HARDWARE_BUTTON = 8 # Port PC 8

# Expander Pins

GPA0, GPA1, GPA2, GPA3, GPA4, GPA5, GPA6, GPA7 = 0, 1, 2, 3, 4, 5, 6, 7
GPB0, GPB1, GPB2, GPB3, GPB4, GPB5, GPB6, GPB7 = 8, 9, 10, 11, 12, 13, 14, 15

ALL_GPIO = [GPA0, GPA1, GPA2, GPA3, GPA4, GPA5, GPA6, GPA7, GPB0, GPB1, GPB2, GPB3, GPB4, GPB5, GPB6, GPB7]

TIMEZONE = "America/Guatemala"