import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.ina_sensors import INA_Sensors
from time import sleep

while True:
    try:
        print("")

        ina_controller = INA_Sensors()
        data_json = ina_controller.get_all()

        counter = 0
        for key in data_json.keys(): 

            msg = " ".join([key, str(data_json[key])])

            match key:
                case _ if "Voltage" in key: " ".join([msg,"V"])
                case _ if "Current" in key: " ".join([msg,"mA"])

            match counter:
                case _ if counter % 2 == 0: print(msg, end=" | ")
                case _ if counter % 2 == 1: print(msg, end="\n")
            
            counter += 1
        
        sleep(2)
    
    except KeyboardInterrupt: break