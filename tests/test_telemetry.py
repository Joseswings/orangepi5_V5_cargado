import requests
import time
import json

# ==========================================================
# CONFIGURACIÓN DE CREDENCIALES
# ==========================================================
# La IP pública de tu servidor virtual en DigitalOcean
THINGSBOARD_HOST = "142.93.240.174" 
# Puerto estándar HTTP de ThingsBoard (suele ser el 8080)
THINGSBOARD_PORT = "8080"         

# REEMPLAZA ESTO: Pega aquí el Access Token que copiaste de ThingsBoard
ACCESS_TOKEN = "7iLUre7NX9lVluJrQKWr" 
# ==========================================================

# Construimos la URL oficial de telemetría de ThingsBoard
url = f"http://142.93.240.174:8080/api/v1/7iLUre7NX9lVluJrQKWr/telemetry"

# Simulamos los datos que obtuvimos en los pasos anteriores:
# El voltaje de 26.2 V que leíste del MUST y un porcentaje estimado de carga (SOC)
payload = {
    "Voltage - MUST": 26.2,
    "SOC - BMS": 35.0
}

headers = {
    "Content-Type": "application/json"
}

print(f"[INFO] Intentando enviar datos a {url}...")
print(f"[DATOS] {json.dumps(payload)}")

try:
    # Realizamos la petición POST enviando el JSON
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5)
    
    # HTTP 200 significa que ThingsBoard recibió y aceptó el JSON
    if response.status_code == 200:
        print("[ÉXITO] ¡Telemetría enviada correctamente a ThingsBoard!")
        print(f"Respuesta del servidor: {response.status_code} OK")
    else:
        print(f"[FALLO] El servidor respondió con un error: {response.status_code}")
        print(f"Detalle: {response.text}")

except requests.exceptions.Timeout:
    print("[ERROR] Tiempo de espera agotado. Verifica que ThingsBoard esté corriendo y que el puerto 8080 esté abierto en el servidor.")
except requests.exceptions.ConnectionError:
    print("[ERROR] No se pudo conectar al servidor. Revisa el internet de la Orange Pi o la dirección IP.")
except Exception as error:
    print(f"[ERROR] Ocurrió un fallo inesperado: {error}")
