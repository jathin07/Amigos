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

    # Cloudflare R2 Configuration
    R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "amigos-storage")
    R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "4eef1037b718d26dca5940bb91972ec3")
    R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "8a0ba6292608521213c00448b6d1f4c2")
    R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "e57ff732b52fa9c8e5ca28609317e7d071895aacda55b61bb2508637c06108ca")
    R2_ENDPOINT = os.getenv("R2_ENDPOINT", "https://4eef1037b718d26dca5940bb91972ec3.r2.cloudflarestorage.com")
    R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "https://cdn.amigostourism.com")
    R2_PRESIGNED_EXPIRY = int(os.getenv("R2_PRESIGNED_EXPIRY", 600))

    # Caching configuration
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)
