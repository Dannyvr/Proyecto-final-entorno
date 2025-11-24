from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# NOTA: El tipo ahora es dinámico (str) y se valida contra models/type.py con categoria="amenaza".
# Los estados son dinámicos y se validan contra models/status.py con categoria="amenaza".

@dataclass
class Threat:
    id: int
    zona_id: int
    nombre: str
    tipo: str  # Ahora es dinámico, validado contra type_repository
    costo_hormigas: int
    estado: str = "activa"  # Estados válidos: "activa", "en_combate", "resuelta"
    hora_deteccion: datetime = None
    hora_resolucion: Optional[datetime] = None

    def __post_init__(self):
        if self.hora_deteccion is None:
            self.hora_deteccion = datetime.now()
