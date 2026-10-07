"""CLINOVA AI — Core Configuration.

Continuous Care Intelligence System.
Non-diagnostic, advisory, human-in-the-loop clinical intelligence workstation.
"""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = _CURRENT_FILE.parents[3]
BACKEND_ROOT = _CURRENT_FILE.parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Metadata
    APP_NAME: str = "Clinova AI"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"  # development, testing, staging, production
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    DEFAULT_FACILITY: str = "Government District Hospital"

    # Network & Hosts
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Persistence
    DATABASE_URL: str = "sqlite+aiosqlite:///./clinova-dev.db"

    # Clinical Safety & Operation Flags
    DEMO_MODE: bool = True
    OFFLINE_MODE: bool = True
    SYNTHETIC_DATA_ONLY: bool = True
    ANONYMIZATION_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    DATA_RETENTION_HOURS: int = 24

    # Security
    SECRET_KEY: str = "clinova-native-dev-secret-key-32chars-minimum-2026!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()