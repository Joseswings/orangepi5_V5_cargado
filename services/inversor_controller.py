import serial
from time import sleep
from services.usb_controller import USB_Serial
from services.loggers import logger

class Inversor:

    # Name of the file for log specific errors
    MODULE="inversor"

    client = None

    _apply_config = True

    def __new__(cls):
        if not cls._apply_config: return cls

        usb = USB_Serial()
        devices = usb.get_devices()

        for device in devices:
            try:
                
                path = "".join(["/dev/", device])
                
                cls.client = serial.Serial(
                    port=path,
                    baudrate=2400,
                    bytesize=serial.EIGHTBITS,
                    stopbits=serial.STOPBITS_ONE,
                    parity=serial.PARITY_NONE,
                    timeout=0.5
                )

                data, _ = cls.get_inversor_data()
                
                if data is None: 
                    cls.client.close()
                    raise Exception

                usb.remove_device(device,"Inversor")
                cls._apply_config = False
                break
            
            except Exception: cls.client = None

        return cls
    

    @classmethod
    def get_inversor_data(cls)->tuple[dict|None, bool]:
        try:

            if cls.client is None: return None, False
            
            """ 
            Data format: 
            (MMM.M NNN.N PPP.P QQQ RR.R S.SS TT.T b7b6b5b4b3b2b1b0 
            """

            # Write the command to get the Inversor data and read the bytes
            cls.client.write(b"Q1")
            data_bytes = cls.client.read_until()

            # Decode the bytes
            try: data_row:list = data_bytes.decode('utf-8').replace("(","").split(" ")
            except UnicodeDecodeError: return None, False
            
            if len(data_row) < 8: return None, False

            # Separate and parse the data into a json file
            data = {
                "Input Voltage - Inversor":   float(data_row[0]),
                "Fault Voltage - Inversor":   float(data_row[1]),
                "Output Voltage - Inversor":  float(data_row[2]),
                "Output Current - Inversor":  float(data_row[3]),
                "Input Frecuency - Inversor": float(data_row[4]),
                "Battery Voltage - Inversor": float(data_row[5]),
                "Temperature - Inversor":     float(data_row[6]),

                "Utility Failure - Inversor":      bool(int(data_row[7][0])),
                "Low battery - Inversor":          bool(int(data_row[7][1])),
                "Bypass - Inversor":               bool(int(data_row[7][2])),
                "UPS damaged - Inversor":          bool(int(data_row[7][3])),
                "UPS type is off-line - Inversor": bool(int(data_row[7][4])),
                "Under test - Inversor":           bool(int(data_row[7][5])),
                "Shutdown state - Inversor":       bool(int(data_row[7][6])),
                "Buzzer on - Inversor":            bool(int(data_row[7][7])) 
            }

            return data, True

        except Exception as error: 
            logger.log({"Get inversor data":str(error)}, logger.level.ERROR)
            return None, False

    
    # Test method
    @classmethod
    def test_inversor(cls) -> bool:

        if cls.client is None: return False

        usb = USB_Serial()

        try:

            # Exit if device is not configured
            if usb.devices["Inversor"] is None: return False
            
            # If device is configured try to get data to test connection
            data, _ = cls.get_inversor_data()
            if data is None: raise Exception("Lost connection with Inversor")

            return True
            
        except Exception as error:
            logger.log({"Test Inversor":str(error)}, logger.level.WARNING)
            usb.clean_device("Inversor")
            cls._apply_config = True
            return False

