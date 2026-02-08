"""
Core module for the billing system.
Provides database connectivity and configuration management.
"""

from app.core.database import (
    DatabaseConnection,
    db,
    Base,
    get_db,
    init_db,
    close_db,
)

from app.core.config import (
    Settings,
    settings,
)

__all__ = [
    # Database
    "DatabaseConnection",
    "db",
    "Base",
    "get_db",
    "init_db",
    "close_db",
    # Configuration
    "Settings",
    "settings",
]
