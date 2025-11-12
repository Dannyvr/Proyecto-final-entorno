from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class TipoRecurso(str, Enum):
    HOJA = "HOJA"
    SEMILLA = "SEMILLA"
    FLOR = "FLOR"
    FRUTO = "FRUTO"


class EstadoRecurso(str, Enum):
    DISPONIBLE = "disponible"
    EN_RECOLECCION = "en_recoleccion"
    RECOLECTADO = "recolectado"


@dataclass
class Resource:
    id: int
    zona_id: int
    nombre: str
    tipo: TipoRecurso
    cantidad_unitaria: int
    peso: int
    duracion_recoleccion: int
    hormigas_requeridas: int
    estado: EstadoRecurso = EstadoRecurso.DISPONIBLE
    hora_creacion: datetime = None
    hora_recoleccion: Optional[datetime] = None

    def __post_init__(self):
        if self.hora_creacion is None:
            self.hora_creacion = datetime.now()
