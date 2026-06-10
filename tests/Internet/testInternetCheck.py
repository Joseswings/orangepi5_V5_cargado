import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.scheduled_tasks import internet_check
from time import sleep

while True:
    try:
        internet_check()
        sleep(10)
    except Exception as error:
        print(error)
        sleep(1)