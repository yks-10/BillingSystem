"""Notification Service configuration."""

import sys
from pathlib import Path
from pydantic import Field

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.config.base_settings import BaseServiceSettings


class NotificationServiceSettings(BaseServiceSettings):
    """Notification Service specific settings."""
    
    SERVICE_NAME: str = Field(default="notification-service", description="Service name")
    SERVICE_PORT: int = Field(default=8004, description="Service port")
    
    # Email settings
    MAIL_USERNAME: str = Field(default="", description="Email username")
    MAIL_PASSWORD: str = Field(default="", description="Email password")
    MAIL_FROM: str = Field(default="noreply@billingsystem.com", description="Sender email")
    MAIL_PORT: int = Field(default=587, description="SMTP port")
    MAIL_SERVER: str = Field(default="smtp.gmail.com", description="SMTP server")
    MAIL_FROM_NAME: str = Field(default="Billing System", description="Sender name")
    MAIL_STARTTLS: bool = Field(default=True, description="Use STARTTLS")
    MAIL_SSL_TLS: bool = Field(default=False, description="Use SSL/TLS")
    USE_CREDENTIALS: bool = Field(default=True, description="Use email credentials")
    VALIDATE_CERTS: bool = Field(default=True, description="Validate certificates")
    
    class Config:
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"


settings = NotificationServiceSettings()
