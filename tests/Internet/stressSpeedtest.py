import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.internet_check import checkInterfaceSpeedtest
from time import sleep

while True:
    try:
        checkInterfaceSpeedtest("eth0")
        checkInterfaceSpeedtest("wlan0")
        sleep(30)
    except Exception as error:
        print(error)