from unittest import TestCase, main

from time import sleep

import services.helpers as helper

from services.json_controller import read_data_in_json, save_data_in_json, save_telemetry, send_saved_telemetry
from services.internet_check import checkInternetPing, checkInterfaceSpeedtest

from services.loggers import logger
from env_config import env

# Disable logging when performing UT
logger.set_enabled_logging(False)

class Test(TestCase):

    @staticmethod
    def log_test_failed(module:str, error:any):
        logger.set_enabled_logging(True)
        
        log_msg = " ".join([module, "test failed:", str(error)])
        logger.log(log_msg, logger.level.ERROR)
        
        logger.set_enabled_logging(False)
        
        raise

    def setUp(self):

        # Try to load all controllers connected to the V5
        try: 
            from services.ads_controller import ADS
            self.ads = ADS()
        except: self.ads = None
        
        try:
            from services.bms_controller import BMS 
            self.bms = BMS()
        except: self.bms = None

        try: 
            from services.gpio_controller import GPIOController
            self.gpio = GPIOController()
        except: self.gpio = None

        try:
            from services.gpio_expander import GPIOExpander
            self.expander = GPIOExpander()
        except: self.expander = None

        try:
            from services.ina_sensors import INA_Sensors 
            self.ina = INA_Sensors()
        except: self.ina = None
        
        try:
            from services.emc2302_fan_controller import EMC2302FanController
            self.fans = EMC2302FanController()
        except: self.fans = None

        try:
            from services.usb_controller import USB_Serial
            self.usb = USB_Serial()
        except: self.usb = None
        

        # Load modules independent of the V5 hardware
        try:
            from services.inversor_controller import Inversor
            self.inversor = Inversor()
        except: self.inversor = None

        try:
            from services.usb_controller import USB_Serial 
            self.usb = USB_Serial()
        except: self.usb = None

        try:
            from services.mikrotik_controller import Mikrotik
            self.mikrotik = Mikrotik()
        except: self.mikrotik = None

        try:
            from services.http_service import http
            self.http = http
        except: self.http = None
        

    def test_logger(self):
        # Enable the logs for the test
        logger.set_enabled_logging(True)
        logger.log("Test Info")
        logger.log("Test Warning", logger.level.WARNING)
        logger.log("Test Error", logger.level.ERROR)
        logger.set_enabled_logging(False)


    def test_env(self):
        try:
            new_env_value = env.get_env_value("BATTERY_TYPE")
            self.assertIn(new_env_value, ["24V-Lithium", "24V-Lithium-Redodo", "24V-Lead-Acid", "12V-Lithium", "12V-Lithium-Redodo", "12V-Lead-Acid", "12V-Lead-Acid-Autocraft"])
            self.assertEqual(new_env_value, env.BATTERY_TYPE)
        
        except AssertionError as error: self.log_test_failed("Env", error)


    def test_helpers(self):
        try:
            self.assertTrue(helper.executeScript("ls -l"))

            year = helper.get_year()
            self.assertIn("20", year)

            dates:list = [helper.getActualDate(), helper.getPrevDate(), helper.getActualDate(), helper.get_datetime_with_ms()]
            for date in dates: self.assertIn(year, date)

            unix_ts     = helper.get_unix_timestamp()
            datetime_ts = helper.parse_unixts_to_datetime(unix_ts)
            self.assertIn(year, datetime_ts)
        
        except AssertionError as error: self.log_test_failed("Helpers", error)


    def test_json(self):
        try:
            write_json = {"test":True}
            self.assertTrue(save_data_in_json(write_json,"test"))
            
            read_json = read_data_in_json("test",'Actual')
            self.assertEqual(write_json, read_json)


            self.assertTrue(send_saved_telemetry("test"))
            self.assertTrue(save_telemetry({"test":True}, "test"))
            self.assertTrue(send_saved_telemetry("test"))
        
        except AssertionError as error: self.log_test_failed("Json", error)


    def test_http(self):
        try:
            self.assertIsNotNone(self.inversor)
            self.assertTrue(self.http.thingsboard_post_request({"test":True},topic="Test"))
            self.assertTrue(self.http.antstack_post_request("test", {"test":True}, True))
        
        except AssertionError as error: self.log_test_failed("HTTP", error)
    
    def test_inversor(self):
        try:
            self.assertIsNotNone(self.inversor)
            
            data, state = self.inversor.get_inversor_data()
            self.assertIsNotNone(data)
            self.assertTrue(state)

        except AssertionError as error: self.log_test_failed("Inversor", error)


    # Test usb and charge controller before bms
    def test_usb(self):
        try:
            self.assertIsNotNone(self.usb)

            self.assertIsNone(self.usb.devices["Solar_Charger"])

            detected:list = self.usb.get_devices()
            self.assertGreater(len(detected), 0)

            solar_controller, controller_type = self.usb.get_solar_controller()
            self.assertIsNotNone(controller_type)
            self.assertIsNotNone(solar_controller)

            # Test Solar Charge Controller
            self.assertIsNotNone(solar_controller.readRegisterBlock("RealTimeData"))
        
        except AssertionError as error: self.log_test_failed("USB", error)       


    def test_ads(self):
        try:
            self.assertIsNotNone(self.ads)
            self.assertIsNotNone(self.ads.get_channel_reading(0))

            voltage = self.ads.get_ADS_Voltage()
            self.assertIsNotNone(voltage)

            temperature = self.ads.get_ADS_Temperature()
            self.assertIsNot(temperature, -1)

            individual_data = {
                "Voltage - ADS":voltage,
                "Temperature - ADS": temperature,
            }

            all_data, state = self.ads.get_ADS_data()
            self.assertIsNotNone(all_data)
            self.assertTrue(state)

            for key in individual_data.keys():  self.assertAlmostEqual(individual_data[key], all_data[key], delta=0.5)
        
        except AssertionError as error: self.log_test_failed("ADS", error)


    def test_bms(self):
        try:
            self.assertIsNotNone(self.bms)
            self.assertTrue(self.bms.test_bms())

            individual_data = {
                "SOC":self.bms.get_soc_percent(),
                "Voltage - BMS":self.bms.get_temperatures(),
                "Current - BMS":self.bms.get_cycles(),
                "Cycles - BMS":self.bms.get_current(),
            }

            all_data, state = self.bms.get_BMS_data()
            self.assertTrue(state)
            self.assertAlmostEqual(individual_data["SOC"], all_data["SOC"],0)
        
        except AssertionError as error: self.log_test_failed("BMS", error)


    def test_ina(self):
        try:
            self.assertIsNotNone(self.ina)
            voltage, current = self.ina.get_sensor("Inversor")
            self.assertTrue(voltage != 0 and current != 0 )
            self.assertIsNotNone(self.ina.get_all())

        except AssertionError as error: self.log_test_failed("INA", error)


    def test_expander(self):
        try:
            self.assertIsNotNone(self.expander)
            self.assertEqual(self.expander.get_name_GPIO("GPA7"),"Inversor")
            
            self.assertTrue( self.expander.setPinOn("GPA1"))
            sleep(2)
            self.assertTrue( self.expander.setPinOff("GPA1"))
        
        except AssertionError as error: self.log_test_failed("Expander", error)


    def test_fans(self):
        try:
            self.assertIsNotNone(self.fans)
            fan_speed = self.fans.get_automatic_fans_speed()
            self.assertTrue(self.fans.set_fan_speed("FAN_ONE",fan_speed))
            self.assertTrue(self.fans.set_fan_speed("FAN_TWO",fan_speed))
        
        except AssertionError as error: self.log_test_failed("Fans", error)


    def test_mikrotik(self):
        try:
            self.assertIsNotNone(self.mikrotik)

            self.mikrotik.upload_scripts()

            json, done = self.mikrotik.get_users_data()
            self.assertTrue(done)
            self.assertIsNotNone(json)
        
        except AssertionError as error: self.log_test_failed("Mikrotik", error)


    def test_internet(self):
        try:
            interfaces:list[str] = ['wlan0','eth0']

            for interface in interfaces:
                ping =  checkInternetPing(interface)
                speedtest = checkInterfaceSpeedtest(interface)
                
                self.assertTrue(ping or speedtest)
        
        except AssertionError as error: self.log_test_failed("Internet", error)
    

if __name__ == "__main__": main()