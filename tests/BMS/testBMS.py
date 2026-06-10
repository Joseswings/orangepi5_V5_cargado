import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.bms_controller import BMS
from time import sleep

bms = BMS()
print(end="\n")

while True:
    try:
        data, state = bms.get_BMS_data()
        if not state: 
            sleep(5)
            continue
        
        counter = 0
        for key in data.keys():
            msg = "".join([key,": ", str(data[key])])
            match counter % 2:
                case 0: print(msg, end=" ")
                case 1: print(" | ", msg, end="\n")
            counter += 1
    
        print(end="\n\n")
        sleep(5)   
    
    except KeyboardInterrupt: break        
        

