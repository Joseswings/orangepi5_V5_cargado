import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

print("Iniciando prueba de lectura Modbus en la Orange Pi...")

# === CORREGIDO: Cambiamos 'port' a '/dev/ttyUSB0' ===
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)

if client.connect():
    print("¡Conexión serial exitosa en /dev/ttyUSB0!")
    time.sleep(1)
    
    try:
        # Leer el registro del controlador Must
        read = client.read_holding_registers(address=0x2777, count=2, unit=1)
        
        if not read.isError():
            print("--- DATOS RECIBIDOS AFIRMATIVOS ---")
            print(f"Lista de registros: {read.registers}")
            print(f"Porcentaje de batería (Registro 0x2777): {read.registers[0]}%")
        else:
            print("Error al leer los registros Modbus (Respuesta vacía o incorrecta)")
            
    except Exception as e:
        print(f"Ocurrió un error durante la lectura: {e}")
        
    client.close()
else:
    print("No se pudo abrir el puerto /dev/ttyUSB0. Revisa que el cable esté bien conectado o que tengas permisos.")
