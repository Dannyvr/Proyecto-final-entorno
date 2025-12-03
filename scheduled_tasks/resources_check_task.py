import requests

from models.resource import EstadoRecurso, Resource, TipoRecurso
from repositories.resource_repository import ResourceRepository

def resources_completion_task():
    print("Iniciando tarea programada: resources_completion_task")
    
    #get_updates()

def get_updates():
    url = "https://<<ENDPOINT>>/api/zones"
    response = requests.get(url)
    response.raise_for_status()

    responsa_payload = response.json()

    for detail in responsa_payload:
        print(f"Zone ID: {detail['zone_id']} - Status: {detail['status']}")
        zone_id = detail['zone_id']
        resource_id = detail['resource_id']
        resource_name = detail['resource_name']
        resource_type = detail['resource_type']
        if detail['status'] == 'completed':
            type = TipoRecurso(resource_type)
            resource = Resource(
                id=resource_id,
                zona_id=zone_id,
                nombre=resource_name,
                tipo=resource_type,
                cantidad_unitaria=0,
                peso=0,
                duracion_recoleccion=0,
                hormigas_requeridas=0,
                estado=EstadoRecurso.RECOLECTADO
            )

            resource_repo = ResourceRepository()
            resource_repo.update(resource.id, resource)
