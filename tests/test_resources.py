import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
from main import app

# PARA EJECUTAR ESTOS TESTS, USAR:
# pytest tests/test_resources.py -v

client = TestClient(app)


@pytest.mark.parametrize("zona_id, payload", [
    (1, {"nombre": "Semilla Girasol", "tipo": "SEMILLA", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}),
    (2, {"nombre": "Manzana", "tipo": "FRUTO", "cantidad_unitaria": 20, "peso": 10, "duracion_recoleccion": 30, "hormigas_requeridas": 5}),
])
def test_crear_recurso_exito(zona_id, payload):
    """T1: Debe crear un recurso y devolver un ID con status 201"""
    response = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response.status_code == 201
    data = response.json()
    validar_esquema_recurso(data)
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["zona_id"] == zona_id
    assert data["estado"] == "disponible"
    # Remover el recurso creado para no afectar otros tests
    client.delete(f"/resources/{data['id']}") 
    
    
def test_crear_recurso_zona_no_existe():
    """T2: Debe devolver 404 si la zona no existe al crear un recurso"""
    zona_id = 9999  # Zona que no existe
    payload = {"nombre": "Margarita", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}
    response = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert "no existe" in data["detail"]["error"]
    
    
@pytest.mark.parametrize("payload, campo_faltante", [
    ({"tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3},"nombre"),
    ({"nombre": "Orquidea", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3},"tipo"),
    ({"nombre": "Orquidea", "tipo": "FLOR", "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3},"cantidad_unitaria"),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "duracion_recoleccion": 15, "hormigas_requeridas": 3},"peso"),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "hormigas_requeridas": 3},"duracion_recoleccion"),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15},"hormigas_requeridas"),
])
def test_crear_recurso_datos_incompletos(payload, campo_faltante):
    """T3: Debe devolver 400 si faltan datos obligatorios al crear un recurso"""
    zona_id = 1  # Asumimos que esta zona existe
    response = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()
    
    
@pytest.mark.parametrize("payload, campos_invalidos", [
    ({"nombre": "", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}, ["nombre"]),
    ({"nombre": "Orquidea", "tipo": "LIQUIDO", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}, ["tipo"]),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": -5, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}, ["cantidad_unitaria"]),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": -1.0, "duracion_recoleccion": 15, "hormigas_requeridas": 3}, ["peso"]),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": -10, "hormigas_requeridas": 3}, ["duracion_recoleccion"]),
    ({"nombre": "Orquidea", "tipo": "FLOR", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": -2}, ["hormigas_requeridas"]),
])
def test_crear_recurso_datos_invalidos(payload, campos_invalidos):
    """T4: Debe devolver 400 si los datos son inválidos al crear un recurso"""
    zona_id = 1  # Asumimos que esta zona existe
    response = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

       
@pytest.mark.parametrize("payload, nombre_duplicado", [
    ({"nombre": "Avellana", "tipo": "SEMILLA", "cantidad_unitaria": 10, "peso": 5, "duracion_recoleccion": 15, "hormigas_requeridas": 3}, "Avellana"),
])
def test_crear_recurso_nombre_duplicado(payload, nombre_duplicado):
    """T5: Debe devolver 409 si el nombre del recurso ya existe en la zona"""
    zona_id = 1  # Asumimos que esta zona existe
    # Crear el recurso por primera vez
    response1 = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response1.status_code == 201
    
    # Intentar crear el mismo recurso nuevamente
    response2 = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert response2.status_code == 409
    
    # Remover el recurso creado para no afectar otros tests
    client.delete(f"/resources/{response1.json()['id']}")  

def validar_esquema_recurso(data: Dict[str, Any]):
    """T6: Valida que la respuesta del recurso tenga el esquema correcto"""
    assert isinstance(data["id"], int)
    assert isinstance(data["zona_id"], int)
    assert isinstance(data["nombre"], str)
    assert data["tipo"] in ["HOJA", "SEMILLA", "FLOR", "FRUTO", "NECTAR", "HONGO", "AGUA"]
    assert isinstance(data["cantidad_unitaria"], int)
    assert isinstance(data["peso"], int)
    assert isinstance(data["duracion_recoleccion"], int)
    assert isinstance(data["hormigas_requeridas"], int)
    assert data["estado"] in ["disponible", "en_recoleccion", "recolectado"]
    assert isinstance(data["hora_creacion"], str)
    if data["hora_recoleccion"] is not None:
        assert isinstance(data["hora_recoleccion"], str)
        
        
def test_listar_recursos():
    """T7: Debe listar todos los recursos con 200"""
    response = client.get("/resources")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for recurso in data:
        validar_esquema_recurso(recurso)
      
        
def test_listar_recursos_filtro_estado():
    """T8: Debe listar recursos filtrando por estado"""
    estado_filtro = "disponible"
    response = client.get(f"/resources?estado={estado_filtro}")
    assert response.status_code == 200
    data = response.json()
    for recurso in data:
        validar_esquema_recurso(recurso)
        assert recurso["estado"] == estado_filtro
        
        
def test_listar_recursos_filtro_zona():
    """T9: Debe listar recursos filtrando por zona_id"""
    zona_id_filtro = 1
    response = client.get(f"/resources?zona_id={zona_id_filtro}")
    assert response.status_code == 200
    data = response.json()
    for recurso in data:
        validar_esquema_recurso(recurso)
        assert recurso["zona_id"] == zona_id_filtro
        
        
def test_listar_recursos_vacio():
    """T10: Debe devolver una lista vacía si no hay recursos"""
    # Asumimos que la zona 9999 no tiene recursos
    zona_id = 9999
    response = client.get(f"/resources?zona_id={zona_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    
    
def test_obtener_recurso_por_id_exito():
    """T11: Debe obtener un recurso por ID con 200"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Hoja Roble", "tipo": "HOJA", "cantidad_unitaria": 15, "peso": 7, "duracion_recoleccion": 20, "hormigas_requeridas": 4}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Ahora obtenemos el recurso por ID
    response = client.get(f"/resources/{recurso_id}")
    assert response.status_code == 200
    data = response.json()
    validar_esquema_recurso(data)
    assert data["id"] == recurso_id
    assert data["nombre"] == "Hoja Roble"
    
    
def test_obtener_recurso_por_id_no_existe():
    """T12: Debe devolver 404 si el recurso no existe al obtener por ID"""
    recurso_id = 9999  # ID que no existe
    response = client.get(f"/resources/{recurso_id}")
    assert response.status_code == 404
    data = response.json()
    assert "no existe" in data["detail"]["error"]
   

def test_actualizar_estado_recurso_a_en_recoleccion():
    """T13: Debe actualizar el estado de un recurso a 'en_recoleccion'"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Flor Tulipan", "tipo": "FLOR", "cantidad_unitaria": 12, "peso": 6, "duracion_recoleccion": 25, "hormigas_requeridas": 4}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Ahora actualizamos el estado del recurso
    update_payload = {"estado": "en_recoleccion"}
    response = client.put(f"/resources/{recurso_id}", json=update_payload)
    assert response.status_code == 200
    

def test_actualizar_estado_recurso_a_recolectado():
    """T14: Debe actualizar el estado de un recurso a 'recolectado' (pasando por 'en_recoleccion') con 200"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Fruto Cereza", "tipo": "FRUTO", "cantidad_unitaria": 18, "peso": 9, "duracion_recoleccion": 30, "hormigas_requeridas": 5}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Primero actualizamos el estado a 'en_recoleccion'
    update_payload_en_recoleccion = {"estado": "en_recoleccion"}
    response_en_recoleccion = client.put(f"/resources/{recurso_id}", json=update_payload_en_recoleccion)
    assert response_en_recoleccion.status_code == 200
    
    # Ahora actualizamos el estado del recurso
    update_payload = {"estado": "recolectado"}
    response = client.put(f"/resources/{recurso_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    validar_esquema_recurso(data)
    assert data["id"] == recurso_id
    assert "hora_recoleccion" in data or data["estado"] == "recolectado"
    
    
def test_actualizar_estado_recurso_no_existe():
    """T15: Debe devolver 404 si el recurso no existe al actualizar estado"""
    recurso_id = 9999  # ID que no existe
    update_payload = {"estado": "en_recoleccion"}
    response = client.put(f"/resources/{recurso_id}", json=update_payload)
    assert response.status_code == 404
    data = response.json()
    assert "no existe" in data["detail"]["error"]
    
    
@pytest.mark.parametrize("cantidad_unitaria", [-1])
def test_actualizar_recurso_cantidad_invalida(cantidad_unitaria):
    """T16: Debe devolver 400 si la cantidad es negativa o mayor a la disponible"""
    
    # Recurso válido existente
    zona_id = 1
    payload = {
        "nombre": "Hoja Pino",
        "tipo": "HOJA",
        "cantidad_unitaria": 10,
        "peso": 4,
        "duracion_recoleccion": 15,
        "hormigas_requeridas": 3
    }
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    assert crear_response.status_code == 201
    recurso_id = crear_response.json()["id"]

    # Se intenta actualizar con cantidad inválida
    update_payload = {"cantidad_unitaria": cantidad_unitaria}
    response = client.put(f"/resources/{recurso_id}", json=update_payload)

    # Se devuelve 400 y el detalle del error
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

    # El recurso no debe haberse modificado
    get_response = client.get(f"/resources/{recurso_id}")
    assert get_response.status_code == 200
    assert get_response.json()["cantidad_unitaria"] == 10
    

def test_actualizar_recursos_persistencia():
    """T17: Verifica que los cambios en el recurso persisten después de la actualización"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Flor Rosa", "tipo": "FLOR", "cantidad_unitaria": 14, "peso": 7, "duracion_recoleccion": 20, "hormigas_requeridas": 4}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Actualizamos el estado del recurso
    update_payload = {"estado": "en_recoleccion"}
    client.put(f"/resources/{recurso_id}", json=update_payload)
    
    #Luego se actualiza el recurso a recolectado
    update_payload_recolectado = {"estado": "recolectado"}
    client.put(f"/resources/{recurso_id}", json=update_payload_recolectado)
    
    # Obtenemos el recurso nuevamente para verificar persistencia
    response_get = client.get(f"/resources/{recurso_id}")
    assert response_get.status_code == 200
    assert response_get.json()["estado"] == "recolectado"
    

def test_eliminar_recurso_exito():
    """T18: Debe eliminar un recurso existente y devolver 200"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Mango", "tipo": "FRUTO", "cantidad_unitaria": 25, "peso": 12, "duracion_recoleccion": 35, "hormigas_requeridas": 6}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Ahora eliminamos el recurso
    response = client.delete(f"/resources/{recurso_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    
def test_eliminar_recurso_no_existe():
    """T19: Debe devolver 200 si el recurso no existe al intentar eliminarlo"""
    recurso_id = 9999  # ID que no existe
    response = client.delete(f"/resources/{recurso_id}")
    assert response.status_code == 200
    

def test_reintentar_eliminar_recurso():
    """T20: Debe devolver 404 si se intenta eliminar un recurso ya eliminado"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Hoja de menta", "tipo": "HOJA", "cantidad_unitaria": 8, "peso": 3, "duracion_recoleccion": 10, "hormigas_requeridas": 2}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Ahora eliminamos el recurso
    response_delete = client.delete(f"/resources/{recurso_id}")
    assert response_delete.status_code == 200
    
    # Intentamos eliminar nuevamente el mismo recurso
    response_reintento = client.delete(f"/resources/{recurso_id}")
    assert response_reintento.status_code == 404
    

def test_validar_actualizacion_inventario_tras_eliminacion():
    """T21: Verifica que el inventario se actualiza correctamente tras eliminar un recurso"""
    # Primero creamos un recurso para obtener su ID
    zona_id = 1
    payload = {"nombre": "Fruto Kiwi", "tipo": "FRUTO", "cantidad_unitaria": 30, "peso": 15, "duracion_recoleccion": 40, "hormigas_requeridas": 7}
    crear_response = client.post(f"/resources/zone/{zona_id}", json=payload)
    recurso_id = crear_response.json()["id"]
    
    # Ahora eliminamos el recurso
    response_delete = client.delete(f"/resources/{recurso_id}")
    assert response_delete.status_code == 200
    
    # Verificamos que el recurso ya no aparece en el listado de recursos
    response_list = client.get("/resources")
    assert response_list.status_code == 200
    data = response_list.json()
    ids_recursos = [recurso["id"] for recurso in data]
    assert recurso_id not in ids_recursos
    