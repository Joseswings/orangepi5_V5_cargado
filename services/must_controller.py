#IMPORTANT: Use pymodbus version 2.5.3
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from time import sleep

from services.loggers import logger

class MustController:

    MODULE = "must"

    client = None

    def __new__(cls):
        return cls
    
    registers = {

        "DeviceData":[
            {"address": 0x2714, "name":"Must - Hardware version", "mode":"holding", "count":1},
            {"address": 0x2715, "name":"Must - Software version", "mode":"holding", "count":1},
            {"address": 0x2719, "name":"Must - Rated Current", "mode":"holding", "count":1},
            {"address": 0x271a, "name":"Must - Communication Protocol Edition", "mode":"holding", "count":1},
        ],

        ## Real Time Data
        "RealTimeData":[
            #{"address": 0x3B61, "name":"Must - Charger workstate", "mode":"holding", "count":1},
            #{"address": 0x3B62, "name":"Must - Mppt state", "mode":"holding", "count":1},
            #{"address": 0x3B63, "name":"Must - charging state", "mode":"holding", "count":1},
            #{"address": 0x3B65, "name":"Must - PV voltage", "mode":"holding", "count":1},
            #{"address": 0x3B66, "name":"Must - Battery voltage", "mode":"holding", "count":1},
            #{"address": 0x3B67, "name":"Must - Charger current", "mode":"holding", "count":1},
            {"address": 0x3B68, "name":"Must - Charger power", "mode":"holding", "count":1},
            #{"address": 0x3B69, "name":"Must - Radiator temperature", "mode":"holding", "count":1},
            #{"address": 0x3B6a, "name":"Must - External temperature", "mode":"holding", "count":1},
            #{"address": 0x3B6b, "name":"Must - Battery Relay", "mode":"holding", "count":1},
            #{"address": 0x3B6c, "name":"Must - PV Relay", "mode":"holding", "count":1},
            #{"address": 0x3B6d, "name":"Must - Error message", "mode":"holding", "count":1},
            #{"address": 0x3B6e, "name":"Must - Warning message", "mode":"holding", "count":1},
            #{"address": 0x3B6f, "name":"Must - BattVol Grade", "mode":"holding", "count":1},
            #{"address": 0x3B70, "name":"Must - Rated Current", "mode":"holding", "count":1},
            {"address": 0x3B71, "name":"Must - Accumulated PV power", "mode":"holding", "count":2},
            #{"address": 0x3B73, "name":"Must - Accumulated day", "mode":"holding", "count":1},
            #{"address": 0x3B74, "name":"Must - Accumulated hour", "mode":"holding", "count":1},
            #{"address": 0x3B75, "name":"Must - Accumulated minute", "mode":"holding", "count":1},
            {"address": 0x3B77, "name":"Must - Soc", "mode":"holding", "count":1},
            #{"address": 0x3B78, "name":"Must - Arrow Flag", "mode":"holding", "count":1},

        ],
    }

    @classmethod
    def connect(cls, serial_ports:list):
        for port in serial_ports:
            try:
                path = "/dev/" + port
                cls.client = ModbusClient(method='rtu', port=path, baudrate=9600, timeout=1)
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
                    data = read.registers[0]
                case 2:
                    # Double register for acumulated PV power
                    HighData = read.registers[0] * 1000
                    LowData =  read.registers[1] / 10

                    data =  HighData + LowData
                
                case _: raise Exception("Invalid count value")
            
            return data

        except Exception as error: 
            if log_action: logger.log({"Must read register":str(error)}, logger.level.ERROR)
            return None
    
    @classmethod
    def readRegisterBlock(cls, block):

        json = {}
        try:
            for register in cls.registers[block]:
                try:
                    sleep(0.4)
                    data = cls.readRegister(register["address"],register["mode"],register["count"])
                    json[register["name"]] = data
                except Exception: pass

            return json
        
        except Exception as error: 
            logger.log({"Must read register block":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None
    
    @classmethod
    def testConnection(cls):
        try:
            register = {"address": 0x3B77, "name":"Must - SoC", "mode":"holding", "count":1}
            sleep(0.4)
            data = cls.readRegister(register["address"],register["mode"],register["count"], log_action=False)
            if data is None: raise Exception("Unable to get data from test register")
            return data
        
        except Exception as error: 
            logger.log({"Must test connection":str(error)}, logger.level.WARNING)
            return None

    @classmethod
    def get_inversor_voltage(self) -> float | None:
        """Lee el registro 15206 y devuelve el voltaje del inversor formateado (/10.0)"""
        try:
            # Usamos el método nativo de lectura modbus de la clase
            voltaje_registro = self.readRegister(address=15206, mode="holding", count=1, log_action=False)
            if isinstance(voltaje_registro, int):
                return voltaje_registro / 10.0
        except Exception as e:
            print(f"[Must Service Error]: {e}")
        return None
