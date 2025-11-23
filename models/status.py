from dataclasses import dataclass
from typing import List, Dict


@dataclass
class StatusInfo:
    """Información de un estado genérico"""
    codigo: str
    nombre: str
    descripcion: str
    categoria: str  # 'recurso' o 'amenaza'


def get_all_statuses(categoria: str = None) -> List[Dict[str, str]]:
    """
    Retorna todos los estados disponibles desde el CSV.
    Si se proporciona categoria, filtra por 'recurso' o 'amenaza'.
    """
    from repositories.status_repository import StatusRepository
    
    repo = StatusRepository()
    statuses = repo.get_all(categoria)
    
    return [
        {
            "codigo": status.codigo,
            "nombre": status.nombre,
            "descripcion": status.descripcion,
            "categoria": status.categoria
        }
        for status in statuses
    ]
