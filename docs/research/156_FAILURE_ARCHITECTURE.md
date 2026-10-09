# CLINOVA AI — System Failure & Graceful Degradation Architecture

> **Document ID:** `RES-156`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Safety, Reliability Engineering & Clinical Risk Management Group  

---

## 1. The Safe Failure Philosophy: Never Fake Success

In consumer applications, modern software often employs "optimistic UI updates" or silent fallbacks to create an illusion of seamlessness.

**In Clinical Systems, Faking Success Kills Patients:**
- If an OCR model fails to extract a patient's low platelet count from a lab slip, the system must NEVER quietly display a blank or assume normal values.
- If a facility capability check fails due to stale network telemetry, the system must NEVER blindly route an ambulance assuming the ICU bed exists.
- **The Safe Failure Law:** When a subsystem fails, CLINOVA AI **degrades safely, exposes the exact failure boundary to clinicians, and provides explicit human manual procedures**.

---

## 2. Standardized Failure Lifecycle Architecture

Every failure across any subsystem follows an immutable six-phase containment lifecycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CANONICAL FAILURE LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DETECTION                                                               │
│     • Timeout boundary, exception trap, health probe, or validation error   │
│                                  │                                          │
│                                  ▼                                          │
│  2. FAIL-SAFE BEHAVIOR                                                      │
│     • Non-destructive fallback activated; transaction rolled back or bounded│
│                                  │                                          │
│                                  ▼                                          │
│  3. USER MESSAGE                                                            │
│     • Clear, unvarnished clinical banner; zero opaque technical error codes │
│                                  │                                          │
│                                  ▼                                          │
│  4. HUMAN FALLBACK                                                          │
│     • Physical bedside exam, manual data entry, or direct telephone call    │
│                                  │                                          │
│                                  ▼                                          │
│  5. RECOVERY                                                                │
│     • Idempotent state re-synchronization or background retry               │
│                                  │                                          │
│                                  ▼                                          │
│  6. AUDIT LOGGING                                                           │
│     • Failure event, trigger, duration, and human action logged in ledger   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Eleven-Scenario Failure Matrix

| # | Failure Scenario | Detection Mechanism | Fail-Safe Behavior | Frontline Clinical User Message | Human Fallback Procedure | Recovery & Audit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Network Outage (WAN / Cloud Down)** | Health probe ping timeout to Central Hub ($> 30\text{s}$) | Edge node switches seamlessly to `OFFLINE_AUTONOMOUS` mode | Amber banner: *"Operating in Offline Local Mode. Records saved to local clinic server."* | Complete care as normal on local clinic Wi-Fi LAN | Auto-pushes pending sync journals upon WAN restoration |
| **2** | **Local Clinic Server Outage** | Tablet client receives HTTP Connection Refused | Tablets display offline contingency screen | Red banner: *"Local Clinic Server Unreachable. Switch to Emergency Paper Triage."* | Use physical paper triage slips; register retroactively | Server restarts via systemd watchdog; logs boot audit |
| **3** | **Database Unavailable / Locked** | SQLite `SQLITE_BUSY` ($> 5\text{s}$) or PG connection pool drop | Transaction rolls back immediately; returns HTTP 503 | Yellow alert: *"Database is temporarily busy. Retrying in 2 seconds..."* | Staff pauses 5 seconds; retry button displayed | Pool re-establishes connection; logs retry count |
| **4** | **Object Storage Unavailable** | Local disk write error or S3 connection timeout | Media metadata created with status `STORAGE_UNAVAILABLE` | Warning: *"File upload deferred. Physical document must be kept at bedside."* | Nurse inspects paper prescription slip directly | Background worker retries disk flush; logs disk alert |
| **5** | **AI SLM Runtime Unavailable** | Loopback socket timeout to Ollama/Qwen3 ($> 3000\text{ms}$) | Invokes `DeterministicFallbackExtractor` (Regex & dictionary matching) | Info badge: *"Structured via Clinical Heuristic Engine (AI offline)."* | Doctor verifies extracted symptom tags manually | Watchdog restarts local SLM container; logs AI drop |
| **6** | **OCR Engine Unavailable / Crashed** | Subprocess exit code $\neq 0$ or memory limit hit | Document scan stored with status `OCR_EXTRACTION_FAILED` | Notice: *"Automated scan reading unavailable. View physical image below."* | Doctor views high-res slip image directly on Workbench | Resets worker process; flags document for manual entry |
| **7** | **ASR Speech Model Unavailable** | Audio processing timeout ($> 8000\text{ms}$) or VAD error | Audio file saved with status `TRANSCRIPTION_FAILED` | Notice: *"Voice transcript unavailable. Audio recording is ready for playback."* | Doctor clicks play to listen to 30-second patient audio | Resets audio worker; logs audio duration and format |
| **8** | **Offline Synchronization Conflict** | Duplicate sequence or conflicting clinical edit upon reconnect | Non-destructive `APPEND_ONLY` or `SAFETY_PESSIMISTIC` resolution | Amber badge: *"Conflicting data merged. Clinical review required."* | RMP reviews side-by-side values on Doctor Workbench | Reconciler merges journal; logs conflict resolution |
| **9** | **Stale Facility Data** | Last telemetry update $> 4\text{ hours}$ old | FACILITYGRAPH marks hospital capability `STALE` | Warning: *"Target hospital bed status STALE (Updated 5h ago). Phone verification required."* | Referral nurse dials target hospital casualty desk directly | Telemetry update refreshes status to `CURRENT` |
| **10**| **Bad Credentials / Expired JWT** | Token signature verification failure (HTTP 401) | Request rejected; client redirects to login screen | Prompt: *"Your session has expired. Please enter PIN to re-authenticate."* | Staff enters 4-digit PIN to refresh token in $< 5\text{s}$ | Emits security log; tracks repeated auth failures |
| **11**| **Permission Denied (RBAC Violation)** | User role lacks authority for clinical command (HTTP 403) | Command hard-blocked; zero database state change | Error: *"Action restricted to Registered Medical Practitioners under NMC Reg 27."* | Nurse requests doctor to sign off prescription order | Logs unauthorized attempt to `audit_logs` |
