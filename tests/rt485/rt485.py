#IMPORTANT: Use pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time

client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)

client.connect()
time.sleep(2)
read=client.read_holding_registers(address = 0x311A, count =1, unit=1) #address to start the lecture, count is used to determinate the number of the register 

data=read.registers #read register all register 
print(data) #print register data
