# CLINOVA AI — Secret Classification & Cryptographic Credential Taxonomy

> **Document ID:** `RES-166`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Information Security, Cryptography & Privacy Engineering Group  

---

## 1. Secret Classification Framework

In healthcare architectures processing sensitive patient data under the **Digital Personal Data Protection (DPDP) Act, 2023** and **Bharatiya Sakshya Adhiniyam, 2023**, credential compromise can result in total breach of medical confidentiality, legal inadmissibility of forensic records, or arbitrary clinical data tampering.

CLINOVA AI categorizes every configuration parameter and credential into six mutually exclusive security classes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA SIX-TIER CREDENTIAL TAXONOMY                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CLASS 1: PUBLIC_RUNTIME_CONFIG ]                                         │
│  └── Browser-readable, bundled in client JS, zero confidentiality.          │
│                                                                             │
│  [ CLASS 2: SERVER_ONLY_SECRET ]                                            │
│  └── Backend runtime secret; NEVER leaves server memory or loopback.        │
│                                                                             │
│  [ CLASS 3: LOCAL_ONLY_SECRET ]                                             │
│  └── Node-specific secret (edge Mini-PC disk encryption, local IPC token).  │
│                                                                             │
│  [ CLASS 4: DEPLOYMENT_SECRET ]                                             │
│  └── CI/CD pipeline, container registry, or infrastructure provisioning.    │
│                                                                             │
│  [ CLASS 5: OPTIONAL_PROVIDER_CONFIG ]                                      │
│  └── Secondary upstream cloud endpoints or developer tokens (unpaid/free).   │
│                                                                             │
│  [ CLASS 6: NON_SECRET_CONFIGURATION ]                                      │
│  └── Operational tunables, timeouts, port numbers, log levels, flags.       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Inventory of Variables by Security Class

### Class 1: `PUBLIC_RUNTIME_CONFIG` (Browser-Safe)
These values are built into or served to the client browser. They carry **Zero Confidentiality** and cannot be used to bypass backend authorization.
- `NEXT_PUBLIC_APP_ENV`: Deployment environment badge (`dev`, `phc_edge`, etc.).
- `NEXT_PUBLIC_CLINOVA_ENVIRONMENT_ID`: Active operational facility profile (`ENV_PHC`, etc.).
- `NEXT_PUBLIC_API_URL`: Fully qualified backend HTTP endpoint for AJAX/REST calls.
- `NEXT_PUBLIC_APP_NAME`: Human-readable application branding.
- `NEXT_PUBLIC_VERSION`: Application release version.
- `NEXT_PUBLIC_DATA_MODE`: Banner toggle indicator (`synthetic` or `live`).
- `NEXT_PUBLIC_SUPABASE_URL`: Public Supabase API gateway URL (when Supabase is enabled).
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Public anonymous JWT token scoped exclusively to public Row Level Security (RLS) tables.

### Class 2: `SERVER_ONLY_SECRET` (Strictly Backend Memory)
These values MUST NEVER be exposed to the browser, client bundle, or logged to disk:
- `SECRET_KEY`: Cryptographic symmetric key used for HMAC-SHA256 signing of clinical session JWTs and state anti-tamper tokens.
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase administrative master key that completely bypasses Row Level Security. **Strictly forbidden on client, frontline edge tablets, and local demo environments.**
- `DATABASE_URL`: Connection string containing Postgres/Supabase database user credentials and passwords.
- `MASTER_ENCRYPTION_KEY`: AES-256-GCM symmetric key used to encrypt sensitive patient identifiers at rest on edge nodes.
- `EDGE_SYNC_HMAC_SECRET`: Shared secret used to authenticate edge sync journal push/pull batches to the district hub.

### Class 3: `LOCAL_ONLY_SECRET` (Hardware Node Bound)
These secrets exist solely on a physical on-premise hardware node and are never replicated across the network:
- `LOCAL_SQLITE_ENCRYPTION_KEY`: Hardware-tied key (via TPM 2.0 or local OS keystore) encrypting the edge SQLite database on rural Mini-PCs.
- `LOCAL_ADMIN_BOOTSTRAP_HASH`: PBKDF2/Argon2id password hash for emergency local offline administrator login when the central directory is unreachable.
- `LOCAL_LAN_TLS_KEY`: Private key for the local clinic server's self-signed or private PKI TLS certificate for HTTPS over rural clinic Wi-Fi.

### Class 4: `DEPLOYMENT_SECRET` (Build & Infrastructure Only)
Secrets restricted to GitHub Actions, automated build runners, or cloud provisioning engines:
- `GITHUB_TOKEN` / `REGISTRY_AUTH_TOKEN`: Container image pull/push credentials.
- `SUPABASE_ACCESS_TOKEN`: Management API token for provisioning remote Supabase cloud projects.
- `SSH_DEPLOY_KEY`: Automated server deployment key.

### Class 5: `OPTIONAL_PROVIDER_CONFIG` (Pluggable AI & Auxiliary)
Optional upstream keys for external evaluation or benchmark testing. None of these are mandatory for core clinical safety or triage:
- `GEMINI_API_KEY`: Google Gemini API key (optional cloud multimodal benchmark).
- `GROQ_API_KEY`: Groq LPU inference key (optional ultra-fast cloud LLM fallback).
- `SARVAM_API_KEY`: Sarvam AI speech key (optional Indic vernacular benchmark).
- `OCR_SPACE_API_KEY`: Free-tier cloud OCR fallback key.

### Class 6: `NON_SECRET_CONFIGURATION` (Tunable Parameters)
Plain operational variables carrying no authentication or encryption payload:
- `BACKEND_HOST`, `BACKEND_PORT`, `FRONTEND_PORT`
- `CORS_ORIGINS`
- `STORAGE_MODE`, `STORAGE_PATH`, `STORAGE_TEMP_PATH`
- `MAX_UPLOAD_SIZE_BYTES`, `MEDIA_RETENTION_POLICY_DAYS`
- `OFFLINE_MODE`, `SYNC_MODE`, `SYNC_BATCH_SIZE`
- `LOG_LEVEL`, `LOG_DESTINATION`, `AUDIT_MODE`
- All `FEATURE_*` flags

---

## 3. Strict Boundary Rules: Forbidden Exposures

Under no circumstances may any of the following seven credentials be present in browser bundles or accessible via frontend code:

| Forbidden Secret | Catastrophic Risk if Exposed | Enforcement Mechanism |
| :--- | :--- | :--- |
| `SUPABASE_SERVICE_ROLE_KEY` | Attacker bypasses all RLS and can read, alter, or drop all hospital clinical records. | Automated build lint check; forbidden prefix check; runtime bundle inspection. |
| `DATABASE_URL` (with password) | Attacker executes arbitrary SQL directly against database port. | Never referenced outside `backend/app/core/`. |
| `SECRET_KEY` (JWT secret) | Attacker forges arbitrary Doctor/Admin clinical session tokens. | Pydantic `SecretStr` masking; runtime environment isolation. |
| `MASTER_ENCRYPTION_KEY` | Attacker decrypts offline backups and local media stores. | Retained exclusively in kernel memory or OS vault. |
| `EDGE_SYNC_HMAC_SECRET` | Attacker injects fraudulent sync journals into district hub. | Never dispatched to frontline tablets. |
| `LOCAL_LAN_TLS_KEY` | Attacker performs Man-in-the-Middle decryption on clinic LAN. | Stored with `chmod 600` root permissions on edge server. |
| Administrative API Keys | Attacker can manipulate cloud tenant configurations or billing. | Excluded from application deployment images. |

---

## 4. Secret Lifecycle, Rotation & Emergency Revocation

While Phase 9 does not implement automated rotation scripts, it specifies the mandatory operational procedures:

### 4.1 Rotation Ownership & Responsibilities
- **District Hospital / Cloud:** Hospital Chief Information Security Officer (CISO) and System Administrator own `SECRET_KEY` and database credentials. Rotated quarterly.
- **PHC Edge Node:** District Technical Officer owns hardware provisioning and local node secrets. Rotated bi-annually during facility audit.
- **Development / Demo:** Individual engineers maintain ephemeral local secrets. Zero real secrets are ever issued to dev/demo.

### 4.2 Standard Rotation Procedure (Zero-Downtime Session Key Migration)
1. **Dual-Key Staging:** The backend accepts an array of valid verification keys `[SECRET_KEY_ACTIVE, SECRET_KEY_PREVIOUS]`.
2. **Issue New:** New logins receive tokens signed with `SECRET_KEY_ACTIVE`.
3. **Verify Existing:** Active sessions signed with `SECRET_KEY_PREVIOUS` continue to validate until token expiry (60 minutes).
4. **Retire Old:** After 60 minutes, `SECRET_KEY_PREVIOUS` is purged from configuration.

### 4.3 Emergency Revocation Protocol (Leaked Secret Response)
Upon detection of credential leakage (e.g., secret detected in git commit or client HTTP trace):
1. **Step 1 (Immediate Invalidation):** Regenerate `SECRET_KEY` immediately. All active sessions across all devices are terminated instantaneously (`HTTP 401 Unauthorized`).
2. **Step 2 (Database Credential Roll):** If database passwords or `SUPABASE_SERVICE_ROLE_KEY` leaked, regenerate database credentials in PostgreSQL/Supabase dashboard and execute rolling restart of backend containers.
3. **Step 3 (Audit Review):** Query immutable Merkle audit log (`audit_events`) for all operations signed during the potential exposure window to identify unauthorized record mutations.
4. **Step 4 (Section 63 BSA Re-Certification):** Flag all records modified during the incident window for manual RMP verification.

### 4.4 Offline Edge Credential Rotation
For rural PHCs without continuous internet connectivity:
- District Technical Officers carry an encrypted USB security dongle containing signed rotation manifests.
- The local clinic server verifies the digital signature of the manifest using the District Public Key before applying new local database or TLS keys.
