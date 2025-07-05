from typing import Dict, List, Optional, Type

from src.models.schemas import DataSourceConfig

from .base import DataSource
from .reddit import RedditDataSource
from .twitter import TwitterDataSource


class DataSourceManager:
    """Manager for data sources"""

    def __init__(self, plugin_dirs=None):
        self._data_sources: Dict[str, DataSource] = {}
        self._available_sources: Dict[str, Type[DataSource]] = {
            "twitter": TwitterDataSource,
            "reddit": RedditDataSource,
        }
        # Support for dynamic plugin loading
        if plugin_dirs is None:
            plugin_dirs = ["src/core/datasources/plugins"]
        self._plugin_dirs = plugin_dirs
        self.load_plugins()

    def load_plugins(self):
        """Dynamically load data source plugins from plugin directories"""
        import importlib.util
        import os

        for plugin_dir in self._plugin_dirs:
            if not os.path.isdir(plugin_dir):
                continue
            for fname in os.listdir(plugin_dir):
                if fname.endswith(".py") and not fname.startswith("__"):
                    module_name = fname[:-3]
                    module_path = os.path.join(plugin_dir, fname)
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        # Register all DataSource subclasses in the module
                        for attr in dir(mod):
                            obj = getattr(mod, attr)
                            if (
                                isinstance(obj, type)
                                and issubclass(obj, DataSource)
                                and obj is not DataSource
                            ):
                                self.register_data_source(module_name, obj)

    def register_data_source(self, name: str, source_class: Type[DataSource]):
        """Register a new data source type"""
        self._available_sources[name] = source_class

    def add_data_source(self, config: DataSourceConfig) -> bool:
        """
        Add a configured data source

        Args:
            config: DataSourceConfig with source configuration

        Returns:
            True if successfully added, False otherwise
        """
        if config.name in self._available_sources:
            source_class = self._available_sources[config.name]
            data_source = source_class(config)

            if data_source.is_available():
                self._data_sources[config.name] = data_source
                return True
            else:
                print(
                    f"Data source {config.name} is not available (missing configuration)"
                )
                return False
        else:
            print(f"Unknown data source type: {config.name}")
            return False

    def remove_data_source(self, name: str) -> bool:
        """
        Remove a data source

        Args:
            name: Name of the data source to remove

        Returns:
            True if successfully removed, False if not found
        """
        if name in self._data_sources:
            # Close any open connections
            data_source = self._data_sources[name]
            if hasattr(data_source, "close"):
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(data_source.close())
                except:
                    pass

            del self._data_sources[name]
            return True
        return False

    def get_data_source(self, name: str) -> Optional[DataSource]:
        """Get a data source by name"""
        return self._data_sources.get(name)

    def get_enabled_sources(self) -> List[DataSource]:
        """Get all enabled data sources"""
        return [
            source for source in self._data_sources.values() if source.config.enabled
        ]

    def get_available_source_types(self) -> List[str]:
        """Get list of available data source types"""
        return list(self._available_sources.keys())

    def get_configured_sources(self) -> List[str]:
        """Get list of currently configured data sources"""
        return list(self._data_sources.keys())

    def update_source_config(self, name: str, config: DataSourceConfig) -> bool:
        """
        Update configuration for an existing data source

        Args:
            name: Name of the data source
            config: New configuration

        Returns:
            True if successfully updated, False otherwise
        """
        if name in self._data_sources:
            # Remove old source
            self.remove_data_source(name)

            # Add with new config
            return self.add_data_source(config)
        return False

    def get_rate_limit_status(self) -> Dict[str, Dict]:
        """Get rate limit status for all data sources"""
        status = {}
        for name, source in self._data_sources.items():
            status[name] = source.get_rate_limit_info()
        return status

    async def close_all(self):
        """Close all data source connections"""
        for source in self._data_sources.values():
            if hasattr(source, "close"):
                try:
                    await source.close()
                except:
                    pass


# Global instance
data_source_manager = DataSourceManager()
