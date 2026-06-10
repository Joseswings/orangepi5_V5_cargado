from pymodbus.client.sync import ModbusSerialClient as ModbusClient
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

# Configuración del puerto serial físico del controlador MUST
MUST_PORT = '/dev/ttyUSB0'
MUST_BAUDRATE = 9600

# URL de destino para la telemetría HTTP POST
tb_url = f"http://{THINGSBOARD_HOST}:{THINGSBOARD_PORT}/api/v1/{ACCESS_TOKEN}/telemetry"

# ==========================================================
# 2. LECTURA DEL HARDWARE (MODBUS RTU)
# ==========================================================
print("[HARDWARE] Conectando al controlador solar MUST...")
client = ModbusClient(method='rtu', port=MUST_PORT, baudrate=MUST_BAUDRATE, timeout=1)
client.connect()
time.sleep(1)  # Estabilización de la línea serial

voltaje_real = None

try:
    # Solicitamos el registro de voltaje de batería (15206) al esclavo 1
    read = client.read_holding_registers(address=15206, count=1, unit=1)
    
    if not read.isError():
        voltaje_bruto = read.registers[0]
        # Escalamos el valor decimal dividiendo entre 10.0
        voltaje_real = voltaje_bruto / 10.0
        print(f"[HARDWARE] Lectura exitosa: Batería a {voltaje_real} V")
    else:
        print(f"[ERROR HARDWARE] Error al leer Modbus: {read}")

except Exception as error:
    print(f"[ERROR HARDWARE] Fallo crítico leyendo el dispositivo: {error}")
finally:
    # Siempre cerramos el puerto serial para no dejarlo bloqueado
    client.close()

# ==========================================================
# 3. ENVÍO DE TELEMETRÍA A LA NUBE (HTTP POST)
# ==========================================================
# Solo procedemos al envío si la lectura de hardware fue exitosa
if voltaje_real is not None:
    # Estructuramos el JSON con el formato definitivo para el Dashboard
    payload = {
        "Voltage - MUST": voltaje_real
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"[NUBE] Enviando telemetría a ThingsBoard...")
    try:
        response = requests.post(tb_url, data=json.dumps(payload), headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("[ÉXITO] ¡Datos del MUST reflejados en ThingsBoard correctamente!")
        else:
            print(f"[FALLO NUBE] Servidor rechazó el paquete. Código: {response.status_code}")
            
    except Exception as error:
        print(f"[ERROR NUBE] No se pudo transmitir por internet: {error}")
else:
    print("[CANCELADO] No se envió telemetría debido a que falló la lectura del MUST.")
