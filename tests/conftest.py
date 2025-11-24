import pytest
import os
import csv
from datetime import datetime


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Fixture que se ejecuta UNA SOLA VEZ al inicio de la sesión de pruebas.
    Inicializa las zonas necesarias para todos los tests.
    """
    zones_file = "data/zones.csv"
    
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Verificar si el archivo existe y tiene zonas
    zones_exist = False
    if os.path.exists(zones_file):
        with open(zones_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if len(rows) >= 2:  # Al menos 2 zonas
                zones_exist = True
    
    # Solo crear zonas si no existen
    if not zones_exist:
        with open(zones_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'nombre', 'tipo', 'fecha_creacion', 'elementos_asociados']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'id': '1',
                'nombre': 'Jardín Principal',
                'tipo': 'JARDIN',
                'fecha_creacion': '2025-11-19 10:00:00',

            })
            writer.writerow({
                'id': '2',
                'nombre': 'Lago Azul',
                'tipo': 'LAGO',
                'fecha_creacion': '2025-11-19 10:05:00',

            })
    
    yield
    
    # Cleanup después de todos los tests (opcional)
    # No eliminamos las zonas base para que puedan reutilizarse


def _read_csv_data(filepath):
    """Lee datos de un CSV y retorna lista de diccionarios"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _write_csv_data(filepath, fieldnames, data):
    """Escribe datos a un CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data():
    """
    Fixture que captura el estado inicial ANTES del test
    y elimina solo los registros nuevos DESPUÉS del test.
    """
    resources_file = "data/resources.csv"
    threats_file = "data/threats.csv"
    zones_file = "data/zones.csv"
    
    # Guardar estado inicial
    initial_resources = _read_csv_data(resources_file)
    initial_threats = _read_csv_data(threats_file)
    initial_zones = _read_csv_data(zones_file)
    
    initial_resource_ids = {r['id'] for r in initial_resources}
    initial_threat_ids = {t['id'] for t in initial_threats}
    initial_zone_ids = {z['id'] for z in initial_zones}
    
    yield  # Ejecutar el test
    
    # Después del test: restaurar solo datos iniciales (eliminar nuevos)
    current_resources = _read_csv_data(resources_file)
    current_threats = _read_csv_data(threats_file)
    current_zones = _read_csv_data(zones_file)
    
    # Filtrar solo registros que existían antes del test
    filtered_resources = [r for r in current_resources if r['id'] in initial_resource_ids]
    filtered_threats = [t for t in current_threats if t['id'] in initial_threat_ids]
    filtered_zones = [z for z in current_zones if z['id'] in initial_zone_ids]
    
    # Escribir de vuelta solo los registros originales
    if os.path.exists(resources_file):
        fieldnames = ['id','zona_id','nombre','tipo','cantidad_unitaria','peso',
                     'duracion_recoleccion','hormigas_requeridas','estado',
                     'hora_creacion','hora_recoleccion']
        _write_csv_data(resources_file, fieldnames, filtered_resources)
    
    if os.path.exists(threats_file):
        fieldnames = ['id','zona_id','nombre','tipo','costo_hormigas',
                     'estado','hora_deteccion','hora_resolucion']
        _write_csv_data(threats_file, fieldnames, filtered_threats)
    
    if os.path.exists(zones_file):
        fieldnames = ['id','nombre','tipo','fecha_creacion']
        _write_csv_data(zones_file, fieldnames, filtered_zones)
