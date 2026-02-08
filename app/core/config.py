import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="billing_db", description="Database name")
    DB_USER: str = Field(default="postgres", description="Database user")
    DB_PASSWORD: str = Field(default="", description="Database password")
    DB_POOL_SIZE: int = Field(default=10, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Maximum pool overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Application settings
    APP_NAME: str = Field(default="Billing System", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Email settings
    MAIL_USERNAME: str = Field(default="", description="Email username")
    MAIL_PASSWORD: str = Field(default="", description="Email password")
    MAIL_FROM: str = Field(default="noreply@billingsystem.com", description="Sender email address")
    MAIL_PORT: int = Field(default=587, description="SMTP port")
    MAIL_SERVER: str = Field(default="smtp.gmail.com", description="SMTP server")
    MAIL_FROM_NAME: str = Field(default="Billing System", description="Sender name")
    MAIL_STARTTLS: bool = Field(default=True, description="Use STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, description="Use SSL/TLS")
    USE_CREDENTIALS: bool = Field(default=True, description="Use email credentials")
    VALIDATE_CERTS: bool = Field(default=True, description="Validate certificates")
    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual components."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def async_database_url(self) -> str:
        """Construct async database URL for async operations."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        # Look for .env file in the app directory
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
