import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize("zona_id, payload", [
    (1, {"nombre": "Águila cazadora", "tipo": "AGUILA", "costo_hormigas": 5}),
    (2, {"nombre": "Serpiente venenosa", "tipo": "SERPIENTE", "costo_hormigas": 8}),
])
def test_crear_amenaza_exito(zona_id, payload):
    """T1: Debe crear una amenaza y devolver un ID con status 201"""
    response = client.post(f"/threats/zone/{zona_id}", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["nombre"] == payload["nombre"]
    assert data["tipo"] == payload["tipo"]
    assert data["zona_id"] == zona_id


def test_crear_amenaza_zona_inexistente():
    """T2: Debe devolver 404 si la zona no existe"""
    response = client.post("/threats/zone/9999", json={
        "nombre": "Amenaza fantasma",
        "tipo": "AGUILA",
        "costo_hormigas": 3
    })
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]["error"]


@pytest.mark.parametrize("payload, campo_faltante", [
    ({"tipo": "AGUILA", "costo_hormigas": 5}, "nombre"),
    ({"nombre": "Sin tipo", "costo_hormigas": 5}, "tipo"),
    ({"nombre": "Sin costo", "tipo": "SERPIENTE"}, "costo_hormigas"),
])
def test_crear_amenaza_datos_faltantes(payload, campo_faltante):
    """T3: Debe devolver 400 si falta un campo obligatorio"""
    response = client.post("/threats/zone/1", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.parametrize("costo_invalido", [0, -5])
def test_crear_amenaza_costo_invalido(costo_invalido):
    """T4: Debe devolver 400 si el costo es 0 o negativo"""
    response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza inválida",
        "tipo": "AGUILA",
        "costo_hormigas": costo_invalido
    })
    assert response.status_code == 400
    assert "error" in response.json()


def test_crear_amenaza_tipo_invalido():
    """T5: Debe rechazar tipos no válidos con 400 (sistema de enums estáticos)"""
    response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza desconocida",
        "tipo": "DINOSAURIO",
        "costo_hormigas": 10
    })
    # Con sistema de enums, solo tipos definidos son válidos
    assert response.status_code == 400


def test_listar_amenazas_retorna_lista():
    """T6: Debe devolver una lista de amenazas existentes con 200"""
    # Crear una amenaza primero
    client.post("/threats/zone/1", json={
        "nombre": "Amenaza test",
        "tipo": "AGUILA",
        "costo_hormigas": 5
    })
    
    response = client.get("/threats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_listar_amenazas_vacio():
    """T7: Debe devolver una lista vacía si no hay amenazas"""
    response = client.get("/threats")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_filtrar_amenazas_por_zona():
    """T8: Debe filtrar amenazas por zona_id"""
    response = client.get("/threats?zona_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_filtrar_amenazas_por_estado():
    """T9: Debe filtrar amenazas por estado"""
    response = client.get("/threats?estado=activa")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_obtener_amenaza_por_id_exito():
    """T10: Debe devolver los detalles de una amenaza existente"""
    # Crear amenaza primero
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza detalle",
        "tipo": "SERPIENTE",
        "costo_hormigas": 7
    })
    threat_id = create_response.json()["id"]

    response = client.get(f"/threats/{threat_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == threat_id
    assert data["nombre"] == "Amenaza detalle"


def test_obtener_amenaza_por_id_no_existe():
    """T11: Debe devolver 404 si la amenaza no existe"""
    response = client.get("/threats/9999")
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]["error"]


def test_actualizar_amenaza_a_en_combate():
    """T12: Debe actualizar el estado de una amenaza a 'en_combate'"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza combate",
        "tipo": "AGUILA",
        "costo_hormigas": 4
    })
    threat_id = create_response.json()["id"]

    # Actualizar a en_combate
    response = client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})
    assert response.status_code == 200


def test_actualizar_amenaza_a_resuelta():
    """T13: Debe actualizar el estado de una amenaza a 'resuelta' (pasando por en_combate)"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza resuelta",
        "tipo": "SERPIENTE",
        "costo_hormigas": 6
    })
    threat_id = create_response.json()["id"]

    # Primero actualizar a en_combate
    client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})

    # Luego actualizar a resuelta
    response = client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})
    assert response.status_code == 200
    data = response.json()
    assert "hora_resolucion" in data or data["estado"] == "resuelta"


def test_actualizar_amenaza_persistencia():
    """T14: Verificar persistencia después de actualizar"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza persistencia",
        "tipo": "AGUILA",
        "costo_hormigas": 3
    })
    threat_id = create_response.json()["id"]

    # Actualizar a en_combate primero
    client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})

    # Luego actualizar a resuelta
    client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})

    # Verificar persistencia
    get_response = client.get(f"/threats/{threat_id}")
    assert get_response.status_code == 200
    assert get_response.json()["estado"] == "resuelta"


def test_actualizar_amenaza_inexistente():
    """T15: Debe devolver 404 al intentar actualizar amenaza inexistente"""
    response = client.put("/threats/9999", json={"estado": "resuelta"})
    assert response.status_code == 404


def test_actualizar_amenaza_ya_resuelta():
    """T16: Debe responder 200 OK al intentar resolver amenaza ya resuelta (idempotencia)"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza ya resuelta",
        "tipo": "AGUILA",
        "costo_hormigas": 4
    })
    threat_id = create_response.json()["id"]

    # Actualizar a en_combate primero
    client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})

    # Actualizar a resuelta primera vez
    client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})

    # Intentar resolver de nuevo (idempotencia - ya está resuelta, se mantiene)
    response = client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})
    assert response.status_code == 200


def test_eliminar_amenaza_exito():
    """T17: Debe eliminar una amenaza existente y devolver 200"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza eliminar",
        "tipo": "AGUILA",
        "costo_hormigas": 5
    })
    threat_id = create_response.json()["id"]

    # Eliminar
    response = client.delete(f"/threats/{threat_id}")
    assert response.status_code == 200
    assert "message" in response.json()


def test_eliminar_amenaza_en_combate():
    """T18: Debe devolver 409 si la amenaza está en combate"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza en batalla",
        "tipo": "SERPIENTE",
        "costo_hormigas": 8
    })
    threat_id = create_response.json()["id"]

    # Actualizar a en_combate
    client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})

    # Intentar eliminar
    response = client.delete(f"/threats/{threat_id}")
    assert response.status_code == 409
    assert "no se puede eliminar" in response.json()["detail"]["error"]


def test_eliminar_amenaza_inexistente():
    """T19: Debe devolver 200 aunque la amenaza no exista (idempotente)"""
    response = client.delete("/threats/9999")
    assert response.status_code == 200


def test_transicion_estado_valida_combate_a_resuelta():
    """T20: Debe permitir transición de 'en_combate' a 'resuelta'"""
    # Crear amenaza
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza transición válida",
        "tipo": "SERPIENTE",
        "costo_hormigas": 6
    })
    threat_id = create_response.json()["id"]

    # Actualizar a en_combate
    response1 = client.put(f"/threats/{threat_id}", json={"estado": "en_combate"})
    assert response1.status_code == 200

    # Actualizar a resuelta (transición válida)
    response2 = client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})
    assert response2.status_code == 200
    
    # Verificar que el estado es resuelta
    get_response = client.get(f"/threats/{threat_id}")
    assert get_response.json()["estado"] == "resuelta"


def test_transicion_estado_invalida_activa_a_resuelta():
    """T21: Debe rechazar transición de 'activa' a 'resuelta' (409 Conflict)"""
    # Crear amenaza (estado inicial: activa)
    create_response = client.post("/threats/zone/1", json={
        "nombre": "Amenaza transición inválida",
        "tipo": "ARANA",
        "costo_hormigas": 3
    })
    threat_id = create_response.json()["id"]

    # Intentar cambiar directamente a resuelta (transición inválida)
    response = client.put(f"/threats/{threat_id}", json={"estado": "resuelta"})
    assert response.status_code == 409
    assert "error" in response.json()["detail"]
