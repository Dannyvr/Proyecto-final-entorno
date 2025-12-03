from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
