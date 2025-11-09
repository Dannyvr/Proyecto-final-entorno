import csv
import os
from typing import List, Optional
from datetime import datetime



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
                if int(row['id']) == zone_id:
                    return True
        return False
