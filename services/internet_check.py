import netifaces
import speedtest

from psutil import net_if_addrs

from services.helpers import executeScript
from services.http_service import http, send_notification_whatsapp
from services.loggers import logger

MODULE = "internet"
        
def interfaceExists(interface:str)->bool:
    try:
        interfaces = net_if_addrs()
        if interface in list(interfaces.keys()): return True
        return False

    except Exception: return False
        

def try_wifi(ssid:str, password:str, interface:str)->bool:
    try:
        
        script = "".join(["nmcli device wifi connect ",ssid," password ",password," ifname ",interface])
        if not executeScript(script): return False
        
        message = " ".join(["Orange Pi connected to", ssid])
        logger.log(message)

        if ssid == "STARLINK":
            try: send_notification_whatsapp("starlink_default")
            except: pass
        
        return True
    
    except Exception: return False


def restartNetwork():
    try:
        executeScript("systemctl restart NetworkManager")
        executeScript("/etc/init.d/networking restart")
        return True
    except Exception as error:
        logger.log({"Restart interfaces error":str(error)}, logger.level.ERROR, MODULE, True)
        return False

def reconnectWifi(interface:str)->bool:
    try:
        # Fist check if interface exist
        if not interfaceExists(interface): return False

        if try_wifi("KingoTaller","kingotaller", interface): return True
        if try_wifi("KINGO","Lingo2023!", interface): return True
        if try_wifi("kingo_","Lingo2023!", interface): return True
        if try_wifi("STARLINK","", interface): return True

        message = " ".join(["Reconnect wifi interface failed on interface:", interface])
        logger.log(message, logger.level.WARNING)

        return False
                
    except Exception as error:
        logger.log({"Reconnect wifi":str(error)}, logger.level.ERROR, MODULE, True)
        return False


def checkInternetPing(interface:str)->bool:
    """Function to check internet conection through specific interface"""
    try:
        
        # Fist check if interface exist
        if not interfaceExists(interface): return False
        
        hostname = "google.com"
        ping = f"timeout 2.0 ping -c 1 -I {interface} {hostname}"

        # Then execute the script and check the response
        if executeScript(ping):
            logger.log({"Check internet ping":"".join(["Ping successfully to ",hostname," with interface ",interface])})
            return True
        else:
            logger.log({"Check internet ping":"".join(["Ping failed to ",hostname," with interface ",interface])}, logger.level.ERROR, MODULE, True)
            return False
    except Exception as error:
        logger.log({"Check internet ping":str(error)}, logger.level.ERROR, MODULE, True)
        return False

def checkInterfaceSpeedtest(interface:str)->bool:

    try:  
        
        # Fist check if interface exist
        if not interfaceExists(interface): return False
        
        # Get the Ip of the interface
        try:  interface_address = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]
        except KeyError: return False
        
        # Do the speedtest, if failed, the exception raises
        st = speedtest.Speedtest(config=None,source_address=interface_address)
        ip_id = "".join(["IP Interface - ",interface])
        speedtest_id = "".join(["Speedtest - ",interface])
        download =  round((st.download() / 1000000),2)

        payload = {
            ip_id:interface_address,
            speedtest_id:download,
        }

        # Check if download is not 0 Mb/s
        if download > 0:
            
            # After the test, upload the values to thingsboard
            http.thingsboard_post_request(payload, topic="Interface Speedtest")
            logger.log({"Successfull Speedtest":payload})
            return True

        logger.log({"Speedtest download is 0 Mb/s":payload}, logger.level.WARNING)
        return False
        
    except Exception as error:
        logger.log({"Check interface Speedtest":str(error), "Interface":interface}, logger.level.ERROR, MODULE, True)
        return False
