"""
Servicio de generación automática de recursos.
Genera recursos periódicamente usando APScheduler.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Dict
import logging
import random

from models.resource import Resource, TipoRecurso, EstadoRecurso
from repositories.resource_repository import ResourceRepository
from repositories.zone_repository import ZoneRepository
from config.resources_scheduler_config import ResourcesSchedulerConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceScheduler:
    """
    Scheduler para generación automática de recursos.
    Rota entre tipos de recursos y genera instancias secuenciales
    (hoja 1, hoja 2, etc.)
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.resource_repo = ResourceRepository()
        self.zone_repo = ZoneRepository()
        self.is_running = False
        
        # Contadores para cada tipo de recurso
        self.resource_counters: Dict[TipoRecurso, int] = {
            tipo: 0 for tipo in ResourcesSchedulerConfig.RESOURCE_TYPES
        }
        
        # Índice del tipo de recurso actual en la rotación (aleatorio al inicio)
        self.current_type_index = random.randint(0, len(ResourcesSchedulerConfig.RESOURCE_TYPES) - 1)
        
        # Inicializar contadores basándose en recursos existentes
        self._initialize_counters()
        
    def _initialize_counters(self):
        """
        Inicializa los contadores basándose en los recursos existentes
        para continuar la secuencia correctamente.
        """
        try:
            all_resources = self.resource_repo.get_all()
            
            for resource in all_resources:
                if resource.tipo in self.resource_counters:
                    # Extraer el número del nombre (ej: "hoja 5" -> 5)
                    base_name = ResourcesSchedulerConfig.RESOURCE_NAMES.get(resource.tipo, "")
                    if base_name and resource.nombre.startswith(base_name):
                        try:
                            # Intentar extraer el número del nombre
                            parts = resource.nombre.split()
                            if len(parts) >= 2 and parts[-1].isdigit():
                                number = int(parts[1])
                                if number > self.resource_counters[resource.tipo]:
                                    self.resource_counters[resource.tipo] = number
                        except (ValueError, IndexError):
                            continue
            logger.info(f"Contadores de recursos inicializados: {self.resource_counters}")
        except Exception as e:
            logger.error(f"Error al inicializar contadores de recursos: {e}")
            
            
    def _get_next_resource_type(self) -> TipoRecurso:
        """Obtiene el siguiente tipo de recurso en la rotación"""
        resource_types = ResourcesSchedulerConfig.RESOURCE_TYPES[self.current_type_index]
        
        # Actualizar el índice para la próxima llamada
        self.current_type_index = (self.current_type_index + 1) % len(ResourcesSchedulerConfig.RESOURCE_TYPES)
        
        return resource_types
               
            
    def _generate_resource(self):   
        """
        Genera un nuevo recurso y lo guarda en el repositorio automáticamente. 
        Esta función es llamada periódicamente por el scheduler.
        """
        try:
            # Validar que la zona por defecto exista
            default_zone = self.zone_repo.zone_exists(ResourcesSchedulerConfig.DEFAULT_ZONE_ID)
            if not default_zone:
                logger.warning(
                    f"La zona por defecto con ID {ResourcesSchedulerConfig.DEFAULT_ZONE_ID} no existe. "
                    "No se puede generar el recurso."
                )
                return
            
            # Obtener el siguiente tipo de recurso en la rotación
            resource_type = self._get_next_resource_type()
            
            # Incrementar el contador para este tipo de recurso
            self.resource_counters[resource_type] += 1
            resource_number = self.resource_counters[resource_type]
            
            # Construir el nombre del recurso
            base_name = ResourcesSchedulerConfig.RESOURCE_NAMES.get(resource_type, "recurso")
            resource_name = f"{base_name} {resource_number}"
            
            # Obtener cantidades y peso aleatorios dentro del rango definido
            quantity_range = ResourcesSchedulerConfig.RESOURCE_QUANTITIES.get(resource_type, (1, 1))
            weight_range = ResourcesSchedulerConfig.RESOURCE_WEIGHTS.get(resource_type, (1, 1))
            
            cantidad_unitaria = random.randint(quantity_range[0], quantity_range[1])
            peso = random.randint(weight_range[0], weight_range[1])
            
            # Obtener duración de recolección y hormigas requeridas aleatorias
            duration_range = ResourcesSchedulerConfig.RESOURCE_COLLECTION_DURATIONS.get(resource_type, (10, 10))
            ants_range = ResourcesSchedulerConfig.RESOURCE_ANT_REQUIREMENTS.get(resource_type, (1, 1))
            
            rango_duracion = random.randint(duration_range[0], duration_range[1])
            rango_hormigas = random.randint(ants_range[0], ants_range[1])
            
            # Seleccionar una zona aleatoria existente (o la zona por defecto)
            zones = self.zone_repo.obtenerTodasLasZonas()
            if not zones:
                logger.warning("No hay zonas disponibles para asignar recursos.")
                return
            
            selected_zone = random.choice(zones)
            if not selected_zone:
                logger.warning("No se pudo seleccionar una zona válida.")
                return
            
            # Crear el recurso
            new_resource = Resource(
                id=0,
                zona_id=selected_zone.id,
                nombre=resource_name,
                tipo=resource_type,
                cantidad_unitaria=cantidad_unitaria,
                peso=peso,
                duracion_recoleccion=rango_duracion,  
                hormigas_requeridas=rango_hormigas,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            )
            
            # Guardar el recurso en el repositorio
            self.resource_repo.create(new_resource)
            
            logger.info(
                f"✅ Recurso generado exitosamente: {new_resource.nombre} "  
                f"(ID: {new_resource.id}, Tipo: {new_resource.tipo.value}, "
                f"Zona: {new_resource.zona_id})"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generando recurso automático: {e}")
            
            
    def start(self):
        """Inicia el scheduler de generación automática de recursos"""
        if self.is_running:
            logger.warning("El scheduler ya está en ejecución.")
            return
            
        try:
            # Agregar el job al scheduler
            self.scheduler.add_job(
                func=self._generate_resource, 
                trigger='interval', 
                seconds=ResourcesSchedulerConfig.INTERVAL_SECONDS,
                id='resource_generator',
                name='Generador Automático de Recursos',
                replace_existing=True
            )
        
            # Iniciar el scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(
                f"🚀 Scheduler de recursos iniciado. "
                f"Generando recursos cada {ResourcesSchedulerConfig.INTERVAL_SECONDS}."
            )
            logger.info(f"Tipos de recursos en rotación: {[t.value for t in ResourcesSchedulerConfig.RESOURCE_TYPES]}")
        
        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
            self.is_running = False
            

    
    def stop(self):
        """Detiene el scheduler de generación automática de recursos"""
        if not self.is_running:
                logger.warning("El scheduler no está en ejecución.")
                return
            
        try:
            self.scheduler.remove_job('resource_generator')
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("🛑 Scheduler de recursos detenido")
        except Exception as e:
            logger.error(f"❌ Error deteniendo scheduler: {e}")
            
    def get_status(self) -> dict:
        """Obtiene el estado actual del scheduler (corriendo o no)"""
        return {
            "is_running": self.is_running,
            "interval_seconds": ResourcesSchedulerConfig.INTERVAL_SECONDS,
            "default_zone_id": ResourcesSchedulerConfig.DEFAULT_ZONE_ID,
            "resource_types": [t.value for t in ResourcesSchedulerConfig.RESOURCE_TYPES],
            "resource_counters": {t.value: count for t, count in self.resource_counters.items()},
            "current_type_index": self.current_type_index,
            "next_resource_type": ResourcesSchedulerConfig.RESOURCE_TYPES[self.current_type_index].value
        }
        
        
# Instancia global del scheduler
resource_scheduler = ResourceScheduler()