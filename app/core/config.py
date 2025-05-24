from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "UTM API"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str  # This should come directly from .env

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # First Superuser
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULL_NAME: str
    FIRST_SUPERUSER_IIN: str

    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:8080"
    ]
    
    # WebSocket
    WS_TELEMETRY_PATH: str = "/ws/telemetry"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()