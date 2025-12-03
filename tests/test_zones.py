import pytest
from fastapi.testclient import TestClient
from main import app

# PARA EJECUTAR ESTOS TESTS, USAR:
# pytest tests/test_zones.py -v

client = TestClient(app)


@pytest.mark.parametrize("payload", [
    {"id": 11, "nombre": "Zona Jardín", "tipo": "JARDIN"},
    {"id": 12, "nombre": "Zona del Lago", "tipo": "LAGO"},
])
def test_crear_zona_exito(payload):
    """Debe crear una zona y devolver status 201"""
    response = client.post("/zones", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["nombre"] == payload["nombre"]
    assert data["tipo"] == payload["tipo"]
    assert "fecha_creacion" in data
    # remover la zona creada para no afectar otros tests
    client.delete(f"/zones/{data['id']}")


@pytest.mark.parametrize("payload", [
    {"tipo": "JARDIN"},  # Falta nombre
    {"nombre": "Zona sin tipo"},  # Falta tipo
    {},  # Falta ambos
])
def test_crear_zona_datos_faltantes(payload):
    """Debe devolver 400 si falta un campo obligatorio"""
    response = client.post("/zones", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Datos inválidos o faltantes" in response.json()["error"]


def test_eliminar_zona_exito():
    """Debe eliminar una zona existente y devolver 200"""
    # Crear primero
    create_response = client.post("/zones", json={"id": 110, "nombre": "Eliminar", "tipo": "ARENA"})
    assert create_response.status_code == 201
    zone_id = create_response.json()["id"]

    # Eliminar
    response = client.delete(f"/zones/{zone_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Zona {zone_id} eliminada con éxito"


def test_eliminar_zona_inexistente():
    """Debe devolver 404 si el ID no existe"""
    response = client.delete("/zones/9999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data["detail"]
    assert "no existe" in data["detail"]["error"]


def test_listar_zonas_retorna_lista():
    """Debe devolver una lista de zonas existentes con 200"""
    client.post("/zones", json={"id": 200, "nombre": "Zona Bosque", "tipo": "ARBOL"})
    response = client.get("/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("id" in zona for zona in data)
    assert all("nombre" in zona for zona in data)
    assert all("tipo" in zona for zona in data)
    #remover la zona creada para no afectar otros tests
    client.delete("/zones/200")

def test_listar_zonas_por_tipo():
    """Debe devolver una lista de zonas filtradas por tipo"""
    # Crear zonas de diferentes tipos
    client.post("/zones", json={"id": 400, "nombre": "Zona Playa", "tipo": "ARENA"})
    client.post("/zones", json={"id": 401, "nombre": "Zona Montaña", "tipo": "ROCA"})

    response = client.get("/zones/tipo/ARENA")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(zona["tipo"] == "ARENA" for zona in data)

    # Remover las zonas creadas para no afectar otros tests
    client.delete("/zones/400")
    client.delete("/zones/401")


def test_obtener_zona_por_id_exito():
    """Debe devolver los detalles de una zona existente"""
    create_response = client.post("/zones", json={"id": 300, "nombre": "Zona Lago", "tipo": "LAGO"})
    assert create_response.status_code == 201
    zone_id = create_response.json()["id"]

    response = client.get(f"/zones/{zone_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == zone_id
    assert data["nombre"] == "Zona Lago"
    assert data["tipo"] == "LAGO"
    # remover la zona creada para no afectar otros tests
    client.delete(f"/zones/{zone_id}")


def test_obtener_zona_por_id_no_existe():
    """Debe devolver 404 si la zona no existe"""
    response = client.get("/zones/99999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data["detail"]
    assert "no existe" in data["detail"]["error"]
