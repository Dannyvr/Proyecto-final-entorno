from pydantic import BaseModel
from datetime import datetime
from models.zone import TipoZona
from typing import Optional


class ZoneCreate(BaseModel):
    id: Optional[int] = None
    nombre: str
    tipo: TipoZona


class ZoneResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoZona
    fecha_creacion: datetime

    class Config:
        orm_mode = True
