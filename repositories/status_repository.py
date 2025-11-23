import csv
import os
from typing import List, Optional
from models.status import StatusInfo

CSV_FILE = "data/statuses.csv"
CSV_HEADERS = ["codigo", "nombre", "descripcion", "categoria"]


class StatusRepository:
    def __init__(self):
        self._ensure_csv_exists()
        self._initialize_statuses()

    def _ensure_csv_exists(self):
        """Crea el archivo CSV si no existe"""
        os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()

    def _initialize_statuses(self):
        """Inicializa los estados fijos en el CSV si está vacío"""
        # Estados fijos del sistema
        fixed_statuses = [
            StatusInfo(
                codigo="disponible",
                nombre="Disponible",
                descripcion="Recurso listo para ser recolectado",
                categoria="recurso"
            ),
            StatusInfo(
                codigo="en_recoleccion",
                nombre="En recolección",
                descripcion="Recurso siendo recolectado por hormigas trabajadoras",
                categoria="recurso"
            ),
            StatusInfo(
                codigo="recolectado",
                nombre="Recolectado",
                descripcion="Recurso completamente recolectado y almacenado",
                categoria="recurso"
            ),
            StatusInfo(
                codigo="activa",
                nombre="Activa",
                descripcion="Amenaza detectada y presente en la zona",
                categoria="amenaza"
            ),
            StatusInfo(
                codigo="en_combate",
                nombre="En combate",
                descripcion="Amenaza siendo enfrentada por las hormigas defensoras",
                categoria="amenaza"
            ),
            StatusInfo(
                codigo="resuelta",
                nombre="Resuelta",
                descripcion="Amenaza neutralizada o eliminada",
                categoria="amenaza"
            ),
        ]

        # Verificar si el archivo está vacío (solo tiene headers)
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_statuses = list(reader)

        # Si está vacío, agregar los estados fijos
        if not existing_statuses:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
                for status in fixed_statuses:
                    writer.writerow(self._model_to_dict(status))

    def _dict_to_model(self, row: dict) -> StatusInfo:
        """Convierte un diccionario CSV a modelo StatusInfo"""
        return StatusInfo(
            codigo=row["codigo"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            categoria=row["categoria"]
        )

    def _model_to_dict(self, status: StatusInfo) -> dict:
        """Convierte un modelo StatusInfo a diccionario CSV"""
        return {
            "codigo": status.codigo,
            "nombre": status.nombre,
            "descripcion": status.descripcion,
            "categoria": status.categoria
        }

    def get_all(self, categoria: str = None) -> List[StatusInfo]:
        """Obtiene todos los estados, opcionalmente filtrados por categoría"""
        statuses = []
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = self._dict_to_model(row)
                if categoria is None or status.categoria == categoria.lower():
                    statuses.append(status)
        return statuses

    def get_by_codigo(self, codigo: str, categoria: str = None) -> Optional[StatusInfo]:
        """Obtiene un estado por código y opcionalmente categoría"""
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["codigo"] == codigo:
                    if categoria is None or row["categoria"] == categoria.lower():
                        return self._dict_to_model(row)
        return None

    def codigo_exists(self, codigo: str, categoria: str = None) -> bool:
        """Verifica si un código de estado existe"""
        return self.get_by_codigo(codigo, categoria) is not None
