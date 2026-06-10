#IMPORTANT: Use pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time

class MustModVoltages:
    client = None

    @classmethod
    def connect(cls, serial_ports):
        """To make the connection with the port"""
        for port in serial_ports:
            try:
                path = port
                cls.client = ModbusClient(method='rtu', port=path, baudrate=9600, timeout=1)
                cls.client.connect()
                time.sleep(2)
                if cls.client.is_socket_open():  # Check if connection is successful
                    return True, port
            except Exception as e:
                print(f"Error connecting to {port}: {e}")
        
        return False, None

    @classmethod
    def modifyVoltages(cls, BatteryFloatVoltage, BatteryAbsorptionVoltage):
        """To change the parameters"""
        try:
            write = cls.client.write_registers(address=0x2777, values=[BatteryFloatVoltage, BatteryAbsorptionVoltage], count=2, unit=1)
            print(f"Write result: {write}")
            time.sleep(1)
            read = cls.client.read_holding_registers(address=0x2777, count=2, unit=1)
            print(f"New float voltage and abpsorption voltage: {read.registers}")
        except Exception as error:
            print(f"Error modifying voltages: {error}")
        finally:
            cls.client.close()

# The serial ports to try:
serial_ports = [f'/dev/ttyUSB{i}' for i in range(4)] + [f'/dev/ttyS{i}' for i in range(4)]
modifier = MustModVoltages()
success, port = modifier.connect(serial_ports)
if success:
    print(f"Connected successfully to port: {port}")
    modifier.modifyVoltages(288, 292)
else:
    print("Failed to connect to any serial port.")