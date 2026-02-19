"""Order Service configuration."""

import sys
from pathlib import Path
from pydantic import Field

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.config.base_settings import BaseServiceSettings


class OrderServiceSettings(BaseServiceSettings):
    """Order Service specific settings."""
    
    SERVICE_NAME: str = Field(default="order-service", description="Service name")
    SERVICE_PORT: int = Field(default=8002, description="Service port")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/order_db",
        description="Order database URL"
    )
    
    class Config:
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"


settings = OrderServiceSettings()
