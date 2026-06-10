import schedule


from time import sleep

from services.gpio_expander import GPIOExpander
from services.ads_controller import ADS
from services.bms_controller import BMS
from services.loggers import logger
from services.json_controller import send_telemetry_thingsboard
from services.http_service import schedule_whatsapp_notification, send_notification_whatsapp
from env_config import env 


class BatteryState:
    """Singleton to manage the state of charge of the device
    
    Atributes:
    ----------
        critical (bool) : Check if the battery is in a critical state of charge
        notification_warning (bool) : Check if warning notification already was made
        systems_down (bool) : Means if the device has been turned off due to programation

        charge_check (bool) : In case of reboot or error check if the charge check was done to shedule shutdown and restore

        expander (instance): Controler of the GPIO of the expander
        bms (instance): Controller to obtain data from battery
        
        battery_profiles (dict): Dictionary that stores all the thresholds for all battery types
    
    """

    MODULE = "battery_state"

    critical = False
    notification_warning = False
    systems_down = False

    charge_check = False

    expander = GPIOExpander()
    bms = BMS()
    ads = ADS()
    
    # Define the battery profiles
    battery_profiles = {
        "24V-Lithium":             {"critical":25.5, "warning":25.8, "restore":26.5},
        "24V-Lithium-Redodo":      {"critical":25.5, "warning":26.0, "restore":26.5},
        "24V-Lead-Acid":           {"critical":25.1, "warning":25.5, "restore":25.6},
        "12V-Lithium":             {"critical":13.0, "warning":13.05,"restore":13.1},
        "12V-Lithium-Redodo":      {"critical":10.6, "warning":11.2, "restore":12.5},
        "12V-Lead-Acid":           {"critical":11.5, "warning":11.7, "restore":13.1},
        "12V-Lead-Acid-Autocraft": {"critical":11.25,"warning":11.7, "restore":12.3}, # Caracterización abril 2024
    }
    
    # Get the battery profile, if the env variable was not defined use the 24V lithium as default
    try: 
        b_type = env.BATTERY_TYPE
        if b_type is None: raise Exception
        b_profile = battery_profiles[b_type]
    except Exception: 
        b_type = "24V-Lithium"
        b_profile = battery_profiles[b_type]
    
    # Define the SoC profile
    s_profile = {"critical":25.0, "warning":30.0, "restore":40.0}

    def __new__(cls):
        return cls
    
    @classmethod
    def test_warning(cls):
        """Function to test the warning and turn off the expander"""
        cls.critical = True
        cls.expander.turnAllPinsOff()

    @classmethod
    def save_energy_during_night(cls):
        """Function to turn off the systems, and restore downtime due to programation"""
        cls.systems_down = True
        cls.expander.turnAllPinsOff()
        logger.log("System shutdown")
    
    @classmethod
    def restore_systems(cls):
        """Function to restore the system, reset critical and warning, send WA notification and restore downtime """
        cls.systems_down = False
        cls.critical = False
        cls.notification_warning = False
        cls.expander.turnAllPinsOn()
        logger.log("System restored")

    @classmethod
    def get_system_status(cls)->tuple[bool,bool]:
        """Function to return the state of the system

        Returns:
            tuple[bool,bool]: Returns the state of the system
        """
        return cls.systems_down, cls.critical
    
    @classmethod
    def is_inversor_down(cls)->bool:
        """Function that return the state of the inversor if the system is able to send telemetry due to internet conection

        Returns:
            bool: State of the inversor
        """
        return cls.systems_down or cls.critical

    @classmethod
    def get_charge_check(cls)->bool:
        """Returns internal value charge check

        Returns:
            bool: Indicates if SoC check was made at 6pm
        """
        return cls.charge_check

    @classmethod
    def set_charge_check(cls, state:bool):
        """Private method to change charge check value

        Args:
            state (bool): Indicates if SoC check was made at 6pm
        """
        cls.charge_check = state
        
    @classmethod
    def restore_critical(cls, device:str, restore_value:float,
                         unit:str, rectify:bool = False):
        """Method to handle the restore state

        Args:
            device (str): Name of the device
            restore_value (float): Threshold value
            unit (str): Units of the device
            rectify (bool, optional): Condition to add or omit steps. Defaults to False.
        """
        try:
        
            # Reset variables
            cls.critical = False
            cls.notification_warning = False
            cls.expander.turnAllPinsOn() 
            
            message = "".join([device, " over ", str(restore_value) , unit, " - Systems turned on"])
            if rectify: message += " again"

            logger.log(message)
            
            # If not the first time after critical return
            if rectify: return
        
            # After turn on the pins wait to reconnect internet and send WA notification if value is SoC
            if device == "BMS SOC":
                try:
                    action = "restore_charge"
                    schedule.every(5).minutes.do(schedule_whatsapp_notification, action=action)\
                    .tag("".join([action," schedule-whatsapp-notification"]))
                except Exception as error:
                    logger.log({"WA restore_charge schedule error":str(error)}, logger.level.ERROR)
                        
        except Exception as error:
            logger.log({"Battery State restore critical error":str(error)}, logger.level.ERROR, cls.MODULE, True)
        
        
    
    @classmethod
    def raise_up_critical(cls, device:str, critical_value:float,
                          unit:str, rectify:bool = False )->None:
        """Method to handle the critical state

        Args:
            device (str): Name of the device
            critical_value (float): Threshold value
            unit (str): Units of the device
            rectify (bool, optional): Condition to add or omit steps. Defaults to False.
        """
        try:
            
            # Raise up the critical state and turn off the system and start downtime
            cls.critical = True
            cls.expander.turnAllPinsOff()
            
            message = "".join([device, " under ", str(critical_value), unit," - Systems down"])
            if rectify: message += " again"
            
            logger.log(message, logger.level.WARNING)
        
        except Exception as error:
            logger.log({"Battery State raise critical error":str(error)}, logger.level.ERROR, cls.MODULE, True)
            
    @classmethod
    def raise_up_warning(cls, device:str, warning_value:float, unit:str):
        """Method to handle the warning state

        Args:
            device (str): Name of the device
            warning_value (float): Threshold value
            unit (str): Units of the device
        """
        try:
            message = "".join([device, " under ", str(warning_value), unit])
            logger.log(message, logger.level.WARNING)
            
            # Check if notification was already sent
            if device == "BMS SOC" and not cls.notification_warning:
                cls.notification_warning = True
                send_notification_whatsapp("warning")
                logger.log("warning whatsapp notification send")
            
        except Exception as error:
            logger.log({"Battery State raise critical error":str(error)}, logger.level.ERROR, cls.MODULE, True)

    @classmethod
    def check_values(cls, value:float,device:str, a_value:float = 0)->bool:
        """Check the state of charge of the system to turn off or restore the system and manage the critical state.

        Args:
            value (float): Actual value from the device
            device (str): Name of the device
            a_value (float): Aditional condition

        Returns:
            bool: State of the operation
        """
        try:
            
            # Threshold to turn on the critical state
            critical_t = None
            # Threshold to send a notification of low charge
            warning_t  = None
            # When critical is up, set the limit to restore the system
            restore_t  = None
            
            if value is None: raise Exception("Actual value is None")
            
            # Get the thresholds variables
            match device:
                case "BMS SOC":
                    # Get thresholds from soc profile
                    critical_t, warning_t, restore_t, unit = \
                    cls.s_profile["critical"], cls.s_profile["warning"],cls.s_profile["restore"], "%"
                case "ADS Voltage":
                    # Get thresholds from battery profile
                    critical_t, warning_t, restore_t, unit = \
                    cls.b_profile["critical"], cls.b_profile["warning"],cls.b_profile["restore"], "V"
                case _: raise Exception("Incorrect device")

            # Check the critical state
            if not cls.critical:

                match value:

                    # Case for mismatch between SOC and Voltage
                    case _ if (
                        device == "BMS SOC" and
                        cls.b_type in ["24V-Lithium", "12V-Lithium"]  and
                        value > critical_t and
                        a_value != 0 and
                        a_value < cls.b_profile["critical"]
                    ):
                        cls.raise_up_critical("BMS Voltage", cls.b_profile["critical"], "V")
                        logger.log( "SOC over critical value but voltage under critical value", logger.level.WARNING )

                    # Case for soc over critical but the battery is damaged and shows voltage under 24V
                    case _ if value > critical_t  and cls.b_type == "24V-Lithium" and a_value != 0 and a_value < 24:
                        cls.raise_up_critical("BMS Voltage",24,"V")
                        send_notification_whatsapp("battery_damaged")

                    # Case for soc over critical but the battery shows lower voltage for the corresponding SoC
                    case _ if value > critical_t  and cls.b_type == "24V-Lithium" and a_value != 0 and a_value < 24.9:
                        cls.raise_up_critical("BMS Voltage",24.9,"V")
                        send_notification_whatsapp("voltage_mismatch")
                        
                    case _ if value >= restore_t: 
                        cls.restore_critical(device, restore_t, unit, rectify=True)
                        
                    case _ if value > critical_t <= warning_t: 
                        cls.raise_up_warning(device,warning_t,unit)
                    
                    case _ if value <= critical_t: 
                        cls.raise_up_critical(device,critical_t,unit)
                    
                    case _:
                        logger.log("".join([device, " over ", str(warning_t), unit]))
            
            # Conditions for system if critical state is up
            else:

                match value:

                    # Case for mismatch between SOC and Voltage when voltage is under critical threshold but soc is over restore threshold
                    case _ if (
                        device == "BMS SOC" and
                        cls.b_type in ["24V-Lithium", "12V-Lithium"]  and
                        value > restore_t and
                        a_value != 0 and
                        a_value < cls.b_profile["critical"]
                    ):
                        cls.raise_up_critical("BMS Voltage", cls.b_profile["critical"], "V", rectify=True)
                        logger.log( "SOC over restore value but voltage under critical value", logger.level.WARNING )
                    
                    # Case for mismatch between SOC and Voltage when voltage is over restore threshold but soc is under restore threshold
                    case _ if (
                        device == "BMS SOC" and
                        cls.b_type in ["24V-Lithium", "12V-Lithium"]  and
                        value < restore_t and
                        a_value != 0 and
                        a_value > cls.b_profile["restore"]
                    ):
                        cls.restore_critical("BMS Voltage", cls.b_profile["restore"], "V")
                        logger.log( "SOC under restore value but voltage over critical value", logger.level.WARNING )

                    case _ if value >= restore_t:  cls.restore_critical(device,restore_t,unit)
                    case _ if value <= critical_t:  cls.raise_up_critical(device, critical_t, unit, rectify=True)
                    case _: logger.log("Battery still charging")
                    
            return True
        except Exception as error:
            logger.log({"Battery State check_values error":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False


    @classmethod
    def check_state(cls):
        """Function to control the outputs depending on battery state"""
        try:

            # If BMS got disconnected, obtain again the instance
            if cls.bms.test_bms() == False: cls.bms = BMS()
            
            # Get the data from BMS and ADS
            soc_json, checkBMS = cls.bms.get_BMS_data()
            ads_json, checkADS = cls.ads.get_ADS_data()

            # Check the systems do determinate if telemetry is going to be sent or saved
            inversor_down = cls.is_inversor_down()
            
            # Send values to Thingsboard if Json exists
            try:
                if checkBMS: send_telemetry_thingsboard(soc_json, name="BMS data", inversor_down=inversor_down)
                if checkADS: send_telemetry_thingsboard(ads_json, name="ADS data", inversor_down=inversor_down)
            except Exception: pass

            # Check if the system is down due to programation after saving telemetry to skip restore/critical action
            if cls.systems_down: return
            
            match (checkBMS, checkADS):
                # If soc value exist, check first with SoC
                case (True, _):
                    soc_percent = soc_json["SOC"]
                    soc_voltage = soc_json["Voltage - BMS"] if soc_json["Voltage - BMS"] is not None else 0
                    
                    try: 
                        if checkADS: soc_voltage = ads_json["Voltage - ADS"] if ads_json["Voltage - ADS"] is not None else soc_voltage
                    except: pass
                    cls.check_values(soc_percent, "BMS SOC", soc_voltage)
                
                case ( _, True):
                    ads_voltage = ads_json["Voltage - ADS"]
                    cls.check_values(ads_voltage, "ADS Voltage")
                
                case _: raise Exception("Unable to get any variables")
        
        except Exception as error:
            logger.log({"Battery_State check state":str(error)}, logger.level.ERROR, cls.MODULE, True)