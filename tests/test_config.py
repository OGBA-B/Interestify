"""
Tests for the configuration management system
"""

import os
import pytest
from unittest.mock import patch

from src.config.app_config import AppConfig, get_app_config, reload_config
from src.config.security_config import SecurityConfig, get_security_config, reload_security_config


class TestAppConfig:
    """Test the AppConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AppConfig()
        
        assert config.app_name == "Interestify"
        assert config.version == "2.0.0"
        assert config.debug is False
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.cors_origins == ["*"]
        assert config.enable_analytics is True
        assert config.enable_caching is True
    
    def test_from_env(self):
        """Test configuration from environment variables"""
        env_vars = {
            'DEBUG': 'true',
            'HOST': '127.0.0.1',
            'PORT': '9000',
            'CORS_ORIGINS': 'http://localhost:3000,https://example.com',
            'DATABASE_URL': 'postgresql://test',
            'CACHE_TTL': '7200',
            'LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict(os.environ, env_vars):
            config = AppConfig.from_env()
            
            assert config.debug is True
            assert config.host == '127.0.0.1'
            assert config.port == 9000
            assert config.cors_origins == ['http://localhost:3000', 'https://example.com']
            assert config.database.url == 'postgresql://test'
            assert config.cache.ttl == 7200
            assert config.logging.level == 'DEBUG'
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string"""
        config = AppConfig(cors_origins="http://localhost:3000,https://example.com")
        assert config.cors_origins == ['http://localhost:3000', 'https://example.com']
    
    def test_database_config_validation(self):
        """Test database configuration validation"""
        config = AppConfig()
        
        assert config.database.pool_size >= 1
        assert config.database.pool_size <= 50
        assert config.database.max_overflow >= 0
    
    def test_cache_config_validation(self):
        """Test cache configuration validation"""
        config = AppConfig()
        
        assert config.cache.ttl >= 60
        assert config.cache.ttl <= 86400
        assert config.cache.max_size >= 10
        assert config.cache.memory_limit_mb >= 10.0
    
    def test_logging_config_validation(self):
        """Test logging configuration validation"""
        config = AppConfig()
        
        assert config.logging.level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert config.logging.max_file_size_mb >= 1
        assert config.logging.backup_count >= 1


class TestSecurityConfig:
    """Test the SecurityConfig class"""
    
    def test_default_config(self):
        """Test default security configuration"""
        config = SecurityConfig()
        
        assert config.jwt_algorithm == "HS256"
        assert config.jwt_expiration_hours == 24
        assert config.enable_authentication is False
        assert config.require_api_keys is False
        assert config.enable_encryption is True
        assert config.min_password_length == 8
        assert config.enable_csp is True
    
    def test_from_env(self):
        """Test security configuration from environment"""
        env_vars = {
            'SECURITY_ENABLE_AUTHENTICATION': 'true',
            'SECURITY_REQUIRE_API_KEYS': 'true',
            'SECURITY_FORCE_HTTPS': 'true',
            'SECURITY_JWT_SECRET_KEY': 'test-jwt-key',
            'SECURITY_SECRET_KEY': 'test-secret-key'
        }
        
        with patch.dict(os.environ, env_vars):
            config = SecurityConfig.from_env()
            
            assert config.enable_authentication is True
            assert config.require_api_keys is True
            assert config.force_https is True
            assert config.jwt_secret_key == 'test-jwt-key'
            assert config.secret_key == 'test-secret-key'
    
    def test_jwt_algorithm_validation(self):
        """Test JWT algorithm validation"""
        # Valid algorithm
        config = SecurityConfig(jwt_algorithm="HS256")
        assert config.jwt_algorithm == "HS256"
        
        # Invalid algorithm should raise error
        with pytest.raises(ValueError, match="JWT algorithm must be one of"):
            SecurityConfig(jwt_algorithm="INVALID")
    
    def test_password_validation(self):
        """Test password validation"""
        config = SecurityConfig()
        
        # Valid password
        valid, errors = config.validate_password("StrongP@ss1")
        assert valid is True
        assert len(errors) == 0
        
        # Invalid password - too short
        valid, errors = config.validate_password("weak")
        assert valid is False
        assert any("at least 8 characters" in error for error in errors)
        
        # Invalid password - missing uppercase
        valid, errors = config.validate_password("weakpass1!")
        assert valid is False
        assert any("uppercase letter" in error for error in errors)
        
        # Invalid password - missing number
        valid, errors = config.validate_password("WeakPass!")
        assert valid is False
        assert any("number" in error for error in errors)
        
        # Invalid password - missing special character
        valid, errors = config.validate_password("WeakPass1")
        assert valid is False
        assert any("special character" in error for error in errors)
    
    def test_csp_header_generation(self):
        """Test CSP header generation"""
        config = SecurityConfig()
        
        csp_header = config.get_csp_header()
        assert "default-src 'self'" in csp_header
        assert "script-src 'self' 'unsafe-inline'" in csp_header
        
        # Test with CSP disabled
        config_no_csp = SecurityConfig(enable_csp=False)
        assert config_no_csp.get_csp_header() == ""
    
    def test_encryption_disabled_without_cryptography(self):
        """Test that encryption is disabled when cryptography is not available"""
        # This test assumes cryptography is available, but tests the fallback logic
        config = SecurityConfig(enable_encryption=True, encryption_key=None)
        
        # Should have generated an encryption key or disabled encryption
        if config.enable_encryption:
            assert config.encryption_key is not None
        else:
            assert config.encryption_key is None


class TestConfigurationGlobals:
    """Test global configuration functions"""
    
    def test_get_app_config_singleton(self):
        """Test that get_app_config returns singleton instance"""
        config1 = get_app_config()
        config2 = get_app_config()
        
        assert config1 is config2
    
    def test_get_security_config_singleton(self):
        """Test that get_security_config returns singleton instance"""
        config1 = get_security_config()
        config2 = get_security_config()
        
        assert config1 is config2
    
    def test_reload_config(self):
        """Test configuration reload functionality"""
        # Get initial config
        initial_config = get_app_config()
        
        # Reload configuration
        reloaded_config = reload_config()
        
        # Should be a new instance with same values
        assert reloaded_config is not initial_config
        assert reloaded_config.app_name == initial_config.app_name
    
    def test_reload_security_config(self):
        """Test security configuration reload functionality"""
        # Get initial config
        initial_config = get_security_config()
        
        # Reload configuration
        reloaded_config = reload_security_config()
        
        # Should be a new instance with same values
        assert reloaded_config is not initial_config
        assert reloaded_config.jwt_algorithm == initial_config.jwt_algorithm