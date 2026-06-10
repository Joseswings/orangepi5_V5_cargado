from usbid import USB

usb = USB()

for bus_key in usb.keys():
    bus = usb[bus_key]

    for port_key in bus.keys():
        try:
            port = bus[port_key]
            childs = int(port.maxchild) + 1
            
            # If not hub in Usb bus, detect if there is an serial port
            try:
                serial_device = port.interfaces[0].tty
                if "tty" in serial_device:
                    print(serial_device)    
            except:
                pass

            childs = int(port.maxchild) + 1

            for i in range(1,childs):
                try:
                    path = bus_key + '-1.' + str(i) + ':1.0'
                    hub_interface = usb.get_interface(path)

                    if "tty" in hub_interface.tty:
                        print(hub_interface.tty) 

                    #print(hub_interface.interface)
                    #print(hub_interface.modalias)
                    #print(hub_interface.manufacturer)
                    #print(hub_interface.product)
                    #print(hub_interface.bAlternateSetting)
                    #print(hub_interface.bInterfaceClass)
                    #print(hub_interface.bInterfaceNumber)
                    #print(hub_interface.bInterfaceProtocol)
                    #print(hub_interface.bInterfaceSubClass)
                    #print(hub_interface.bNumEndpoints)
                    #print(hub_interface.supports_autosuspend)
                    #print(hub_interface.uevent)
                except:
                    pass
        except:
            pass