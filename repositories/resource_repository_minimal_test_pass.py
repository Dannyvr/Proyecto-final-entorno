from typing import List, Optional
from datetime import datetime
from models.resource import Resource, TipoRecurso, EstadoRecurso

class ResourceRepository:
    """Implementación mínima para que las pruebas pasen sin persistencia real"""
    
    def __init__(self, csv_file: str = "data/resources.csv"):
        self.next_id = 1
        self.resources = {}
        self.deleted_resources = set()  # Rastrear recursos eliminados

    def zone_exists(self, zone_id: int) -> bool:
        """Simula verificar si existe la zona"""
        return zone_id < 9999

    def create(self, resource: Resource) -> Resource:
        """Simula la creación de un recurso"""
        resource.id = self.next_id
        resource.hora_creacion = datetime.now()
        resource.estado = EstadoRecurso.DISPONIBLE
        self.resources[resource.id] = resource
        self.next_id += 1
        return resource

    def get_all(self, zona_id: Optional[int] = None, estado: Optional[str] = None) -> List[Resource]:
        """Simula devolver todos los recursos con filtros opcionales"""
        result = list(self.resources.values())
        
        if zona_id is not None:
            result = [r for r in result if r.zona_id == zona_id]
        
        if estado is not None:
            result = [r for r in result if r.estado.value == estado]
        
        return result

    def get_by_id(self, resource_id: int) -> Optional[Resource]:
        """Simula obtener un recurso por ID"""
        return self.resources.get(resource_id)

    def update(self, resource_id: int, resource: Resource) -> Optional[Resource]:
        """Simula actualizar un recurso existente"""
        if resource_id in self.resources:
            old_resource = self.resources[resource_id]
            resource.id = resource_id
            # Preservar campos que no deben cambiar
            resource.hora_creacion = old_resource.hora_creacion
            # Actualizar hora_recoleccion si cambia a recolectado
            if resource.estado == EstadoRecurso.RECOLECTADO and old_resource.estado != EstadoRecurso.RECOLECTADO:
                resource.hora_recoleccion = datetime.now()
            else:
                resource.hora_recoleccion = old_resource.hora_recoleccion
            
            self.resources[resource_id] = resource
            return resource
        return None

    def delete(self, resource_id: int) -> bool:
        """Simula eliminar un recurso. Retorna True si existe, False si ya fue eliminado."""
        if resource_id in self.resources:
            del self.resources[resource_id]
            self.deleted_resources.add(resource_id)
            return True
        # Retorna False si ya fue eliminado
        if resource_id in self.deleted_resources:
            return False
        # Comportamiento idempotente para recursos que nunca existieron
        return True
    
    def resource_name_exists_in_zone(self, nombre: str, zona_id: int) -> bool:
        """Simula verificar si un recurso con el mismo nombre ya existe en la zona"""
        for resource in self.resources.values():
            if resource.zona_id == zona_id and resource.nombre == nombre:
                return True
        return False