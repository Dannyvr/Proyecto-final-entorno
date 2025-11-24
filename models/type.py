from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Type:
    """Modelo genérico para tipos (zona, recurso, amenaza)"""
    id: int
    codigo: str
    nombre: str
    descripcion: str
    categoria: str  # 'zona', 'recurso', 'amenaza'
    fecha_creacion: datetime = None

    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
