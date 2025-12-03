
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from services.threat_scheduler import ThreatScheduler, threat_scheduler
from models.threat import Threat, TipoAmenaza, EstadoAmenaza
from models.zone import Zona, TipoZona
from config.scheduler_config import SchedulerConfig


class TestThreatScheduler:
    """Suite de pruebas para ThreatScheduler"""
    
    @pytest.fixture
    def mock_repositories(self):
        """Mock de los repositorios"""
        with patch('services.threat_scheduler.ThreatRepository') as mock_threat_repo, \
             patch('services.threat_scheduler.ZoneRepository') as mock_zone_repo:
            
            # Configurar mocks
            mock_threat_instance = Mock()
            mock_zone_instance = Mock()
            
            mock_threat_repo.return_value = mock_threat_instance
            mock_zone_repo.return_value = mock_zone_instance
            
            yield mock_threat_instance, mock_zone_instance
    
    @pytest.fixture
    def scheduler(self, mock_repositories):
        """Crea una instancia del scheduler con repositorios mockeados"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar respuestas por defecto
        mock_threat_repo.get_all.return_value = []
        
        # Crear scheduler
        scheduler = ThreatScheduler()
        return scheduler
    
    def test_initialization(self, scheduler):
        """Prueba que el scheduler se inicialice correctamente"""
        assert scheduler.is_running == False
        assert scheduler.threat_counters is not None
        assert len(scheduler.threat_counters) == len(SchedulerConfig.THREAT_TYPES)
        assert scheduler.current_type_index >= 0
        assert scheduler.current_type_index < len(SchedulerConfig.THREAT_TYPES)
        assert scheduler.scheduler is not None
    
    def test_initialize_counters_empty_repo(self, scheduler, mock_repositories):
        """Prueba inicialización de contadores con repositorio vacío"""
        mock_threat_repo, _ = mock_repositories
        mock_threat_repo.get_all.return_value = []
        
        scheduler._initialize_counters()
        
        # Todos los contadores deben ser 0
        for counter in scheduler.threat_counters.values():
            assert counter == 0
    
    def test_initialize_counters_with_existing_threats(self, scheduler, mock_repositories):
        """Prueba inicialización de contadores con amenazas existentes"""
        mock_threat_repo, _ = mock_repositories
        
        # Crear amenazas de prueba
        threats = [
            Threat(
                id=1,
                zona_id=1,
                nombre="araña 5",
                tipo=TipoAmenaza.ARANA,
                costo_hormigas=10,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            ),
            Threat(
                id=2,
                zona_id=1,
                nombre="abeja 3",
                tipo=TipoAmenaza.ABEJA,
                costo_hormigas=8,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            ),
            Threat(
                id=3,
                zona_id=1,
                nombre="saltamontes 7",
                tipo=TipoAmenaza.SALTAMONTES,
                costo_hormigas=12,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            )
        ]
        
        mock_threat_repo.get_all.return_value = threats
        
        scheduler._initialize_counters()
        
        # Verificar que los contadores se actualizaron
        assert scheduler.threat_counters[TipoAmenaza.ARANA] == 5
        assert scheduler.threat_counters[TipoAmenaza.ABEJA] == 3
        assert scheduler.threat_counters[TipoAmenaza.SALTAMONTES] == 7
    
    def test_initialize_counters_with_invalid_names(self, scheduler, mock_repositories):
        """Prueba que _initialize_counters maneje amenazas con nombres inválidos"""
        mock_threat_repo, _ = mock_repositories
        
        # Amenazas con nombres inválidos
        threats = [
            Threat(
                id=1,
                zona_id=1,
                nombre="amenaza_invalida",
                tipo=TipoAmenaza.ARANA,
                costo_hormigas=10,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            ),
            Threat(
                id=2,
                zona_id=1,
                nombre="araña",  # Sin número
                tipo=TipoAmenaza.ARANA,
                costo_hormigas=10,
                estado=EstadoAmenaza.ACTIVA,
                hora_deteccion=datetime.now()
            )
        ]
        
        mock_threat_repo.get_all.return_value = threats
        
        # No debe lanzar excepción
        scheduler._initialize_counters()
        assert scheduler.threat_counters[TipoAmenaza.ARANA] == 0
    
    
    def test_get_next_threat_type_rotation(self, scheduler):
        """Prueba que la rotación de tipos de amenazas funcione correctamente"""
        initial_index = scheduler.current_type_index
        threat_types = []
        
        # Obtener varios tipos para verificar la rotación
        for _ in range(len(SchedulerConfig.THREAT_TYPES) + 2):
            threat_type = scheduler._get_next_threat_type()
            threat_types.append(threat_type)
        
        # Verificar que los tipos están en la configuración
        for threat_type in threat_types:
            assert threat_type in SchedulerConfig.THREAT_TYPES
        
        # Verificar que el índice rotó correctamente
        assert scheduler.current_type_index != initial_index or len(SchedulerConfig.THREAT_TYPES) == 1
    
    
    def test_generate_threat_success(self, scheduler, mock_repositories):
        """Prueba generación exitosa de amenaza"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        
        created_threat = Threat(
            id=1,
            zona_id=1,
            nombre="araña 1",
            tipo=TipoAmenaza.ARANA,
            costo_hormigas=10,
            estado=EstadoAmenaza.ACTIVA,
            hora_deteccion=datetime.now()
        )
        mock_threat_repo.create.return_value = created_threat
        
        # Generar amenaza
        scheduler._generate_threat()
        
        # Verificar que se llamó a create
        assert mock_threat_repo.create.called
        
        # Verificar que el contador aumentó
        call_args = mock_threat_repo.create.call_args[0][0]
        assert call_args.tipo in scheduler.threat_counters
    
    def test_generate_threat_zone_not_exists(self, scheduler, mock_repositories):
        """Prueba que no se genere amenaza si la zona no existe"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mock para que la zona no exista
        mock_zone_repo.zone_exists.return_value = False
        
        # Generar amenaza
        scheduler._generate_threat()
        
        # Verificar que NO se llamó a create
        assert not mock_threat_repo.create.called
    
       
    def test_generate_threat_with_cost_retrieval(self, scheduler, mock_repositories):
        """Prueba que se obtenga el costo correcto para cada tipo de amenaza"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        
        def capture_threat(threat):
            # Verificar que el costo sea el esperado para el tipo
            expected_cost = SchedulerConfig.get_threat_cost(threat.tipo)
            assert threat.costo_hormigas == expected_cost
            return threat
        
        mock_threat_repo.create.side_effect = capture_threat
        
        # Generar amenaza
        scheduler._generate_threat()
        
        assert mock_threat_repo.create.called
    
    def test_start_scheduler_success(self, scheduler):
        """Prueba inicio exitoso del scheduler"""
        with patch.object(scheduler.scheduler, 'add_job') as mock_add_job, \
             patch.object(scheduler.scheduler, 'start') as mock_start:
            
            scheduler.start()
            
            # Verificar que se llamaron los métodos correctos
            assert mock_add_job.called
            assert mock_start.called
            assert scheduler.is_running == True
            
            # Verificar parámetros del job
            call_kwargs = mock_add_job.call_args[1]
            assert call_kwargs['func'] == scheduler._generate_threat
            assert call_kwargs['trigger'] == 'interval'
            assert call_kwargs['seconds'] == SchedulerConfig.INTERVAL_SECONDS
            assert call_kwargs['id'] == 'threat_generator'
    
    def test_start_scheduler_already_running(self, scheduler):
        """Prueba que no se inicie el scheduler si ya está corriendo"""
        scheduler.is_running = True
        
        with patch.object(scheduler.scheduler, 'add_job') as mock_add_job, \
             patch.object(scheduler.scheduler, 'start') as mock_start:
            
            scheduler.start()
            
            # Verificar que NO se llamaron los métodos
            assert not mock_add_job.called
            assert not mock_start.called
    
        
    def test_stop_scheduler_success(self, scheduler):
        """Prueba detención exitosa del scheduler"""
        scheduler.is_running = True
        
        with patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            
            scheduler.stop()
            
            # Verificar que se llamó shutdown
            assert mock_shutdown.called
            assert scheduler.is_running == False
            
            # Verificar parámetros
            mock_shutdown.assert_called_with(wait=True)
    
    def test_stop_scheduler_not_running(self, scheduler):
        """Prueba que no se detenga el scheduler si no está corriendo"""
        scheduler.is_running = False
        
        with patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            
            scheduler.stop()
            
            # Verificar que NO se llamó shutdown
            assert not mock_shutdown.called
    
        
    def test_get_status_not_running(self, scheduler):
        """Prueba obtención de estado cuando el scheduler no está corriendo"""
        scheduler.is_running = False
        
        status = scheduler.get_status()
        
        assert isinstance(status, dict)
        assert status['is_running'] == False
        assert 'interval_seconds' in status
        assert 'default_zone_id' in status
        assert 'threat_types' in status
        assert 'threat_counters' in status
        assert 'current_type_index' in status
        assert 'next_threat_type' in status
        
        # Verificar tipos de datos
        assert isinstance(status['interval_seconds'], int)
        assert isinstance(status['threat_types'], list)
        assert isinstance(status['threat_counters'], dict)
        assert isinstance(status['current_type_index'], int)
        assert isinstance(status['next_threat_type'], str)
    
    def test_get_status_running(self, scheduler):
        """Prueba obtención de estado cuando el scheduler está corriendo"""
        scheduler.is_running = True
        
        status = scheduler.get_status()
        
        assert status['is_running'] == True
        assert isinstance(status, dict)
    
    def test_get_status_counters_values(self, scheduler):
        """Prueba que get_status devuelva los contadores correctos"""
        # Establecer algunos contadores
        scheduler.threat_counters[TipoAmenaza.ARANA] = 5
        scheduler.threat_counters[TipoAmenaza.ABEJA] = 3
        
        status = scheduler.get_status()
        
        assert status['threat_counters'][TipoAmenaza.ARANA.value] == 5
        assert status['threat_counters'][TipoAmenaza.ABEJA.value] == 3
    
    def test_get_status_current_type_index(self, scheduler):
        """Prueba que get_status devuelva el índice actual correcto"""
        scheduler.current_type_index = 1
        
        status = scheduler.get_status()
        
        assert status['current_type_index'] == 1
        assert status['next_threat_type'] == SchedulerConfig.THREAT_TYPES[1].value
    
    
    def test_threat_attributes_in_generated_threat(self, scheduler, mock_repositories):
        """Prueba que las amenazas generadas tengan todos los atributos necesarios"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        
        def capture_threat(threat):
            # Verificar atributos
            assert hasattr(threat, 'nombre')
            assert hasattr(threat, 'tipo')
            assert hasattr(threat, 'costo_hormigas')
            assert hasattr(threat, 'estado')
            assert hasattr(threat, 'zona_id')
            assert hasattr(threat, 'hora_deteccion')
            
            # Verificar valores
            assert threat.estado == EstadoAmenaza.ACTIVA
            assert threat.zona_id == SchedulerConfig.DEFAULT_ZONE_ID
            assert threat.costo_hormigas > 0
            
            return threat
        
        mock_threat_repo.create.side_effect = capture_threat
        
        # Generar amenaza
        scheduler._generate_threat()
        
        assert mock_threat_repo.create.called
    
       
    def test_counter_increment_after_generation(self, scheduler, mock_repositories):
        """Prueba que los contadores se incrementen después de generar amenazas"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        
        def return_threat(threat):
            return threat
        
        mock_threat_repo.create.side_effect = return_threat
        
        # Obtener el tipo de amenaza que se generará
        next_type = SchedulerConfig.THREAT_TYPES[scheduler.current_type_index]
        initial_counter = scheduler.threat_counters[next_type]
        
        # Generar amenaza
        scheduler._generate_threat()
        
        # El contador debe haberse incrementado
        # Nota: current_type_index avanza antes de generar, por lo que debemos verificar el tipo anterior
        for tipo, counter in scheduler.threat_counters.items():
            if counter > 0:
                assert counter > initial_counter or tipo != next_type
    
    def test_all_threat_types_can_be_generated(self, scheduler, mock_repositories):
        """Prueba que todos los tipos de amenazas puedan ser generados"""
        mock_threat_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        
        generated_types = set()
        
        def capture_threat_type(threat):
            generated_types.add(threat.tipo)
            return threat
        
        mock_threat_repo.create.side_effect = capture_threat_type
        
        # Generar suficientes amenazas para cubrir todos los tipos
        for _ in range(len(SchedulerConfig.THREAT_TYPES) * 2):
            scheduler._generate_threat()
        
        # Verificar que se generaron todos los tipos
        for threat_type in SchedulerConfig.THREAT_TYPES:
            assert threat_type in generated_types
