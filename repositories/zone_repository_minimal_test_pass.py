from typing import List, Optional
from datetime import datetime
from models.zone import Zona, TipoZona


class ZoneRepository:
    """Implementación mínima para que las pruebas pasen sin persistencia real"""

    def zone_exists(self, zone_id: int) -> bool:
        """Simula verificar si existe"""
        return True


    def crearZona(self, zona: Zona) -> None:
        """Simula la creación de una zona"""
        zona = Zona(
            id=1,
            nombre="Arbol de jocote",
            tipo=TipoZona.ARBOL,
            fecha_creacion=datetime.now()
        )

    def eliminarZona(self, zone_id: int) -> bool:
        """Simula la eliminación de una zona"""
        return True

    def obtenerZonaPorId(self, zone_id: int) -> Optional[Zona]:
        """Simula obtener una zona por ID"""
        zona = Zona(
            id=1,
            nombre="Arbol de jocote",
            tipo=TipoZona.ARBOL,
            fecha_creacion=datetime.now()
        )
        return zona

    def obtenerTodasLasZonas(self) -> List[Zona]:
        """Simula devolver todas las zonas"""
        zona1 = Zona(
            id=1,
            nombre="Arbol de jocote",
            tipo=TipoZona.ARBOL,
            fecha_creacion=datetime.now()
        )
        zona2 = Zona(
            id=2,
            nombre="Zona de arena",
            tipo=TipoZona.ARENA,
            fecha_creacion=datetime.now()
        )
        return [zona1, zona2]

    