from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from dalybms import DalyBMS
import requests
import json
import time

# ==========================================================
# CONFIGURACIÓN DE CREDENCIALES Y PUERTOS
# ==========================================================
THINGSBOARD_HOST = "142.93.240.174"
THINGSBOARD_PORT = "8080"
ACCESS_TOKEN = "7iLUre7NX9lVluJrQKWr"  # Reemplaza con tu Token real

# Asignación estática de puertos para la prueba
BMS_PORT = '/dev/ttyUSB1'
MUST_PORT = '/dev/ttyUSB0'

tb_url = f"http://{THINGSBOARD_HOST}:{THINGSBOARD_PORT}/api/v1/{ACCESS_TOKEN}/telemetry"

# Diccionario vacío para recolectar todos los datos
payload = {}

# ==========================================================
# FASE 1: LECTURA DEL BMS DALY
# ==========================================================
print("[BMS] Conectando a la batería Daly...")
bms = DalyBMS()

try:
    bms.connect(BMS_PORT)
    data_bms = bms.get_soc()
    
    if data_bms and isinstance(data_bms, dict):
        payload["SOC - BMS"] = data_bms["soc_percent"]
        payload["Voltage - BMS"] = data_bms["total_voltage"]
        print(f"[BMS] Éxito -> SOC: {data_bms['soc_percent']}%, Voltaje: {data_bms['total_voltage']}V")
    else:
        print("[BMS] Error: No se recibieron datos válidos.")
except Exception as error:
    print(f"[BMS] Fallo crítico de comunicación: {error}")

# ==========================================================
# FASE 2: LECTURA DEL CONTROLADOR MUST
# ==========================================================
print("\n[MUST] Conectando al controlador solar...")
must_client = ModbusClient(method='rtu', port=MUST_PORT, baudrate=9600, timeout=1)
must_client.connect()
time.sleep(0.5)  # Pausa de estabilización

try:
    read = must_client.read_holding_registers(address=15206, count=1, unit=1)
    if not read.isError():
        voltaje_must = read.registers[0] / 10.0
        payload["Voltage - MUST"] = voltaje_must
        print(f"[MUST] Éxito -> Voltaje Inversor: {voltaje_must}V")
    else:
        print(f"[MUST] Error Modbus: {read}")
except Exception as error:
    print(f"[MUST] Fallo crítico de comunicación: {error}")
finally:
    must_client.close()

# ==========================================================
# FASE 3: ENVÍO UNIFICADO A LA NUBE
# ==========================================================
if payload:
    headers = {"Content-Type": "application/json"}
    print(f"\n[NUBE] Enviando paquete unificado a ThingsBoard...")
    print(f"[JSON] {json.dumps(payload)}")
    
    try:
        response = requests.post(tb_url, data=json.dumps(payload), headers=headers, timeout=5)
        if response.status_code == 200:
            print("[ÉXITO] ¡Toda la planta solar ha sido registrada en la nube!")
        else:
            print(f"[FALLO NUBE] Código de rechazo del servidor: {response.status_code}")
    except Exception as error:
        print(f"[ERROR RED] No se pudo conectar al servidor: {error}")
else:
    print("\n[CANCELADO] No se recolectó ningún dato del hardware.")
