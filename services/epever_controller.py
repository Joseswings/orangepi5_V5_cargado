#from epevermodbus.driver import EpeverChargeController

#IMPORTANT: Use pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from time import sleep

from services.loggers import logger

class EpeverController:

    MODULE = "epever"

    client = None

    def __new__(cls): return cls

    registers = {

        ## Real Time Data
        "RealTimeData":[
            {"address": 0x2000, "name":"Epever - TemperatureInside", "mode":"holding", "count":1},
            {"address": 0x200C, "name":"Epever - Day/Night", "mode":"holding", "count":1},
            {"address": 0x3100, "name":"Epever - PV_ArrayVoltage", "mode":"input", "count":1},
            {"address": 0x3101, "name":"Epever - PV_ArrayCurrent", "mode":"input", "count":1},
            {"address": 0x3102, "name":"Epever - PV_ArrayPower", "mode":"input", "count":2},
            {"address": 0x310C, "name":"Epever - LoadVoltage", "mode":"input", "count":1},
            {"address": 0x310D, "name":"Epever - LoadCurrent", "mode":"input", "count":1},
            {"address": 0x310E, "name":"Epever - LoadPower", "mode":"input", "count":2},
            {"address": 0x3110, "name":"Epever - BatteryTemperature", "mode":"input", "count":1},
            {"address": 0x3111, "name":"Epever - DeviceTemperature", "mode":"input", "count":1},
            {"address": 0x311A, "name":"Epever - BatterySOC", "mode":"input", "count":1},
            {"address": 0x311D, "name":"Epever - BatteryRealRatedVoltage", "mode":"input", "count":1},
            {"address": 0x3200, "name":"Epever - BatteryStatus", "mode":"input", "count":1},
            {"address": 0x3201, "name":"Epever - ChargingEquipmentStatus", "mode":"input", "count":1},
            {"address": 0x3201, "name":"Epever - DischargingEquipmentStatus", "mode":"input", "count":1},
            {"address": 0x3302, "name":"Epever - MaximumBatteryVoltageToday", "mode":"input", "count":1},
            {"address": 0x3303, "name":"Epever - MinimumBatteryVoltageToday", "mode":"input", "count":1},
            {"address": 0x3304, "name":"Epever - ConsumedEnergyToday", "mode":"input", "count":2},
            {"address": 0x3306, "name":"Epever - ConsumedEnergyMonth", "mode":"input", "count":2},
            {"address": 0x3308, "name":"Epever - ConsumedEnergyYear", "mode":"input", "count":2},
            {"address": 0x330A, "name":"Epever - TotalConsumedEnergy", "mode":"input", "count":2},
            {"address": 0x330C, "name":"Epever - GeneratedEnergyToday", "mode":"input", "count":2},
            {"address": 0x330E, "name":"Epever - GeneratedEnergyMonth", "mode":"input", "count":2},
            {"address": 0x3310, "name":"Epever - GeneratedEnergyYear", "mode":"input", "count":2},
            {"address": 0x3312, "name":"Epever - TotalGeneratedEnergy", "mode":"input", "count":2},
            {"address": 0x331A, "name":"Epever - BatteryVoltage", "mode":"input", "count":1},
            {"address": 0x331B, "name":"Epever - BatteryCurrent", "mode":"input", "count":2},
        ],

        ## Battery Parameters
        "BatteryParameters":[
            {"address": 0x3005, "name":"Epever - RatedChargingTemp", "mode":"input", "count":1},
            {"address": 0x300E, "name":"Epever - RatedLoadCurrent", "mode":"input", "count":1},
            {"address": 0x311D, "name":"Epever - BatteryRealRatedVoltage", "mode":"input", "count":1},
            {"address": 0x9000, "name":"Epever - BatteryType", "mode":"holding", "count":1},
            {"address": 0x9001, "name":"Epever - BatteryCapacity", "mode":"holding", "count":1},
            {"address": 0x9002, "name":"Epever - TemperatureCompensation", "mode":"holding", "count":1},
            {"address": 0x9003, "name":"Epever - OverVoltageDisconect", "mode":"holding", "count":1},
            {"address": 0x9004, "name":"Epever - ChargingLimitVoltage", "mode":"holding", "count":1},
            {"address": 0x9005, "name":"Epever - OverVoltageReconnect", "mode":"holding", "count":1},
            {"address": 0x9006, "name":"Epever - EqualizeChargingVoltage", "mode":"holding", "count":1},
            {"address": 0x9007, "name":"Epever - BoostChargingVoltage", "mode":"holding", "count":1},
            {"address": 0x9008, "name":"Epever - FloatChargingVoltage", "mode":"holding", "count":1},
            {"address": 0x9009, "name":"Epever - BoostReconectCharging", "mode":"holding", "count":1},
            {"address": 0x900A, "name":"Epever - LowVoltageReconnect", "mode":"holding", "count":1},
            {"address": 0x900B, "name":"Epever - UnderVoltageWarningRecover", "mode":"holding", "count":1},
            {"address": 0x900C, "name":"Epever - UnderVoltageWarning", "mode":"holding", "count":1},
            {"address": 0x900D, "name":"Epever - LowVoltageDisconnect", "mode":"holding", "count":1},
            {"address": 0x900E, "name":"Epever - DischargingLimitVoltage", "mode":"holding", "count":1},
            {"address": 0x9067, "name":"Epever - BatteryRatedVoltageLevel", "mode":"holding", "count":1},
            {"address": 0x906A, "name":"Epever - DefaultLoadOnOff", "mode":"holding", "count":1},
            {"address": 0x906B, "name":"Epever - EqualizeDuration", "mode":"holding", "count":1},
            {"address": 0x906C, "name":"Epever - BoostDuration", "mode":"holding", "count":1},
            {"address": 0x906D, "name":"Epever - BatteryDischarge", "mode":"holding", "count":1},
            {"address": 0x906E, "name":"Epever - BatteryCharge", "mode":"holding", "count":1},
            {"address": 0x9070, "name":"Epever - ChargingMode", "mode":"holding", "count":1},
            {"address": 0x9107, "name":"Epever - BatteryProtection", "mode":"holding", "count":1},
        ],

        ## Load Parameter
        "LoadParameters":[
            {"address": 0x901E, "name":"Epever - NightTimeThresholdV", "mode":"holding", "count":1},
            {"address": 0x901F, "name":"Epever - LightSignalStartup", "mode":"holding", "count":1},
            {"address": 0x9020, "name":"Epever - DayTimeThresholdV", "mode":"holding", "count":1},
            {"address": 0x9021, "name":"Epever - LightSignalCloseDelayTime", "mode":"holding", "count":1},
            {"address": 0x903D, "name":"Epever - LoadControlMode", "mode":"holding", "count":1},
            {"address": 0x903E, "name":"Epever - LightOnTime1", "mode":"holding", "count":1},
            {"address": 0x903F, "name":"Epever - LightOnTime2", "mode":"holding", "count":1},
            {"address": 0x9042, "name":"Epever - Time1ControlTurnOn", "mode":"holding", "count":1},
            {"address": 0x9045, "name":"Epever - Time1ControlTurnOff", "mode":"holding", "count":1},
            {"address": 0x9048, "name":"Epever - Time2ControlTurnOn", "mode":"holding", "count":1},
            {"address": 0x904B, "name":"Epever - Time2ControlTurnOff", "mode":"holding", "count":1},
            {"address": 0x9065, "name":"Epever - NightTime", "mode":"holding", "count":1},
            {"address": 0x9069, "name":"Epever - TimingControlChoose", "mode":"holding", "count":1},
        ],

        ## Device Parameters
        "DeviceParameters":[
            {"address": 0x9010, "name":"Epever - LowerTempChargingLimit", "mode":"holding", "count":1},
            {"address": 0x9011, "name":"Epever - LowerTempDischargingLimit", "mode":"holding", "count":1},
            {"address": 0x9017, "name":"Epever - BatteryUpperLimitTemp", "mode":"holding", "count":1},
            {"address": 0x9018, "name":"Epever - BatteryLowerLimitTemp", "mode":"holding", "count":1},
            {"address": 0x9019, "name":"Epever - DeviceOverTemperature", "mode":"holding", "count":1},
            {"address": 0x901A, "name":"Epever - DeviceRecoveryTemp", "mode":"holding", "count":1},
            {"address": 0x9063, "name":"Epever - BacklightTime", "mode":"holding", "count":1},
        ],

        ## Rated Parameter
        "RatedParameters":[
            {"address": 0x3000, "name":"Epever - ArrayRatedVoltage", "mode":"input", "count":1},
            {"address": 0x3001, "name":"Epever - ArrayRatedCurrent", "mode":"input", "count":1},
            {"address": 0x3002, "name":"Epever - ArrayRatedPower", "mode":"input", "count":2},
            {"address": 0x3004, "name":"Epever - BatteryRatedVoltage", "mode":"input", "count":1},
            {"address": 0x3005, "name":"Epever - BatteryRatedCurrent", "mode":"input", "count":1},
            {"address": 0x3006, "name":"Epever - BatteryRatedPower", "mode":"input", "count":2},
            {"address": 0x300D, "name":"Epever - RatedLoadVoltage", "mode":"input", "count":1},
            {"address": 0x300E, "name":"Epever - RatedLoadCurrent", "mode":"input", "count":1},
            {"address": 0x300F, "name":"Epever - RatedLoadPower", "mode":"input", "count":2},
        ],
    }

    @classmethod
    def connect(cls, serial_ports:list):
        for port in serial_ports:
            try:
                path = "/dev/" + port
                cls.client = ModbusClient(method='rtu', port=path, baudrate=115200, timeout=1)
                cls.client.connect()
                sleep(2)
                
                # For successful connection return True and the tty port
                if cls.testConnection() is not None: return True, port

            except Exception: continue
        
        return False, None


    @classmethod
    def readRegister(cls, address:hex, mode:str, count:int, log_action=True):
        try:
            match mode:
                case "input":   read = cls.client.read_input_registers(address=address,count=count,unit=1)
                case "holding": read = cls.client.read_holding_registers(address=address,count=count,unit=1)
                case _: raise Exception("Invalid read mode")

            match count:
                case 1:
                    data = read.registers[0] #read register all register 
                case 2:
                    # Concat the hex
                    LowData = hex(read.registers[0])[2:].zfill(4)
                    HighData = hex(read.registers[1])[2:].zfill(4)

                    stringHex =  "0x" + str(HighData) + str(LowData)
                    data =  int(stringHex,16)

                case _: raise Exception("Invalid count value")
            
            return data

        except Exception as error: 
            if log_action: logger.log({"Epever read register":str(error)}, logger.level.ERROR)
            return None


    @classmethod
    def readRegisterBlock(cls, block):

        json = {}
        try:
            for register in cls.registers[block]:
                try:
                    data = cls.readRegister(register["address"],register["mode"],register["count"])
                    json[register["name"]] = data
                except Exception: pass
            return json
        
        except Exception as error: 
            logger.log({"Epever read register block":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None


    @classmethod
    def testConnection(cls):
        try:
            register = {"address": 0x311A, "name":"Epever - BatterySOC", "mode":"input", "count":1}
            data = cls.readRegister(register["address"],register["mode"],register["count"], log_action=False)
            if data is None:  raise Exception("Unable to get data from test register")
            return data
        
        except Exception as error: 
            logger.log({"Epever test connection":str(error)}, logger.level.WARNING)
            return None
    

    ## To Do  read single register 