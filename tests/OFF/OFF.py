import sys
import wiringpi
from wiringpi import GPIO

INTERRUPT1 = 16    # Port PC10 Interrupt Expander
INTERRUPT2 = 14    # Port PH6 Interrupt Expander
RESET_EXPANDER = 2 # Port PC9 

wiringpi.wiringPiSetup()
wiringpi.pinMode(INTERRUPT1, GPIO.OUTPUT)
wiringpi.pinMode(INTERRUPT2, GPIO.OUTPUT)
wiringpi.pinMode(RESET_EXPANDER, GPIO.OUTPUT)

wiringpi.digitalWrite(INTERRUPT1, GPIO.LOW)
wiringpi.digitalWrite(INTERRUPT2, GPIO.LOW)
wiringpi.digitalWrite(RESET_EXPANDER, GPIO.LOW)

sys.exit('Programa ejecutado.')


