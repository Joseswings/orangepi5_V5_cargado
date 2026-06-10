import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.bms_controller import BMS

new_soc = 100

bms = BMS()
bms.set_soc(new_soc)