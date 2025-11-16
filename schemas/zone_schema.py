from pydantic import BaseModel
from datetime import datetime
from models.zone import TipoZona


class ZoneCreate(BaseModel):
    id: int
    nombre: str
    tipo: TipoZona


class ZoneResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoZona
    fecha_creacion: datetime

    class Config:
        orm_mode = True
