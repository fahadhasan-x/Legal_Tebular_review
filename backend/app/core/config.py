"""
Application Configuration
Environment variables and settings management
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-in-production"
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Redis & Celery
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # AI/LLM
    GEMINI_API_KEY: str
    GROQ_API_KEY: str = ""
    
    # File Upload
    UPLOAD_DIR: str = "/data/uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".html", ".txt"]
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3004",
        "http://127.0.0.1:3004"
    ]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    # Extraction
    EXTRACTION_TIMEOUT: int = 300  # 5 minutes
    MAX_RETRIES: int = 3
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8192
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


# Create global settings instance
settings = Settings()
