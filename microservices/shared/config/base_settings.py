"""Base configuration settings for all microservices."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class BaseServiceSettings(BaseSettings):
    """Base settings that all services inherit from."""
    
    # Service info
    SERVICE_NAME: str = Field(..., description="Name of the microservice")
    SERVICE_PORT: int = Field(..., description="Port the service runs on")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # API Gateway
    API_GATEWAY_URL: str = Field(default="http://localhost:8000", description="API Gateway URL")
    
    # Other services
    PRODUCT_SERVICE_URL: str = Field(default="http://localhost:8001", description="Product Service URL")
    ORDER_SERVICE_URL: str = Field(default="http://localhost:8002", description="Order Service URL")
    DENOMINATION_SERVICE_URL: str = Field(default="http://localhost:8003", description="Denomination Service URL")
    NOTIFICATION_SERVICE_URL: str = Field(default="http://localhost:8004", description="Notification Service URL")
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection URL")
    DB_POOL_SIZE: int = Field(default=10, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Maximum pool overflow")
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # CORS
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = True
