import datetime
import calendar
import constants
import subprocess

from dateutil import tz
from services.loggers import logger

MODULE = "helpers"

def executeScript(script:str)->bool:
    try:
        result = subprocess.call([script], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        match result:
            case 0: return True
            case _: return False

    except subprocess.TimeoutExpired: return False
    except TimeoutError: return False
    except Exception as error: 
        logger.log({"Execute on shell":str(error)}, logger.level.ERROR, MODULE, True)
        return False

def get_year()->str:
    year = str(datetime.datetime.now().year)
    return year

# Funciones para obtener la feccha actual y la del dia siguiente en formato YYYY-MM-DD
def getActualDate():
    actualDate = datetime.datetime.today()
    actualDate = str(actualDate.strftime ('%Y-%m-%d'))
    return actualDate

def getNextDate():
    nextDate = datetime.datetime.today() + datetime.timedelta(days=1)
    nextDate = str(nextDate.strftime ('%Y-%m-%d'))
    return nextDate

def getPrevDate():
    prevDate = datetime.datetime.today() - datetime.timedelta(days=1)
    prevDate = str(prevDate.strftime ('%Y-%m-%d'))
    return prevDate

def get_datetime_with_ms():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    return timestamp

def parse_unixts_to_datetime(timestamp:float|str)->str:
    new_timestamp = datetime.datetime.fromtimestamp(float(timestamp)/1000, tz=tz.gettz(constants.TIMEZONE))
    new_timestamp = new_timestamp.strftime('%Y-%m-%d  %H:%M:%S')
    return new_timestamp

def get_unix_timestamp(): 
    timestamp = datetime.datetime.now()
    timestamp = (calendar.timegm(timestamp.timetuple()) + 21600) * 1000
    return str(timestamp)