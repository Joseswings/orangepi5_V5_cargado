#IMPORTANT: Use pymodbus version 2.5.3
import time
from pymodbus.client.sync import ModbusSerialClient

print("=== Leyendo Datos Reales del Must PC1800 desde CSV Mapeado ===")

# Conexión al puerto confirmado por dmesg
client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB1', baudrate=9600, timeout=1.5)

if client.connect():
    time.sleep(0.5)
    try:
        # LEER VOLTAJE DE BATERÍA (Registro 15202 según tu CSV)
        read_batt = client.read_holding_registers(address=15206, count=1, unit=1)
        
        # LEER VOLTAJE PA PANEL SOLAR (Registro 15201 por curiosidad)
        read_pv = client.read_holding_registers(address=15201, count=1, unit=1)
        
        if not read_batt.isError():
            v_bateria = read_batt.registers[0] / 10.0
            print(f"✓ Voltaje de Batería (Reg 15202): {v_bateria} V")
            
            # --- CÁLCULO ESTIMADO DE SOC EN BASE A VOLTAJE (Para sistemas de 24V) ---
            # Si tu sistema es de 24V, estimamos el SoC de forma segura:
            if v_bateria >= 26.5: soc_estimado = 100
            elif v_bateria <= 24.0: soc_estimado = 0
            else: soc_estimado = int((v_bateria - 24.0) * 40) # Mapeo simple de 24V a 26.5V
            
            print(f"✓ SoC Estimado de Batería: {soc_estimado}%")
        else:
            print("X Error leyendo el registro de Batería 15202.")
            
        if not read_pv.isError():
            print(f"✓ Voltaje de Paneles PV (Reg 15201): {read_pv.registers[0] / 10.0} V")

    except Exception as e:
        print(f"X Fallo en la comunicación: {e}")
        
    client.close()
else:
    print("No se pudo conectar al puerto /dev/ttyUSB1")
