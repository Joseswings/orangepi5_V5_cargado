
import datetime

from os import system
from pathlib import Path

from services.ssh_controller import SSH
from services.http_service import whatsapp_post_request
from services.loggers import logger
from env_config import env

class Mikrotik():

    MODULE = "mikrotik"

    ip       = env.MIKROTIK_IP
    port     = env.MIKROTIK_PORT
    user     = env.MIKROTIK_USER
    password = env.MIKROTIK_PASSWORD

    downtime_start = None

    client = SSH()

    def __new__(cls):
        return cls

    @classmethod
    def ssh_mikrotik(cls):
        "Funtion to open a connection to the Mikrotik using SSH controller and reuse the function"
        cls.client.open_ssh(cls.ip, cls.port, cls.user, cls.password)

    @classmethod
    def get_users_data(cls)->object:
        try:
            cls.ssh_mikrotik()
            json = cls.client.get_json("/import flash/scripts/usersScheduler.rsc")
            return json, True
        
        except: return None, False
        
    @classmethod
    def upload_scripts(cls):
        try:
            cls.ssh_mikrotik()
            cls.client.open_sftp()
            
            local_path =  "".join([str(Path(__file__).resolve().parent.parent), "/docs/scripts"])
            remote_path = "flash/scripts"
            files = ["usersUptime.rsc","usersProfiles.rsc","usersScheduler.rsc"]

            cls.client.upload_files(local_path, remote_path, files)
            logger.log("Mikrotik files uploaded")
            return True
        
        except Exception as error:
            logger.log({"Mikrotik SFTP transfer":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False
    
    @classmethod
    def check_users_in_schedule(cls):
        try:
            cls.ssh_mikrotik()
            
            users_json = cls.client.get_json("/import flash/scripts/usersProfiles.rsc")
            scheduled_json = cls.client.get_json("/import flash/scripts/usersScheduler.rsc")

            users_list, schedule_list = [], []
            not_scheduled = []

            for user in users_json:  users_list.append(user["user"])

            for schedule in scheduled_json:  schedule_list.append(schedule["user"])

            for user in users_list:
                if user not in schedule_list: not_scheduled.append(user)

            for user in not_scheduled:
                script = "/ip hotspot user remove [find name=" + str(user) +"]"

                cls.client.execute_script(script)
                logger.log({"User deleted":user})

            cls.client.close_ssh()
        
        except Exception as error: logger.log({"Mikrotik clear scheduler failed":str(error)}, logger.level.ERROR, cls.MODULE, True)

    @classmethod
    def modify_all_schedulers(cls,days, hours, minutes):
        try:
            cls.ssh_mikrotik()
            schedulers = cls.client.get_json("/import flash/scripts/usersScheduler.rsc")

            for user in schedulers:
                try:
                    old_date = "".join([user["startDate"]," ",user["startTime"]])

                    new_date = datetime.datetime.strptime(old_date,"%Y-%m-%d %H:%M:%S")
                    new_date = new_date + datetime.timedelta(days=days,hours=hours,minutes=minutes)
                    new_date = str(new_date).split(" ")

                    script = f'/system scheduler set [find name="{user["user"]}"] start-date="{ new_date[0] }" start-time="{ new_date[1] }'
                    
                    # TODO Modificar por downtime solo despues de las 8 am

                    if cls.client.execute_script(script):
                        logger.log({"User Schedule modified":user["user"],"old date":old_date,"new_date": "".join([new_date[0]," ",new_date[1]])})
                
                except Exception as error: logger.log({"Mikrotik modify scheduler":str(error), "user":str(user)}, logger.level.ERROR, cls.MODULE, True)

            cls.client.close_ssh()

        except Exception as error: logger.log({"Mikrotik modify all scheduler failed":str(error)}, logger.level.ERROR, cls.MODULE, True)

    @classmethod
    def notify_users_session_expiration_whatsapp(cls):
        """"""
        try:

            cls.ssh_mikrotik()
            users_info = cls.client.get_json("/import flash/scripts/usersUptime.rsc")

            for user in users_info:
                try:
                    if len(user["user"]) != 8: return

                    number = "".join(["502" , user["user"] ,"@s.whatsapp.net"])
                    time_left = str(user["timeLeft"])

                    if "w" in time_left or "d" in time_left: continue
                    
                    time_left = datetime.datetime.strptime(time_left, "%H:%M:%S")
                    time_left = time_left.time()

                    message = " ".join(["Buenos días, este es un mensaje automático. Tu sesión de KingoNet está por expirar en ", str(time_left)])

                    user_json = {
                        "numero":number,
                        "mensaje":message
                    }

                    whatsapp_post_request(user_json)
                
                except Exception as error: logger.log({"Mikrotik WA send expiration notification to user":str(error), "user":user["user"] }, logger.level.ERROR, cls.MODULE, True)
            
        except Exception as error: logger.log({"Mikrotik notify session expiration":str(error)}, logger.level.ERROR, cls.MODULE, True)

    @classmethod
    def set_downtime(cls):
        """Function to save the time when critical state has been activated"""
        try:
            timestamp = datetime.datetime.today()
            cls.downtime_start = timestamp
            logger.log({"Downtime started at":timestamp.strftime("%Y-%m-%d %H:%M:%S")})
        
        except Exception as error: logger.log({"Mikrotik set downtime":str(error)}, logger.level.ERROR, cls.MODULE, True)

    
    @classmethod
    def restore_downtime(cls):
        try:
            if cls.downtime_start is None: return
            
            restore_time = datetime.datetime.today()
            add_time = restore_time - cls.downtime_start
            
            days = add_time.days
            seconds = add_time.seconds

            if days == 0 and seconds < 60: 
                cls.downtime_start = None
                return
            
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)

            logger.log({
                "Restoring downtime":str(add_time),
                "Downtime Start":cls.downtime_start.strftime("%Y-%m-%d %H:%M:%S"),
                "Downtime End":restore_time.strftime("%Y-%m-%d %H:%M:%S")
            })

            cls.modify_all_schedulers(days=days,hours=hours,minutes=minutes)
            cls.downtime_start = None

        except Exception as error:
            logger.log({"Mikrotik restore downtime":str(error)}, logger.level.ERROR, cls.MODULE, True)
            cls.downtime_start = None
    
    @classmethod
    def shutdown(cls):
        
        script = "system shutdown"

        try:
            cls.ssh_mikrotik()
            cls.client.execute_script(script)
            logger.log("Mikrotik successful shutdown")
            cls.client.close_ssh()
            system("reboot")
        except Exception as error: logger.log({"Mikrotik shutdown":str(error)}, logger.level.ERROR, cls.MODULE, True)


    @classmethod
    def reboot(cls)->bool:
        
        script = "system reboot"

        try:
            cls.ssh_mikrotik()
            cls.client.execute_script(script)
            logger.log("Mikrotik successful reboot")
            cls.client.close_ssh()
            return True
        except Exception as error:
            logger.log({"Mikrotik reboot":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False