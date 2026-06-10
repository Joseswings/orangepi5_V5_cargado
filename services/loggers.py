import os
import sys
import logging
from pathlib import Path
from collections import namedtuple
from logging.handlers import TimedRotatingFileHandler


class Logger:

    log_enabled:bool = True
    logger = None

    _apply_config = True

    Levels = namedtuple("Levels",["INFO", "ERROR", "WARNING", "CRITICAL", "DEBUG"])
    level = Levels(
        INFO=logging.INFO, 
        ERROR=logging.ERROR,
        WARNING=logging.WARNING, 
        CRITICAL=logging.CRITICAL, 
        DEBUG=logging.DEBUG
    )

    def __new__(cls): 

        if not cls._apply_config: return cls

        # Build paths inside the project like this: BASE_DIR / 'subdir'.
        BASE_DIR = Path(__file__).resolve().parent.parent
        LOGGING_DIR = os.path.join(BASE_DIR, 'logs') 

        log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

        cls.logger = logging.getLogger('main')
        cls.logger.setLevel(cls.level.INFO)
        
        log_main_handler = TimedRotatingFileHandler(os.path.join(LOGGING_DIR, 'run.log'), when="midnight", interval=1, backupCount=10)
        log_main_handler.setFormatter(log_format)
        log_main_handler.namer = lambda name: name.replace(".log", "") + ".log"
        
        log_main_stream_handler = logging.StreamHandler(sys.stdout)
        log_main_stream_handler.setFormatter(log_format)
        
        cls.logger.addHandler(log_main_handler)
        cls.logger.addHandler(log_main_stream_handler)
        
        cls.apply_config = False
        
        return cls

    @classmethod
    def set_enabled_logging(cls, enable:bool): cls.log_enabled = enable

    
    @classmethod
    def log(cls, data:str|dict, log_level:int = level.INFO, module_name:str = None,  post_error:bool = False):
        try:
            if not cls.log_enabled: return
            match log_level:
                case cls.level.ERROR:    cls.log_error(module_name, data, post_error)
                case cls.level.INFO:     cls.logger.info(data)
                case cls.level.WARNING:  cls.logger.warning(data)
                case cls.level.CRITICAL: cls.logger.critical(data)
                case cls.level.DEBUG:    cls.logger.debug(data)
                case _: cls.logger.error("Log level does not exists")
        
        except Exception as error: cls.logger.error(str(error))

    @classmethod
    def log_error(cls, module_name:str = None, error_data:dict = None, post_error:bool = False):

        cls.logger.error(error_data)
        if not post_error: return

        # Import inside function to avoid circular reference
        from services.http_service import http
        
        collection_type = "_".join(["error",module_name])
        done = http.antstack_post_request(collection_type=collection_type, data=error_data)
        
        if not done: 
            from services.json_controller import save_error
            save_error(collection_type, error_data)
            return


logger = Logger()
