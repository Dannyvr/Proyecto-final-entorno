
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from services.resource_scheduler import ResourceScheduler, resource_scheduler
from models.resource import Resource, TipoRecurso, EstadoRecurso
from models.zone import Zona, TipoZona
from config.resources_scheduler_config import ResourcesSchedulerConfig


class TestResourceScheduler:
    """Suite de pruebas para ResourceScheduler"""
    
    @pytest.fixture
    def mock_repositories(self):
        """Mock de los repositorios"""
        with patch('services.resource_scheduler.ResourceRepository') as mock_resource_repo, \
             patch('services.resource_scheduler.ZoneRepository') as mock_zone_repo:
            
            # Configurar mocks
            mock_resource_instance = Mock()
            mock_zone_instance = Mock()
            
            mock_resource_repo.return_value = mock_resource_instance
            mock_zone_repo.return_value = mock_zone_instance
            
            yield mock_resource_instance, mock_zone_instance
    
    @pytest.fixture
    def scheduler(self, mock_repositories):
        """Crea una instancia del scheduler con repositorios mockeados"""
        mock_resource_repo, mock_zone_repo = mock_repositories
        
        # Configurar respuestas por defecto
        mock_resource_repo.get_all.return_value = []
        
        # Crear scheduler
        scheduler = ResourceScheduler()
        return scheduler
    
    def test_initialization(self, scheduler):
        """Prueba que el scheduler se inicialice correctamente"""
        assert scheduler.is_running == False
        assert scheduler.resource_counters is not None
        assert len(scheduler.resource_counters) == len(ResourcesSchedulerConfig.RESOURCE_TYPES)
        assert scheduler.current_type_index >= 0
        assert scheduler.current_type_index < len(ResourcesSchedulerConfig.RESOURCE_TYPES)
        assert scheduler.scheduler is not None
    
    def test_initialize_counters_empty_repo(self, scheduler, mock_repositories):
        """Prueba inicialización de contadores con repositorio vacío"""
        mock_resource_repo, _ = mock_repositories
        mock_resource_repo.get_all.return_value = []
        
        scheduler._initialize_counters()
        
        # Todos los contadores deben ser 0
        for counter in scheduler.resource_counters.values():
            assert counter == 0
    
    def test_initialize_counters_with_existing_resources(self, scheduler, mock_repositories):
        """Prueba inicialización de contadores con recursos existentes"""
        mock_resource_repo, _ = mock_repositories
        
        # Crear recursos de prueba
        resources = [
            Resource(
                id=1,
                zona_id=1,
                nombre="hoja 5",
                tipo=TipoRecurso.HOJA,
                cantidad_unitaria=10,
                peso=2,
                duracion_recoleccion=15,
                hormigas_requeridas=3,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            ),
            Resource(
                id=2,
                zona_id=1,
                nombre="semilla 3",
                tipo=TipoRecurso.SEMILLA,
                cantidad_unitaria=5,
                peso=1,
                duracion_recoleccion=10,
                hormigas_requeridas=2,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            ),
            Resource(
                id=3,
                zona_id=1,
                nombre="flor 7",
                tipo=TipoRecurso.FLOR,
                cantidad_unitaria=8,
                peso=3,
                duracion_recoleccion=20,
                hormigas_requeridas=4,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            )
        ]
        
        mock_resource_repo.get_all.return_value = resources
        
        scheduler._initialize_counters()
        
        # Verificar que los contadores se actualizaron
        assert scheduler.resource_counters[TipoRecurso.HOJA] == 5
        assert scheduler.resource_counters[TipoRecurso.SEMILLA] == 3
        assert scheduler.resource_counters[TipoRecurso.FLOR] == 7
    
    def test_initialize_counters_with_invalid_names(self, scheduler, mock_repositories):
        """Prueba que _initialize_counters maneje recursos con nombres inválidos"""
        mock_resource_repo, _ = mock_repositories
        
        # Recursos con nombres inválidos
        resources = [
            Resource(
                id=1,
                zona_id=1,
                nombre="recurso_invalido",
                tipo=TipoRecurso.HOJA,
                cantidad_unitaria=10,
                peso=2,
                duracion_recoleccion=15,
                hormigas_requeridas=3,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            ),
            Resource(
                id=2,
                zona_id=1,
                nombre="hoja",  # Sin número
                tipo=TipoRecurso.HOJA,
                cantidad_unitaria=10,
                peso=2,
                duracion_recoleccion=15,
                hormigas_requeridas=3,
                estado=EstadoRecurso.DISPONIBLE,
                hora_creacion=datetime.now()
            )
        ]
        
        mock_resource_repo.get_all.return_value = resources
        
        # No debe lanzar excepción
        scheduler._initialize_counters()
        assert scheduler.resource_counters[TipoRecurso.HOJA] == 0
    
    def test_initialize_counters_exception_handling(self, scheduler, mock_repositories):
        """Prueba que _initialize_counters maneje excepciones correctamente"""
        mock_resource_repo, _ = mock_repositories
        mock_resource_repo.get_all.side_effect = Exception("Database error")
        
        # No debe lanzar excepción
        scheduler._initialize_counters()
        
        # Los contadores deben permanecer en 0
        for counter in scheduler.resource_counters.values():
            assert counter == 0
    
    
       
    def test_generate_resource_success(self, scheduler, mock_repositories):
        """Prueba generación exitosa de recurso"""
        mock_resource_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        mock_zone = Zona(
            id=1,
            nombre="Zona Test",
            tipo=TipoZona.JARDIN,
            fecha_creacion=datetime.now()
        )
        mock_zone_repo.obtenerTodasLasZonas.return_value = [mock_zone]
        
        created_resource = Resource(
            id=1,
            zona_id=1,
            nombre="hoja 1",
            tipo=TipoRecurso.HOJA,
            cantidad_unitaria=10,
            peso=2,
            duracion_recoleccion=15,
            hormigas_requeridas=3,
            estado=EstadoRecurso.DISPONIBLE,
            hora_creacion=datetime.now()
        )
        mock_resource_repo.create.return_value = created_resource
        
        # Generar recurso
        scheduler._generate_resource()
        
        # Verificar que se llamó a create
        assert mock_resource_repo.create.called
        
        # Verificar que el contador aumentó
        call_args = mock_resource_repo.create.call_args[0][0]
        assert call_args.tipo in scheduler.resource_counters
    
    def test_generate_resource_zone_not_exists(self, scheduler, mock_repositories):
        """Prueba que no se genere recurso si la zona no existe"""
        mock_resource_repo, mock_zone_repo = mock_repositories
        
        # Configurar mock para que la zona no exista
        mock_zone_repo.zone_exists.return_value = False
        
        # Generar recurso
        scheduler._generate_resource()
        
        # Verificar que NO se llamó a create
        assert not mock_resource_repo.create.called
    
    def test_generate_resource_no_zones_available(self, scheduler, mock_repositories):
        """Prueba que no se genere recurso si no hay zonas disponibles"""
        mock_resource_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        mock_zone_repo.obtenerTodasLasZonas.return_value = []
        
        # Generar recurso
        scheduler._generate_resource()
        
        # Verificar que NO se llamó a create
        assert not mock_resource_repo.create.called
    
  
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
            assert call_kwargs['func'] == scheduler._generate_resource
            assert call_kwargs['trigger'] == 'interval'
            assert call_kwargs['seconds'] == ResourcesSchedulerConfig.INTERVAL_SECONDS
            assert call_kwargs['id'] == 'resource_generator'
    
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
        
        with patch.object(scheduler.scheduler, 'remove_job') as mock_remove_job, \
             patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            
            scheduler.stop()
            
            # Verificar que se llamaron los métodos correctos
            assert mock_remove_job.called
            assert mock_shutdown.called
            assert scheduler.is_running == False
            
            # Verificar parámetros
            mock_remove_job.assert_called_with('resource_generator')
            mock_shutdown.assert_called_with(wait=True)
    
    def test_stop_scheduler_not_running(self, scheduler):
        """Prueba que no se detenga el scheduler si no está corriendo"""
        scheduler.is_running = False
        
        with patch.object(scheduler.scheduler, 'remove_job') as mock_remove_job, \
             patch.object(scheduler.scheduler, 'shutdown') as mock_shutdown:
            
            scheduler.stop()
            
            # Verificar que NO se llamaron los métodos
            assert not mock_remove_job.called
            assert not mock_shutdown.called
    
       
    def test_get_status_not_running(self, scheduler):
        """Prueba obtención de estado cuando el scheduler no está corriendo"""
        scheduler.is_running = False
        
        status = scheduler.get_status()
        
        assert isinstance(status, dict)
        assert status['is_running'] == False
        assert 'interval_seconds' in status
        assert 'default_zone_id' in status
        assert 'resource_types' in status
        assert 'resource_counters' in status
        assert 'current_type_index' in status
        assert 'next_resource_type' in status
        
        # Verificar tipos de datos
        assert isinstance(status['interval_seconds'], int)
        assert isinstance(status['resource_types'], list)
        assert isinstance(status['resource_counters'], dict)
        assert isinstance(status['current_type_index'], int)
        assert isinstance(status['next_resource_type'], str)
    
    def test_get_status_running(self, scheduler):
        """Prueba obtención de estado cuando el scheduler está corriendo"""
        scheduler.is_running = True
        
        status = scheduler.get_status()
        
        assert status['is_running'] == True
        assert isinstance(status, dict)
    
    def test_get_status_counters_values(self, scheduler):
        """Prueba que get_status devuelva los contadores correctos"""
        # Establecer algunos contadores
        scheduler.resource_counters[TipoRecurso.HOJA] = 5
        scheduler.resource_counters[TipoRecurso.SEMILLA] = 3
        
        status = scheduler.get_status()
        
        assert status['resource_counters'][TipoRecurso.HOJA.value] == 5
        assert status['resource_counters'][TipoRecurso.SEMILLA.value] == 3
    
    def test_get_status_current_type_index(self, scheduler):
        """Prueba que get_status devuelva el índice actual correcto"""
        scheduler.current_type_index = 2
        
        status = scheduler.get_status()
        
        assert status['current_type_index'] == 2
        assert status['next_resource_type'] == ResourcesSchedulerConfig.RESOURCE_TYPES[2].value
    
       
    def test_resource_attributes_in_generated_resource(self, scheduler, mock_repositories):
        """Prueba que los recursos generados tengan todos los atributos necesarios"""
        mock_resource_repo, mock_zone_repo = mock_repositories
        
        # Configurar mocks
        mock_zone_repo.zone_exists.return_value = True
        mock_zone = Zona(
            id=1,
            nombre="Zona Test",
            tipo=TipoZona.JARDIN,
            fecha_creacion=datetime.now()
        )
        mock_zone_repo.obtenerTodasLasZonas.return_value = [mock_zone]
        
        def capture_resource(resource):
            # Verificar atributos
            assert hasattr(resource, 'nombre')
            assert hasattr(resource, 'tipo')
            assert hasattr(resource, 'cantidad_unitaria')
            assert hasattr(resource, 'peso')
            assert hasattr(resource, 'duracion_recoleccion')
            assert hasattr(resource, 'hormigas_requeridas')
            assert hasattr(resource, 'estado')
            assert hasattr(resource, 'zona_id')
            assert hasattr(resource, 'hora_creacion')
            
            # Verificar valores
            assert resource.estado == EstadoRecurso.DISPONIBLE
            assert resource.zona_id == 1
            assert resource.cantidad_unitaria > 0
            assert resource.peso > 0
            assert resource.duracion_recoleccion > 0
            assert resource.hormigas_requeridas > 0
            
            return resource
        
        mock_resource_repo.create.side_effect = capture_resource
        
        # Generar recurso
        scheduler._generate_resource()
        
        assert mock_resource_repo.create.called
