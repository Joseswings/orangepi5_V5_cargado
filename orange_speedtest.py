import psutil
import speedtest

interfaces = psutil.net_if_addrs()
#print(list(interfaces.keys()))

net_interfaces = ["wlan0","wlan1","eth0"]

for interface in net_interfaces:
    #print(interfaces[interface])

    try:
        for protocol in list(interfaces[interface]):
            if protocol.family == 2:
                interface_address = protocol.address
                print("Speedtest on interface ", interface, " with ip ", interface_address, end=": ")
                st = speedtest.Speedtest(config=None,source_address=interface_address)
                print(round((st.download() / 1000000),2), "Mb/s", end="\n\n")
    except Exception as error:
        print(error)
