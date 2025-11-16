from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class TipoAmenaza(str, Enum):
    AGUILA = "AGUILA"
    SERPIENTE = "SERPIENTE"
    ARANA = "ARANA"
    ESCORPION = "ESCORPION"


class EstadoAmenaza(str, Enum):
    ACTIVA = "activa"
    EN_COMBATE = "en_combate"
    RESUELTA = "resuelta"


@dataclass
class Threat:
    id: int
    zona_id: int
    nombre: str
    tipo: TipoAmenaza
    costo_hormigas: int
    estado: EstadoAmenaza = EstadoAmenaza.ACTIVA
    hora_deteccion: datetime = None
    hora_resolucion: Optional[datetime] = None

    def __post_init__(self):
        if self.hora_deteccion is None:
            self.hora_deteccion = datetime.now()
