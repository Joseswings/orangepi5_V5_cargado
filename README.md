
# Requirements

Download the lastest [Official Ubuntu Server Image Kernel 6.1](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-Pi-Zero-3.html) for the OrangePi Zero 3

* The image must match with the ram of the device
* SD card must not exceed 64 GB

Install the image into a SD card with [Win32 DiskImager](https://win32diskimager.org/).  

Supported Python versions: Python3.5 to Python3.10

Open a terminal and run with this command to check Python version:  

`python3 --version`

It must respond one of the Python version supported.   

If any of the supported Python version are not installed, then try to install using the official operating system documentation.




---
# GPIO used in OrangePi

![Pinout OrangePi](./docs/images/pinout.png)

These are the GPIO ports to used in Orange Pi

---
##### Communication
- RX # Port PC6
- TX # Port PC5
- ALERT_ESP      # Port PC 11
- RESET_EXPANDER # Port PC 9 
- CABINET        # Port PH 9
- INTERRUPT1     # Port PC 10 Interrupt Expander
- INTERRUPT2     # Port PH 6 Interrupt Expander

---
##### Side panel

- GREEN_LED # Port PH 7
- RED_LED   # Port PH 8
- BLUE_LED  # Port PC 7
- CHASIS    # Port PC 15
- SOFTWARE_BUTTON # Port PC 14
- HARDWARE_BUTTON # Port PC 8


---
##### GPIO Expander 

- GPA7 = GPIO 10 INVERSOR
- GPA6 = GPIO 14 MIKROTIK
- GPA5 = GPIO 13 S48V
- GPA4 = WARNING_INA_1     
- GPA3 = CRITICAL_INA_1    
- GPA2 = GPIO 16 FAN   
- GPA1 = GPIO FRIDGE 2 
- GPA0 = GPIO 6 AXU1   
- GPB6 = WARNING_INA_2 
- GPB7 = CRITICAL_INA_2
- GPB3 = GPIO 15 AUX3
- GPB4 = GPIO 0 AUX 2
- GPB5 = WARNING_INA_3 
- GPB2 = CRITICAL_INA_3
- GPB0 = A+_COM
- GPB1 = B-_COM

#### Wiring Pi

To have control of the GPIO is required to install the Py library [WiringPi](https://github.com/orangepi-xunlong/wiringOP-Python) 

![Wiring Pi](./docs/images/wiringpi.png)

The instructions for installing and test the library are in the Manual in the path `/docs/manuals`

Mapping the pinout is required, the library uses the wPi ID and the name of the pin is next to the wPi ID to verify if is the correct pin

---
# Installation

To access SSH into the OrangePi device from the local network, OpenVPN or Wireguard VPN Mikrotik Tunnel.

With a SFTP Client upload the file `/docs/Installation/Install_OrangePi.bash` into the root folder of the OrangePi 

And upload an unique OpenVPN file with the ID

To grant Execution permision to the file use the command `chmod u+x ./Install_OrangePi.bash`

Then execute the bash file with `./Install_OrangePi.bash`

* *Reboot is required after installation and configuration*


This installation file will:

- Enable the hardware interfaces of the Orange Pi
- Set the local timezone
- Install libraries for the Orange Pi
- Install the WiringPi-Python library
- Clone the repository
- Install the Python dependencies
- Create .env and crontab file

The final path of the proyect will be:

`/root/kingo-energy/V5-Controller`

* Path is required for the configuration of the crontab tasks

The Python dependencies are installed from the `requirements.txt` if a library don't install correctly from the installation bash, run the following command:

`pip install -r requirements.txt`

After the installation bash .env and crontab file will be created but configurations are needed.

Example of an `.env` and `crontab` file, replace the values surrounded by the characters "<   >" with the right values given by Ubidots platform: 

### .env Example

```

THINGSBOARD_DEVICE_TOKEN="<device-token>"
THINGSBOARD_HTTP_HOST="http://thingsboard.cloud"

ANTSTACK_HTTP_HOST="https://us-central1-stack-ant-prod.cloudfunctions.net"
ANTSTACK_HTTP_USER="123456789"
ANTSTACK_HTTP_PASSWORD="221144"

MIKROTIK_USER="SuperKingo"
MIKROTIK_PASSWORD="kingoadmin"
MIKROTIK_IP="192.170.0.1"
MIKROTIK_PORT="22"

LOCATION="<device-location>"
SHOPKEEPER_PHONE="<phone-number>"

WA_NOTIFICATIONS=0

BATTERY_TYPE="24V-Lithium"

```

#### Thingsboard token

The thingsboard token can be obtained at the moment of the creation of a device in the platform in the `Entities -> Devices -> Add New Devices` menu and create the new device with the name OrangePi- and the same ID of the OpenVPN file 

![ThingsBoard Add Device](./docs/images/thingsboard_add_device.png)

![ThingsBoard Credentials](./docs/images/thingsboard_credentials.png)

Copy the token and add it into the .env file

At the moment of the installation of the device set the Location and the Shopkeeper Phone

#### Battery types

- "24V-Lithium"
- "24V-Lead-Acid"
- "12V-Lithium"
- "12V-Lithium-Redodo"
- "12V-Lead-Acid"
- "12V-Lead-Acid-Autocraft"

### Crontab Example

To configure the crontab file use `crontab -e` and select option 1 to edit the file with `nano` and change the ID of the OpenVPN file uploaded into the root folder

```

@reboot python3 /root/kingo-energy/V5-Controller/tests/ON/ON.py
#@reboot python3 /root/kingo-energy/V5-Controller/encenderExpander.py
#@reboot python3 /root/kingo-energy/V5-Controller/run.py
@reboot openvpn --config OrangePi-<ID>.ovpn

```

- The ON.py turn ON the required GPIO to init the I2C slaves, required to init the Expander
- The run.py is the main controller of the V5 
- In case the run.py fails, the `encenderExpander.py` will turn on the essential pins of the V5 to provide remote conection to the OrangePi

---
# Deployment

To run the main program execute into the proyect folder:

`python3 run.py`

A V5 is required for the code to work due to I2C detections to load the slaves and principal controllers

Logs from the execution of the code are saved in the folder `/logs`

Logs are Time Rotated by day, from the last 10 days, the log of the actual day will appear as `run.log`

The rest of the logs will apear as `run.<date>.log`

---
# PM2

Use the following commands to manage the PM2 enviorement:

To init or stop the pm2 process

`pm2 <start|restart|stop> v5-controller` 

To show the status of the process and host metrics

`pm2 status` 

To show the output of the shell in real time and the last 15 entries

`pm2 log` 

To show more details of the V5-Controller process and the host metrics:

`pm2 monit `

---
#### PM2 logs


PM2 will create 2 log files of the execution of the process, the logs can be found using:

To show the output registered on the shell including log entries generated by the V5-Controller logger

`cat /root/.pm2/logs/v5-controller-out.log` 

To show the errors detected on the shell

`cat /root/.pm2/logs/v5-controller-error.log` 

---

# Testing 

To run the test file to check the integrity of the V5 enviorement run the following command on the project directory:


`python3 -m unittest`


The process will test all the features and components of the system. If a test fail, it will show up at the end of the execution and giving detail of what module did fail.

---
# Serial Communication

Connection to the OrangePi is able throught serial communication.

From Windows search the COM port on `Device Manager` then enter into the OrangePi setting the baudrate to 115200

To get SuperUser priviledges use the following command: 

`sudo su`

Enter the OrangePi credentials and then `cd /root` to access the main folder of the OrangePi and all the files

To exit from SuperUser Mode use `Ctrl + d`


---
# Open VPN (Server)

After installation you can check the [Open VPN Monitoring App](http://143.244.179.211/) to validate if after a reboot the OrangePi connects to the VPN

To create new OpenVPN files SSH into the server with the given credentials. Use `ls` to check the files created and check the last ID created

With `nano OpenVPN.bash` edit the script to create multiple OpenVPN files setting the `init_` and `end_` ID to create. Then save the file and execute `./OpenVPN.bash`

To get the OpenVPN files use SFTP and download all the .ovpn files and upload them into the corresponding Orange Pi

---
# I2C Slaves

The V5 works with many components that use I2C Slaves with the following addresses:

- `0x18` Temperature Sensor (In development)
- `0x20` GPIO Expander
- `0x2e` EMC (Fan Controller)
- `0x40` INA3221 #1
- `0x41` INA3221 #2
- `0x42` INA3221 #3
- `0x48` ADS

The OrangePi uses the bus #3 of the I2C and in the manual there is the following command to show all addresses detected in the bus

---
# USB Controller

The V5 Contains a USB-Hub, and multiple devices use USB connection for serial communication. The ttyUSB devices are assigned randomly, so for the V5-Controller there is a Usb-Controller that search all devices connected to the OrangePi directly to the usb port or throught the Usb-Hub in 1 level

* *Multiple hubs can be connected making multiple levels, but the code only search 1 level of usb-hub*

At the init of the code, the controller is going to seach the available devices and save them in a list, if any device is configured is going to be deleted from the available list and registered to the corresponding device, indicating that the serial device will be omited when testing other connections to the serial devices.

The battery controller is in `/services/dalybms_controller.py` and it's one of the principal device of the fuctioning of the system, giving the state of charge of the battery for the turn on/off of the system.

There are 2 models of the solar charge controller: Epever and MUST. Serial communication is used to send telemetry, so the usb controller is going to try detect what solar charge controller is connected and register it.

Since there is a Usb-Hub, multiple serial devices can be detected on the usb.

With the command `pyusb-chain --list --allinfo` will show the tree of the usb interface and will give the `ttyUSB#` device and info related with de device.

---
# BMS Battery


Info of the BMS battery can be obtained from the library.

To obtain all the info from the battery execute

`daly-bms-cli  -d /dev/ttyUSB<ID> --all`

To obtain only the SoC values execute

`daly-bms-cli -d /dev/ttyUSB<ID> --soc`

*Check with the usb chain ttyUSB devices detected and change the ID*


# Usb Wifi

With `ifconfig` extract the Mac Address of the Usb Wifi Adapter

To configure the Adapter execute the following command:

`nano /etc/udev/rules.d/70-persistent-net.rules`

Add the following line and give the Mac Address of the antena:

`SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="<Mac-Address>", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="wlan*", NAME="wlan1"`

---
# Test files

In the folder `./tests/*` will found several test files, to execute them, from the project folder use the following command 

`python3 /tests/<Device>/<Test-name>.py`

Actual tests folders are:

- ADS
- BMS
- EMC
- Expander
- GPIO
- INA
- Internet
- Mikrotik
- ON
- OFF
- rt485
- SolarCharger
- USB

---
# Ifmetric

To change priority of the default interface used by the OrangePi, with `sudo ifmetric <Interface> <Metric>` the priority order can be modified. 

The metric value means that a lower value is a higher priority.

By default the interface `wlan0` metric value is `600` and `eth0` metric value is `100`. 

In case the eth0 interface fails, priority can be changed and reverted with the command