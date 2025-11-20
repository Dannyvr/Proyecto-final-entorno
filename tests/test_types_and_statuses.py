import pytest
from fastapi.testclient import TestClient
from main import app

# PARA EJECUTAR ESTOS TESTS, USAR:
# pytest tests/test_types_and_statuses.py -v

client = TestClient(app)


# ============================================
# TESTS PARA STATUSES (FIJOS)
# ============================================

def test_obtener_todos_los_estados():
    """Debe retornar todos los estados (recursos + amenazas) con 200"""
    response = client.get("/statuses")
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que es una lista con 6 estados (3 recurso + 3 amenaza)
    assert isinstance(data, list)
    assert len(data) == 6
    
    # Verificar estructura
    for status in data:
        assert "codigo" in status
        assert "nombre" in status
        assert "descripcion" in status
        assert "categoria" in status
        assert status["categoria"] in ["recurso", "amenaza"]


def test_filtrar_estados_por_categoria_recurso():
    """Debe filtrar estados de recurso"""
    response = client.get("/statuses?categoria=recurso")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    assert all(s["categoria"] == "recurso" for s in data)
    codigos = [s["codigo"] for s in data]
    assert "disponible" in codigos
    assert "en_recoleccion" in codigos
    assert "recolectado" in codigos


def test_filtrar_estados_por_categoria_amenaza():
    """Debe filtrar estados de amenaza"""
    response = client.get("/statuses?categoria=amenaza")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    assert all(s["categoria"] == "amenaza" for s in data)
    codigos = [s["codigo"] for s in data]
    assert "activa" in codigos
    assert "en_combate" in codigos
    assert "resuelta" in codigos


def test_estados_categoria_invalida():
    """Debe retornar 400 si la categoría no es válida"""
    response = client.get("/statuses?categoria=invalida")
    assert response.status_code == 400
    assert "error" in response.json()["detail"]


def test_estados_son_inmutables():
    """Los estados no deben cambiar entre llamadas"""
    response1 = client.get("/statuses")
    response2 = client.get("/statuses")
    
    assert response1.json() == response2.json()


# ============================================
# TESTS PARA TYPES (DINÁMICOS - CRUD)
# ============================================

def test_crear_tipo_zona_exito():
    """Debe crear un tipo de zona con 201"""
    payload = {
        "codigo": "BOSQUE",
        "nombre": "Bosque",
        "descripcion": "Área arbolada con vegetación densa",
        "categoria": "zona"
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["codigo"] == "BOSQUE"
    assert data["categoria"] == "zona"
    assert "fecha_creacion" in data
    
    # Limpiar
    client.delete(f"/types/{data['id']}")


def test_crear_tipo_recurso_exito():
    """Debe crear un tipo de recurso con 201"""
    payload = {
        "codigo": "MIEL",
        "nombre": "Miel",
        "descripcion": "Néctar procesado por abejas",
        "categoria": "recurso"
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert data["codigo"] == "MIEL"
    assert data["categoria"] == "recurso"
    
    # Limpiar
    client.delete(f"/types/{data['id']}")


def test_crear_tipo_amenaza_exito():
    """Debe crear un tipo de amenaza con 201"""
    payload = {
        "codigo": "OSO",
        "nombre": "Oso",
        "descripcion": "Mamífero grande depredador",
        "categoria": "amenaza"
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert data["codigo"] == "OSO"
    assert data["categoria"] == "amenaza"
    
    # Limpiar
    client.delete(f"/types/{data['id']}")


def test_crear_tipo_codigo_duplicado():
    """Debe retornar 409 si el código ya existe en la misma categoría"""
    # Usar código único para cada ejecución
    import time
    codigo_unico = f"DUP{int(time.time() * 1000) % 10000}"
    
    payload = {
        "codigo": codigo_unico,
        "nombre": "Duplicado",
        "descripcion": "Test duplicado",
        "categoria": "zona"
    }
    
    # Crear primera vez
    response1 = client.post("/types", json=payload)
    assert response1.status_code == 201
    type_id = response1.json()["id"]
    
    # Intentar crear nuevamente
    response2 = client.post("/types", json=payload)
    assert response2.status_code == 409
    assert "error" in response2.json()["detail"]
    
    # Limpiar
    client.delete(f"/types/{type_id}")


def test_crear_tipo_categoria_invalida():
    """Debe retornar 400 si la categoría no es válida"""
    payload = {
        "codigo": "INVALIDO",
        "nombre": "Inválido",
        "descripcion": "Test categoría inválida",
        "categoria": "invalido"
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 400


def test_crear_tipo_codigo_minusculas():
    """Debe retornar 400 si el código no está en mayúsculas"""
    payload = {
        "codigo": "minusculas",
        "nombre": "Minúsculas",
        "descripcion": "Test código en minúsculas",
        "categoria": "zona"
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 400


def test_crear_tipo_datos_faltantes():
    """Debe retornar 400 si faltan campos obligatorios"""
    payload = {
        "codigo": "FALTA",
        "nombre": "Sin descripción"
        # Falta descripcion y categoria
    }
    response = client.post("/types", json=payload)
    assert response.status_code == 400


def test_listar_tipos_todos():
    """Debe listar todos los tipos sin filtro"""
    # Crear algunos tipos
    tipos = [
        {"codigo": "TEST1", "nombre": "Test 1", "descripcion": "Desc 1", "categoria": "zona"},
        {"codigo": "TEST2", "nombre": "Test 2", "descripcion": "Desc 2", "categoria": "recurso"},
    ]
    ids = []
    for tipo in tipos:
        resp = client.post("/types", json=tipo)
        ids.append(resp.json()["id"])
    
    # Listar
    response = client.get("/types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Limpiar
    for id_ in ids:
        client.delete(f"/types/{id_}")


def test_listar_tipos_filtrar_por_categoria():
    """Debe filtrar tipos por categoría"""
    # Crear tipos de diferentes categorías
    tipo_zona = {"codigo": "TESTZ", "nombre": "Zona", "descripcion": "Desc", "categoria": "zona"}
    tipo_recurso = {"codigo": "TESTR", "nombre": "Recurso", "descripcion": "Desc", "categoria": "recurso"}
    
    resp1 = client.post("/types", json=tipo_zona)
    resp2 = client.post("/types", json=tipo_recurso)
    id1 = resp1.json()["id"]
    id2 = resp2.json()["id"]
    
    # Filtrar por zona
    response = client.get("/types?categoria=zona")
    assert response.status_code == 200
    zonas = [t for t in response.json() if t["id"] == id1]
    assert len(zonas) == 1
    assert zonas[0]["categoria"] == "zona"
    
    # Limpiar
    client.delete(f"/types/{id1}")
    client.delete(f"/types/{id2}")


def test_obtener_tipo_por_id_exito():
    """Debe obtener un tipo por ID con 200"""
    payload = {"codigo": "GETID", "nombre": "Get ID", "descripcion": "Test", "categoria": "zona"}
    create_resp = client.post("/types", json=payload)
    type_id = create_resp.json()["id"]
    
    response = client.get(f"/types/{type_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == type_id
    assert data["codigo"] == "GETID"
    
    # Limpiar
    client.delete(f"/types/{type_id}")


def test_obtener_tipo_inexistente():
    """Debe retornar 404 si el tipo no existe"""
    response = client.get("/types/99999")
    assert response.status_code == 404
    assert "error" in response.json()["detail"]


def test_actualizar_tipo_exito():
    """Debe actualizar nombre y descripción con 200"""
    # Crear tipo
    payload = {"codigo": "UPDATE", "nombre": "Original", "descripcion": "Desc original", "categoria": "zona"}
    create_resp = client.post("/types", json=payload)
    type_id = create_resp.json()["id"]
    
    # Actualizar
    update_payload = {"nombre": "Actualizado", "descripcion": "Nueva descripción"}
    response = client.put(f"/types/{type_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Actualizado"
    assert data["descripcion"] == "Nueva descripción"
    assert data["codigo"] == "UPDATE"  # No debe cambiar
    
    # Limpiar
    client.delete(f"/types/{type_id}")


def test_actualizar_tipo_inexistente():
    """Debe retornar 404 si el tipo no existe"""
    update_payload = {"nombre": "Actualizado"}
    response = client.put("/types/99999", json=update_payload)
    assert response.status_code == 404


def test_eliminar_tipo_exito():
    """Debe eliminar un tipo con 200"""
    # Crear tipo
    payload = {"codigo": "DELETE", "nombre": "Delete", "descripcion": "Test", "categoria": "zona"}
    create_resp = client.post("/types", json=payload)
    type_id = create_resp.json()["id"]
    
    # Eliminar
    response = client.delete(f"/types/{type_id}")
    assert response.status_code == 200
    assert "eliminado" in response.json()["message"]
    
    # Verificar que fue eliminado
    get_resp = client.get(f"/types/{type_id}")
    assert get_resp.status_code == 404


def test_eliminar_tipo_inexistente():
    """Debe retornar 200 (idempotente) si el tipo no existe"""
    response = client.delete("/types/99999")
    assert response.status_code == 200
    assert "idempotente" in response.json()["message"]


# ============================================
# TESTS DE INTEGRACIÓN
# ============================================

def test_flujo_completo_crud_tipo():
    """Test de flujo completo: crear, leer, actualizar, eliminar"""
    # 1. Crear
    payload = {"codigo": "FLUJO", "nombre": "Flujo", "descripcion": "Test flujo", "categoria": "amenaza"}
    create_resp = client.post("/types", json=payload)
    assert create_resp.status_code == 201
    type_id = create_resp.json()["id"]
    
    # 2. Leer
    get_resp = client.get(f"/types/{type_id}")
    assert get_resp.status_code == 200
    
    # 3. Actualizar
    update_resp = client.put(f"/types/{type_id}", json={"nombre": "Flujo Actualizado"})
    assert update_resp.status_code == 200
    
    # 4. Verificar actualización
    get_resp2 = client.get(f"/types/{type_id}")
    assert get_resp2.json()["nombre"] == "Flujo Actualizado"
    
    # 5. Eliminar
    delete_resp = client.delete(f"/types/{type_id}")
    assert delete_resp.status_code == 200
    
    # 6. Verificar eliminación
    get_resp3 = client.get(f"/types/{type_id}")
    assert get_resp3.status_code == 404
