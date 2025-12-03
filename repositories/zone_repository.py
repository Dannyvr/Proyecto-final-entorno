import csv
import os
from typing import List, Optional
from datetime import datetime
from models.zone import Zona, TipoZona


class ZoneRepository:
    def __init__(self, csv_file: str = "data/zones.csv"):
        self.csv_file = csv_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea el archivo CSV si no existe"""
        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'nombre', 'tipo', 'fecha_creacion', 'elementos_asociados'])

    def zone_exists(self, zone_id: int) -> bool:
        """Verifica si una zona existe"""

        if not os.path.exists(self.csv_file):
            return False

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_id = row.get('id')

                # Ignorar IDs vacíos o None
                if not raw_id or raw_id.strip() == "":
                    continue

                try:
                    if int(raw_id) == zone_id:
                        return True
                except ValueError:
                    # Si el CSV tiene basura (ej: texto donde debería haber un número)
                    continue

        return False

    def crearZona(self, zona: Zona) -> None:
        """Agrega una nueva zona al CSV"""
        if self.zone_exists(zona.id):
            raise ValueError(f"La zona con id {zona.id} ya existe.")

        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                zona.id,
                zona.nombre,
                zona.tipo.value,
                zona.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            ])

    def eliminarZona(self, zone_id: int) -> bool:
        """Elimina una zona por ID. Devuelve True si se eliminó."""
        if not os.path.exists(self.csv_file):
            return False

        zonas = []
        eliminado = False

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['id']) != zone_id:
                    zonas.append(row)
                else:
                    eliminado = True

        if eliminado:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'nombre', 'tipo', 'fecha_creacion'])
                writer.writeheader()
                writer.writerows(zonas)

        return eliminado

    def obtenerZonaPorId(self, zone_id: int) -> Optional[Zona]:
        """Devuelve una zona por su ID o None si no existe"""
        if not os.path.exists(self.csv_file):
            return None

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['id']) == zone_id:
                    return Zona(
                        id=int(row['id']),
                        nombre=row['nombre'],
                        tipo=TipoZona(row['tipo']),
                        fecha_creacion=datetime.strptime(row['fecha_creacion'], '%Y-%m-%d %H:%M:%S')
                    )
        return None

    def obtenerTodasLasZonas(self) -> List[Zona]:
        """Devuelve una lista con todas las zonas"""
        zonas = []
        if not os.path.exists(self.csv_file):
            return zonas

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                zonas.append(Zona(
                    id=int(row['id']),
                    nombre=row['nombre'],
                    tipo=TipoZona(row['tipo']),
                    fecha_creacion=datetime.strptime(row['fecha_creacion'], '%Y-%m-%d %H:%M:%S')
                ))
        return zonas
    
    def obtenerZonasPorTipo(self, tipo: TipoZona) -> List[Zona]:
        """Devuelve una lista con las zonas filtradas por tipo"""
        zonas = self.obtenerTodasLasZonas()
        return [zona for zona in zonas if zona.tipo == tipo]