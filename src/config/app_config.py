"""
Application Configuration

Centralized configuration management with validation using Pydantic.
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(default="sqlite+aiosqlite:///./interestify.db", description="Database URL")
    echo: bool = Field(default=False, description="Enable SQL query logging")
    pool_size: int = Field(default=5, ge=1, le=50, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, le=100, description="Max overflow connections")


class CacheConfig(BaseModel):
    """Cache configuration"""
    ttl: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    max_size: int = Field(default=1000, ge=10, le=10000, description="Maximum cache entries")
    memory_limit_mb: float = Field(default=100.0, ge=10.0, le=1000.0, description="Memory limit in MB")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    default_limit: int = Field(default=100, ge=1, le=10000, description="Default rate limit per hour")
    burst_limit: int = Field(default=200, ge=1, le=20000, description="Burst rate limit")
    window_seconds: int = Field(default=3600, ge=60, le=86400, description="Rate limit window in seconds")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file_path: Optional[str] = Field(default=None, description="Log file path")
    max_file_size_mb: int = Field(default=10, ge=1, le=100, description="Max log file size in MB")
    backup_count: int = Field(default=5, ge=1, le=20, description="Number of backup log files")

    @validator('level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class AppConfig(BaseModel):
    """Main application configuration"""
    
    # App settings
    app_name: str = Field(default="Interestify", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, le=16, description="Number of worker processes")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    
    # Feature flags
    enable_analytics: bool = Field(default=True, description="Enable analytics features")
    enable_caching: bool = Field(default=True, description="Enable caching")
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    
    # External API settings
    max_request_timeout: int = Field(default=30, ge=5, le=120, description="Max request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Retry delay in seconds")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @validator('cors_methods', pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v

    @validator('cors_headers', pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(',')]
        return v

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', '8000')),
            cors_origins=os.getenv('CORS_ORIGINS', '*').split(','),
            database=DatabaseConfig(
                url=os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./interestify.db'),
                echo=os.getenv('DATABASE_ECHO', 'false').lower() == 'true'
            ),
            cache=CacheConfig(
                ttl=int(os.getenv('CACHE_TTL', '3600')),
                max_size=int(os.getenv('CACHE_MAX_SIZE', '1000'))
            ),
            logging=LoggingConfig(
                level=os.getenv('LOG_LEVEL', 'INFO').upper(),
                file_path=os.getenv('LOG_FILE_PATH')
            )
        )


# Global configuration instance
_app_config: Optional[AppConfig] = None


def get_app_config() -> AppConfig:
    """Get the global application configuration instance"""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig.from_env()
    return _app_config


def reload_config() -> AppConfig:
    """Reload configuration from environment"""
    global _app_config
    _app_config = AppConfig.from_env()
    return _app_config