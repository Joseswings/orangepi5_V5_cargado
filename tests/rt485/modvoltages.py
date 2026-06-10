#IMPORTANT: Use pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time

client = ModbusClient(method='rtu', port='/dev/ttyS5', baudrate=9600, timeout=1)

client.connect()
time.sleep(2)
#write = client.write_register(address=0x2777,value=138)
write = client.write_registers(address=0x2777,values=[146,138],count=2,unit=1)
print(write)
time.sleep(1)
read=client.read_holding_registers(address = 0x2777, count =2, unit=1) #address>
print(read)
print(type(read))
data=read.registers #read register all register
print(data) #print register data

