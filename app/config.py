import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Garbage Truck Monitoring System"
    SECRET_KEY: str = "super_secret_key_waste_monitoring_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite+aiosqlite:///./waste_monitoring.db"
    OSRM_SERVER_URL: str = "https://router.project-osrm.org"
    GOOGLE_MAPS_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
