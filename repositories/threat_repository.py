import csv
import os
from typing import List, Optional
from models.threat import Threat, TipoAmenaza, EstadoAmenaza
from datetime import datetime


class ThreatRepository:
    def __init__(self, csv_file: str = "data/threats.csv"):
        self.csv_file = csv_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crea el archivo CSV si no existe"""
        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'zona_id', 'nombre', 'tipo', 'costo_hormigas', 
                               'estado', 'hora_deteccion', 'hora_resolucion'])

    def get_all(self, zona_id: Optional[int] = None, estado: Optional[str] = None) -> List[Threat]:
        """Lee todos los registros del CSV con filtros opcionales"""
        threats = []
        if not os.path.exists(self.csv_file):
            return threats

        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                threat = self._dict_to_model(row)
                
                # Aplicar filtros
                if zona_id is not None and threat.zona_id != zona_id:
                    continue
                if estado is not None and threat.estado.value != estado:
                    continue
                    
                threats.append(threat)
        return threats
        
    def _dict_to_model(self, data: dict) -> Threat:
        """Convierte un diccionario a modelo Threat"""
        return Threat(
            id=int(data['id']),
            zona_id=int(data['zona_id']),
            nombre=data['nombre'],
            tipo=TipoAmenaza(data['tipo']),
            costo_hormigas=int(data['costo_hormigas']),
            estado=EstadoAmenaza(data['estado']),
            hora_deteccion=datetime.fromisoformat(data['hora_deteccion']) if data['hora_deteccion'] else None,
            hora_resolucion=datetime.fromisoformat(data['hora_resolucion']) if data.get('hora_resolucion') and data['hora_resolucion'] else None
        )

    def _model_to_dict(self, threat: Threat) -> dict:
        """Convierte un modelo Threat a diccionario"""
        return {
            'id': threat.id,
            'zona_id': threat.zona_id,
            'nombre': threat.nombre,
            'tipo': threat.tipo.value,
            'costo_hormigas': threat.costo_hormigas,
            'estado': threat.estado.value,
            'hora_deteccion': threat.hora_deteccion.isoformat() if threat.hora_deteccion else '',
            'hora_resolucion': threat.hora_resolucion.isoformat() if threat.hora_resolucion else ''
        }

    def _save_all(self, threats: List[Threat]):
        """Guarda todos los registros en el CSV"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'zona_id', 'nombre', 'tipo', 'costo_hormigas', 
                         'estado', 'hora_deteccion', 'hora_resolucion']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for threat in threats:
                writer.writerow(self._model_to_dict(threat))

    def create(self, threat: Threat) -> Threat:
        """Crea una nueva amenaza"""
        all_threats = self.get_all()
        
        # Asignar ID
        if not threat.id:
            max_id = max([t.id for t in all_threats], default=0)
            threat.id = max_id + 1
        
        all_threats.append(threat)
        self._save_all(all_threats)
        return threat


    def get_by_id(self, threat_id: int) -> Optional[Threat]:
        """Busca una amenaza por ID"""
        all_threats = self.get_all()
        for threat in all_threats:
            if threat.id == threat_id:
                return threat
        return None


    def update(self, threat_id: int, threat: Threat) -> Optional[Threat]:
        """Actualiza una amenaza existente"""
        all_threats = self.get_all()
        for i, t in enumerate(all_threats):
            if t.id == threat_id:
                threat.id = threat_id
                all_threats[i] = threat
                self._save_all(all_threats)
                return threat
        return None

    def delete(self, threat_id: int) -> bool:
        """Elimina una amenaza"""
        all_threats = self.get_all()
        initial_length = len(all_threats)
        all_threats = [t for t in all_threats if t.id != threat_id]
        
        if len(all_threats) < initial_length:
            self._save_all(all_threats)
            return True
        return False


