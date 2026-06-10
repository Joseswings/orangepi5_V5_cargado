import os
from dotenv import load_dotenv
from services.loggers import logger

class ENV:

    # Create the Singleton
    def __new__(cls): return cls
    
    @staticmethod
    def get_env_value(value):
        """ Get value from environment, if value does not exists then raise exception """
        try: return os.environ.get(value)

        except KeyError as key: raise Exception(f'Could not get {key} from .env file')
        except Exception as error: 
            logger.log({"Get Env value":str(error)}, logger.level.ERROR, "env", True)
            return None

    # Load .env file to os.environment
    load_dotenv()

    # ThingsBoard config values
    THINGSBOARD_DEVICE_TOKEN= get_env_value('7iLUre7NX9lVluJrQKWr')
    THINGSBOARD_HTTP_HOST= get_env_value('http://142.93.240.174:8080')

    ANTSTACK_HTTP_HOST=get_env_value("ANTSTACK_HTTP_HOST")
    ANTSTACK_HTTP_USER=get_env_value("ANTSTACK_HTTP_USER")
    ANTSTACK_HTTP_PASSWORD=get_env_value("ANTSTACK_HTTP_PASSWORD")

    # Mikrotik Authentication
    MIKROTIK_USER = get_env_value('MIKROTIK_USER')
    MIKROTIK_PASSWORD = get_env_value('MIKROTIK_PASSWORD')
    MIKROTIK_IP = get_env_value('MIKROTIK_IP')
    MIKROTIK_PORT = get_env_value('MIKROTIK_PORT')

    # Contact information
    LOCATION = get_env_value('LOCATION')
    SHOPKEEPER_PHONE = get_env_value('SHOPKEEPER_PHONE')

    # Send WA notifications
    WA_NOTIFICATIONS = get_env_value('WA_NOTIFICATIONS')

    # Battery profile
    BATTERY_TYPE = get_env_value('BATTERY_TYPE')

    # Starlink auth
    STARLINK_HOST = get_env_value('STARLINK_HOST')
    STARLINK_ID = get_env_value('STARLINK_ID')
    STARLINK_SECRET = get_env_value('STARLINK_SECRET')

# Export the Singleton
env = ENV()
