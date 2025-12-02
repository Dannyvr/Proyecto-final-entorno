"""
Servicio de generación automática de amenazas.
Genera amenazas periódicamente usando APScheduler.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from typing import Dict
import logging
import random

from models.threat import Threat, TipoAmenaza, EstadoAmenaza
from repositories.threat_repository import ThreatRepository
from repositories.zone_repository import ZoneRepository
from config.scheduler_config import SchedulerConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatScheduler:
    """
    Scheduler para generación automática de amenazas.
    Rota entre tipos de amenazas (araña, abeja, saltamontes) y
    genera instancias secuenciales (araña 1, araña 2, etc.)
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.threat_repo = ThreatRepository()
        self.zone_repo = ZoneRepository()
        self.is_running = False
        
        # Contadores para cada tipo de amenaza
        self.threat_counters: Dict[TipoAmenaza, int] = {
            tipo: 0 for tipo in SchedulerConfig.THREAT_TYPES
        }
        
        # Índice del tipo de amenaza actual en la rotación (aleatorio al inicio)
        self.current_type_index = random.randint(0, len(SchedulerConfig.THREAT_TYPES) - 1)
        
        # Inicializar contadores basándose en amenazas existentes
        self._initialize_counters()
    
    def _initialize_counters(self):
        """
        Inicializa los contadores basándose en las amenazas existentes
        para continuar la secuencia correctamente.
        """
        try:
            all_threats = self.threat_repo.get_all()
            
            for threat in all_threats:
                if threat.tipo in self.threat_counters:
                    # Extraer el número del nombre (ej: "araña 5" -> 5)
                    base_name = SchedulerConfig.THREAT_NAMES.get(threat.tipo, "")
                    if base_name and threat.nombre.startswith(base_name):
                        try:
                            # Intentar extraer el número del nombre
                            parts = threat.nombre.split()
                            if len(parts) >= 2 and parts[-1].isdigit():
                                num = int(parts[-1])
                                if num > self.threat_counters[threat.tipo]:
                                    self.threat_counters[threat.tipo] = num
                        except (ValueError, IndexError):
                            continue
            
            logger.info(f"Contadores inicializados: {self.threat_counters}")
        except Exception as e:
            logger.error(f"Error inicializando contadores: {e}")
    
    def _get_next_threat_type(self) -> TipoAmenaza:
        """Obtiene el siguiente tipo de amenaza en la rotación"""
        threat_type = SchedulerConfig.THREAT_TYPES[self.current_type_index]
        
        # Avanzar al siguiente índice (con rotación circular)
        self.current_type_index = (self.current_type_index + 1) % len(SchedulerConfig.THREAT_TYPES)
        
        return threat_type
    
    def _generate_threat(self):
        """
        Genera una nueva amenaza automáticamente.
        Esta función es llamada periódicamente por el scheduler.
        """
        try:
            # Validar que la zona por defecto existe
            if not self.zone_repo.zone_exists(SchedulerConfig.DEFAULT_ZONE_ID):
                logger.error(f"La zona {SchedulerConfig.DEFAULT_ZONE_ID} no existe. No se puede generar amenaza.")
                return
            
            # Obtener el siguiente tipo de amenaza en la rotación
            threat_type = self._get_next_threat_type()
            
            # Incrementar contador para este tipo
            self.threat_counters[threat_type] += 1
            counter = self.threat_counters[threat_type]
            
            # Generar nombre (ej: "araña 1", "abeja 2")
            base_name = SchedulerConfig.THREAT_NAMES[threat_type]
            threat_name = f"{base_name} {counter}"
            
            # Obtener costo para este tipo de amenaza
            cost = SchedulerConfig.get_threat_cost(threat_type)
            
            # Crear la amenaza
            threat = Threat(
                id=0,  # Se auto-asignará en el repositorio
                zona_id=SchedulerConfig.DEFAULT_ZONE_ID,
                nombre=threat_name,
                tipo=threat_type,
                costo_hormigas=cost,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            )
            
            # Guardar en el repositorio
            created_threat = self.threat_repo.create(threat)
            
            logger.info(
                f"✅ Amenaza generada automáticamente: {created_threat.nombre} "
                f"(ID: {created_threat.id}, Tipo: {created_threat.tipo.value}, "
                f"Costo: {created_threat.costo_hormigas}, Zona: {created_threat.zona_id})"
            )
            
        except Exception as e:
            logger.error(f"❌ Error generando amenaza automática: {e}")
    
    def start(self):
        """Inicia el scheduler de generación automática de amenazas"""
        if self.is_running:
            logger.warning("El scheduler ya está en ejecución")
            return
        
        try:
            # Agregar el job al scheduler
            self.scheduler.add_job(
                func=self._generate_threat,
                trigger="interval",
                seconds=SchedulerConfig.INTERVAL_SECONDS,
                id="threat_generator",
                name="Generador Automático de Amenazas",
                replace_existing=True
            )
            
            # Iniciar el scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info(
                f"🚀 Scheduler de amenazas iniciado. "
                f"Generando amenazas cada {SchedulerConfig.INTERVAL_SECONDS} segundos en zona {SchedulerConfig.DEFAULT_ZONE_ID}"
            )
            logger.info(f"Tipos de amenazas en rotación: {[t.value for t in SchedulerConfig.THREAT_TYPES]}")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando scheduler: {e}")
            self.is_running = False
    
    def stop(self):
        """Detiene el scheduler de generación automática de amenazas"""
        if not self.is_running:
            logger.warning("El scheduler no está en ejecución")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("🛑 Scheduler de amenazas detenido")
        except Exception as e:
            logger.error(f"❌ Error deteniendo scheduler: {e}")
    
    def get_status(self) -> dict:
        """Obtiene el estado actual del scheduler"""
        return {
            "is_running": self.is_running,
            "interval_seconds": SchedulerConfig.INTERVAL_SECONDS,
            "default_zone_id": SchedulerConfig.DEFAULT_ZONE_ID,
            "threat_types": [t.value for t in SchedulerConfig.THREAT_TYPES],
            "threat_counters": {t.value: count for t, count in self.threat_counters.items()},
            "current_type_index": self.current_type_index,
            "next_threat_type": SchedulerConfig.THREAT_TYPES[self.current_type_index].value
        }


# Instancia global del scheduler
threat_scheduler = ThreatScheduler()
