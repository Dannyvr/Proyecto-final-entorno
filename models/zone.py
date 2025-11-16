from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class TipoZona(str, Enum):
    JARDIN = "JARDIN"
    LAGO = "LAGO"
    ARENA = "ARENA"
    ARBOL = "ARBOL"
    CASA = "CASA"
    PLANTA = "PLANTA"


@dataclass
class Zona:
    id: int
    nombre: str
    tipo: TipoZona
    fecha_creacion: datetime = None

    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
