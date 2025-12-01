"""
Script de prueba para el sistema de generación automática de recursos.
Este script verifica que todos los componentes estén funcionando correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path (subir un nivel desde tests/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.resource import TipoRecurso, EstadoRecurso
from config.resources_scheduler_config import ResourcesSchedulerConfig
from services.resource_scheduler import ResourceScheduler

def test_config():
    """Prueba que la configuración se cargue correctamente"""
    print("=== Test de Configuración ===")
    print(f"✓ Intervalo: {ResourcesSchedulerConfig.INTERVAL_SECONDS} segundos")
    print(f"✓ Zona por defecto: {ResourcesSchedulerConfig.DEFAULT_ZONE_ID}")
    print(f"✓ Auto-inicio: {ResourcesSchedulerConfig.AUTO_START}")
    print(f"✓ Tipos de recursos: {[t.value for t in ResourcesSchedulerConfig.RESOURCE_TYPES]}")
    print(f"✓ Nombres: {ResourcesSchedulerConfig.RESOURCE_NAMES}")
    print(f"✓ Cantidades: {ResourcesSchedulerConfig.RESOURCE_QUANTITIES}")
    print(f"✓ Pesos: {ResourcesSchedulerConfig.RESOURCE_WEIGHTS}")
    print(f"✓ Duraciones de recolección: {ResourcesSchedulerConfig.RESOURCE_COLLECTION_DURATIONS}")
    print(f"✓ Hormigas requeridas: {ResourcesSchedulerConfig.RESOURCE_ANT_REQUIREMENTS}")
    print()
    
def test_resource_types():
    """Prueba que los nuevos tipos de recursos existan"""
    print("=== Test de Tipos de Recursos ===")
    required_types = [TipoRecurso.HOJA, TipoRecurso.SEMILLA, TipoRecurso.FLOR,
                      TipoRecurso.FRUTO, TipoRecurso.NECTAR, TipoRecurso.HONGO,
                      TipoRecurso.AGUA]
    for tipo in required_types:
        print(f"✓ {tipo.value} existe")
    print()
    
def test_scheduler_creation():
    """Prueba que el scheduler se pueda crear"""
    print("=== Test de Creación del Scheduler ===")
    scheduler = ResourceScheduler()
    print(f"✓ Scheduler creado")
    print(f"✓ Estado inicial: {scheduler.get_status()}")
    print()
    
def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("=" * 50)
    print("PRUEBAS DEL SISTEMA DE GENERACIÓN DE RECURSOS")
    print("=" * 50)
    print()
    
    try:
        test_config()
        test_resource_types()
        test_scheduler_creation()
        
        print("=" * 50)
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 50)
        print()
        print("Para probar el sistema completo:")
        print("1. Ejecuta: uvicorn main:app --reload")
        print("2. Observa los logs para ver los recursos generándose")
        print("3. Visita: http://localhost:8000/resources/scheduler/status")
        print()
        
    except AssertionError as e:
        print("=" * 50)
        print("❌ ERROR EN LAS PRUEBAS")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    run_all_tests()