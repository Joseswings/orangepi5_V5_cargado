import constants
import schedule

from subprocess import check_output
from re import search
from time import sleep

from services.bms_controller import BMS
from services.ina_sensors import INA_Sensors
from services.usb_controller import USB_Serial
from services.battery_state import BatteryState
from services.gpio_expander import GPIOExpander
from services.inversor_controller import Inversor
from services.mikrotik_controller import Mikrotik
from services.emc2302_fan_controller import EMC2302FanController
from services.internet_check import reconnectWifi, checkInterfaceSpeedtest, checkInternetPing, restartNetwork
from services.http_service import send_notification_whatsapp, schedule_whatsapp_notification
from services.json_controller import send_telemetry_thingsboard, read_data_in_json, save_data_in_json, send_saved_errors
from services.loggers import logger

# Name of the file for log specific errors
MODULE="tasks"

def check_emc_fans_control():
    """ Scheduled task to check EMC fans control """
    try:
        auto = True
        # If enable_manual_fan_controller_speed is 0 (False), set the speed to auto
        fan_controller = EMC2302FanController()
        fan_controller.update_fans_speed(auto)
    
    except Exception as error: logger.log({"Check fans":str(error)}, logger.level.ERROR, MODULE, True)

def report_orpi_status():
    """ Scheduled task to report the Orange Pi status """
    try:
        # Run the command `/etc/update-motd.d/30-armbian-sysinfo` and get the output
        output = check_output(['/etc/update-motd.d/30-armbian-sysinfo'])

        # Regex to get the OrPi status information
        cpu_temp_regex = r'CPU temp:\s+\x1b\[0;91m\s*([\d.]+)°C\x1b\[0m'
        memory_usage_regex = r'Memory usage:\s+\x1b\[0;92m\s*([\d.]+)%\x1b\[0m'
        ip_address_regex = r'IP:\s+\x1b\[92m([\d.: ]+)\x1b\[0m'
        system_load_regex = r'System load:\s+\x1b\[0;92m\s*([\d.]+)%\x1b\[0m'
        up_time_regex = r'Up time:\s+\x1b\[92m([:\d]+)\x1b\[0m'

        # Search for the values
        cpu_temp = search(cpu_temp_regex, output.decode('utf-8')).group(1)
        memory_usage = search(memory_usage_regex, output.decode('utf-8')).group(1)
        ip = search(ip_address_regex, output.decode('utf-8')).group(1)
        system_load = search(system_load_regex, output.decode('utf-8')).group(1)
        up_time = search(up_time_regex, output.decode('utf-8')).group(1)

        logger.log(f'CPU temp: {cpu_temp}°C, Memory usage: {memory_usage}%, IP: {ip}, System load: {system_load}%, Up time: {up_time}')

        # Payloads limpios tipados numéricamente para ThingsBoard
        status_data = {
            'orpi_cpu_temp': float(cpu_temp),
            'orpi_memory_usage': float(memory_usage),
            'orpi_system_load': float(system_load),
            'orpi_ip_str': str(ip),
            'orpi_up_time_str': str(up_time),
        }
        
        # MIGRACIÓN EXPLICITA: Enviamos el JSON usando la función nativa del proyecto
        send_telemetry_thingsboard(status_data, name="OrangePi Status Info")

    except Exception as error:
        logger.log({"Report OrPi Status error": str(error)}, logger.level.ERROR, MODULE, True)
    
    print(status_data)

def charge_warning():
    """Task to test the warning value"""
    controller = BatteryState()
    controller.test_warning()
    
def get_shutdown_hours(metric:str, actual_value:float|None,
                       threshold_1:float, threshold_2:float, 
                       threshold_3:float, threshold_4:float 
                       )->tuple[bool,int,str,str]:
    """Function to get total hours to shutdown the system, the init and the end hour

    Args:
        metric (str): Device value to check
        actual_value (float): Read of the value at 5:30 PM
        threshold_1 (float): First threshold to check, if value is upper the system keeps alive during night
        threshold_2 (float): Second threshold to check if value is between first or third threshold
        threshold_3 (float): Third threshold to check if value is between second or fourth threshold
        threshold_4 (float): Last threshold to check, if value is lower the system turns off 10 hours

    Raises:
        Exception: Value None is detected for the actual_value

    Returns:
        tuple[bool,int,str,str]: State of the operation, total hours to shutdown the system, the init and the end hour
    """
    try:
        
        if actual_value is None: raise Exception ("".join(["Value is None for ",metric]))
        
        if actual_value >= threshold_1:
            message = "".join([metric, " is ", str(actual_value), " systems on during night"])
            logger.log(message)
            return True, 0, None, None

        else:
            if   actual_value >= threshold_2: hours, init_time, end_time = 2,  "02:00", "04:00"
            elif actual_value >= threshold_3: hours, init_time, end_time = 6,  "00:00", "06:00"
            elif actual_value >= threshold_4: hours, init_time, end_time = 8,  "00:00", "08:00"
            else:                             hours, init_time, end_time = 10, "22:00", "08:00"
            
            message = "".join([metric, " is ", str(actual_value), " shutdown systems during ", init_time," - ", end_time ])
            logger.log(message)
        
            return True, hours, init_time, end_time
            
    except Exception as error:
        logger.log({"Get shutdown hours":str(error)}, logger.level.ERROR, MODULE, True)
        return False, None, None, None
    

def schedule_shutdown_jobs(hours:int, init_time:str, end_time:str):
    try:
        local_timezone = constants.TIMEZONE
        schedule.every().day.at(init_time, local_timezone).do(schedule_shutdown_system).tag("schedule-shutdown")
        schedule.every().day.at(end_time,  local_timezone).do(schedule_restore_system).tag("schedule-restore")    
        return True
    except Exception as error:
        logger.log({"Schedule shutdown jobs":str(error)}, logger.level.ERROR, MODULE, True)
        return False

    
def set_shutdown_hours(metrics:dict)->bool:
    """Function to set the shutdown hours checking all available metrics sequentialy and send notification to WA if the system turns off during night

    Args:
        metrics (dict): Dictionary with metrics to check a value metric with 4 thresholds to set the hours

    Returns:
        bool: State of the operation
    """
    for key in metrics.keys():
        try:
            state, hours, init_time, end_time = get_shutdown_hours(key, metrics[key]["actual_value"],
                                                                   metrics[key]["threshold_1"], metrics[key]["threshold_2"],
                                                                   metrics[key]["threshold_3"], metrics[key]["threshold_4"],)
            
            if not state: return False
            
            controller = BatteryState()
            match hours:
                case 0:
                    # In case the charge drop under the critical at night, restore the critical state at 8 am
                    controller.set_charge_check(True)
                    
                    try: 
                        logger.log({"Shutdown":"Scheduled","Check":controller.get_charge_check()})
                        schedule.every().day.at("08:00", constants.TIMEZONE).do(schedule_preventive_restore_system).tag("schedule-preventive-restore")
                    except: pass
                    return True
                case None:
                    raise Exception("Hours value is None")
                case _ if hours > 0:

                    shutdown_hours = {"hours":hours, "init_time":init_time, "end_time":end_time}
                    save_data_in_json(shutdown_hours, "shutdown")

                    schedule_shutdown_jobs(hours, init_time, end_time)
                    controller.set_charge_check(True)

                    try: logger.log({"Shutdown":"Scheduled","Check":controller.get_charge_check()})
                    except: pass
                    
                    try:
                        action = "shutdown_schedule"
                        schedule.every(1).minutes.do(schedule_whatsapp_notification,action=action,init_time=init_time)\
                        .tag("".join([action," schedule-whatsapp-notification"]))
                    
                    except Exception as error: logger.log({"WA shutdown schedule":str(error)}, logger.level.ERROR, MODULE, True)
                    return True
                    
        except Exception as error: logger.log({"Set shutdown hours":str(error)}, logger.level.ERROR, MODULE, True)

    return False


def schedule_charge_remain():
    """Task to check the state of charge at 6 PM and schedule the shutdown and restore depending on the remaining charge"""
    try:

        # Load the controllers and set the value variables to None
        battery, soc =   BMS(), None
        usb, today_acc = USB_Serial(), None
        
        json = {}
        
        try: 
            soc = battery.get_soc_percent()
            if soc is not None: json["SOC 6PM"] = soc
        except: pass
        
        try:
            solar_controller, _ = usb.get_solar_controller()
            # When Solar controler is not detected get removed and the controller type
            # Most common Solar Controller is Must, try to check Must AccPV Power even if Epever is detected
            try: 
                
                try:
                    # If read to must fail, get the last data saved in a json
                    total_acc_pv = solar_controller.readRegisterBlock("RealTimeData")["Must - Accumulated PV power"]
                    if total_acc_pv is None:raise Exception("Unable to read Must")
                except Exception as error:
                    total_acc_pv = read_data_in_json("must","Actual")["Acc_PV"]
                    logger.log({"Must Acc PV schedule":str(error)}, logger.level.ERROR, MODULE, True)
                    
                logger.log({"Total Accumulated PV": str(total_acc_pv)})
                
                # Check if data from Must is not None too send it to Thingsboard and save it into a local json
                if total_acc_pv is None: raise Exception("Unable to get Must data")
                
                json["AccDay 6PM"] = total_acc_pv
                
                tries = 0
                while tries < 3:
                    controller = BatteryState()
                    if controller.get_charge_check(): break
                    try:
                        if save_data_in_json({"Acc_PV":total_acc_pv},"must"): break
                        else: raise Exception
                    except: 
                        tries += 1
                
                prev_acc_pv = read_data_in_json("must","Prev")["Acc_PV"]
                
                # Check if prev data exists
                if prev_acc_pv is None:raise Exception("No prev data available")
                
                today_acc = round((total_acc_pv - prev_acc_pv),4) 
                logger.log({"Today Accumulated PV": str(today_acc)})
            
            except: pass
                
        except Exception as error: logger.log({"Calculate Must Accumulated":str(error)}, logger.level.ERROR, MODULE, True)
        
        metrics = {
            "SoC":    {"actual_value":soc,      "threshold_1":70, "threshold_2":60, "threshold_3":50, "threshold_4":40},
            "Accday": {"actual_value":today_acc,"threshold_1":1.2,"threshold_2":1.1,"threshold_3":0.9,"threshold_4":0.7},
        }
        
        if set_shutdown_hours(metrics):
            logger.log(json)
            send_telemetry_thingsboard(json, "6:00 PM checks")
            
    except Exception as error: logger.log({"Schedule charge remain":str(error)}, logger.level.ERROR, MODULE, True)
 

def reset_charge_check():
    """At 12:00 reset the charge check to false"""
    controller = BatteryState()
    controller.set_charge_check(False)
    logger.log("Check reset")


# Default shutdown of the system and scheduled
def turn_off_night():
    """Default task to shutdown the system"""
    controller = BatteryState()

    #Check if schedule has been programmed
    check = controller.get_charge_check()
    logger.log({"Shutdown":"Default","Check":check})

    # Skip in case scheduled
    if check: return

    # If system fails or reboot, check if data is saved for shutdown and try to schedule at 1am
    try:
        shutdown_hours:dict = read_data_in_json("shutdown", "Prev")
        if schedule_shutdown_jobs(shutdown_hours["hours"], "02:00", shutdown_hours["end_time"]): 
            controller = BatteryState()
            controller.set_charge_check(True)
            return
    except Exception as error: logger.log({"Get shutdown hours from Json":str(error)}, logger.level.WARNING)

    # If schedule was not programmed then execute the default shutdown
    send_notification_whatsapp(action="shutdown_default")
    sleep(15)
    
    controller.save_energy_during_night()

def schedule_shutdown_system():
    """Task to shutdown the system once"""
    controller = BatteryState()

    send_notification_whatsapp(action="shutdown_schedule")
    sleep(15)

    controller.save_energy_during_night()
    logger.log({"Shutdown":"Schedule"})
    schedule.clear("schedule-shutdown")

def reboot_orangepi():
    """ Task to shutdown the Mikrotik and reboot the orangepi """
    mikrotik = Mikrotik()
    mikrotik.shutdown()

# Default restore of the system and scheduled
def hard_turn_on():
    controller = BatteryState()
    controller.restore_systems()

def turn_on_day():
    """Default task to restore the system"""
    controller = BatteryState()
    check = controller.get_charge_check()
    logger.log({"Restore":"Default","Check":check})

    # Skip in case scheduled
    if check: return

    controller.restore_systems()
    try:
        action = "restore_default"
        schedule.every(5).minutes.do(schedule_whatsapp_notification,action=action)\
        .tag("".join([action," schedule-whatsapp-notification"]))
    
    except Exception as error: logger.log({"WA schedule when default restore":str(error)}, logger.level.ERROR, MODULE, True)


def schedule_preventive_restore_system():
    """Task to restore the system once"""
    controller = BatteryState()
    controller.restore_systems()

    logger.log({"Restore":"Preventive"})
    schedule.clear("schedule-preventive-restore")


def schedule_restore_system():
    """Task to restore the system once"""
    controller = BatteryState()
    controller.restore_systems()

    logger.log({"Restore":"Schedule"})
    
    try:
        action = "restore_schedule"
        schedule.every(5).minutes.do(schedule_whatsapp_notification,action=action)\
        .tag("".join([action," schedule-whatsapp-notification"]))
    
    except Exception as error: logger.log({"WA shutdown when restore systems":str(error)}, logger.level.ERROR, MODULE, True)
    
    schedule.clear("schedule-restore")

def on_boot_expander():
    """Task to turn all principal outputs on and multiplexor on Epever channel"""
    expander = GPIOExpander()
    expander.turnAllPinsOn()

def turn_off_expander():
    """Task to turn off the outputs of the expander, excluding Mikrotik"""
    expander = GPIOExpander()
    expander.turnAllPinsOff()
def check_charge():
    """Cada minuto coordina la recolección de telemetría unificada de los servicios específicos"""
    try:
        controller = BatteryState()
        systems_down, critical = controller.get_system_status()
        logger.log({"Systems down": systems_down, "Critical": critical})

        # Control del estado interno de la batería
        controller.check_state()

        # Diccionario unificado final
        payload_unificado = {}

        # 1. Solicitar telemetría al Servicio del BMS Daly de forma directa y segura
        try:
            from services.bms_controller import BMS
            battery_service = BMS()
            
            # Intentamos obtener el SOC usando el método que ya tiene por defecto el proyecto
            soc_percent = battery_service.get_soc_percent()
            if soc_percent is not None:
                payload_unificado["SOC - BMS"] = float(soc_percent)
                logger.log(f"[TELEMETRIA BMS] SOC detectado: {soc_percent}%")
                
            # Intentamos obtener el voltaje usando los métodos nativos del objeto bms interno
            if hasattr(battery_service, 'get_voltage'):
                payload_unificado["Voltage - BMS"] = float(battery_service.get_voltage())
            elif hasattr(battery_service, 'bms'):
                try:
                    data_bms = battery_service.bms.get_soc()
                    if data_bms and "total_voltage" in data_bms:
                        payload_unificado["Voltage - BMS"] = float(data_bms["total_voltage"])
                        logger.log(f"[TELEMETRIA BMS] Voltaje detectado: {data_bms['total_voltage']}V")
                except:
                    pass
        except Exception as error:
            logger.log({"Error al obtener telemetría del servicio BMS": str(error)}, logger.level.WARNING)

        # 2. Solicitar telemetría al Servicio del Controlador Solar (Vía Mapeo Dinámico)
        # CORRECCIÓN DE IMPORTACIÓN: Declaramos localmente USB_Serial para eliminar el NameError
        from services.usb_controller import USB_Serial
        usb = USB_Serial()
        solar_controller, controller_type = usb.get_solar_controller()
        
        if solar_controller is not None:
            inversor_down = controller.is_inversor_down()

            if controller_type == "Must":
                try:
                    # Le pedimos el voltaje al servicio específico del Must
                    if hasattr(solar_controller, 'get_inversor_voltage'):
                        voltaje_must = solar_controller.get_inversor_voltage()
                        if voltaje_must is not None:
                            payload_unificado["Voltage - MUST"] = voltaje_must
                    else:
                        # Fallback directo al registro modbus si el método no se guardó correctamente
                        voltaje_registro = solar_controller.readRegister(address=15206, mode="holding", count=1, log_action=False)
                        if isinstance(voltaje_registro, int):
                            payload_unificado["Voltage - MUST"] = voltaje_registro / 10.0

                    # Mantenemos la persistencia de datos diarios en JSON original del proyecto
                    data_block = solar_controller.readRegisterBlock("RealTimeData")
                    if data_block and "Must - Accumulated PV power" in data_block:
                        total_acc_pv = data_block["Must - Accumulated PV power"]
                        if total_acc_pv is not None: 
                            save_data_in_json({"Acc_PV": total_acc_pv}, "must")

                except Exception as error:
                    logger.log({"Error al obtener voltaje del servicio Must": str(error)}, logger.level.WARNING)
            else:
                # Si es Epever, mantiene su recolección por bloque original
                data_epever = solar_controller.readRegisterBlock("RealTimeData")
                send_telemetry_thingsboard(data_epever, name="Solar controller realtime data", inversor_down=inversor_down)

        # 3. Despachar el paquete unificado si contiene lecturas
        if payload_unificado:
            logger.log(f"[NUBE] Enviando paquete unificado a ThingsBoard: {payload_unificado}")
            send_telemetry_thingsboard(
                payload_unificado, 
                name="Planta Solar Unificada", 
                inversor_down=controller.is_inversor_down()
            )
    
    except Exception as error: 
        logger.log({"Fallo critico en Check charge orquestador": str(error)}, logger.level.ERROR, MODULE, True)


def uploadEpeverBatteryParams():
    """Task to get and upload epever params if detected"""
    try:
        controller = BatteryState()
        systems_down, critical = controller.get_system_status()
        inversor_down = controller.is_inversor_down()

        if not systems_down and not critical:
            usb = USB_Serial()
            solar_controller,controller_type = usb.get_solar_controller()
            if solar_controller is not None:
                if controller_type == "Epever":
                    data = solar_controller.readRegisterBlock("BatteryParameters")
                    send_telemetry_thingsboard(data, name="Epever battery params",inversor_down=inversor_down)
    
    except Exception as error: logger.log({"Epever upload battery params":str(error)}, logger.level.ERROR, MODULE, True)


def upload_inversor():
    """Task to get and upload Inversor data"""
    try:

        inversor = Inversor()
        
        # If Inversor got disconnected, obtain again the instance configured
        if not inversor.test_inversor(): inversor = Inversor()

        # Get the data and save or send it to ThingsBoard
        json, state = inversor.get_inversor_data()
        if not state: return

        controller = BatteryState()
        send_telemetry_thingsboard(json, name="Inversor", inversor_down=controller.is_inversor_down())
    
    except Exception as error: logger.log({"Inversor check":str(error)}, logger.level.ERROR, MODULE, True)


def upload_ina_sensors():
    """Task to get and upload INA data"""
    try:
        ina = INA_Sensors()
        json = ina.get_all()
        controller = BatteryState()

        send_telemetry_thingsboard(json, name="INA data", inversor_down=controller.is_inversor_down())
    
    except Exception as error: logger.log({"INA check":str(error)}, logger.level.ERROR, MODULE, True)

def clear_scheduler():
    client = Mikrotik()
    client.check_users_in_schedule()

def internet_check():
    """Every hour check internet connection through ethernet interface"""
    try:
        controller = BatteryState()
        inversor_down = controller.is_inversor_down()

        # Check if the system is on
        if inversor_down: return

        # Get the Inversor and Mikrotik Pins
        mikrotik_pin   = "GPA6"
        starlink_pin_1 = "GPA7"
        starlink_pin_2 = "GPA5"

        # Get the instances for expander and mikrotik
        expander = GPIOExpander()
        mikrotik = Mikrotik()
        
        # First check the eth0 interface with both test ping/speedtest
        internet_on_eth0:bool = checkInterfaceSpeedtest("eth0") or checkInternetPing("eth0")
        
        # Check if any test pass and then send the saved errors
        if internet_on_eth0:
            send_saved_errors()
            return
            
        # If both tests failed, reboot the Mikrotik
        # Try first clean reboot to mikrotik, then do the hard reset
        if not mikrotik.reboot():
            expander.hardReset(mikrotik_pin)
            logger.log("Soft Reset Mikrotik")

        # Try reconnect the wifi before ping and speedtest
        reconnectWifi("wlan0")
        reconnectWifi("wlan1")

        # Check both test ping/speedtest
        internet_on_wlan0:bool = checkInterfaceSpeedtest("wlan0") or checkInternetPing("wlan0")
        internet_on_wlan1:bool = checkInterfaceSpeedtest("wlan1") or checkInternetPing("wlan1")

        # If there is internet connection on any wlan interface, send the saved errors
        if  internet_on_wlan0 or internet_on_wlan1:
            send_saved_errors()
            return
        
        # If all tests failed, reboot the Starlink
        expander.hardResetStarlink(starlink_pin_1,starlink_pin_2)
        logger.log("Hard reset Starlink", logger.level.WARNING)
        return

    except Exception as error: logger.log({"Internet check":str(error)}, logger.level.ERROR, MODULE, True)

def reconnect_wlan():
    """Task to check wlan interface connection"""
    try:
        controller = BatteryState()
        inversor_down = controller.is_inversor_down()

        # Check if the system is on and try config nmcli in any interface
        if inversor_down: return
        if reconnectWifi("wlan0") or reconnectWifi("wlan1"): return
            
        counter = 0
        while counter < 3:
            restartNetwork()
            sleep(2)
            if reconnectWifi("wlan0") or reconnectWifi("wlan1"): return
            counter += 1

    except Exception as error: logger.log({"Reconnect wlan":str(error)}, logger.level.ERROR)

def schedule_modify_mikrotik_scheduler(days:int,hours:int,minutes:int):
    """Task to restore internet time to users before shutdown once at certain hour"""
    try:
        mikrotik = Mikrotik()
        mikrotik.modify_all_schedulers(days=days,hours=hours,minutes=minutes)
        logger.log({"Modify Scheduler":True})
    
    except Exception as error: logger.log({"Modify scheduler":str(error)}, logger.level.ERROR, MODULE, True)
    
    schedule.clear("scheduler-modify")

def check_mikrotik_files():
    """At init, check if scripts are uploaded to the mikrotik"""
    mikrotik = Mikrotik()
    mikrotik.upload_scripts()