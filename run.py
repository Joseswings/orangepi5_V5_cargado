import schedule
import constants
from time import sleep

from services.loggers import logger

def check_libraries():
    from pathlib import Path
    from services.helpers import executeScript

    script = " ".join(["cd", str(Path(__file__).resolve().parent), "&&", "pip install -r requirements.txt"])
    executeScript(script)


def init_expander():
    # First configure the expander before loading the rest of the modules
    from services.gpio_expander import GPIOExpander
    expander = GPIOExpander()
    expander.turnAllPinsOn()


def create_tasks():
    import services.scheduled_tasks as scheduled_tasks

    # Tasks to run once or at boot
        
    schedule.every(constants.WIFI_RECONNECT_INTERVAL).minutes.do(scheduled_tasks.reconnect_wlan)
    schedule.every(constants.BATTERY_CHARGE_CHECK_INTERVAL).seconds.do(scheduled_tasks.check_charge)
    schedule.run_all()

    # Schedule for the tasks

    # Monitoring tasks
    #schedule.every(constants.SOLENOID_CHECK_INTERVAL).seconds.do(scheduled_tasks.check_solenoid_status)
    #schedule.every(constants.ORPI_STATUS_CHECK_INTERVAL).minutes.do(scheduled_tasks.report_orpi_status)


    schedule.every(constants.PING_CHECK_INTERVAL).minutes.do(scheduled_tasks.internet_check)
    schedule.every(constants.EMC2302_FANS_CHECK_INTERVAL).seconds.do(scheduled_tasks.check_emc_fans_control)
    schedule.every(constants.EPEVER_BATTERY_PARAMS_CHECK_INTERVAL).seconds.do(scheduled_tasks.uploadEpeverBatteryParams)
    schedule.every(constants.INA_SENSORS_CHECK_INTERVAL).seconds.do(scheduled_tasks.upload_ina_sensors)
    schedule.every(constants.INVERSOR_CHECK_INTERVAL).seconds.do(scheduled_tasks.upload_inversor)

    schedule.every().day.at("01:00", constants.TIMEZONE).do(scheduled_tasks.turn_off_night)
    schedule.every().day.at("06:00", constants.TIMEZONE).do(scheduled_tasks.turn_on_day)
    #schedule.every().day.at("12:00", constants.TIMEZONE).do(scheduled_tasks.hard_turn_on)
    schedule.every().monday.at("11:00", constants.TIMEZONE).do(scheduled_tasks.reboot_orangepi)

    schedule.every().day.at("12:00", constants.TIMEZONE).do(scheduled_tasks.reset_charge_check)
    schedule.every().day.at("18:00", constants.TIMEZONE).do(scheduled_tasks.schedule_charge_remain)
    

def main():
    try:

        # Config of the system
        init_expander()
        create_tasks()

        while True:
            try:
                # Run the scheduled tasks and wait 1 second for the next iteration
                schedule.run_pending()
                sleep(1)

            except KeyboardInterrupt as error: break

            except Exception as error:
                logger.log({"Run.py Exception":str(error)}, logger.level.ERROR, "main", True)
                sleep(5) # Wait 5 seconds before trying to reconnect

    except Exception as error:
        logger.log({"Run.py failed":str(error)}, logger.level.ERROR)
        
        from pathlib import Path
        from services.helpers import executeScript
        
        script = "python3 " + str(Path(__file__).resolve().parent) + "/encenderExpander.py"
        executeScript(script)

if __name__ == '__main__': 
    #check_libraries()
    main()