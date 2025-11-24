from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ThreatCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    tipo: str = Field(..., min_length=1)  # Validado dinámicamente contra type_repository
    costo_hormigas: int = Field(..., gt=0)


class ThreatUpdate(BaseModel):
    estado: str  # Estados válidos: 'activa', 'en_combate', 'resuelta'


class ThreatResponse(BaseModel):
    id: int
    zona_id: int
    nombre: str
    tipo: str  # Dinámico
    costo_hormigas: int
    estado: str  # Estados válidos: 'activa', 'en_combate', 'resuelta'
    hora_deteccion: datetime
    hora_resolucion: Optional[datetime] = None

    class Config:
        from_attributes = True
