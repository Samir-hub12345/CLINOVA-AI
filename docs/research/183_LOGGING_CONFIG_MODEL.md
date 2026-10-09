# CLINOVA AI — Logging Configuration, Observability & Zero-PHI Audit Model

> **Document ID:** `RES-183`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Observability Engineering, Privacy Compliance & Forensic Systems Group  

---

## 1. Architectural Distinction: Operational Logs vs. Clinical Audit Trail

A critical design requirement in healthcare informatics is maintaining an absolute separation between **Technical Operational Logs** and the **Forensic Clinical Audit Ledger**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 OPERATIONAL LOGS vs. FORENSIC AUDIT LEDGER                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STREAM 1: TECHNICAL OPERATIONAL LOGS ]                                   │
│  ├── Destination: Stdout / Rotating File / Syslog (Prometheus / ELK).       │
│  ├── Purpose: Server health, latency, HTTP status codes, error traces.      │
│  └── PRIVACY LAW: ZERO PROTECTED HEALTH INFORMATION (PHI) PERMITTED!        │
│                                                                             │
│  [ STREAM 2: FORENSIC CLINICAL AUDIT LEDGER ]                               │
│  ├── Destination: Dedicated PostgreSQL/SQLite table (`audit_events`).       │
│  ├── Purpose: Legal admissibility under Section 63 BSA 2023.                │
│  └── SECURITY LAW: IMMUTABLE APPEND-ONLY CRYPTOGRAPHIC MERKLE HASH CHAIN.  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Inviolable Zero-PHI Logging Invariant

**The Observability Privacy Law:**
$$\mathbf{Operational\ Logs} \cap \mathbf{Patient\ Identifiers\ (PHI)} = \emptyset$$

Under no circumstances may patient names, phone numbers, Aadhaar numbers, ABHA IDs, raw clinical symptoms, or unmasked medical history be written to standard operational logs, debug traces, or error monitors.

### Automated Redaction Filter
Any payload serialized to operational logs passes through an automated sanitization filter applying regular expression masks:
- **Aadhaar Mask:** `\b\d{4}\s?\d{4}\s?\d{4}\b` $\to$ `[AADHAAR_REDACTED]`
- **ABHA ID Mask:** `\b\d{2}-\d{4}-\d{4}-\d{4}\b` $\to$ `[ABHA_REDACTED]`
- **Phone Mask:** `\b(?:\+91|0)?[6-9]\d{9}\b` $\to$ `[PHONE_REDACTED]`
- **Secret Key Mask:** Any key named `*KEY*`, `*SECRET*`, `*TOKEN*`, `*PASS*` $\to$ `[SECRET_MASKED]`

---

## 3. Logging Configuration Schema

```python
# Observability Settings Model
class LoggingSettings(BaseModel):
    LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    LOG_DESTINATION: str = Field(
        default="CONSOLE_JSON",
        description="Sink type: CONSOLE_JSON, FILE_ROTATING_JSON, or REMOTE_SYSLOG_JSON",
    )
    LOG_FILE_PATH: Optional[Path] = Field(
        default=Path("/var/log/clinova/app.log"),
        description="Path for rotating log files on physical servers",
    )
    LOG_ROTATION_MAX_BYTES: int = Field(
        default=50 * 1024 * 1024,  # 50 MB
        description="Max log file size before rotation",
    )
    LOG_ROTATION_BACKUP_COUNT: int = Field(
        default=10,
        description="Number of retained historical rotated log files",
    )
    AUDIT_MODE: bool = Field(
        default=True,
        description="Enforces Section 63 BSA cryptographic Merkle audit chaining",
    )
    PHI_LOGGING_POLICY: str = Field(
        default="STRICT_REDACTION",
        description="Redaction engine setting. Must be STRICT_REDACTION in all modes.",
    )
    STRUCTURED_LOG_FORMAT: str = Field(
        default="JSON",
        description="Forces JSON serialization for high-performance machine ingestion",
    )
```

---

## 4. Structured Operational Log Format

All operational logs emitted by FastAPI are serialized as single-line JSON objects containing tracing metadata:

```json
{
  "timestamp": "2026-10-08T11:45:00.123Z",
  "level": "INFO",
  "request_id": "req-987a-42bc-9102",
  "environment": "phc_edge",
  "facility_id": "ENV_PHC",
  "actor_role": "CLINICIAN",
  "actor_id": "user-uuid-4412",
  "endpoint": "/api/v1/cases/case-uuid-8812/vitals",
  "method": "POST",
  "status_code": 200,
  "duration_ms": 14.2,
  "memory_rss_mb": 218.4,
  "message": "Vitals recorded and NEWS2 score evaluated successfully"
}
```

Notice that the exact blood pressure reading (`140/90`) and patient demographic data are **omitted from the operational log**; they reside solely within the encrypted database and the cryptographic `audit_events` ledger.
