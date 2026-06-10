import unittest
import sys
import os

# Asegurar que Python pueda encontrar los módulos de la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class TestThingsBoardConnection(unittest.TestCase):

    def test_send_telemetry_success(self):
        """Prueba que la función nativa send_telemetry_thingsboard realice envíos sin colapsar"""
        
        # Importación local para evitar colisiones e importaciones cíclicas en frío
        from services.json_controller import send_telemetry_thingsboard
        
        # Payload simulado para verificar canales de red
        payload_simulado = {
            "test_orpi_cpu_temp": 40.2,
            "test_bms_soc_percent": 89.5,
            "test_status": "Verificación Unittest en scheduled_tasks"
        }
        
        print("\n[UNITTEST] Despachando telemetría de prueba vía json_controller...")
        
        try:
            # Ejecutamos la función original que usa la OrangePi en producción
            # Si el token o la red fallan, internamente el sistema arrojará una excepción o un log
            send_telemetry_thingsboard(payload_simulado, name="Prueba Unittest")
            resultado_ejecucion = True
        except Exception as e:
            print(f"[ERROR EN TEST]: {e}")
            resultado_ejecucion = False
            
        self.assertTrue(
            resultado_ejecucion, 
            msg="La función send_telemetry_thingsboard falló al procesar el paquete."
        )

if __name__ == '__main__':
    unittest.main()