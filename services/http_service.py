import requests
import schedule
import socket

from time import sleep
from env_config import env
from services.helpers import get_datetime_with_ms
from services.loggers import logger


class HTTP:

    MODULE = "http"

    __antstack_token = None


    def __new__(cls):
       # cls.__update_antstack_token()
       pass
        return cls
    
    @classmethod
    def http_request(cls, url:str, domain_name:str, headers:dict, payload:dict, method:str = "post", log_action:bool = True):
        try:

            response = None
            tries = 2

            while tries > 0:

                try:
                    match method.lower():
                        case "get":  response = requests.get(url=url,  headers=headers, timeout=5)
                        case "post": response = requests.post(url=url, headers=headers, timeout=5, json=payload)
                        case _: raise Exception("Invalid http method")
                except requests.exceptions.Timeout: response = None
                
                # Check if the request was made or continue trying
                if response is not None: break
                tries -=1

            # If after all tries res still none raise the failure
            if response is None: raise Exception(f"Http request failed to {domain_name}")
            return response
        
        except Exception as error: 
            if log_action: logger.log({"HTTP request":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None



    @classmethod
    def check_status_code(cls, status_code:int, request_name:str, log_action:bool = True):
        try:
            log_msg = " ".join([request_name, "request with status:", str(status_code)])

            match status_code:
                case 200: 
                    if log_action: logger.log(log_msg)
                    return True
                
                case _ if status_code >= 500: log_level = logger.level.WARNING
                case _ if status_code >= 400: log_level = logger.level.ERROR
                case _:  log_level = logger.level.WARNING

            if log_action: logger.log(log_msg, log_level)
            return False
        
        except Exception as error: logger.log({"Check status code":str(error)}, logger.level.ERROR, cls.MODULE, True)
    

    @classmethod
    def __get_antstack_token(cls)->str|None:
        return cls.__antstack_token \
            if cls.__antstack_token is not None \
            else cls.__update_antstack_token()

    @classmethod
    def __update_antstack_token(cls)->str|None:
        try:
            
            payload = {
                "dpi":env.ANTSTACK_HTTP_USER, 
                "password":env.ANTSTACK_HTTP_PASSWORD
            }

            url = "{host}//hardware/settings/customer/login".format(host=env.ANTSTACK_HTTP_HOST)
            headers = {"Content-Type":"application/json"}

            response = cls.http_request(url=url, domain_name="AntStack", headers=headers, payload=payload)
            if response is None: return None
            if not cls.check_status_code(response.status_code, request_name="AntStack Login", log_action=False): return None
            
            data = response.json()["data"]
            cls.__antstack_token = data["token"]

            return cls.__antstack_token
    
        except Exception as error:
            logger.log({"AntStack Http post failed":str(error)}, logger.level.ERROR)
            return False
        

    @classmethod
    def antstack_post_request(cls, collection_type:str, data:object, log_action:bool = True):
        """An HTTP request to send data to AntStack

        Args:
            payload (object): Json object with the telemetry or error info to upload
            topic (str, optional): Add info to the logger about the uploaded data. Defaults to None.

        Raises:
            Exception: Checks if response is None

        Returns:
            bool: State of the operation
        """
        try:

            token = cls.__get_antstack_token()
            if token is None: raise Exception("Not available token")

            url = "{host}/hardware/general/collection".format(host=env.ANTSTACK_HTTP_HOST)
            headers = {
                "Content-Type": "application/json",
                "token": token
            }

            collection = "_".join(["v5",collection_type])
            documentRef = "-".join([socket.gethostname(), get_datetime_with_ms()])

            payload = {
                "collection": collection,
                "documentRef":documentRef,
                "data": data
            }

            response = cls.http_request(url, "AntStack", headers, payload, log_action=log_action)
            if response is None: return False

            # Refresh token if request was unauthorized
            if response.status_code == 401: 
                headers["token"] = cls.__update_antstack_token()
                
                # Check again if the token is available
                if headers["token"] is None: raise Exception("Unable to refresh token")
                
                response = cls.http_request(url, "AntStack", headers, payload, log_action=log_action)

            request_name = " ".join(["AntStack", collection_type])
            return cls.check_status_code(response.status_code, request_name=request_name, log_action=log_action)
    
        except Exception as error:
            logger.log({"AntStack Http post":str(error)}, logger.level.ERROR)
            return False
        
    
    @classmethod
    def thingsboard_post_request(cls, payload:object, topic:str = None, log_action:bool = True)->bool:
        """An HTTP request to update the device in ThingsBoard

        Args:
            payload (object): Json object with the telemetry to upload
            topic (str, optional): Add info to the logger about the uploaded data. Defaults to None.

        Raises:
            Exception: Checks if response is None

        Returns:
            bool: State of the operation
        """
        
        try:

            url = "{host}/api/v1/{token}/telemetry".format(host=env.THINGSBOARD_HTTP_HOST, token=env.THINGSBOARD_DEVICE_TOKEN)
            headers = {"Content-Type": "application/json"}
            domain_name = "ThingsBoard"
        
            response = cls.http_request(url, domain_name, headers, payload, log_action=log_action)
            if response is None: return False

            request_name = " ".join([domain_name, topic, "telemetry"])
            return cls.check_status_code(response.status_code, request_name=request_name, log_action=log_action)

        except Exception as error:
            logger.log({"ThingsBoard Http post":str(error)}, logger.level.ERROR, MODULE, True)
            return False


http = HTTP()

# Name of the file for log specific errors
MODULE = "http"

def check_status_code(status_code:int, log_msg:str, log_action:bool = True):

    match status_code:
        case 200: 
            if log_action: logger.log(log_msg)
            return True
        
        case _ if status_code >= 500: log_level = logger.level.WARNING
        case _ if status_code >= 400: log_level = logger.level.ERROR
        case _:  log_level = logger.level.WARNING

    if log_action: logger.log(log_msg, log_level)
    return False

      
def whatsapp_post_request(payload:object):
    """ An HTTP request to send a message to whatsapp"""
    url = "http://143.244.179.211:5000/enviar-mensaje"
    headers = {"Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    req = None

    try:
        while status >= 400 and attempts <= 5:
            try: 
                req = requests.post(url=url, headers=headers, json=payload)
                status = req.status_code
            except Exception: pass
            
            attempts += 1
            sleep(10)

        if req is None: raise Exception("Could not send data to WA server")

        log_msg:str = f'WhatsApp HTTP request response {req.status_code}'

        return check_status_code(status, log_msg)
    
    except Exception as error:
        logger.log({"WhatsApp Http post failed":str(error)}, logger.level.ERROR, MODULE, True)
        return False
    
def send_notification_whatsapp(action:str, init_time:str = None):
    """Function to send notifications to WhatsApp by defined messages depending on the action key

    Args:
        action (str): Type of message 
        init_time (float, optional): Add info to the message . Defaults to None.
    """
    try:
        if int(env.WA_NOTIFICATIONS) == True:
            info = {
                "critical":"se apagará por llegar al nivel de carga por debajo del 25%",
                "warning":"se apagará pronto por llegar al nivel de carga por debajo del 30%",
                "restore_charge":"ha restaurado el sistema por llegar al nivel de carga por encima del 40%",
                "shutdown_schedule":"se apagará el sistema por programación para preservar energía",
                "restore_schedule":"ha restaurado el sistema por programación",
                "shutdown_default":"se apagará el sistema por programación default",
                "restore_default":"ha restaurado el sistema por programación default",
                "starlink_default":"ha detectado una conexión a un Starlink con configuración de fábrica",
                "battery_damaged":"ha detectado una batería dañada marcando un voltage menor a 24V",
                "voltage_mismatch":"ha detectado una batería con un offset entre voltaje y SoC",
            }

            if init_time is not None: info["shutdown_schedule"] = "".join([info["shutdown_schedule"]," a las ",init_time]) 

            shopkeeper_phone = "".join(["502" , env.SHOPKEEPER_PHONE,"@s.whatsapp.net"])
            message = "".join(["Hola, este es un aviso automático de que su equipo KingoNet ubicado en *",env.LOCATION,"* ",info[action] ])

            try:
                group_json = {"numero":"120363216426546506@g.us", "mensaje":message}
                
                if whatsapp_post_request(group_json): logger.log("".join([action," whatsapp notification sent to group"]))
                else: raise Exception("Unable to send whatsapp notification to group")
            
            except Exception as error: logger.log({"WA group notification":str(error)}, logger.level.ERROR, MODULE, True)
            
            try:
                shopkeeper_json = {"numero":shopkeeper_phone, "mensaje":message}
                if whatsapp_post_request(shopkeeper_json): logger.log("".join([action," whatsapp notification sent to shopkeeper"]))
            except Exception: pass

    except Exception as error: logger.log({"WhatsApp send notification":str(error)}, logger.level.ERROR, MODULE, True)

def schedule_whatsapp_notification(action:str, init_time:str = None):
    send_notification_whatsapp(action=action,init_time=init_time)
    schedule.clear("".join([action," schedule-whatsapp-notification"]))