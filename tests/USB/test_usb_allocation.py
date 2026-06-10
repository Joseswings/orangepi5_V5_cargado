import asyncio
from services.usb_controller_async import USB_Serial
from services.loggers import logger

async def test_allocation():
    print("--- INICIANDO TEST DE PUERTOS USB ---")
    
    # 1. Forzamos el escaneo inicial
    await USB_Serial.initialize()
    puertos_disponibles = await USB_Serial.get_devices()
    print(f"Puertos físicos detectados: {puertos_disponibles}")
    
    if not puertos_disponibles:
        print("No se encontraron dispositivos seriales. Revisa los cables físicos.")
        return

    # 2. Simulamos que el BMS escanea y toma el suyo (Supongamos que es el primero)
    # En tu lógica real esto lo hace bms_controller, aquí lo forzamos para probar
    puerto_bms = puertos_disponibles[0]
    await USB_Serial.remove_device(puerto_bms, "BMS")
    print(f"-> BMS ha reservado el puerto: {puerto_bms}")
    
    # 3. Verificamos qué queda disponible
    puertos_restantes = await USB_Serial.get_devices()
    print(f"Puertos disponibles para el Inversor: {puertos_restantes}")
    
    # 4. Probamos la lógica del Inversor MUST/EPEVER
    # connect_solar_charge_controller iterará SOLO por los puertos_restantes
    print("-> Intentando conectar Controlador Solar...")
    controlador, tipo = await USB_Serial.get_solar_controller()
    
    if tipo:
        print(f"¡ÉXITO! {tipo} conectado en: {USB_Serial.devices['Solar_Charger']}")
    else:
        print("FALLO: Ningún inversor respondió en los puertos restantes.")
        
    print("\n--- ESTADO FINAL DEL POOL DE DISPOSITIVOS ---")
    print(USB_Serial.devices)

if __name__ == "__main__":
    asyncio.run(test_allocation())
