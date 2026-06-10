import serial
from time import sleep

client = serial.Serial('/dev/ttyUSB0', 2400)

command = 'Q1<cr>\r\n'

client.write(bytearray(command,'ascii'))
print(f'Serial: command {command} sent')

query_format = "(MMM.M NNN.N PPP.P QQQ RR.R S.SS TT.T 76543210"

while 1:
    try:
        data = client.read(len(query_format))
        print(data)
        sleep(0.5)

    except KeyboardInterrupt: break
    except Exception as error: print(error)
