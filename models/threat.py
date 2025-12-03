from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class TipoAmenaza(str, Enum):
    AGUILA = "AGUILA"
    ARANA = "ARANA"
    ABEJA = "ABEJA"
    SALTAMONTES = "SALTAMONTES"
    ESCARABAJO = "ESCARABAJO"
    MANTIS = "MANTIS"
    LAGARTIJA = "LAGARTIJA"
    PAJARO = "PAJARO"
    SERPIENTE = "SERPIENTE"


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
    hora_deteccion: Optional[datetime] = None
    hora_resolucion: Optional[datetime] = None
