from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from schemas.threat_schema import ThreatCreate, ThreatUpdate, ThreatResponse
from models.threat import Threat, TipoAmenaza, EstadoAmenaza
from repositories.threat_repository import ThreatRepository
from repositories.zone_repository import ZoneRepository
from services.threat_scheduler import threat_scheduler
#from repositories.threat_repository_minimal_test_pass import ThreatRepository
router = APIRouter(prefix="/threats", tags=["threats"])

threat_repo = ThreatRepository()
zone_repo = ZoneRepository()


@router.get("/types", response_model=List[dict])
async def obtener_tipos_amenaza():
    """Retorna todos los tipos de amenaza disponibles"""
    return [
        {
            "codigo": tipo.value,
            "nombre": tipo.name,
            "descripcion": f"Amenaza tipo {tipo.name.lower()}"
        }
        for tipo in TipoAmenaza
    ]


@router.get("/statuses", response_model=List[dict])
async def obtener_estados_amenaza():
    """Retorna todos los estados posibles de una amenaza"""
    return [
        {
            "codigo": estado.value,
            "nombre": estado.name,
            "descripcion": _get_estado_descripcion(estado)
        }
        for estado in EstadoAmenaza
    ]


@router.post("/zone/{zona_id}", response_model=ThreatResponse, status_code=201)
async def crear_amenaza(zona_id: int, threat_data: ThreatCreate):
    """Crea una nueva amenaza en una zona específica"""
    # Validar que la zona existe
    if not zone_repo.zone_exists(zona_id):
        raise HTTPException(status_code=404, detail={"error": f"La zona {zona_id} no existe"})
    
    # Crear amenaza
    threat = Threat(
        id=0,  # Se asignará automáticamente
        zona_id=zona_id,
        nombre=threat_data.nombre,
        tipo=threat_data.tipo,
        costo_hormigas=threat_data.costo_hormigas,
        estado=EstadoAmenaza.ACTIVA,
        hora_deteccion=None
    )
    
    created_threat = threat_repo.create(threat)
    return created_threat


@router.get("", response_model=List[ThreatResponse])
async def listar_amenazas(
    zona_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None)
):
    """Lista todas las amenazas con filtros opcionales"""
    threats = threat_repo.get_all(zona_id=zona_id, estado=estado)
    return threats


@router.get("/{threat_id}", response_model=ThreatResponse)
async def obtener_amenaza(threat_id: int):
    """Obtiene una amenaza por ID"""
    threat = threat_repo.get_by_id(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail={"error": f"La amenaza {threat_id} no existe"})
    
    # Si hora_deteccion es None, llenarla con la hora actual
    if threat.hora_deteccion is None:
        threat.hora_deteccion = datetime.now()
        threat_repo.update(threat_id, threat)
    
    return threat


@router.put("/{threat_id}", response_model=ThreatResponse)
async def actualizar_amenaza(threat_id: int, update_data: ThreatUpdate):
    """Actualiza el estado de una amenaza"""
    threat = threat_repo.get_by_id(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail={"error": f"La amenaza {threat_id} no existe"})
    
    # Validar transiciones de estado permitidas
    # Regla: Solo se puede pasar a "resuelta" desde "en_combate"
    if update_data.estado == EstadoAmenaza.RESUELTA:
        # Permitir idempotencia si ya está resuelta
        if threat.estado == EstadoAmenaza.RESUELTA:
            return threat  # Ya está resuelta, retornar sin cambios
        
        # Validar que está en combate antes de resolver
        if threat.estado != EstadoAmenaza.EN_COMBATE:
            raise HTTPException(
                status_code=409,
                detail={"error": f"No se puede cambiar de '{threat.estado.value}' a 'resuelta'. La amenaza debe estar 'en_combate' primero."}
            )
        threat.hora_resolucion = datetime.now()
    
    # Actualizar estado
    threat.estado = update_data.estado
    
    updated_threat = threat_repo.update(threat_id, threat)
    return updated_threat


@router.delete("/{threat_id}")
async def eliminar_amenaza(threat_id: int):
    """Elimina una amenaza"""
    threat = threat_repo.get_by_id(threat_id)
    
    # Si la amenaza existe y está en combate, no se puede eliminar
    if threat and threat.estado == EstadoAmenaza.EN_COMBATE:
        raise HTTPException(
            status_code=409,
            detail={"error": "La amenaza está en combate y no se puede eliminar"}
        )
    
    # Eliminar (idempotente - siempre retorna 200)
    threat_repo.delete(threat_id)
    return {"message": "Amenaza eliminada con éxito"}


def _get_estado_descripcion(estado: EstadoAmenaza) -> str:
    """Retorna la descripción de un estado de amenaza"""
    descripciones = {
        EstadoAmenaza.ACTIVA: "Amenaza detectada y presente en la zona",
        EstadoAmenaza.EN_COMBATE: "Amenaza siendo enfrentada por las hormigas defensoras",
        EstadoAmenaza.RESUELTA: "Amenaza neutralizada o eliminada"
    }
    return descripciones.get(estado, "")


# Endpoints para control del scheduler automático
@router.get("/scheduler/status")
async def obtener_estado_scheduler():
    """Obtiene el estado actual del scheduler de generación automática de amenazas"""
    return threat_scheduler.get_status()


@router.post("/scheduler/start")
async def iniciar_scheduler():
    """Inicia el scheduler de generación automática de amenazas"""
    threat_scheduler.start()
    return {"message": "Scheduler iniciado", "status": threat_scheduler.get_status()}


@router.post("/scheduler/stop")
async def detener_scheduler():
    """Detiene el scheduler de generación automática de amenazas"""
    threat_scheduler.stop()
    return {"message": "Scheduler detenido", "status": threat_scheduler.get_status()}
