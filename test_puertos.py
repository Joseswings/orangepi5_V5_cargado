from services.usb_controller import USB_Serial
from services.must_controller import MustController

def probar_asignacion():
    print("--- 1. INICIANDO ESCANEO USB ---")
    usb = USB_Serial() # Esto dispara el detect_serial_devices()
    
    puertos = usb.get_devices()
    print(f"Puertos físicos detectados y disponibles: {puertos}")
    
    if len(puertos) == 0:
        print("ERROR: No se detectó ningún ttyUSB. Revisa cables.")
        return
        
    if len(puertos) == 1:
        print("ADVERTENCIA: Solo hay 1 puerto. Probaremos la reserva de todos modos.")

    print("\n--- 2. SIMULANDO CONEXIÓN DEL BMS ---")
    puerto_bms = puertos[0] # El BMS siempre suele agarrar el primero que encuentra
    print(f"BMS reclamando el puerto: {puerto_bms}")
    usb.remove_device(puerto_bms, "BMS")
    
    print(f"Puertos que sobraron para el Inversor: {usb.get_devices()}")
    
    print("\n--- 3. CONECTANDO INVERSOR (MUST/EPEVER) ---")
    # Esto internamente llamará a must.connect() usando SOLO los puertos que sobraron
    controlador, tipo = usb.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO REAL! Inversor {tipo} conectado en: {usb.devices['Solar_Charger']}")
    else:
        print("FALLO: El inversor no respondió a los comandos Modbus en los puertos restantes.")
        
    print("\n--- 4. ESTADO FINAL DE LA MEMORIA ---")
    print(f"Puertos sin usar: {usb.get_devices()}")
    print(f"Diccionario de dueños: {usb.devices}")

if __name__ == '__main__':
    probar_asignacion() from services.usb_controller import USB_Serial
from services.must_controller import MustController

def probar_asignacion():
    print("--- 1. INICIANDO ESCANEO USB ---")
    usb = USB_Serial() # Esto dispara el detect_serial_devices()
    
    puertos = usb.get_devices()
    print(f"Puertos físicos detectados y disponibles: {puertos}")
    
    if len(puertos) == 0:
        print("ERROR: No se detectó ningún ttyUSB. Revisa cables.")
        return
        
    if len(puertos) == 1:
        print("ADVERTENCIA: Solo hay 1 puerto. Probaremos la reserva de todos modos.")

    print("\n--- 2. SIMULANDO CONEXIÓN DEL BMS ---")
    puerto_bms = puertos[0] # El BMS siempre suele agarrar el primero que encuentra
    print(f"BMS reclamando el puerto: {puerto_bms}")
    usb.remove_device(puerto_bms, "BMS")
    
    print(f"Puertos que sobraron para el Inversor: {usb.get_devices()}")
    
    print("\n--- 3. CONECTANDO INVERSOR (MUST/EPEVER) ---")
    # Esto internamente llamará a must.connect() usando SOLO los puertos que sobraron
    controlador, tipo = usb.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO REAL! Inversor {tipo} conectado en: {usb.devices['Solar_Charger']}")
    else:
        print("FALLO: El inversor no respondió a los comandos Modbus en los puertos restantes.")
        
    print("\n--- 4. ESTADO FINAL DE LA MEMORIA ---")
    print(f"Puertos sin usar: {usb.get_devices()}")
    print(f"Diccionario de dueños: {usb.devices}")

if __name__ == '__main__':
    probar_asignacion()from services.usb_controller import USB_Serial
from services.must_controller import MustController

def probar_asignacion():
    print("--- 1. INICIANDO ESCANEO USB ---")
    usb = USB_Serial() # Esto dispara el detect_serial_devices()
    
    puertos = usb.get_devices()
    print(f"Puertos físicos detectados y disponibles: {puertos}")
    
    if len(puertos) == 0:
        print("ERROR: No se detectó ningún ttyUSB. Revisa cables.")
        return
        
    if len(puertos) == 1:
        print("ADVERTENCIA: Solo hay 1 puerto. Probaremos la reserva de todos modos.")

    print("\n--- 2. SIMULANDO CONEXIÓN DEL BMS ---")
    puerto_bms = puertos[0] # El BMS siempre suele agarrar el primero que encuentra
    print(f"BMS reclamando el puerto: {puerto_bms}")
    usb.remove_device(puerto_bms, "BMS")
    
    print(f"Puertos que sobraron para el Inversor: {usb.get_devices()}")
    
    print("\n--- 3. CONECTANDO INVERSOR (MUST/EPEVER) ---")
    # Esto internamente llamará a must.connect() usando SOLO los puertos que sobraron
    controlador, tipo = usb.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO REAL! Inversor {tipo} conectado en: {usb.devices['Solar_Charger']}")
    else:
        print("FALLO: El inversor no respondió a los comandos Modbus en los puertos restantes.")
        
    print("\n--- 4. ESTADO FINAL DE LA MEMORIA ---")
    print(f"Puertos sin usar: {usb.get_devices()}")
    print(f"Diccionario de dueños: {usb.devices}")

if __name__ == '__main__':
    probar_asignacion()
from services.usb_controller import USB_Serial
from services.must_controller import MustController

def probar_asignacion():
    print("--- 1. INICIANDO ESCANEO USB ---")
    usb = USB_Serial() # Esto dispara el detect_serial_devices()
    
    puertos = usb.get_devices()
    print(f"Puertos físicos detectados y disponibles: {puertos}")
    
    if len(puertos) == 0:
        print("ERROR: No se detectó ningún ttyUSB. Revisa cables.")
        return
        
    if len(puertos) == 1:
        print("ADVERTENCIA: Solo hay 1 puerto. Probaremos la reserva de todos modos.")

    print("\n--- 2. SIMULANDO CONEXIÓN DEL BMS ---")
    puerto_bms = puertos[0] # El BMS siempre suele agarrar el primero que encuentra
    print(f"BMS reclamando el puerto: {puerto_bms}")
    usb.remove_device(puerto_bms, "BMS")
    
    print(f"Puertos que sobraron para el Inversor: {usb.get_devices()}")
    
    print("\n--- 3. CONECTANDO INVERSOR (MUST/EPEVER) ---")
    # Esto internamente llamará a must.connect() usando SOLO los puertos que sobraron
    controlador, tipo = usb.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO REAL! Inversor {tipo} conectado en: {usb.devices['Solar_Charger']}")
    else:
        print("FALLO: El inversor no respondió a los comandos Modbus en los puertos restantes.")
        
    print("\n--- 4. ESTADO FINAL DE LA MEMORIA ---")
    print(f"Puertos sin usar: {usb.get_devices()}")
    print(f"Diccionario de dueños: {usb.devices}")

if __name__ == '__main__':
    probar_asignacion()from services.usb_controller import USB_Serial
from services.must_controller import MustController

def probar_asignacion():
    print("--- 1. INICIANDO ESCANEO USB ---")
    usb = USB_Serial() # Esto dispara el detect_serial_devices()
    
    puertos = usb.get_devices()
    print(f"Puertos físicos detectados y disponibles: {puertos}")
    
    if len(puertos) == 0:
        print("ERROR: No se detectó ningún ttyUSB. Revisa cables.")
        return
        
    if len(puertos) == 1:
        print("ADVERTENCIA: Solo hay 1 puerto. Probaremos la reserva de todos modos.")

    print("\n--- 2. SIMULANDO CONEXIÓN DEL BMS ---")
    puerto_bms = puertos[0] # El BMS siempre suele agarrar el primero que encuentra
    print(f"BMS reclamando el puerto: {puerto_bms}")
    usb.remove_device(puerto_bms, "BMS")
    
    print(f"Puertos que sobraron para el Inversor: {usb.get_devices()}")
    
    print("\n--- 3. CONECTANDO INVERSOR (MUST/EPEVER) ---")
    # Esto internamente llamará a must.connect() usando SOLO los puertos que sobraron
    controlador, tipo = usb.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO REAL! Inversor {tipo} conectado en: {usb.devices['Solar_Charger']}")
    else:
        print("FALLO: El inversor no respondió a los comandos Modbus en los puertos restantes.")
        
    print("\n--- 4. ESTADO FINAL DE LA MEMORIA ---")
    print(f"Puertos sin usar: {usb.get_devices()}")
    print(f"Diccionario de dueños: {usb.devices}")

if __name__ == '__main__':
    probar_asignacion()
