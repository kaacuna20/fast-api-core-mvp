from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    APP_API_NAME: str = os.getenv("APP_API_NAME", "My FastAPI Application")
    APP_API_VERSION: str = os.getenv("APP_API_VERSION", "1.0.0")    
    
    # API Keys configuration
    APP_API_KEY: str = os.getenv("APP_API_KEY", "")
    APP_API_KEY_HEADER: str = os.getenv("APP_API_KEY_HEADER", "X-API-Key")

    # JWT configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # CORS configuration
    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://yourdomain.com"
    ]

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_MAX_AGE: int = 600
    
    # Rate limiting
    RATE_LIMIT_SECONDS: int = 2

    # DB configuration
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")
    DB_NAME: str = os.getenv("DB_NAME", "db")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))

    # Storage configuration
    FYLESYSTEM = str(os.getenv("FYLESYSTEM", "local"))
    FYLESYSTEM_LOCAL_STORAGE_PATH = str(os.getenv("FYLESYSTEM_LOCAL_STORAGE_PATH", os.path.join(BASE_DIR, "storage", "app","files")))

    # S3 configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_REGION: str = os.getenv("S3_REGION", "")

    # logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "ERROR")
    LOG_FORMAT_DEBUG: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d"
    LOG_FORMAT_CONSOLE: str = "%(levelname)s: %(message)s"

    # cache configuration
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "redis")
    CACHE_EXPIRE_SECONDS: int = int(os.getenv("CACHE_EXPIRE_SECONDS", 3600))
    CACHE_REDIS_URL: str = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")

    # email configuration
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.example.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "user@example.com")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "password")
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", f"noreply@{os.getenv('APP_API_NAME', 'example.com').replace(' ', '').lower()}.com")
    EMAIL_PATH_TEMPLATE: str = os.getenv("EMAIL_PATH_TEMPLATE", os.path.join(BASE_DIR, "app", "utils", "mail", "templates"))

    # celery configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # environment configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


    class Config:
        env_file = ".env"
        case_sensitive = True

