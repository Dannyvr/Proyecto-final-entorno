import pytest
from fastapi.testclient import TestClient
from main import app

# PARA EJECUTAR ESTOS TESTS, USAR EL COMANDO: pytest tests/test_zones.py

client = TestClient(app)

@pytest.mark.parametrize("payload", [
    {"nombre": "Zona Jardín", "tipo": "JARDIN"},
    {"nombre": "Zona del Lago", "tipo": "LAGO"},
])
def test_crear_zona_exito(payload):
    """Debe crear una zona y devolver un ID con status 200"""
    response = client.post("/zones", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)


@pytest.mark.parametrize("payload, campo_faltante", [
    ({"tipo": "JARDIN"}, "nombre"),
    ({"nombre": "Zona sin tipo"}, "tipo"),
    ({}, "nombre y tipo")
])
def test_crear_zona_datos_faltantes(payload, campo_faltante):
    """Debe devolver 400 si falta un campo obligatorio"""
    response = client.post("/zones", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert campo_faltante in data["error"]
