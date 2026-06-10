import paramiko
import json

import env_config
from services.loggers import logger


class SSH():

    MODULE = "ssh"

    ssh_client = paramiko.SSHClient()
    sftp_client = None

    def __new__(cls):
        return cls

    @classmethod
    def open_ssh(cls, hostname:str, port:int, username:str, password:str):
        try:
            cls.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cls.ssh_client.connect(hostname = hostname,
                                   port = port, 
                                   username = username,
                                   password = password,
                                   timeout = 10)
            return True
        except Exception as error:
            logger.log({"SSH connect":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False
    
    @classmethod
    def close_ssh(cls):
        cls.ssh_client.close()

    @classmethod
    def open_sftp(cls):
        cls.sftp_client = cls.ssh_client.open_sftp()

    @classmethod
    def close_sftp(cls):
        cls.sftp_client.close()
        cls.ssh_client.close()
 
    @classmethod
    def get_file(cls,
                 local_path:str,
                 remote_path:str)->bool:
        try:
            cls.open_sftp()
            cls.sftp_client.get(remote_path,local_path)
            cls.close_sftp()
            return True
        except Exception as error:
            logger.log({"SSH get file":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return False

    @classmethod
    def upload_files(cls, 
                    local_path:str, 
                    remote_path:str, 
                    files:list )->bool:
        try:
            cls.open_sftp()

            try:
                
                directories = remote_path.split("/")
                actual_path = ""

                # Check all the directories to reach the final path
                for next_directory in directories:
                    actual_path = "/".join([actual_path, next_directory])

                    # Check if directory exists
                    try: cls.sftp_client.mkdir(actual_path)
                    except Exception as error: pass

            except Exception as error: logger.log({"SFTP create remote directory":str(error)}, logger.level.ERROR, cls.MODULE, True)
            
            for file_name in files:
                try:
                    local_file = local_path + "/" +  file_name
                    remote_file = remote_path + "/" + file_name

                    cls.sftp_client.put(local_file,remote_file)
                    
                except Exception as error: pass

            cls.close_sftp()
            return True
        except Exception as error: logger.log({"SSH upload":str(error)}, logger.level.ERROR, cls.MODULE, True)
        
    @staticmethod
    def get_ssh_client():
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname= env_config.MIKROTIK_IP,
                               port=env_config.MIKROTIK_PORT, 
                               username=env_config.MIKROTIK_USER,
                               password=env_config.MIKROTIK_PASSWORD,
                               timeout=10)
        
            return ssh_client,True
        except:
            return None, False

    @classmethod
    def execute_script(cls, script:str)->bool:
        try:
            stdin, stdout, stderr = cls.ssh_client.exec_command(script)

            stdout_value = stdout.readlines()
            stdout_len:int = len(stdout_value)

            stderr_value = stderr.readlines()
            stderr_len:int = len(stderr_value)

            if stderr_len > 0 or stdout_len > 0:
                logger.log({"sdterr":str(stderr_value),"stdout":str(stdout_value)}, logger.level.WARNING)
                return False

            return True
        
        except Exception as error: logger.log({"SSH execute script":str(error)}, logger.level.ERROR, cls.MODULE, True)
    
    @classmethod
    def get_json(cls, script:str)->dict|None:

        try:
            stdin, stdout, stderr = cls.ssh_client.exec_command(script)
            stdout_value = stdout.readlines()
            stdout_len:int = len(stdout_value)

            stderr_value = stderr.readlines()
            stderr_len:int = len(stderr_value)

            json_data:dict|None = None
            
            if stderr_len > 0:
                logger.log({"SSH get JSON stderr value found":str(error)}, logger.level.ERROR, cls.MODULE, True)
                return json_data
            
            json_data = stdout_value[:-2]
            json_data = "".join(json_data).replace("\r\n","").replace("}{","},{")
            json_data = json.loads(json_data)

            return json_data

        except Exception as error:
            logger.log({"SSH get JSON":str(error)}, logger.level.ERROR, cls.MODULE, True)
            return None