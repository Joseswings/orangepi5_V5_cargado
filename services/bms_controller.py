from dalybms import DalyBMS
from services.usb_controller import USB_Serial
from services.helpers import executeScript
from services.loggers import logger

class BMS:

    # Name of the file for log specific errors
    MODULE="bms"

    bms = DalyBMS()

    _apply_config = True

    def __new__(cls):
        if not cls._apply_config: return cls

        usb = USB_Serial()
        devices = usb.get_devices()

        for device in devices:
            try:
                path = "/dev/" + device
                
                cls.bms.connect(path)

                # Call status before any operation
                cls.bms.status
                cls.bms.get_status()
                
                soc = cls.get_soc_percent(log_action=False)
                if isinstance(soc,(type(None), bool)): continue

                usb.remove_device(device,"BMS")
                cls._apply_config = False
                break
            except Exception: continue

        return cls
    
    # Test method
    @classmethod
    def test_bms(cls) -> bool:
        try:
            usb = USB_Serial()

            # Exit if device is not configured
            if usb.devices["BMS"] is None: return False

            # Check the conection with the BMS
            soc = cls.get_soc_percent(log_action=False)
            if isinstance(soc, (type(None), bool)): raise IOError("Device lost connection")

            return True
        
        except IOError as error:
            logger.log({"Test BMS":str(error)}, logger.level.WARNING)
            usb.clean_device("BMS")
            cls._apply_config = True
            executeScript("usbreset 002/002")
            return False

        except Exception as error: 
            logger.log({"Test BMS":str(error)}, logger.level.ERROR)
            return False
            
    # Voltage
    @classmethod
    def get_voltage(cls) -> float:
        try:
            data = cls.bms.get_soc()
            voltage = data["total_voltage"]
            return voltage
        except Exception as error: 
            logger.log({"Get SoC voltage":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
    
    # Current
    @classmethod
    def get_current(cls)-> float:
        try:
            data = cls.bms.get_soc()
            current = data["current"]
            return current
        except Exception as error: 
            logger.log({"Get SoC current":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
    
    # State of charge percent
    @classmethod
    def get_soc_percent(cls, log_action:bool = True):
        try:
            data = cls.bms.get_soc()
            soc_percent = data["soc_percent"]
            return soc_percent
        
        except Exception as error: 
            if log_action: logger.log({"Get SoC percent":str(error)}, logger.level.ERROR, cls.MODULE, True)
            cls._apply_config = True
            return None
    
    # Cycles
    @classmethod
    def get_cycles(cls):
        try:
            data = cls.bms.get_status()
            cycles = data["cycles"]
            return cycles
        except Exception as error: 
            logger.log({"Get SoC cycles":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
        
    @classmethod
    def get_all_data(cls)->tuple[float, float, float, float]:
        """Function to get the main values from BMS

        Returns:
            tuple[float, float, float, float]: SoC, Voltage, Current and Cylcles values
        """
        try:
            soc_data = cls.bms.get_soc()
            if isinstance(soc_data, (type(None), bool)): return None, None, None, None
            
            status   = cls.bms.get_status()
            
            soc_percent = soc_data["soc_percent"]
            current     = soc_data["current"]
            voltage     = soc_data["total_voltage"]
            cycles      = status["cycles"]
            
            return soc_percent, voltage, current, cycles
        except Exception as error: 
            logger.log({"Get SoC all data":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None, None, None, None
    
    @classmethod
    def get_temperatures(cls)->dict:
        """Function to get the actual, the highest and the lowest temperature of the battery

        Returns:
            dict: Json object
        """
        try:
            ranges = cls.bms.get_temperature_range()
            temps  = cls.bms.get_temperatures()

            if not isinstance(ranges, dict) or not isinstance(temps, dict): return None
            
            temps_json = {}
            
            temps_json["highest_temperature"] = ranges["highest_temperature"]
            temps_json["lowest_temperature"]  = ranges["lowest_temperature"]
            
            for sensor in temps.keys():
                temp_key = "temperature_sensor_" + str(sensor)
                temps_json[temp_key] = temps[sensor]
            
            return temps_json
        except Exception as error: 
            logger.log({"Get SoC temperatures":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
        
    @classmethod
    def set_soc(cls, new_soc:float)->bool:
        """Function to modify the SoC of the battery

        Args:
            new_soc (int): New value of the SoC

        Returns:
            bool: State of the operation
        """
        try:
            new_soc = round(new_soc, 1)

            match new_soc:
                case _ if 0.0 <= new_soc <= 100.0: cls.bms.set_soc(new_soc)
                case _: raise Exception("No valid SoC value")
        
        except Exception as error: 
            logger.log({"Set SoC":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
    
    @classmethod  
    def get_BMS_data(cls)->tuple[dict|None,bool]:
        """Function to get data from the battery and save it into a Json

        Raises:
            Exception: BMS not detected

        Returns:
            dict: Json object with the values from BMS
            bool: State of the operation
        """
        try:
            #Get all the values and save it into a json
            soc_percent, voltage_bms, current_bms, cycles_bms  = cls.get_all_data()
            if soc_percent is None: return None, False

            data_json = {
                "SOC":soc_percent,
                "Voltage - BMS":voltage_bms,
                "Current - BMS":current_bms,
                "Cycles - BMS": cycles_bms
            }
            
            try:
                temps_json = cls.get_temperatures()
                data_json.update(temps_json)
            except Exception: pass
            
            return data_json, True

        except Exception as error:
            logger.log({"Get Json BMS data":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None, False
    

    @classmethod  
    def get_unified_telemetry(self) -> dict:
        """Devuelve un diccionario con el SoC y Voltaje formateados para ThingsBoard"""
        telemetry = {}
        try:
            soc_percent = self.get_soc_percent()
            if soc_percent is not None:
                telemetry["SOC - BMS"] = float(soc_percent)
                
            # Extraemos el voltaje usando el método nativo si existe, 
            # o desde los datos crudos del objeto bms interno
            if hasattr(self, 'get_voltage'):
                telemetry["Voltage - BMS"] = float(self.get_voltage())
            elif hasattr(self, 'bms') and hasattr(self.bms, 'get_soc'):
                data = self.bms.get_soc()
                if data and "total_voltage" in data:
                    telemetry["Voltage - BMS"] = float(data["total_voltage"])
        except Exception as e:
            print(f"[BMS Service Error]: {e}")
        return telemetry
        