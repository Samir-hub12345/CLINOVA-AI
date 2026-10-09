"""CLINOVA AI — Core Configuration.

Continuous Care Intelligence System.
Non-diagnostic, advisory, human-in-the-loop clinical intelligence workstation.
"""

from pathlib import Path
from typing import List, Union, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = _CURRENT_FILE.parents[3]
BACKEND_ROOT = _CURRENT_FILE.parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_ROOT / ".env"), str(PROJECT_ROOT / ".env"), ".env"),
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
    PORT: Optional[int] = None
    HOST: Optional[str] = None
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://clinova-ai-pink.vercel.app",
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

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if v is not None:
            v = str(v).strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
        if not v or v == "your-database-url-here" or v.startswith("<"):
            dev_db = (BACKEND_ROOT / "clinova-dev.db").as_posix()
            return f"sqlite+aiosqlite:///{dev_db}"
        # Anchor relative SQLite paths to BACKEND_ROOT to prevent CWD divergence between root and backend
        if v.startswith("sqlite+aiosqlite:///./") or v.startswith("sqlite:///./"):
            rel_name = v.split(":///./", 1)[1]
            anchored = (BACKEND_ROOT / rel_name).as_posix()
            return f"sqlite+aiosqlite:///{anchored}"
        # Standardize PostgreSQL URLs for SQLAlchemy async engine (e.g. Render, Supabase, Neon)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("sqlite://") and not v.startswith("sqlite+"):
            return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return v

    # File Storage & Uploads (Phase 20)
    UPLOAD_DIR: str = "storage/documents"

    # Clinical Safety & Operation Flags
    DEMO_MODE: bool = True
    OFFLINE_MODE: bool = True
    SYNTHETIC_DATA_ONLY: bool = True
    ANONYMIZATION_ENABLED: bool = True
    AUDIT_LOGGING_ENABLED: bool = True
    DATA_RETENTION_HOURS: int = 24

    # Security & Authentication (Phase 14)
    SECRET_KEY: str = "clinova-native-dev-secret-key-32chars-minimum-2026!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    DEMO_USER_PASSWORD: str = "ClinovaDemo2026!"
    ALLOW_LEGACY_ACTOR_HEADERS: bool = True  # Strict server-side DB resolution still applies
    ALLOW_LEGACY_ANONYMOUS_FALLBACK: bool = False  # Strictly isolated for legacy Phase 13 test harness

    # Local AI Runtime (Phase 18)
    # MOCK_DETERMINISTIC keeps tests/CI/$0 operation hermetic; LOCAL_OLLAMA selects the
    # local on-premise Ollama daemon (no cloud inference, no paid APIs).
    AI_PROVIDER_MODE: str = "MOCK_DETERMINISTIC"  # MOCK_DETERMINISTIC | LOCAL_OLLAMA | DISABLED
    AI_RUNTIME_ENDPOINT: str = "http://127.0.0.1:11434"
    AI_MODEL_ID: str = "qwen3-4b-instruct"
    AI_TIMEOUT_SECONDS: float = 5.0

    @model_validator(mode="after")
    def validate_production_boundaries(self) -> "Settings":
        # Reconcile dynamic PORT / HOST provided by cloud platforms (Render, Cloud Run, etc.)
        if self.PORT is not None:
            self.BACKEND_PORT = self.PORT
        if self.HOST is not None:
            self.BACKEND_HOST = self.HOST

        # Production safety boundaries
        if self.ENVIRONMENT.lower() == "production":
            if self.HOST is None:
                self.BACKEND_HOST = "0.0.0.0"
            if self.SECRET_KEY == "clinova-native-dev-secret-key-32chars-minimum-2026!" or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "Production configuration violation: SECRET_KEY must be set to a high-entropy secret "
                    "(minimum 32 characters) via environment variable."
                )
            if self.DEBUG:
                self.DEBUG = False
            # Prevent development bypass flags from remaining active in production
            self.ALLOW_LEGACY_ACTOR_HEADERS = False
            self.ALLOW_LEGACY_ANONYMOUS_FALLBACK = False
        return self


settings = Settings()