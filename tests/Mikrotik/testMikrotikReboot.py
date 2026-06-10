import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.mikrotik_controller import Mikrotik

controller = Mikrotik()
controller.reboot()