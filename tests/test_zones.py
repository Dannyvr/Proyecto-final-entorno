import pytest
import httpx
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


def test_eliminar_zona_exito():
    """Debe eliminar una zona existente y devolver 200"""
    # Primero crear una zona
    create_response = client.post("/zones", json={"nombre": "Eliminar", "tipo": "ARENA"})
    zone_id = create_response.json()["id"]

    # Luego eliminarla
    response = client.delete(f"/zones/{zone_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Zona eliminada con éxito"


def test_eliminar_zona_sin_id():
    """Debe devolver 400 si no se proporciona el ID"""
    response = client.delete("/zones/")
    assert response.status_code == 400
    assert "id" in response.json()["error"]


def test_eliminar_zona_inexistente():
    """Debe devolver 200 aunque el ID no exista"""
    response = client.delete("/zones/9999")
    assert response.status_code == 200
    assert response.json()["message"] == "Zona eliminada con éxito"


def test_eliminar_zona_con_elementos():
    """Debe devolver 409 si la zona tiene elementos asociados"""
    # Suponemos que esta zona tiene elementos asociados
    response = client.delete("/zones/10")
    assert response.status_code == 409
    assert "no se puede eliminar" in response.json()["error"]


def test_listar_zonas_retorna_lista():
    """Debe devolver una lista de zonas existentes con 200"""
    client.post("/zones", json={"nombre": "Zona Bosque", "tipo": "ARBOL"})
    response = client.get("/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("id" in zona for zona in data)
    assert all("nombre" in zona for zona in data)


def test_listar_zonas_vacio():
    """Debe devolver una lista vacía si no hay zonas"""
    # Borrar todas las zonas primero (simulado)
    response = client.get("/zones")
    data = response.json()
    if data:  # Si hay zonas, las eliminamos
        for z in data:
            client.delete(f"/zones/{z['id']}")

    response = client.get("/zones")
    assert response.status_code == 200
    assert response.json() == []


def test_obtener_zona_por_id_exito():
    """Debe devolver los detalles de una zona existente"""
    create_response = client.post("/zones", json={"nombre": "Zona Lago", "tipo": "LAGO"})
    zone_id = create_response.json()["id"]

    response = client.get(f"/zones/{zone_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == zone_id
    assert data["nombre"] == "Zona Lago"
    assert data["tipo"] == "LAGO"


def test_obtener_zona_por_id_no_existe():
    """Debe devolver 404 si la zona no existe"""
    response = client.get("/zones/9999")
    assert response.status_code == 404
    data = response.json()
    assert "no existe" in data["error"]
