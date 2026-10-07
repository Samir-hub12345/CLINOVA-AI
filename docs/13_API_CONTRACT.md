# CLINOVA AI — API Contract Specification

> **Document ID:** `DOC-13`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Global API Standards

- **Base URL:** `/api/v1`
- **Protocol:** HTTP/1.1 and HTTP/2 over TLS 1.3
- **Data Format:** `application/json` (UTF-8 encoded)
- **Mandatory Response Headers:**
  - `X-Clinical-Safety: Non-Diagnostic-Advisory-Only`
  - `X-Human-In-The-Loop: Required-Before-Action`
  - `X-Content-Type-Options: nosniff`
- **Standard Error Envelope:**
  ```json
  {
    "error": {
      "code": "VALIDATION_FAILED",
      "message": "Clinical vital sign out of physiological bounds.",
      "details": [{"field": "systolic_bp", "issue": "Value 450 exceeds maximum plausible physiological range (300 mmHg)"}],
      "timestamp": "2026-10-07T16:45:00Z"
    }
  }
  ```

---

## 2. Core Endpoints Summary

### 2.1 System & Clinical Safety
| Method | Path | Purpose | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root system identity and clinical safety disclaimer. | No |
| `GET` | `/health` | Container orchestrator liveness and readiness probe. | No |
| `GET` | `/api/v1/status` | Operational status of all four innovation pillars. | No |
| `GET` | `/api/v1/safety` | Clinical non-diagnostic governance policies. | No |

### 2.2 Multimodal Intake (`/api/v1/intake`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/intake/consent` | `{case_id, patient_ref, language, consent_granted}` | `{consent_id, recorded_at, status}` | Captures patient informed consent. |
| `POST` | `/api/v1/intake/text` | `{patient_ref, narrative_text, language}` | `{case_id, parsed_symptoms, draft_acuity}` | Ingests narrative clinical text. |
| `POST` | `/api/v1/intake/voice` | `multipart/form-data (audio file + metadata)` | `{transcript, confidence, extracted_symptoms}` | Transcribes speech and parses entities. |
| `POST` | `/api/v1/intake/ocr` | `multipart/form-data (image/pdf + metadata)` | `{extracted_text, structured_vitals, confidence}` | Extracts text/tables from clinical reports. |
| `POST` | `/api/v1/intake/translate` | `{text, source_lang, target_lang}` | `{translated_text, target_lang}` | Translates between regional languages. |

### 2.3 Case Queue & CareGraph (`/api/v1/caregraph` & `/api/v1/cases`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/cases/queue` | `?department=ED&status=ACTIVE` | `{queue: [CaseSummary], total_count}` | Prioritized patient list sorted by risk & SLA. |
| `GET` | `/api/v1/caregraph/{case_id}` | None | `{nodes, edges, trajectory, uncertainty}` | Returns full patient CareGraph snapshot. |
| `POST` | `/api/v1/caregraph/{case_id}/vitals`| `{heart_rate, bp_sys, bp_dia, spo2, rr, temp}` | `{updated_risk_score, trajectory_slope, alerts}` | Appends new vital signs; recalculates $\Delta R$. |
| `GET` | `/api/v1/caregraph/{case_id}/missing`| None | `{missing_parameters, uncertainty_score}` | Returns protocol gaps and uncertainty. |
| `POST` | `/api/v1/caregraph/{case_id}/questions`| None | `{recommended_questions: [Question]}` | Generates targeted follow-up questions. |
| `POST` | `/api/v1/caregraph/{case_id}/verify`| `{node_id, verification_status, clinician_note}`| `{updated_node, new_uncertainty}` | Promotes node to clinician-verified status. |

### 2.4 FacilityGraph & Care Feasibility (`/api/v1/facilities`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/facilities` | `?tier=ALL` | `{facilities: [FacilityProfile]}` | Lists network facilities and baseline capacities. |
| `GET` | `/api/v1/facilities/{id}` | None | `{facility: FacilityProfile, real_time_status}` | Detailed capability, bed, and equipment status. |
| `POST` | `/api/v1/facilities/match` | `{facility_id, required_bundle}` | `{status: FEASIBLE/DEGRADED/INFEASIBLE, reason}` | Checks if required care can be delivered here. |
| `POST` | `/api/v1/facilities/referral-rank`| `{current_facility_id, required_bundle}` | `{ranked_destinations: [ReferralOption]}` | Ranks capable destination facilities. |
| `POST` | `/api/v1/referrals/sbar` | `{case_id, destination_facility_id}` | `{sbar_packet: SBARReport}` | Generates standardized SBAR transfer packet. |

### 2.5 SignalGraph & Operational Telemetry (`/api/v1/signalgraph`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/signalgraph/surges` | `?window_hours=48` | `{clusters: [SyndromicCluster], alert_level}`| Returns regional outbreak clusters. |
| `GET` | `/api/v1/signalgraph/load` | None | `{facility_pressures: [FacilityLoadMetric]}`| Department backlogs and wait times. |
| `GET` | `/api/v1/signalgraph/summary`| None | `{active_cases, avg_wait_min, bed_occupancy_pct}`| Macro system health indicators. |

### 2.6 Orchestration Engine & Clinician Decision (`/api/v1/orchestration`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/orchestration/evaluate` | `{case_id, facility_id}` | `{recommended_action, rationale, secondary_pathway}` | Derives safest achievable care action. |
| `POST` | `/api/v1/orchestration/decision` | `{case_id, action, decision_type, override_reason}` | `{decision_id, timestamp, status: AUTHORIZED}` | Clinician sign-off or structured override. |
| `POST` | `/api/v1/cases/{case_id}/outcome` | `{disposition, final_condition, notes}` | `{case_status: OUTCOME, completed_at}` | Records patient outcome; closes encounter. |

### 2.7 Medicolegal Audit (`/api/v1/audit`)
| Method | Path | Request Body | Response Payload | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/audit/logs` | `?case_id={id}&limit=50` | `{logs: [AuditEntry]}` | Returns tamper-evident audit history. |

---

## 3. External Service Contract Matrix (Mandated by Section 14)

Before selecting or binding any external provider, the Master Contract mandates full documentation across the 9 potential service categories:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL PROVIDER RESILIENCE HIERARCHY                   │
│                                                                             │
│   Incoming Request ──> External Cloud API (If Key Present & Healthy)        │
│                               │                                             │
│                               ▼ (Timeout / HTTP Error / Key Empty)          │
│                        Deterministic Local Fallback Engine                  │
│                               │                                             │
│                               ▼                                             │
│                        Unbroken Clinical Triage Workflow                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Service Category | Purpose | Candidate Provider | API / Protocol | Env Variable | Input Schema | Output Schema | Cost / Tier | Failure Behavior | Timeout | Fallback Behavior | Security Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Authentication** | Clinician & worker session authentication & RBAC tokens | Local Auth / OAuth2 (Keycloak / Supabase) | JWT (HS256 / RS256) | `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` | `{username, password, role}` | `{access_token, token_type, expires_in}` | Zero cost (Local self-hosted) | Reject invalid credentials with 401; log failure | 5s | Local dev mode provides fast role-switcher personas | Passwords hashed with Bcrypt/Argon2; tokens signed with 256-bit secret; TLS transmission only |
| **2. LLM (Reasoning)** | Clinical entity extraction, SOAP synthesis, Q&A prompts | Google Gemini (2.5 Flash / 1.5 Flash) / Groq Llama 3 | REST / `google-genai` SDK | `GEMINI_API_KEY`, `GROQ_API_KEY`, `AI_PROVIDER` | Structured clinical narrative & vitals JSON | JSON schema with extracted entities & candidate questions | Free tier ($0) / Paid ($0.30/1M in, $2.50/1M out) | Catch error; flag `AI_INFERRED` unavailable; log medicolegal audit | 8s | Deterministic clinical rule tree + NEWS2 score calculation | Never send unscrubbed PII/names; strip identifiers before transmission; non-diagnostic disclaimer |
| **3. Speech-to-Text (STT)** | Voice symptom intake in regional Indian languages | Web Speech API (Client) / Sarvam AI / Whisper | Web Speech API / REST multipart | `SARVAM_API_KEY` (Optional) | Raw audio stream (WAV, WEBM) + language code | `{transcript, confidence, language_detected}` | Free (Browser) / Sarvam ₹0.50/min | Browser `onerror` event; API non-200 catch | 10s | Graceful fallback to structured narrative text input UI | Ephemeral memory buffer; never persist raw biometric audio without consent |
| **4. Translation** | Multilingual intake across Hindi, Odia, Bengali | AI4Bharat IndicTrans2 / Gemini / Static Lexicon | REST POST / In-memory dictionary | `AI_PROVIDER` | `{text, source_lang, target_lang}` | `{translated_text, target_lang}` | Zero cost (local lexicon) | Revert to source text verbatim; display untranslated badge | 5s | Pre-translated clinical lexicon of common symptoms/emergencies | Safe string escaping; preserve clinical acuity terms without loss of meaning |
| **5. OCR** | Medical lab slip and prescription entity extraction | Tesseract OCR / OCR Space / Gemini Vision | CLI binary / REST multipart | `OCR_SPACE_API_KEY` | Image / PDF binary bytes (`image/jpeg`, `application/pdf`) | `{extracted_text, tabular_kv, confidence}` | Free local / Free tier (25k req/mo) | Return `OCR_FAILED` state; retain raw file | 15s | Prompt triage nurse for manual structured key-value entry | File magic-byte validation (`%PDF`, `\x89PNG`); size capped at 10MB; zero executable execution |
| **6. Maps / Geolocation** | Inter-facility road transit time and referral routing | OpenStreetMap OSRM / Haversine Geo | REST GET / Native Python math | `OSRM_BASE_URL` (Optional) | `(lat1, lon1), (lat2, lon2)` | `{transit_minutes, distance_km}` | Zero cost (OSRM / Haversine) | Fallback to Euclidean/Haversine distance calculation | 3s | Deterministic road distance matrix for regional facility network | Only facility geolocations processed; zero patient residence coordinates transmitted |
| **7. File / Object Storage** | Secure storage for uploaded report scans and audio notes | Local Encrypted Vault / S3-compatible (MinIO) | POSIX filesystem / S3 API | `STORAGE_VAULT_PATH`, `S3_BUCKET_NAME` | Binary payload + metadata | `{vault_uri, file_hash_sha256}` | Zero cost (local disk) | Return 507 Insufficient Storage; notify intake staff | 5s | Ephemeral base64 session cache with 1-hour expiration | Cryptographic SHA-256 integrity check; server-side encryption at rest; 24h retention cleanup |
| **8. Notifications / SMS** | Referral dispatch alerts and ambulance handoff notices | Console logger / Webhook / Twilio | REST Webhook | `ALERT_WEBHOOK_URL` (Optional) | `{facility_id, case_token, urgency, sbar_link}` | `{delivery_status, timestamp}` | Zero cost (dev log) / Variable | Log to stdout/audit table; flag notification pending | 4s | Visual in-app clinical queue banner with audible chime | Never send patient clinical notes in SMS; only send opaque token link to secure workstation |
| **9. Database** | Encounter persistence, audit trail, facility state | SQLite (Dev) / PostgreSQL 16 (Production) | Async SQLAlchemy (aiosqlite / asyncpg) | `DATABASE_URL` | SQLAlchemy ORM models | Query result sets / Record objects | Zero cost (Open Source) | Transaction rollback; raise 503 Database Unavailable | 5s | Read-only in-memory fallback cache for critical triage lookups | Connection pooling; parameterized queries (zero SQL injection); encrypted connection string |

