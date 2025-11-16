from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from schemas.resource_schema import ResourceCreate, ResourceUpdate, ResourceResponse
from models.resource import Resource, EstadoRecurso
from repositories.zone_repository import ZoneRepository
from repositories.resource_repository import ResourceRepository

router = APIRouter(prefix="/resources", tags=["resources"])

resource_repo = ResourceRepository()
zone_repo = ZoneRepository()


@router.post("/zone/{zona_id}", response_model=ResourceResponse, status_code=201)
async def crear_recurso(zona_id: int, resource_data: ResourceCreate):
    """Crea un nuevo recurso en una zona específica"""
    # Validar que la zona existe
    if not zone_repo.zone_exists(zona_id):
        raise HTTPException(status_code=404, detail={"error": f"La zona {zona_id} no existe"})
    
    # Validar que no exista un recurso con el mismo nombre en la zona
    if resource_repo.resource_name_exists_in_zone(resource_data.nombre, zona_id):
        raise HTTPException(status_code=409, detail={"error": f"El recurso con nombre '{resource_data.nombre}' ya existe en la zona {zona_id}"})
    
    # Crear recurso
    resource = Resource(
        id=0,        
        zona_id=zona_id,
        nombre=resource_data.nombre,
        tipo=resource_data.tipo,
        cantidad_unitaria=resource_data.cantidad_unitaria,
        peso=resource_data.peso,
        duracion_recoleccion=resource_data.duracion_recoleccion,
        hormigas_requeridas=resource_data.hormigas_requeridas,
        estado=EstadoRecurso.DISPONIBLE,
        hora_creacion=datetime.now()
    )
    
    created_resource = resource_repo.create(resource)
    return created_resource


@router.get("", response_model=List[ResourceResponse])
async def listar_recursos(
    zona_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None)
):
    """Lista todos los recursos con filtros opcionales"""
    resources = resource_repo.get_all(zona_id=zona_id, estado=estado)
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
async def obtener_recurso(resource_id: int):
    """Obtiene un recurso por ID"""
    resource = resource_repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail={"error": f"El recurso {resource_id} no existe"})
    return resource



@router.put("/{resource_id}", response_model=ResourceResponse)
async def actualizar_recurso(resource_id: int, update_data: ResourceUpdate):
    resource = resource_repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail={"error": f"El recurso {resource_id} no existe"})
    
    # Validar y aplicar cantidad si se proporciona
    if update_data.cantidad_unitaria is not None:
        if update_data.cantidad_unitaria <= 0 or update_data.cantidad_unitaria > resource.cantidad_unitaria:
            raise HTTPException(status_code=400, detail={"error": "Cantidad inválida"})
        resource.cantidad_unitaria = update_data.cantidad_unitaria

    # Actualizar estado si se proporciona
    if update_data.estado:
        if update_data.estado == "recolectado":
            resource.hora_recoleccion = datetime.now()
        resource.estado = EstadoRecurso(update_data.estado)
    
    updated = resource_repo.update(resource_id, resource)
    if not updated:
        raise HTTPException(status_code=404, detail={"error": f"El recurso {resource_id} no existe"})
    return updated


@router.delete("/{resource_id}")
async def eliminar_recurso(resource_id: int):
    """Elimina un recurso por ID"""
    result = resource_repo.delete(resource_id)

    if result == "deleted":
        return {"message": "Recurso eliminado exitosamente"}

    if result == "already_deleted":
        # Reintento de eliminación -> 404 según tests (T20)
        raise HTTPException(status_code=404, detail={"error": f"El recurso {resource_id} ya fue eliminado"})

    # 'never_existed' -> idempotente, devolver 200 (T19)
    return {"message": "Recurso no existe (idempotente)"}
