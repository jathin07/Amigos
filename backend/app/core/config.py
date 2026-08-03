import os
from datetime import timedelta

class BaseConfig:
    import secrets
    import os
    from datetime import timedelta
    
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Auth & JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)))
    
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    ACCOUNT_LOCK_DURATION = timedelta(minutes=int(os.getenv("ACCOUNT_LOCK_DURATION_MINUTES", 30)))
    PASSWORD_RESET_EXPIRY = timedelta(hours=int(os.getenv("PASSWORD_RESET_EXPIRY_HOURS", 24)))
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 12))
    
    # Feature Flags
    FEATURE_AI_ITINERARY = os.getenv("FEATURE_AI_ITINERARY", "False").lower() == "true"
    FEATURE_BACKGROUND_WORKERS = os.getenv("FEATURE_BACKGROUND_WORKERS", "False").lower() == "true"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)
