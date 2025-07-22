"""
Service Configuration and Initialization

This module sets up the dependency injection container and configures
all application services.
"""

from src.core.cache import cache_manager
from src.core.container import container
from src.core.datasources import data_source_manager
from src.services.analysis_service import AnalysisService
from src.services.cache_service import CacheService
from src.services.data_source_service import DataSourceService
from src.utils.database import DatabaseManager


def configure_services():
    """Configure all application services in the DI container"""
    
    # Register existing managers as singletons
    container.register_singleton(type(data_source_manager), data_source_manager)
    container.register_singleton(type(cache_manager), cache_manager)
    
    # Register database manager factory
    container.register_factory(DatabaseManager, lambda: DatabaseManager())
    
    # Register services
    container.register_factory(
        AnalysisService,
        lambda: AnalysisService(container.get(type(data_source_manager)))
    )
    
    container.register_factory(
        DataSourceService,
        lambda: DataSourceService(container.get(type(data_source_manager)))
    )
    
    container.register_factory(
        CacheService,
        lambda: CacheService(container.get(type(cache_manager)))
    )


def get_service(service_type):
    """Get a service instance from the container"""
    return container.get(service_type)


# Initialize services on module import
configure_services()