from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.resource import TipoRecurso, EstadoRecurso

class ResourceCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    tipo: TipoRecurso
    cantidad_unitaria: int = Field(..., gt=0)
    peso: int = Field(..., gt=0)
    duracion_recoleccion: int = Field(..., gt=0)
    hormigas_requeridas: int = Field(..., gt=0)
    
class ResourceUpdate(BaseModel):
    estado: EstadoRecurso
    cantidad_unitaria: Optional[int] = None
    
class ResourceResponse(BaseModel):
    id: int
    zona_id: int
    nombre: str
    tipo: TipoRecurso
    cantidad_unitaria: int
    peso: int
    duracion_recoleccion: int
    hormigas_requeridas: int
    estado: EstadoRecurso
    hora_creacion: datetime
    hora_recoleccion: Optional[datetime] = None

    class Config:
        from_attributes = True