import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.usb_controller import USB_Serial
usb = USB_Serial
usb.detect_serial_devices()

controller, type_controller = usb.get_solar_controller()
data = controller.readRegisterBlock("RealTimeData")

columns = 4
counter = 0

for key in data.keys():
    if (counter % columns) == 0:
        print(key,": ", data[key], end="")
    elif (counter % columns) == (columns - 1):
        print(" | ", key,": ", data[key], end="\n")
    else:
        print(" | ", key,": ", data[key], end="")
    counter += 1
print("")