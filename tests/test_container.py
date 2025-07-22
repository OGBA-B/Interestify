"""
Tests for the dependency injection container
"""

import pytest
from src.core.container import Container


class MockService:
    """Test service class"""
    def __init__(self, value: str = "default"):
        self.value = value


class MockAnotherService:
    """Another test service class"""
    pass


class TestContainer:
    """Test the dependency injection container"""
    
    def setup_method(self):
        self.container = Container()
    
    def test_register_and_get_singleton(self):
        """Test registering and getting a singleton"""
        instance = MockService("singleton")
        self.container.register_singleton(MockService, instance)
        
        result = self.container.get(MockService)
        
        assert result is instance
        assert result.value == "singleton"
        
        # Should return the same instance
        result2 = self.container.get(MockService)
        assert result2 is instance
    
    def test_register_and_get_factory(self):
        """Test registering and getting from factory"""
        def factory():
            return MockService("factory")
        
        self.container.register_factory(MockService, factory)
        
        result = self.container.get(MockService)
        
        assert isinstance(result, MockService)
        assert result.value == "factory"
        
        # Should create a new instance each time
        result2 = self.container.get(MockService)
        assert result2 is not result
        assert result2.value == "factory"
    
    def test_register_transient(self):
        """Test registering a transient service"""
        self.container.register_transient(MockService, MockService)
        
        result = self.container.get(MockService)
        
        assert isinstance(result, MockService)
        assert result.value == "default"
        
        # Should create a new instance each time
        result2 = self.container.get(MockService)
        assert result2 is not result
    
    def test_get_unregistered_service(self):
        """Test getting an unregistered service that can be instantiated"""
        result = self.container.get(MockAnotherService)
        
        assert isinstance(result, MockAnotherService)
    
    def test_get_nonexistent_service(self):
        """Test getting a service that cannot be resolved"""
        class NonInstantiableService:
            def __init__(self, required_param):
                self.required_param = required_param
        
        with pytest.raises(ValueError, match="Cannot resolve service"):
            self.container.get(NonInstantiableService)
    
    def test_get_or_none_success(self):
        """Test get_or_none with existing service"""
        instance = MockService("test")
        self.container.register_singleton(MockService, instance)
        
        result = self.container.get_or_none(MockService)
        
        assert result is instance
    
    def test_get_or_none_failure(self):
        """Test get_or_none with non-resolvable service"""
        class NonInstantiableService:
            def __init__(self, required_param):
                self.required_param = required_param
        
        result = self.container.get_or_none(NonInstantiableService)
        
        assert result is None
    
    def test_clear(self):
        """Test clearing all services"""
        self.container.register_singleton(MockService, MockService("test"))
        self.container.register_factory(MockAnotherService, MockAnotherService)
        
        self.container.clear()
        
        # Should be able to resolve by instantiation after clear
        result = self.container.get(MockAnotherService)
        assert isinstance(result, MockAnotherService)
    
    def test_get_key(self):
        """Test the key generation method"""
        key = self.container._get_key(MockService)
        
        expected_key = f"{MockService.__module__}.{MockService.__name__}"
        assert key == expected_key