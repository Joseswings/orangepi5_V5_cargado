import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from math import log
from services.ads_controller import ADS
from time import sleep


ads = ADS()

while True:
    try:
        data, state = ads.get_ADS_data()
        if state:
            msg = "".join(["Voltage: ",str(data["Voltage - ADS"]),"V | Temperature: ",str(data["Temperature - ADS"]),"° C"])
            print(msg, end="\n\n")
        sleep(5)
    except KeyboardInterrupt: break
    