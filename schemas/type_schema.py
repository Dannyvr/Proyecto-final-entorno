from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class TypeCreate(BaseModel):
    codigo: str = Field(..., min_length=1, description="Código único del tipo (ej: JARDIN, HOJA)")
    nombre: str = Field(..., min_length=1, description="Nombre legible del tipo")
    descripcion: str = Field(..., min_length=1, description="Descripción detallada")
    categoria: str = Field(..., description="Categoría: zona, recurso o amenaza")

    @validator('categoria')
    def validate_categoria(cls, v):
        if v.lower() not in ['zona', 'recurso', 'amenaza']:
            raise ValueError("Categoría debe ser 'zona', 'recurso' o 'amenaza'")
        return v.lower()

    @validator('codigo')
    def validate_codigo(cls, v):
        if not v.isupper():
            raise ValueError("Código debe estar en mayúsculas")
        return v

    class Config:
        orm_mode = True


class TypeUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = Field(None, min_length=1)

    class Config:
        orm_mode = True


class TypeResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str
    categoria: str
    fecha_creacion: datetime

    class Config:
        orm_mode = True
