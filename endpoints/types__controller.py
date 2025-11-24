from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from models.status import get_all_statuses
from models.type import Type
from schemas.type_schema import TypeCreate, TypeUpdate, TypeResponse
from repositories.type_repository import TypeRepository

router = APIRouter(tags=["types-and-statuses"])

type_repo = TypeRepository()


@router.get("/statuses", response_model=List[dict])
async def obtener_estados(categoria: Optional[str] = Query(None, description="Filtrar por categoría: recurso o amenaza")):
    """
    Retorna todos los estados disponibles (FIJOS).
    Los estados son inmutables y no se pueden crear/actualizar/eliminar.
    
    - categoria (opcional): 'recurso' o 'amenaza' para filtrar
    """
    if categoria and categoria.lower() not in ['recurso', 'amenaza']:
        raise HTTPException(status_code=400, detail={"error": "Categoría debe ser 'recurso' o 'amenaza'"})
    
    return get_all_statuses(categoria)


@router.post("/types", response_model=TypeResponse, status_code=201)
async def crear_tipo(type_data: TypeCreate):
    """
    Crea un nuevo tipo (zona, recurso o amenaza) - DINÁMICO.
    
    - codigo: Código único en mayúsculas (ej: JARDIN, HOJA, AGUILA)
    - nombre: Nombre legible
    - descripcion: Descripción detallada
    - categoria: 'zona', 'recurso' o 'amenaza'
    """
    # Validar que el código no exista en la misma categoría
    if type_repo.codigo_exists(type_data.codigo, type_data.categoria):
        raise HTTPException(
            status_code=409,
            detail={"error": f"El código '{type_data.codigo}' ya existe en la categoría '{type_data.categoria}'"}
        )
    
    # Crear tipo
    new_type = Type(
        id=0,  # Se asignará automáticamente
        codigo=type_data.codigo,
        nombre=type_data.nombre,
        descripcion=type_data.descripcion,
        categoria=type_data.categoria,
        fecha_creacion=datetime.now()
    )
    
    created_type = type_repo.create(new_type)
    return created_type


@router.get("/types", response_model=List[TypeResponse])
async def listar_tipos(categoria: Optional[str] = Query(None, description="Filtrar por categoría: zona, recurso o amenaza")):
    """
    Lista todos los tipos disponibles con filtro opcional por categoría.
    
    - categoria (opcional): 'zona', 'recurso' o 'amenaza'
    """
    if categoria and categoria.lower() not in ['zona', 'recurso', 'amenaza']:
        raise HTTPException(status_code=400, detail={"error": "Categoría debe ser 'zona', 'recurso' o 'amenaza'"})
    
    types = type_repo.get_all(categoria)
    return types


@router.get("/types/{type_id}", response_model=TypeResponse)
async def obtener_tipo(type_id: int):
    """
    Obtiene un tipo específico por ID.
    """
    type_obj = type_repo.get_by_id(type_id)
    if not type_obj:
        raise HTTPException(status_code=404, detail={"error": f"El tipo {type_id} no existe"})
    return type_obj


@router.put("/types/{type_id}", response_model=TypeResponse)
async def actualizar_tipo(type_id: int, update_data: TypeUpdate):
    """
    Actualiza un tipo existente (solo nombre y descripción).
    El código y categoría no se pueden modificar.
    """
    existing_type = type_repo.get_by_id(type_id)
    if not existing_type:
        raise HTTPException(status_code=404, detail={"error": f"El tipo {type_id} no existe"})
    
    # Actualizar solo campos proporcionados
    if update_data.nombre:
        existing_type.nombre = update_data.nombre
    if update_data.descripcion:
        existing_type.descripcion = update_data.descripcion
    
    updated_type = type_repo.update(type_id, existing_type)
    return updated_type


@router.delete("/types/{type_id}")
async def eliminar_tipo(type_id: int):
    """
    Elimina un tipo por ID.
    """
    deleted = type_repo.delete(type_id)
    if not deleted:
        # Idempotente - siempre retorna 200
        return {"message": "Tipo no existe (idempotente)"}
    
    return {"message": f"Tipo {type_id} eliminado con éxito"}
