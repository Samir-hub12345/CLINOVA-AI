from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Clinova AI"
    ENVIRONMENT: str = "development"  # "development", "testing", "staging", "production"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "change-this-in-production-to-a-secure-random-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database & Cache
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinova"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Object Storage & Documents
    STORAGE_PROVIDER: str = "local_object_store"  # "local_object_store", "s3", "minio"
    STORAGE_LOCAL_DIR: str = "storage_data"
    STORAGE_BUCKET: str = "medical-documents"
    MAX_FILE_SIZE_BYTES: int = 500 * 1024 * 1024  # 500 MB limit for medical files
    PRESIGNED_URL_TTL_SECONDS: int = 900  # 15 minutes
    SCAN_ENABLED: bool = True
    CLAMAV_HOST: Optional[str] = None
    CLAMAV_PORT: int = 3310
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # AI Configuration & Prototype Settings
    DEMO_MODE: bool = True
    OFFLINE_DEMO: bool = False  # Enabled by the beginner local launch script.
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "mock"  # "mock", "gemini"
    STT_PROVIDER: str = "local"  # "local", "faster-whisper", "mock"
    OCR_PROVIDER: str = "local"  # "local", "paddleocr", "mock"
    TRANSLATION_PROVIDER: str = "local"  # "local", "indictrans2", "mock"
    DEFAULT_FACILITY: str = "Government District Hospital"
    RETENTION_HOURS: int = 24

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        """Ensures production configuration cannot accidentally use insecure development defaults."""
        if self.ENVIRONMENT.lower() == "production":
            if self.DEBUG:
                raise ValueError("FATAL CONFIGURATION ERROR: DEBUG cannot be enabled in production.")
            if "change-this" in self.SECRET_KEY.lower() or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "FATAL CONFIGURATION ERROR: Insecure SECRET_KEY detected for production environment. "
                    "A cryptographically strong secret of at least 32 characters is required."
                )
            if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
                raise ValueError("FATAL CONFIGURATION ERROR: Production DATABASE_URL must not point to localhost.")
        return self

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()