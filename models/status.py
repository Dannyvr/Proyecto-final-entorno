from dataclasses import dataclass
from typing import List, Dict


@dataclass
class StatusInfo:
    """Información de un estado genérico"""
    codigo: str
    nombre: str
    descripcion: str
    categoria: str  # 'recurso' o 'amenaza'


# Catálogo de estados fijos (hardcoded)
STATUSES_CATALOG: List[StatusInfo] = [
    # Estados de Recurso
    StatusInfo(
        codigo="disponible",
        nombre="Disponible",
        descripcion="Recurso listo para ser recolectado",
        categoria="recurso"
    ),
    StatusInfo(
        codigo="en_recoleccion",
        nombre="En recolección",
        descripcion="Recurso siendo recolectado por hormigas trabajadoras",
        categoria="recurso"
    ),
    StatusInfo(
        codigo="recolectado",
        nombre="Recolectado",
        descripcion="Recurso completamente recolectado y almacenado",
        categoria="recurso"
    ),
    # Estados de Amenaza
    StatusInfo(
        codigo="activa",
        nombre="Activa",
        descripcion="Amenaza detectada y presente en la zona",
        categoria="amenaza"
    ),
    StatusInfo(
        codigo="en_combate",
        nombre="En combate",
        descripcion="Amenaza siendo enfrentada por las hormigas defensoras",
        categoria="amenaza"
    ),
    StatusInfo(
        codigo="resuelta",
        nombre="Resuelta",
        descripcion="Amenaza neutralizada o eliminada",
        categoria="amenaza"
    ),
]


def get_all_statuses(categoria: str = None) -> List[Dict[str, str]]:
    """
    Retorna todos los estados disponibles.
    Si se proporciona categoria, filtra por 'recurso' o 'amenaza'.
    """
    statuses = STATUSES_CATALOG
    
    if categoria:
        statuses = [s for s in statuses if s.categoria == categoria.lower()]
    
    return [
        {
            "codigo": status.codigo,
            "nombre": status.nombre,
            "descripcion": status.descripcion,
            "categoria": status.categoria
        }
        for status in statuses
    ]
