"""
Data Source Repository Interface and Implementation

Handles persistence operations for data source configurations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.schemas import DataSourceConfig
from src.utils.database import DatabaseManager


class DataSourceRepository(ABC):
    """Abstract repository for data source configuration operations"""
    
    @abstractmethod
    async def save_config(self, config: DataSourceConfig) -> bool:
        """Save a data source configuration"""
        pass
    
    @abstractmethod
    async def get_config(self, name: str) -> Optional[DataSourceConfig]:
        """Get data source configuration by name"""
        pass
    
    @abstractmethod
    async def get_all_configs(self) -> List[DataSourceConfig]:
        """Get all data source configurations"""
        pass
    
    @abstractmethod
    async def update_config(self, name: str, config: DataSourceConfig) -> bool:
        """Update data source configuration"""
        pass
    
    @abstractmethod
    async def delete_config(self, name: str) -> bool:
        """Delete data source configuration"""
        pass
    
    @abstractmethod
    async def get_enabled_configs(self) -> List[DataSourceConfig]:
        """Get all enabled data source configurations"""
        pass


class DatabaseDataSourceRepository(DataSourceRepository):
    """Database implementation of data source repository"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def save_config(self, config: DataSourceConfig) -> bool:
        """Save data source configuration to database"""
        try:
            await self.db_manager.save_data_source_config(config)
            return True
        except Exception as e:
            logger.error(f"Error saving data source config: {e}")
            return False
    
    async def get_config(self, name: str) -> Optional[DataSourceConfig]:
        """Get data source configuration by name from database"""
        try:
            configs = await self.db_manager.get_all_data_source_configs()
            for config in configs:
                if config.name == name:
                    return config
            return None
        except Exception as e:
            print(f"Error retrieving data source config: {e}")
            return None
    
    async def get_all_configs(self) -> List[DataSourceConfig]:
        """Get all data source configurations from database"""
        try:
            return await self.db_manager.get_all_data_source_configs()
        except Exception as e:
            print(f"Error retrieving all data source configs: {e}")
            return []
    
    async def update_config(self, name: str, config: DataSourceConfig) -> bool:
        """Update data source configuration in database"""
        try:
            await self.db_manager.update_data_source_config(name, config)
            return True
        except Exception as e:
            print(f"Error updating data source config: {e}")
            return False
    
    async def delete_config(self, name: str) -> bool:
        """Delete data source configuration from database"""
        try:
            await self.db_manager.delete_data_source_config(name)
            return True
        except Exception as e:
            print(f"Error deleting data source config: {e}")
            return False
    
    async def get_enabled_configs(self) -> List[DataSourceConfig]:
        """Get all enabled data source configurations from database"""
        try:
            all_configs = await self.get_all_configs()
            return [config for config in all_configs if config.enabled]
        except Exception as e:
            print(f"Error retrieving enabled data source configs: {e}")
            return []