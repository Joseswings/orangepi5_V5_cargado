import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.inversor_controller import Inversor
from time import sleep

inversor = Inversor()
print(end="\n")

while True:
    try:
        data, state = inversor.get_inversor_data()
        if not state: 
            sleep(5)
            
            # If Inversor got disconnected, obtain again the instance configured
            if not inversor.test_inversor(): inversor = Inversor()
            
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