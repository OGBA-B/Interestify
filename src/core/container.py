"""
Dependency Injection Container for Interestify

This module provides a simple dependency injection container that manages
the lifecycle of application services and their dependencies.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar('T')


class Container:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton instance"""
        key = self._get_key(service_type)
        self._singletons[key] = instance
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating instances"""
        key = self._get_key(service_type)
        self._factories[key] = factory
    
    def register_transient(self, service_type: Type[T], implementation: Type[T]) -> None:
        """Register a transient service (new instance each time)"""
        key = self._get_key(service_type)
        self._factories[key] = implementation
    
    def get(self, service_type: Type[T]) -> T:
        """Get an instance of the requested service"""
        key = self._get_key(service_type)
        
        # Check if it's a singleton
        if key in self._singletons:
            return self._singletons[key]
        
        # Check if there's a factory
        if key in self._factories:
            factory = self._factories[key]
            if callable(factory):
                return factory()
            else:
                # It's a class, instantiate it
                return factory()
        
        # Try to instantiate directly
        try:
            return service_type()
        except Exception as e:
            raise ValueError(f"Cannot resolve service {service_type.__name__}: {e}")
    
    def get_or_none(self, service_type: Type[T]) -> Optional[T]:
        """Get an instance or None if not found"""
        try:
            return self.get(service_type)
        except:
            return None
    
    def _get_key(self, service_type: Type) -> str:
        """Get string key for service type"""
        return f"{service_type.__module__}.{service_type.__name__}"
    
    def clear(self) -> None:
        """Clear all registered services"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()


# Global container instance
container = Container()