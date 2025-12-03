from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.threat import TipoAmenaza, EstadoAmenaza


class ThreatCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    tipo: TipoAmenaza
    costo_hormigas: int = Field(..., gt=0)


class ThreatUpdate(BaseModel):
    estado: EstadoAmenaza


class ThreatResponse(BaseModel):
    id: int
    zona_id: int
    nombre: str
    tipo: TipoAmenaza
    costo_hormigas: int
    estado: EstadoAmenaza
    hora_deteccion: Optional[datetime] = None
    hora_resolucion: Optional[datetime] = None

    class Config:
        from_attributes = True
