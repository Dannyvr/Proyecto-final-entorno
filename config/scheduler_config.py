"""
Configuración del sistema de generación automática de amenazas.
"""
from models.threat import TipoAmenaza
from typing import List, Tuple
import os


class SchedulerConfig:
    """Configuración para el scheduler de amenazas automáticas"""
    
    # Intervalo de tiempo entre generación de amenazas (en segundos)
    # Por defecto: 300 segundos (5 minuto)
    # Puede ser configurado mediante variable de entorno THREAT_INTERVAL
    INTERVAL_SECONDS: int = int(os.getenv("THREAT_INTERVAL", "300"))
    
    # Tipos de amenazas a rotar (en orden)
    THREAT_TYPES: List[TipoAmenaza] = [
        TipoAmenaza.ARANA,
        TipoAmenaza.ABEJA,
        TipoAmenaza.SALTAMONTES
    ]
    
    # Nombres base para cada tipo de amenaza
    THREAT_NAMES = {
        TipoAmenaza.ARANA: "araña",
        TipoAmenaza.ABEJA: "abeja",
        TipoAmenaza.SALTAMONTES: "saltamontes"
    }
    
    # Rangos de costo de hormigas para cada tipo de amenaza
    # (min, max)
    THREAT_COSTS = {
        TipoAmenaza.ARANA: (3, 5),
        TipoAmenaza.ABEJA: (4, 7),
        TipoAmenaza.SALTAMONTES: (2, 4)
    }
    
    # Zona por defecto donde se generarán las amenazas
    # 1 = Zona Jardín, 2 = Zona Lago
    # Puede ser configurado mediante variable de entorno DEFAULT_THREAT_ZONE
    DEFAULT_ZONE_ID: int = int(os.getenv("DEFAULT_THREAT_ZONE", "1"))
    
    # Habilitar/deshabilitar el scheduler automático al iniciar
    # Puede ser configurado mediante variable de entorno AUTO_START_SCHEDULER
    AUTO_START: bool = os.getenv("AUTO_START_SCHEDULER", "true").lower() == "true"
    
    @classmethod
    def get_threat_cost(cls, tipo: TipoAmenaza) -> int:
        """Obtiene un costo aleatorio dentro del rango para el tipo de amenaza"""
        import random
        min_cost, max_cost = cls.THREAT_COSTS.get(tipo, (3, 5))
        return random.randint(min_cost, max_cost)
