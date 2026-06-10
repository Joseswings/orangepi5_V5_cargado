# IMPORTANTE: Usa pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import serial.tools.list_ports
import time
from pymodbus.exceptions import ModbusIOException

def find_available_serial_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            client = ModbusClient(method='rtu', port=port.device, baudrate=9600, timeout=1)
            if client.connect():
                # Intentar leer un registro para verificar la conexión
                read = client.read_holding_registers(address=0x0000, count=1, unit=1)
                if not isinstance(read, ModbusIOException):
                    print(f"Successfully connected to port: {port.device}")
                    return client, port.device
                client.close()
        except Exception as e:
            print(f"Failed to connect on port {port.device}: {e}")
    return None, None

client, connected_port = find_available_serial_port()
if client is None:
    raise Exception("No available serial ports for Modbus connection.")

time.sleep(2)

try:
    # Escribir en los registros
    write = client.write_registers(address=0x2777, values=[288, 292], unit=1)
    print(f"Write operation result: {write}")
    time.sleep(1)

    # Leer de los registros
    read = client.read_holding_registers(address=0x2777, count=2, unit=1)
    print(f"Read operation result: {read}")
    print(type(read))

    # Obtener datos de los registros
    if hasattr(read, 'registers'):
        data = read.registers
        print(f"Register data: {data}")  # Imprimir datos de los registros
    else:
        print("Failed to read registers")

except Exception as e:
    print(f"Modbus operation failed: {e}")
finally:
    client.close()
    print(f"Connection to port {connected_port} closed.")