import netifaces

print("eth0 ip:", netifaces.ifaddresses("eth0")[netifaces.AF_INET][0]["addr"])
print("wlan0 ip", netifaces.ifaddresses("eth0")[netifaces.AF_INET][0]["addr"])
