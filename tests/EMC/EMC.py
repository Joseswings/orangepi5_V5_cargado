import smbus
import time

# EMC2302 address
ADDRESS = 0x2e

# Initialize I2C bus
bus = smbus.SMBus(3)

# Set fan speed (in RPM)
def set_fan_speed(speed):
    # Convert speed to register value
    register_value = int(1350000 / speed)
    #register_value = int(3932160 / speed)
    # Write register value to EMC2302
    bus.write_word_data(ADDRESS, 0x30, register_value)

while(1):
    # Set fan speed to 50% (approximately 1350 RPM)
    print("Velocidad: 1350 RPM (50%)")
    set_fan_speed(1350)

    # Wait for 10 seconds
    time.sleep(10)

    # Set fan speed to 100% (approximately 2700 RPM)
    print("Velocidad: 2700 RPM (100%)")
    set_fan_speed(2700)

    # Wait for 10 seconds
    time.sleep(10)

    # Set fan speed to 1%
    print("Velocidad: 1 RPM (1%)")
    set_fan_speed(1)
    time.sleep(10)

    #set_fan_speed(2700)
