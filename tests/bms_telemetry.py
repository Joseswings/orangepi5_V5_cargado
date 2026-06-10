from dalybms import DalyBMS
import requests
import json
import time

# ==========================================================
# 1. CONFIGURACIÓN DE CREDENCIALES Y HARDWARE
# ==========================================================
# Configuración del servidor ThingsBoard en tu VPS
THINGSBOARD_HOST = "142.93.240.174"
THINGSBOARD_PORT = "8080"
# Coloca aquí el Token de tu dispositivo en ThingsBoard
ACCESS_TOKEN = "7iLUre7NX9lVluJrQKWr" 

# IMPORTANTE: Aquí asignamos el puerto USB del BMS.
# Si el MUST está en ttyUSB0, el BMS debería ser ttyUSB1.
BMS_PORT = '/dev/ttyUSB0' 

tb_url = f"http://{THINGSBOARD_HOST}:{THINGSBOARD_PORT}/api/v1/{ACCESS_TOKEN}/telemetry"

# ==========================================================
# 2. LECTURA DE LA BATERÍA DALY BMS
# ==========================================================
print("[HARDWARE] Conectando a la batería Daly BMS...")
bms = DalyBMS()

soc_percent = None
voltage_bms = None

try:
    # Intentamos abrir el puerto serial asignado al adaptador de la batería
    bms.connect(BMS_PORT)
    
    # Solicitamos el diccionario de estado de carga (igual que en tu bms_controller.py)
    data_bms = bms.get_soc()
    
    if data_bms and isinstance(data_bms, dict):
        soc_percent = data_bms["soc_percent"]
        voltage_bms = data_bms["total_voltage"]
        print(f"[HARDWARE] Lectura exitosa de la batería:")
        print(f"  -> Porcentaje (SOC): {soc_percent}%")
        print(f"  -> Voltaje BMS: {voltage_bms} V")
    else:
        print("[ERROR HARDWARE] El BMS respondió, pero no devolvió un formato de datos válido.")

except Exception as error:
    print(f"[ERROR HARDWARE] Fallo crítico al comunicarse con el BMS Daly: {error}")
    print("[TIP] Verifica si el puerto correcto es /dev/ttyUSB0 o /dev/ttyUSB1 usando el comando 'ls /dev/ttyUSB*'.")

# ==========================================================
# 3. ENVÍO DE TELEMETRÍA A THINGSBOARD (HTTP POST)
# ==========================================================
# Solo disparamos el paquete si logramos extraer los datos de la batería
if soc_percent is not None and voltage_bms is not None:
    payload = {
        "SOC - BMS": soc_percent,
        "Voltage - BMS": voltage_bms
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n[NUBE] Enviando telemetría de la batería a ThingsBoard...")
    try:
        response = requests.post(tb_url, data=json.dumps(payload), headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("[ÉXITO] ¡Porcentaje y Voltaje de la batería reflejados en ThingsBoard!")
        else:
            print(f"[FALLO NUBE] El servidor rechazó los datos del BMS. Código: {response.status_code}")
            
    except Exception as error:
        print(f"[ERROR NUBE] No se pudo transmitir por internet: {error}")
else:
    print("\n[CANCELADO] No se envió telemetría debido a un fallo en la lectura física del BMS.")
