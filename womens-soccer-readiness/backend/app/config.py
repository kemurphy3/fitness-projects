import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/soccer_readiness"
    )
    
    # For local development with SQLite (can be toggled)
    use_sqlite: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    sqlite_url: str = "sqlite:///./soccer_app.db"
    
    # JWT Settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App settings
    app_name: str = "Women's Soccer Readiness Coach"
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS settings
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings()