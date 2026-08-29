"""
Application Factory Package Initialization.
Re-exports the core application factory and extensions.
"""

from app.core.startup import create_app
from app.core.extensions import db, migrate, cache

__all__ = ["create_app", "db", "migrate", "cache"]
