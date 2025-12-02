from typing import List, Optional
from models.resource import Resource, TipoRecurso, EstadoRecurso
from datetime import datetime
import os
import csv

class ResourceRepository:
    def __init__(self, csv_file: str = "data/resources.csv"):
        self.csv_file = csv_file
        self._ensure_file_exists()
        # Registrar IDs que fueron eliminados en esta instancia (para distinguir "nunca existió" vs "ya eliminado")
        self._deleted_ids = set()

    def _ensure_file_exists(self):
        """Crea el archivo CSV si no existe"""
        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id','zona_id','nombre','tipo','cantidad_unitaria','peso','duracion_recoleccion','hormigas_requeridas','estado','hora_creacion','hora_recoleccion'])

    def get_all(self, zona_id: Optional[int] = None, estado: Optional[str] = None) -> List[Resource]:
        """Lee todos los registros del CSV con filtros opcionales"""
        resources = []
        if not os.path.exists(self.csv_file):
            return resources

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                resource = self._dict_to_model(row)
                if zona_id is not None and resource.zona_id != zona_id:
                    continue
                if estado is not None and resource.estado.value != estado:
                    continue
                resources.append(resource)
        return resources
        
    def _dict_to_model(self, data: dict) -> Resource:
        """Convierte un diccionario a modelo Resource"""
        return Resource(
            id=int(data['id']),
            zona_id=int(data['zona_id']),
            nombre=data['nombre'],
            tipo=TipoRecurso(data['tipo']),
            cantidad_unitaria=int(data['cantidad_unitaria']),
            peso=int(data['peso']),
            duracion_recoleccion=int(data['duracion_recoleccion']),
            hormigas_requeridas=int(data['hormigas_requeridas']),
            estado=EstadoRecurso(data['estado']),
            hora_creacion=datetime.fromisoformat(data['hora_creacion']) if data['hora_creacion'] else None, # type: ignore
            hora_recoleccion=datetime.fromisoformat(data['hora_recoleccion']) if data.get('hora_recoleccion') and data['hora_recoleccion'] else None
        )

    def _model_to_dict(self, resource: Resource) -> dict:
        """Convierte un modelo Resource a diccionario"""
        return {
            'id': resource.id,
            'zona_id': resource.zona_id,
            'nombre': resource.nombre,
            'tipo': resource.tipo.value,
            'cantidad_unitaria': resource.cantidad_unitaria,
            'peso': resource.peso,
            'duracion_recoleccion': resource.duracion_recoleccion,
            'hormigas_requeridas': resource.hormigas_requeridas,
            'estado': resource.estado.value,
            'hora_creacion': resource.hora_creacion.isoformat() if resource.hora_creacion else '',
            'hora_recoleccion': resource.hora_recoleccion.isoformat() if resource.hora_recoleccion else ''
        }
        
    def _save_all(self, resources: List[Resource]):
        """Guarda todos los registros en el CSV"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id','zona_id','nombre','tipo','cantidad_unitaria','peso','duracion_recoleccion','hormigas_requeridas','estado','hora_creacion','hora_recoleccion']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in resources:
                writer.writerow(self._model_to_dict(r))
    
    def create(self, resource: Resource) -> Resource:
        """Crea un nuevo recurso y lo guarda en el CSV"""
        resources = self.get_all()
        resource.id = max([r.id for r in resources], default=0) + 1
        resources.append(resource)
        self._save_all(resources)
        return resource
    
    def resource_name_exists_in_zone(self, nombre: str, zona_id: int) -> bool:
        """Verifica si un recurso con el mismo nombre ya existe en la zona"""
        resources = self.get_all(zona_id=zona_id)
        for resource in resources:
            if resource.nombre == nombre:
                return True
        return False
    
    def get_by_id(self, resource_id: int) -> Optional[Resource]:
        """Obtiene un recurso por su ID"""
        resources = self.get_all()
        for resource in resources:
            if resource.id == resource_id:
                return resource
        return None
    
    def update(self, resource_id: int, updated_resource: Resource) -> Optional[Resource]:
        """Actualiza un recurso existente"""
        resources = self.get_all()
        for idx, resource in enumerate(resources):
            if resource.id == resource_id:
                resources[idx] = updated_resource
                self._save_all(resources)
                return updated_resource
        return None
    
    def delete(self, resource_id: int) -> str:
        """Elimina un recurso por su ID.
        Retorna:
          - 'deleted' si se eliminó ahora,
          - 'already_deleted' si ya fue eliminado antes en esta instancia,
          - 'never_existed' si nunca hubo un recurso con ese ID.
        """
        resources = self.get_all()
        for idx, resource in enumerate(resources):
            if resource.id == resource_id:
                del resources[idx]
                self._save_all(resources)
                self._deleted_ids.add(resource_id)
                return "deleted"
        # no está en el CSV
        if resource_id in self._deleted_ids:
            return "already_deleted"
        return "never_existed"