"""
Security Configuration

Security-related configuration with proper validation and encryption support.
"""

import os
import secrets
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class APIKeyConfig(BaseModel):
    """API key configuration"""
    name: str = Field(..., description="API key name")
    key: str = Field(..., description="Encrypted API key")
    permissions: list = Field(default_factory=list, description="API key permissions")
    rate_limit: Optional[int] = Field(default=None, description="Custom rate limit for this key")


class SecurityConfig(BaseModel):
    """Security configuration"""
    
    # Secret key for encryption
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="Secret key for encryption")
    
    # JWT settings
    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=8760, description="JWT expiration in hours")
    
    # Authentication settings
    enable_authentication: bool = Field(default=False, description="Enable authentication")
    require_api_keys: bool = Field(default=False, description="Require API keys for requests")
    max_login_attempts: int = Field(default=5, ge=1, le=20, description="Max login attempts before lockout")
    lockout_duration_minutes: int = Field(default=15, ge=1, le=1440, description="Account lockout duration")
    
    # Data encryption
    enable_encryption: bool = Field(default=True, description="Enable data encryption")
    encryption_key: Optional[str] = Field(default=None, description="Data encryption key")
    
    # Password requirements
    min_password_length: int = Field(default=8, ge=6, le=128, description="Minimum password length")
    require_special_chars: bool = Field(default=True, description="Require special characters in passwords")
    require_uppercase: bool = Field(default=True, description="Require uppercase letters in passwords")
    require_numbers: bool = Field(default=True, description="Require numbers in passwords")
    
    # Session settings
    session_timeout_minutes: int = Field(default=30, ge=5, le=1440, description="Session timeout in minutes")
    secure_cookies: bool = Field(default=True, description="Use secure cookies")
    
    # HTTPS settings
    force_https: bool = Field(default=False, description="Force HTTPS connections")
    ssl_cert_path: Optional[str] = Field(default=None, description="SSL certificate path")
    ssl_key_path: Optional[str] = Field(default=None, description="SSL private key path")
    
    # Content Security Policy
    enable_csp: bool = Field(default=True, description="Enable Content Security Policy")
    csp_directives: Dict[str, str] = Field(
        default_factory=lambda: {
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data: https:",
            "connect-src": "'self'",
            "font-src": "'self'",
            "object-src": "'none'",
            "media-src": "'self'",
            "frame-src": "'none'"
        },
        description="Content Security Policy directives"
    )
    
    # Request validation
    max_request_size_mb: int = Field(default=10, ge=1, le=100, description="Maximum request size in MB")
    enable_request_validation: bool = Field(default=True, description="Enable strict request validation")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate encryption key if not provided
        if self.enable_encryption and not self.encryption_key:
            try:
                from cryptography.fernet import Fernet
                self.encryption_key = Fernet.generate_key().decode()
            except ImportError:
                # Cryptography not available, leave encryption_key as None
                # The fernet_cipher property will handle this gracefully
                pass

    @validator('jwt_algorithm')
    def validate_jwt_algorithm(cls, v):
        valid_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if v not in valid_algorithms:
            raise ValueError(f'JWT algorithm must be one of: {valid_algorithms}')
        return v

    @property
    def fernet_cipher(self):
        """Get Fernet cipher for encryption/decryption"""
        if self.enable_encryption and self.encryption_key:
            try:
                from cryptography.fernet import Fernet
                return Fernet(self.encryption_key.encode())
            except ImportError:
                return None
        return None

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.enable_encryption:
            return data
        
        cipher = self.fernet_cipher
        if cipher is None:
            raise ValueError("Encryption is enabled but cryptography package is not available or encryption key is invalid")
        
        return cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.enable_encryption:
            return encrypted_data
        
        cipher = self.fernet_cipher
        if cipher is None:
            raise ValueError("Encryption is enabled but cryptography package is not available or encryption key is invalid")
        
        try:
            return cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")

    def get_csp_header(self) -> str:
        """Get Content Security Policy header value"""
        if not self.enable_csp:
            return ""
        
        directives = []
        for directive, value in self.csp_directives.items():
            directives.append(f"{directive} {value}")
        
        return "; ".join(directives)

    def validate_password(self, password: str) -> tuple[bool, list[str]]:
        """Validate password against security requirements"""
        errors = []
        
        if len(password) < self.min_password_length:
            errors.append(f"Password must be at least {self.min_password_length} characters long")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.require_special_chars and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors

    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create security configuration from environment variables"""
        return cls(
            enable_authentication=os.getenv('SECURITY_ENABLE_AUTHENTICATION', 'false').lower() == 'true',
            require_api_keys=os.getenv('SECURITY_REQUIRE_API_KEYS', 'false').lower() == 'true',
            enable_encryption=os.getenv('SECURITY_ENABLE_ENCRYPTION', 'true').lower() == 'true',
            force_https=os.getenv('SECURITY_FORCE_HTTPS', 'false').lower() == 'true',
            enable_csp=os.getenv('SECURITY_ENABLE_CSP', 'true').lower() == 'true',
            jwt_secret_key=os.getenv('SECURITY_JWT_SECRET_KEY', secrets.token_urlsafe(32)),
            secret_key=os.getenv('SECURITY_SECRET_KEY', secrets.token_urlsafe(32)),
            encryption_key=os.getenv('SECURITY_ENCRYPTION_KEY')
        )


# Global security configuration instance
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """Get the global security configuration instance"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig.from_env()
    return _security_config


def reload_security_config() -> SecurityConfig:
    """Reload security configuration from environment"""
    global _security_config
    _security_config = SecurityConfig.from_env()
    return _security_config