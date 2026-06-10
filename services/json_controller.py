import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
import ijson
import threading
import datetime
from time import sleep
from services.http_service import http
from services.helpers import getPrevDate, getActualDate, get_unix_timestamp
from services.loggers import logger


BASE_DIR = str(Path(__file__).resolve().parent.parent)
JSON_DIR = "".join([BASE_DIR, '/docs/temp/'])

MODULE = "json"

def check_file_exists(file_name:str):
    try: 
        file = open(file_name,"r",encoding="utf8")
        file.close()
    except:
        # If file not exist, create a new file with an empty dict
        file = open(file_name,"a+",encoding="utf8")
        file.write(json.dumps({}))
        file.close()
        module_name = file_name.split("/")[-1]
        logger.log(f"{module_name} file created")


def write_json_file(file_name:str, json_data:dict, function_name):
    try:

        if type(json_data) is not dict: raise TypeError(f"Got non Json object from {function_name} function")

        file = open(file_name,"w",encoding="utf8")
        file.write(json.dumps(json_data, indent=2, ensure_ascii=False))
        file.close()
    
    except TypeError as error: 
        
        file = open(file_name,"w",encoding="utf8")
        file.write(json.dumps({}, indent=2, ensure_ascii=False))
        file.close()

        raise Exception(error)
    
    except Exception as error:  logger.log({"Write Json file":str(error)}, logger.level.ERROR, MODULE, True)


def get_big_json(file_name:str):
    try:

        with open(file_name, 'rb') as file:
            # Use ijson to read a big json file, extract the data and close the file
            for item in ijson.items(file, "", use_float=True): data:dict = item
            file.close()
        
    # If Json file got blank, start with a new empty dict
    except ijson.common.IncompleteJSONError: 
        data = {}
        write_json_file(file_name, data, "Get big json")
        logger.log({"Read big Json file":" ".join(["EOF found error on", file_name.split("/")[-1], "file"])}, logger.level.ERROR, MODULE, True)

    except Exception as error:
        data = {}
        logger.log({"Read big Json file":str(error)}, logger.level.ERROR, MODULE, True)
        
    finally: return data


def save_data_in_json(payload:object, name:str)->bool:
    """Function to save values in a json file under the docs/temp/ directory

    Args:
        payload (object): Data to add into the today's data
        name (str): Name of the file

    Returns:
        bool: State of the operation
    """

    file_name = "".join([JSON_DIR, name,'.json'])
    check_file_exists(file_name)

    try:
        # Try read the file, in case it not exist the exception raise
        with open(file_name,"r+",encoding="utf8") as file:
            
            # Load the json and add the last value
            data = json.load(file)
            try:
                # Try to check if data of today exist and merge the new json info
                data[str(getActualDate())].update(payload)
            except:
                # If data doesn't exists add the new key-value
                data[str(getActualDate())] = payload

            #After reading the data, overwrite the existing json
            file = open(file_name,"w",encoding="utf8")
            file.write(json.dumps(data,indent=2))
            file.close()
        return True
    
    except Exception as error:
        logger.log({"Save in Json":str(error)}, logger.level.ERROR, MODULE, True)
        return False


def read_data_in_json(name:str, date:str)->dict|None:
    """Function to get values in a json file under the docs/temp/ directory

    Args:
        name (str): Name of the file
        date (str): Data of 'Actual' or 'Prev' day

    Returns:
        _type_: Json with the data of date selected
    """
    
    file_name = "".join([ JSON_DIR, name, '.json'])
    check_file_exists(file_name)

    try:
        with open(file_name,"r+",encoding="utf8") as file:
            # Obtain the json from the file and close the file
            data = json.load(file)
            file.close()
            
        match date:
            case "Actual": date = getActualDate()
            case "Prev":   date = getPrevDate()
        
        # Check if date key exists in json
        if date not in data: return None
        
        date_json = data[date]
        return date_json
    
    except Exception as error: 
        logger.log({"Read data Json":str(error)}, logger.level.ERROR, MODULE, True)
        return None



def send_telemetry_thingsboard(payload:object, name:str, inversor_down:bool = False):
    """Function to manage send or save the data from stations"""
    try:

        payload = {"ts":get_unix_timestamp(), "values":payload}
        
        if not inversor_down:
            # Send first actual telemetry and then send the pending telemetry
            if http.thingsboard_post_request(payload, topic=name): 
                send_saved_telemetry(name)
                return

        save_telemetry(payload,name)

    except Exception as error: logger.log({"Send telemetry":str(error)}, logger.level.ERROR, MODULE, True)


def send_saved_telemetry(name:str)->bool:
    """Function to call before send the actual telemetry to thingsboard"""
    try:
        file_name = "".join([JSON_DIR, 'telemetry.json'])
        check_file_exists(file_name)

        # Open the JSON file
        data = get_big_json(file_name)

        # Check if there is data to be sent
        if name not in data: return True
            
        # List for the telemetry that couldn't be sent
        not_sent:list = []
        threads:list = []

        def thread_send_telemetry(telemetry:dict):
            
            done = http.thingsboard_post_request(telemetry, topic=name, log_action=False)
            
            if not done: 
                not_sent.extend([telemetry])
                return
            
            collection_type = "_".join(["telemetry",name]).replace(" data","").replace(" ","_")
            http.antstack_post_request(collection_type.lower(), telemetry, log_action=False)


        # For each element try to send the telemetry, if an error ocurrs
        for telemetry in data[name]:
            thread = threading.Thread(target=thread_send_telemetry,  kwargs={"telemetry":telemetry})
            threads.append(thread)
            thread.start()
            sleep(0.01)

        # Variable to check if there is pending telemetry to be sent
        all_sent:bool = len(not_sent) < 1

        data[name] = not_sent
    
        #After reading the data, overwrite the existing json
        write_json_file(file_name, data, function_name="Send saved telemetry")
        
        return all_sent

    except Exception as error: 
        logger.log({"Send saved telemetry":str(error)}, logger.level.ERROR, MODULE, False)
        return False


def save_telemetry(payload:object, name:str):
    """Function to save last telemetry in case if not able to send it to ThingsBoard"""

    file_name = "".join([JSON_DIR, 'telemetry.json'])
    check_file_exists(file_name)
    
    try:
        # Open the JSON file
        data = get_big_json(file_name)
            
        # Load the json to overwrite and add the last value
        if name not in data.keys(): data[name] = []
        data[name].extend([payload])

        #After reading the data, overwrite the existing json
        write_json_file(file_name, data, function_name="Save telemetry in Json")
        
        return True

    except Exception as error: 
        
        logger.log({"Save telemetry in Json":str(error)}, logger.level.ERROR, MODULE, True)
        return False


def send_saved_errors()->bool:
    """Function to send saved errors to AntStack when restoring internet connection"""
    try:

        # List for the telemetry that couldn't be sent
        not_sent:list = []

        def thread_send_error(collection_type:str,  error_data:dict):
            
            done = http.antstack_post_request(collection_type, error_data, log_action=False)
            if not done: 
                not_sent.extend([error_data])
                return


        file_name = "".join([JSON_DIR, 'errors.json'])
        check_file_exists(file_name)

        all_sent:bool = True

        # Open the JSON file
        data = get_big_json(file_name)

        # Send all saved errors by collection type
        for collection_type in data.keys():

            # Create a list for the threads
            threads:list = []

            # For each element try to send the telemetry, if an error ocurrs
            for error_data in data[collection_type]:
                thread = threading.Thread(target=thread_send_error,  kwargs={"collection_type":collection_type, "error_data":error_data})
                threads.append(thread)
                thread.start()
                sleep(0.01)
            
            # Join all the threads before next iteration
            for thread in threads: thread.join()

            # Variable to check if there is pending telemetry to be sent
            if all_sent: all_sent = len(not_sent) < 1

            # Overwrite the list with only the pending data to be sent and clean the list for the next iteration
            data[collection_type] = not_sent
            not_sent = []
    
        #After reading the data, overwrite the existing json
        write_json_file(file_name, data, function_name="Send saved errors")
        
        return all_sent
    
    except Exception as error: 
        logger.log({"Send saved errors":str(error)}, logger.level.ERROR, MODULE, False)
        return False


def save_error(collection_type:str, error_data:dict)->bool:
    """Function to save errors in case there is no internet connection"""

    file_name = "".join([JSON_DIR, 'errors.json'])
    check_file_exists(file_name)
    
    try:

        # Open the JSON file
        data = get_big_json(file_name)
            
        # Load the json to overwrite and add the last value
        if collection_type not in data.keys(): data[collection_type] = []
        
        # Add timestamp to the saved error
        error_data["timestamp"] = str(datetime.datetime.now())
        data[collection_type].append(error_data)

        #After reading the data, overwrite the existing json
        write_json_file(file_name, data, function_name="Save error in Json")
        
        return True

    except Exception as error: 
        logger.log({"Save error in Json":str(error)}, logger.level.ERROR, MODULE, True)
        return False