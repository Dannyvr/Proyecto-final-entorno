"""
Configuración del sistema de generación automática de recursos.
"""
from models.resource import TipoRecurso
from typing import List, Tuple
import os

class ResourcesSchedulerConfig:
    """Configuración para el scheduler de recursos automáticos"""
    
    # Intervalo de tiempo entre generación de recursos (en segundos)
    # Por defecto: 240 segundos (4 minutos)
    # Puede ser configurado mediante variable de entorno RESOURCES_INTERVAL
    INTERVAL_SECONDS: int = int(os.getenv("RESOURCES_INTERVAL", "240"))
    
    # Tipos de recursos a rotar (en orden)
    RESOURCE_TYPES: List[TipoRecurso] = [
        TipoRecurso.HOJA,
        TipoRecurso.SEMILLA,
        TipoRecurso.FLOR,
        TipoRecurso.FRUTO,
        TipoRecurso.NECTAR,
        TipoRecurso.HONGO,
        TipoRecurso.AGUA
    ]
    
    # Nombres base para cada tipo de recurso
    RESOURCE_NAMES = {
        TipoRecurso.HOJA: "hoja",
        TipoRecurso.SEMILLA: "semilla",
        TipoRecurso.FLOR: "flor",
        TipoRecurso.FRUTO: "fruto",
        TipoRecurso.NECTAR: "nectar",
        TipoRecurso.HONGO: "hongo",
        TipoRecurso.AGUA: "agua"
    }
    
    # Rangos de cantidad para cada tipo de recurso
    # (min, max)
    RESOURCE_QUANTITIES = {
        TipoRecurso.HOJA: (10, 20),
        TipoRecurso.SEMILLA: (5, 15),
        TipoRecurso.FLOR: (8, 18),
        TipoRecurso.FRUTO: (6, 12),
        TipoRecurso.NECTAR: (15, 25),
        TipoRecurso.HONGO: (4, 10),
        TipoRecurso.AGUA: (20, 30)
    }
    
    # Rango de peso unitario por tipo de recurso (en gramos)
    # (min, max)
    RESOURCE_WEIGHTS = {
        TipoRecurso.HOJA: (1, 3),
        TipoRecurso.SEMILLA: (2, 4),
        TipoRecurso.FLOR: (3, 6),
        TipoRecurso.FRUTO: (5, 8),
        TipoRecurso.NECTAR: (1, 2),
        TipoRecurso.HONGO: (4, 7),
        TipoRecurso.AGUA: (10, 15)
    }
    
    #Rango de duración de recolección por tipo de recurso (en segundos)
    # (min, max)
    RESOURCE_COLLECTION_DURATIONS = {
        TipoRecurso.HOJA: (30, 60),
        TipoRecurso.SEMILLA: (45, 90),
        TipoRecurso.FLOR: (60, 120),
        TipoRecurso.FRUTO: (75, 150),
        TipoRecurso.NECTAR: (20, 40),
        TipoRecurso.HONGO: (50, 100),
        TipoRecurso.AGUA: (15, 30)
    }
    
    # Rango de cantidad de hormigas requeridas por tipo de recurso
    # (min, max)
    RESOURCE_ANT_REQUIREMENTS = {
        TipoRecurso.HOJA: (2, 4),
        TipoRecurso.SEMILLA: (3, 5),
        TipoRecurso.FLOR: (4, 6),
        TipoRecurso.FRUTO: (5, 7),
        TipoRecurso.NECTAR: (1, 3),
        TipoRecurso.HONGO: (3, 5),
        TipoRecurso.AGUA: (1, 2)
    }
    
    # Zona por defecto donde se generarán los recursos
    # 1 = Zona Jardín, 2 = Zona Lago
    # Puede ser configurado mediante variable de entorno DEFAULT_RESOURCE_ZONE
    DEFAULT_ZONE_ID: int = int(os.getenv("DEFAULT_RESOURCE_ZONE", "1"))
    
    # Habilitar/deshabilitar el scheduler automático al iniciar
    # Puede ser configurado mediante variable de entorno AUTO_START_RESOURCES_SCHEDULER
    AUTO_START: bool = os.getenv("AUTO_START_RESOURCES_SCHEDULER", "true").lower() == "true"
    
    @classmethod
    def get_resource_quantity(cls, tipo: TipoRecurso) -> int:
        """Obtiene una cantidad aleatoria dentro del rango para el tipo de recurso"""
        import random
        min_qty, max_qty = cls.RESOURCE_QUANTITIES.get(tipo, (5, 10))
        return random.randint(min_qty, max_qty)
    
    @classmethod
    def get_resource_weight(cls, tipo: TipoRecurso) -> int:
        """Obtiene un peso unitario aleatorio dentro del rango para el tipo de recurso"""
        import random
        min_wt, max_wt = cls.RESOURCE_WEIGHTS.get(tipo, (1, 3))
        return random.randint(min_wt, max_wt)
    
    @classmethod
    def get_collection_duration(cls, tipo: TipoRecurso) -> int:
        """Obtiene una duración de recolección aleatoria dentro del rango para el tipo de recurso"""
        import random
        min_dur, max_dur = cls.RESOURCE_COLLECTION_DURATIONS.get(tipo, (30, 60))
        return random.randint(min_dur, max_dur)
    
    @classmethod
    def get_ant_requirement(cls, tipo: TipoRecurso) -> int: 
        """Obtiene una cantidad de hormigas requerida aleatoria dentro del rango para el tipo de recurso"""
        import random
        min_ants, max_ants = cls.RESOURCE_ANT_REQUIREMENTS.get(tipo, (2, 4))
        return random.randint(min_ants, max_ants)
    