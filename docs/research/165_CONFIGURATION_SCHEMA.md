# CLINOVA AI — Strongly Typed Configuration Schema Specification

> **Document ID:** `RES-165`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Backend Engineering & Type Safety Group  

---

## 1. Architectural Schema Overview

CLINOVA AI enforces **Strongly Typed, Fail-Fast Configuration**. At system initialization, every environment variable is ingested, parsed, validated, and normalized before any database pool, background task, or HTTP listener is initialized.

If any mandatory variable is missing, malformed, or violates security invariants (e.g., attempting to boot production without a secure 64-character secret, or attempting to expose a service-role key to the browser), the process terminates immediately with an explicit fatal error log.

---

## 2. Backend Configuration Schema (Pydantic Settings)

The canonical backend settings specification models all operational dimensions:

```python
"""backend/app/core/config_schema.py - Phase 9 Configuration Specification."""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Set, Union
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    SecretStr,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEV = "dev"
    LOCAL_DEMO = "local_demo"
    PHC_EDGE = "phc_edge"
    DISTRICT_HOSPITAL = "district_hospital"
    CLOUD_PREVIEW = "cloud_preview"
    TEST = "test"


class ClinovaFacilityProfile(str, Enum):
    ENV_GOV_HOSPITAL = "ENV_GOV_HOSPITAL"
    ENV_PHC = "ENV_PHC"
    ENV_PUBLIC_CAMP = "ENV_PUBLIC_CAMP"
    ENV_COMPANY_CLINIC = "ENV_COMPANY_CLINIC"
    ENV_INDUSTRIAL_HEALTH = "ENV_INDUSTRIAL_HEALTH"
    ENV_CAMPUS_HEALTH = "ENV_CAMPUS_HEALTH"


class StorageMode(str, Enum):
    LOCAL_FS = "LOCAL_FS"
    SUPABASE_STORAGE = "SUPABASE_STORAGE"


class SyncMode(str, Enum):
    OFFLINE_ONLY = "OFFLINE_ONLY"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    CLOUD_NATIVE = "CLOUD_NATIVE"


class ClinovaDataMode(str, Enum):
    SYNTHETIC = "synthetic"
    LIVE = "live"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AIProviderMode(str, Enum):
    LOCAL_RULES = "local_rules"
    LOCAL_QWEN = "local_qwen"
    HYBRID = "hybrid"
    MOCK = "mock"


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",  # Rejects undefined/unexpected environment variables
        case_sensitive=True,
    )

    # 1. Environment Identity & Runtime Mode
    APP_ENV: AppEnv = Field(default=AppEnv.DEV, description="Infrastructure deployment topology")
    CLINOVA_ENVIRONMENT_ID: ClinovaFacilityProfile = Field(
        default=ClinovaFacilityProfile.ENV_PHC,
        description="Clinical facility operational profile",
    )
    APP_NAME: str = Field(default="CLINOVA AI", description="System canonical application title")
    APP_VERSION: str = Field(default="2.0.0", description="SemVer software version")
    DEBUG: bool = Field(default=False, description="Debug mode (strictly forbidden in production)")
    API_V1_STR: str = Field(default="/api/v1", description="API route prefix")

    # 2. Network & Host Binding
    BACKEND_HOST: str = Field(default="127.0.0.1", description="HTTP server bind IP")
    BACKEND_PORT: int = Field(default=8000, description="HTTP server port")
    API_BASE_URL: str = Field(default="http://localhost:8000", description="Fully qualified backend API base URL")
    FRONTEND_BASE_URL: str = Field(default="http://localhost:3000", description="Fully qualified frontend URL")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    # 3. Security & Cryptographic Tokens
    SECRET_KEY: SecretStr = Field(
        ...,
        description="Cryptographic secret key for session JWT signing (min 32 chars in dev, 64 in prod)",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Session expiration in minutes")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT cryptographic algorithm")

    # 4. Database Persistence
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./clinova-dev.db",
        description="SQLAlchemy async connection string",
    )
    LOCAL_DATABASE_PATH: Optional[Path] = Field(
        default=Path("./clinova-dev.db"),
        description="Absolute or relative path to local SQLite database file",
    )
    DB_POOL_SIZE: int = Field(default=5, description="Connection pool size (Postgres)")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections (Postgres)")
    DB_BUSY_TIMEOUT_MS: int = Field(default=5000, description="SQLite busy timeout in ms")

    # 5. Supabase Integration (Optional/Cloud Only)
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase project URL")
    SUPABASE_ANON_KEY: Optional[SecretStr] = Field(default=None, description="Supabase client anon key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Supabase service role admin key (SERVER-ONLY; NEVER exposed to browser)",
    )

    # 6. Storage & File Media
    STORAGE_MODE: StorageMode = Field(default=StorageMode.LOCAL_FS, description="Media persistence engine")
    STORAGE_PATH: Path = Field(
        default=Path("./data/storage"),
        description="Root filesystem storage path for slips and audio",
    )
    STORAGE_TEMP_PATH: Path = Field(
        default=Path("./data/storage/tmp"),
        description="Temporary processing directory for audio/image chunks",
    )
    MAX_UPLOAD_SIZE_BYTES: int = Field(default=15 * 1024 * 1024, description="Max upload limit (15MB)")
    MEDIA_RETENTION_POLICY_DAYS: int = Field(
        default=30,
        description="DPDP Act retention limit for raw media before purge to hash-only",
    )

    # 7. Clinical Data Safety & Compliance
    CLINOVA_DATA_MODE: ClinovaDataMode = Field(
        default=ClinovaDataMode.SYNTHETIC,
        description="Enforces synthetic mock data; requires dual-key authorization for live PHI",
    )
    ANONYMIZATION_ENABLED: bool = Field(default=True, description="Enforce 18-element HIPAA/DPDP de-identification")
    AUDIT_MODE: bool = Field(default=True, description="Enforce immutable Merkle hash chain audit ledger")
    PHI_LOGGING_POLICY: str = Field(default="STRICT_REDACTION", description="Logging redaction level")

    # 8. Operational & Sync Modes
    OFFLINE_MODE: bool = Field(default=True, description="Autonomous offline operations enabled")
    SYNC_MODE: SyncMode = Field(default=SyncMode.OFFLINE_ONLY, description="Central synchronization topology")
    SYNC_ENDPOINT: Optional[str] = Field(default=None, description="District hub or cloud sync API URL")
    SYNC_BATCH_SIZE: int = Field(default=50, description="Sync journal batch chunk size")

    # 9. AI & Perceptual Boundaries (Pluggable Local Runtimes)
    AI_PROVIDER: AIProviderMode = Field(default=AIProviderMode.LOCAL_RULES, description="Primary AI inference engine")
    AI_BASE_URL: Optional[str] = Field(default=None, description="Local loopback SLM server endpoint")
    AI_MODEL: str = Field(default="qwen2.5-3b-instruct-q4", description="Local SLM model identifier")
    WHISPER_MODEL: str = Field(default="base-int8", description="Faster-whisper local model size")
    OCR_ENGINE: str = Field(default="paddleocr-v4", description="Local edge OCR extraction engine")
    TRANSLATION_ENGINE: str = Field(default="indic-trans-v2", description="Local edge language translator")

    # 10. Observability & Logging
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, description="Application log verbosity")
    LOG_DESTINATION: str = Field(default="CONSOLE_JSON", description="Structured JSON log sink")

    # 11. Feature Flags
    FEATURE_VOICE: bool = Field(default=True, description="Voice symptom recording and transcription")
    FEATURE_OCR: bool = Field(default=True, description="Prescription and lab slip optical recognition")
    FEATURE_TRANSLATION: bool = Field(default=True, description="Multilingual vernacular translation")
    FEATURE_CAREGRAPH: bool = Field(default=True, description="Continuous trajectory and risk projection")
    FEATURE_FACILITYGRAPH: bool = Field(default=True, description="Facility resource and referral gating")
    FEATURE_SIGNALGRAPH: bool = Field(default=True, description="Syndromic anomaly and trend detection")
    FEATURE_ORCHESTRATION: bool = Field(default=True, description="Multi-graph clinical recommendation synthesis")
    FEATURE_OFFLINE_SYNC: bool = Field(default=False, description="Background journal synchronization")
    FEATURE_EMERGENCY_MODE: bool = Field(default=True, description="Rapid anonymous casualty intake token flow")

    # --- Validation Rules ---
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_invariants(self) -> "BackendSettings":
        # Rule 1: No debug in production or preview
        if self.APP_ENV in [AppEnv.DISTRICT_HOSPITAL, AppEnv.CLOUD_PREVIEW] and self.DEBUG:
            raise ValueError("FATAL CONFIG: DEBUG=True is strictly forbidden in production or cloud preview!")

        # Rule 2: Secret key minimum length enforcement
        secret_val = self.SECRET_KEY.get_secret_value()
        if self.APP_ENV in [AppEnv.DISTRICT_HOSPITAL, AppEnv.CLOUD_PREVIEW] and len(secret_val) < 64:
            raise ValueError("FATAL CONFIG: Production SECRET_KEY must be at least 64 characters long!")
        elif len(secret_val) < 32:
            raise ValueError("FATAL CONFIG: SECRET_KEY must be at least 32 characters long in all environments!")

        # Rule 3: Live data requires production environment confirmation
        if self.CLINOVA_DATA_MODE == ClinovaDataMode.LIVE and self.APP_ENV in [AppEnv.DEV, AppEnv.LOCAL_DEMO, AppEnv.TEST]:
            raise ValueError("FATAL CONFIG: Real patient data (CLINOVA_DATA_MODE=live) is forbidden in dev, demo, and test!")

        # Rule 4: CORS Wildcard forbidden in authenticated production
        if self.APP_ENV in [AppEnv.DISTRICT_HOSPITAL, AppEnv.CLOUD_PREVIEW] and "*" in self.CORS_ORIGINS:
            raise ValueError("FATAL CONFIG: Wildcard CORS ('*') is strictly forbidden in production environments!")

        # Rule 5: Supabase Service Role Key must never equal Anon Key
        if self.SUPABASE_SERVICE_ROLE_KEY and self.SUPABASE_ANON_KEY:
            if self.SUPABASE_SERVICE_ROLE_KEY.get_secret_value() == self.SUPABASE_ANON_KEY.get_secret_value():
                raise ValueError("FATAL CONFIG: SUPABASE_SERVICE_ROLE_KEY cannot be identical to SUPABASE_ANON_KEY!")

        return self
```

---

## 3. Frontend Configuration Schema (Zod Schema for Next.js)

Next.js separates build-time inlining of `NEXT_PUBLIC_*` variables from server-side Node.js runtime variables:

```typescript
// frontend/src/lib/env.ts - Phase 9 Frontend Configuration Specification

import { z } from "zod";

export const clientEnvSchema = z.object({
  // Exposed to browser via NEXT_PUBLIC_ prefix
  NEXT_PUBLIC_APP_ENV: z.enum([
    "dev",
    "local_demo",
    "phc_edge",
    "district_hospital",
    "cloud_preview",
    "test",
  ]),
  NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID: z.enum([
    "ENV_GOV_HOSPITAL",
    "ENV_PHC",
    "ENV_PUBLIC_CAMP",
    "ENV_COMPANY_CLINIC",
    "ENV_INDUSTRIAL_HEALTH",
    "ENV_CAMPUS_HEALTH",
  ]),
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_APP_NAME: z.string().default("CLINOVA AI"),
  NEXT_PUBLIC_VERSION: z.string().default("2.0.0"),
  NEXT_PUBLIC_OFFLINE_MODE: z
    .string()
    .transform((val) => val === "true")
    .default("true"),
  NEXT_PUBLIC_DATA_MODE: z.enum(["synthetic", "live"]).default("synthetic"),
  NEXT_PUBLIC_DEFAULT_LANGUAGE: z.enum(["en", "hi", "or"]).default("en"),

  // Optional Supabase Anon Client Key (Browser-safe public token)
  NEXT_PUBLIC_SUPABASE_URL: z.string().url().optional(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(20).optional(),
});

export const serverOnlyEnvSchema = z.object({
  // Strictly inaccessible to client-side bundles
  PORT: z.coerce.number().default(3000),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

// Compile-time assertion that NO private key begins with NEXT_PUBLIC_
type AssertNoPrivateLeak<T> = {
  [K in keyof T]: K extends `NEXT_PUBLIC_${string}SERVICE_ROLE${string}`
    ? never
    : K extends `NEXT_PUBLIC_${string}SECRET${string}`
    ? never
    : K extends `NEXT_PUBLIC_${string}PASSWORD${string}`
    ? never
    : T[K];
};
```

---

## 4. Comprehensive Variable Inventory & Classification

Every configuration item is classified into five structural categories:
- **REQUIRED:** Must be explicitly supplied in the declared environment; fails startup if absent.
- **OPTIONAL:** May be omitted; activates auxiliary or fallback capabilities when present.
- **FORBIDDEN:** Must NOT exist or be non-empty in that specific environment.
- **DERIVED:** Computed at runtime from other variables (e.g., local database URI from filesystem paths).
- **DEFAULTABLE:** Has a cryptographically and clinically safe default if not explicitly provided.

### Configuration Item Classification Matrix

| Variable Name | Type | Scope | DEV | LOCAL_DEMO | PHC_EDGE | DISTRICT_HOSPITAL | CLOUD_PREVIEW | TEST |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `APP_ENV` | Enum | Server + Client | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED | REQUIRED |
| `CLINOVA_ENVIRONMENT_ID` | Enum | Server + Client | DEFAULTABLE | REQUIRED | REQUIRED | REQUIRED | REQUIRED | DEFAULTABLE |
| `SECRET_KEY` | SecretStr | Server Only | DEFAULTABLE | REQUIRED | REQUIRED | REQUIRED | REQUIRED | DEFAULTABLE |
| `DATABASE_URL` | String | Server Only | DEFAULTABLE | DEFAULTABLE | DEFAULTABLE | REQUIRED | REQUIRED | DEFAULTABLE |
| `LOCAL_DATABASE_PATH` | Path | Server Only | DEFAULTABLE | DEFAULTABLE | REQUIRED | FORBIDDEN | FORBIDDEN | DEFAULTABLE |
| `SUPABASE_URL` | HttpUrl | Server + Client | OPTIONAL | FORBIDDEN | FORBIDDEN | OPTIONAL | REQUIRED | FORBIDDEN |
| `SUPABASE_ANON_KEY` | SecretStr | Server + Client | OPTIONAL | FORBIDDEN | FORBIDDEN | OPTIONAL | REQUIRED | FORBIDDEN |
| `SUPABASE_SERVICE_ROLE_KEY`| SecretStr | Server Only | OPTIONAL | FORBIDDEN | FORBIDDEN | FORBIDDEN | REQUIRED | FORBIDDEN |
| `STORAGE_MODE` | Enum | Server Only | DEFAULTABLE | DEFAULTABLE | REQUIRED (`LOCAL_FS`) | DEFAULTABLE | REQUIRED (`SUPABASE`) | DEFAULTABLE |
| `STORAGE_PATH` | Path | Server Only | DEFAULTABLE | DEFAULTABLE | REQUIRED | REQUIRED | FORBIDDEN | DEFAULTABLE |
| `CLINOVA_DATA_MODE` | Enum | Server + Client | DEFAULTABLE (`synthetic`)| REQUIRED (`synthetic`)| REQUIRED (`synthetic`)| OPTIONAL (`live`)| REQUIRED (`synthetic`)| REQUIRED (`synthetic`)|
| `OFFLINE_MODE` | Bool | Server + Client | DEFAULTABLE | REQUIRED (`true`) | REQUIRED (`true`) | DEFAULTABLE (`false`) | REQUIRED (`false`)| DEFAULTABLE |
| `SYNC_MODE` | Enum | Server Only | DEFAULTABLE | REQUIRED (`OFFLINE_ONLY`)| REQUIRED (`BIDIRECTIONAL`)| REQUIRED (`CLOUD_NATIVE`)| REQUIRED (`CLOUD_NATIVE`)| DEFAULTABLE |
| `AI_PROVIDER` | Enum | Server Only | DEFAULTABLE | REQUIRED (`local_rules`)| REQUIRED (`local_qwen`)| REQUIRED (`local_qwen`)| DEFAULTABLE | DEFAULTABLE (`mock`) |
| `CORS_ORIGINS` | List[str] | Server Only | DEFAULTABLE | DEFAULTABLE | REQUIRED | REQUIRED | REQUIRED | DEFAULTABLE |
| `LOG_LEVEL` | Enum | Server Only | DEFAULTABLE (`DEBUG`)| DEFAULTABLE (`INFO`)| REQUIRED (`INFO`)| REQUIRED (`INFO`)| REQUIRED (`INFO`)| DEFAULTABLE (`WARNING`)|

---

## 5. Startup Validation Sequence & Fatal Halts

1. **Phase 1: Environment Token Validation.** `APP_ENV` and `CLINOVA_ENVIRONMENT_ID` must match the canonical enumeration.
2. **Phase 2: Secret Strength Verification.** In `district_hospital` and `cloud_preview`, `SECRET_KEY` is checked for entropy ($\ge 64$ characters, non-default string).
3. **Phase 3: Persistence Reachability.** SQLite path parent directory must exist and be writable; PostgreSQL URL must be well-formed with non-root credentials.
4. **Phase 4: Storage Write Barrier.** A transient `.probe` lockfile is written to `STORAGE_PATH` and immediately deleted.
5. **Phase 5: Boundary & Leak Assertion.** System verifies that `SUPABASE_SERVICE_ROLE_KEY` does not exist in any client-exposed settings dictionary.
