from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from models.zone import Zona, TipoZona
from repositories.zone_repository import ZoneRepository
from schemas.zone_schema import ZoneCreate, ZoneResponse  # Te explico más abajo este schema

router = APIRouter(prefix="/zones", tags=["zones"])

zone_repo = ZoneRepository()


@router.post("", response_model=ZoneResponse, status_code=201)
async def crear_zona(zone_data: ZoneCreate):
    """Crea una nueva zona"""
    # Verificar si ya existe una zona con ese ID (si viene del cliente)
    if zone_repo.zone_exists(zone_data.id):
        raise HTTPException(status_code=400, detail={"error": f"La zona con id {zone_data.id} ya existe"})

    zona = Zona(
        id=zone_data.id,
        nombre=zone_data.nombre,
        tipo=zone_data.tipo,
        fecha_creacion=datetime.now()
    )

    zone_repo.crearZona(zona)
    return zona


@router.get("", response_model=List[ZoneResponse])
async def listar_zonas():
    """Lista todas las zonas"""
    zonas = zone_repo.obtenerTodasLasZonas()
    return zonas


@router.get("/{zona_id}", response_model=ZoneResponse)
async def obtener_zona(zona_id: int):
    """Obtiene una zona por su ID"""
    zona = zone_repo.obtenerZonaPorId(zona_id)
    if not zona:
        raise HTTPException(status_code=404, detail={"error": f"La zona {zona_id} no existe"})
    return zona


@router.delete("/{zona_id}")
async def eliminar_zona(zona_id: int):
    """Elimina una zona por ID"""
    if not zone_repo.zone_exists(zona_id):
        raise HTTPException(status_code=404, detail={"error": f"La zona {zona_id} no existe"})
    
    zone_repo.eliminarZona(zona_id)
    return {"message": f"Zona {zona_id} eliminada con éxito"}
