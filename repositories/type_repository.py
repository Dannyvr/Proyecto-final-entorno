import csv
import os
from typing import List, Optional
from datetime import datetime
from models.type import Type

CSV_FILE = "data/types.csv"
CSV_HEADERS = ["id", "codigo", "nombre", "descripcion", "categoria", "fecha_creacion"]


class TypeRepository:
    def __init__(self):
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Crea el archivo CSV si no existe"""
        os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()

    def _dict_to_model(self, row: dict) -> Type:
        """Convierte un diccionario CSV a modelo Type"""
        return Type(
            id=int(row["id"]),
            codigo=row["codigo"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            categoria=row["categoria"],
            fecha_creacion=datetime.fromisoformat(row["fecha_creacion"])
        )

    def _model_to_dict(self, type_obj: Type) -> dict:
        """Convierte un modelo Type a diccionario CSV"""
        return {
            "id": str(type_obj.id),
            "codigo": type_obj.codigo,
            "nombre": type_obj.nombre,
            "descripcion": type_obj.descripcion,
            "categoria": type_obj.categoria,
            "fecha_creacion": type_obj.fecha_creacion.isoformat()
        }

    def get_all(self, categoria: str = None) -> List[Type]:
        """Obtiene todos los tipos, opcionalmente filtrados por categoría"""
        types = []
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                type_obj = self._dict_to_model(row)
                if categoria is None or type_obj.categoria == categoria.lower():
                    types.append(type_obj)
        return types

    def get_by_id(self, type_id: int) -> Optional[Type]:
        """Obtiene un tipo por ID"""
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["id"]) == type_id:
                    return self._dict_to_model(row)
        return None

    def get_by_codigo(self, codigo: str, categoria: str = None) -> Optional[Type]:
        """Obtiene un tipo por código y opcionalmente categoría"""
        self._ensure_csv_exists()  # Asegurar que el archivo existe
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["codigo"] == codigo:
                    if categoria is None or row["categoria"] == categoria.lower():
                        return self._dict_to_model(row)
        return None

    def create(self, type_obj: Type) -> Type:
        """Crea un nuevo tipo"""
        # Generar ID autoincremental
        types = self.get_all()
        new_id = max([t.id for t in types], default=0) + 1
        type_obj.id = new_id

        # Agregar al CSV
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(self._model_to_dict(type_obj))

        return type_obj

    def update(self, type_id: int, type_obj: Type) -> Optional[Type]:
        """Actualiza un tipo existente"""
        types = self.get_all()
        updated = False

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            
            for existing_type in types:
                if existing_type.id == type_id:
                    type_obj.id = type_id
                    writer.writerow(self._model_to_dict(type_obj))
                    updated = True
                else:
                    writer.writerow(self._model_to_dict(existing_type))

        return type_obj if updated else None

    def delete(self, type_id: int) -> bool:
        """Elimina un tipo"""
        types = self.get_all()
        filtered_types = [t for t in types if t.id != type_id]

        if len(filtered_types) == len(types):
            return False  # No se encontró

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for type_obj in filtered_types:
                writer.writerow(self._model_to_dict(type_obj))

        return True

    def codigo_exists(self, codigo: str, categoria: str) -> bool:
        """Verifica si un código ya existe en una categoría"""
        return self.get_by_codigo(codigo, categoria) is not None
