"""
Data Source Service

Handles data source management operations including registration,
configuration, and lifecycle management. Now uses repository pattern for persistence.
"""

from typing import Any, Dict, List

from src.core.datasources.manager import DataSourceManager
from src.models.schemas import DataSourceConfig
from src.repositories.data_source_repository import DataSourceRepository


class DataSourceService:
    """Service for managing data sources"""
    
    def __init__(self, data_source_manager: DataSourceManager, data_source_repository: DataSourceRepository):
        self.data_source_manager = data_source_manager
        self.data_source_repository = data_source_repository
    
    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Get all configured data sources with their status"""
        sources = []
        for name in self.data_source_manager.get_configured_sources():
            source = self.data_source_manager.get_data_source(name)
            sources.append({
                "name": name,
                "enabled": source.config.enabled,
                "available": source.is_available(),
                "rate_limit": source.config.rate_limit,
                "rate_limit_info": source.get_rate_limit_info(),
            })
        return sources
    
    async def add_source(self, config: DataSourceConfig) -> bool:
        """
        Add a new data source
        
        Args:
            config: Data source configuration
            
        Returns:
            True if successfully added, False otherwise
        """
        # Add to manager first
        if self.data_source_manager.add_data_source(config):
            # Save to repository
            await self.data_source_repository.save_config(config)
            return True
        return False
    
    async def update_source(self, name: str, config: DataSourceConfig) -> bool:
        """
        Update data source configuration
        
        Args:
            name: Name of the data source
            config: New configuration
            
        Returns:
            True if successfully updated, False otherwise
        """
        # Update in manager first
        if self.data_source_manager.update_source_config(name, config):
            # Update in repository
            await self.data_source_repository.update_config(name, config)
            return True
        return False
    
    async def remove_source(self, name: str) -> bool:
        """
        Remove a data source
        
        Args:
            name: Name of the data source to remove
            
        Returns:
            True if successfully removed, False if not found
        """
        # Remove from manager first
        if self.data_source_manager.remove_data_source(name):
            # Remove from repository
            await self.data_source_repository.delete_config(name)
            return True
        return False
    
    def get_available_types(self) -> List[str]:
        """Get list of available data source types"""
        return self.data_source_manager.get_available_source_types()
    
    def get_rate_limit_status(self) -> Dict[str, Dict]:
        """Get rate limit status for all data sources"""
        return self.data_source_manager.get_rate_limit_status()
    
    async def close_all_sources(self):
        """Close all data source connections"""
        await self.data_source_manager.close_all()
    
    async def load_configurations_from_repository(self):
        """Load all data source configurations from repository"""
        configs = await self.data_source_repository.get_all_configs()
        for config in configs:
            self.data_source_manager.add_data_source(config)
    
    async def get_enabled_configurations(self) -> List[DataSourceConfig]:
        """Get all enabled data source configurations from repository"""
        return await self.data_source_repository.get_enabled_configs()