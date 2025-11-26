"""
Script de prueba para el sistema de generación automática de amenazas.
Este script verifica que todos los componentes estén funcionando correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path (subir un nivel desde tests/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.threat import TipoAmenaza, EstadoAmenaza
from config.scheduler_config import SchedulerConfig
from services.threat_scheduler import ThreatScheduler

def test_config():
    """Prueba que la configuración se cargue correctamente"""
    print("=== Test de Configuración ===")
    print(f"✓ Intervalo: {SchedulerConfig.INTERVAL_SECONDS} segundos")
    print(f"✓ Zona por defecto: {SchedulerConfig.DEFAULT_ZONE_ID}")
    print(f"✓ Auto-inicio: {SchedulerConfig.AUTO_START}")
    print(f"✓ Tipos de amenazas: {[t.value for t in SchedulerConfig.THREAT_TYPES]}")
    print(f"✓ Nombres: {SchedulerConfig.THREAT_NAMES}")
    print(f"✓ Costos: {SchedulerConfig.THREAT_COSTS}")
    print()

def test_threat_types():
    """Prueba que los nuevos tipos de amenazas existan"""
    print("=== Test de Tipos de Amenazas ===")
    required_types = [TipoAmenaza.ARANA, TipoAmenaza.ABEJA, TipoAmenaza.SALTAMONTES]
    for tipo in required_types:
        print(f"✓ {tipo.value} existe")
    print()

def test_scheduler_creation():
    """Prueba que el scheduler se pueda crear"""
    print("=== Test de Creación del Scheduler ===")
    scheduler = ThreatScheduler()
    print(f"✓ Scheduler creado")
    print(f"✓ Estado inicial: {scheduler.get_status()}")
    print()

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("=" * 50)
    print("PRUEBAS DEL SISTEMA DE GENERACIÓN DE AMENAZAS")
    print("=" * 50)
    print()
    
    try:
        test_config()
        test_threat_types()
        test_scheduler_creation()
        
        print("=" * 50)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 50)
        print()
        print("Para probar el sistema completo:")
        print("1. Ejecuta: uvicorn main:app --reload")
        print("2. Observa los logs para ver las amenazas generándose")
        print("3. Visita: http://localhost:8000/threats/scheduler/status")
        print()
        
    except Exception as e:
        print("=" * 50)
        print("❌ ERROR EN LAS PRUEBAS")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
