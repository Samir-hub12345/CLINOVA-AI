# CLINOVA AI — Backend Architecture Specification

> **Document ID:** `RES-137`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Backend Architecture, Systems Safety & Python Frameworks Engineering Group  

---

## 1. Backend Design Philosophy: The Modular Monolith

The CLINOVA AI backend is architected as an **Asynchronous Modular Monolith** utilizing FastAPI and Python 3.11+.

### 1.1 Rationale for Modular Monolith over Microservices
1. **Zero-Latency In-Process Communication:** Rural edge nodes (fanless Mini-PCs) have strictly bounded CPU and RAM resources. Running 15 microservices with container network overhead would cause memory thrashing and lock contention. A modular monolith executes across a single Python process pool.
2. **Transactional Database Integrity:** Complex medical workflows (such as admitting a patient, updating the Master Case state, logging an append-only event, and re-deriving the physiological trajectory) require ACID transaction boundaries across domain boundaries.
3. **Strict Domain Isolation:** While sharing a runtime process and database connection pool, domain modules maintain strict directory-level boundary isolation. Modules communicate via explicit Python service interfaces rather than direct raw SQL queries into other modules' internal tables.

---

## 2. Four-Tier Backend Architecture

The backend code is strictly organized across four vertical architectural layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BACKEND FOUR-TIER ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: API / PRESENTATION LAYER ]                                       │
│  ├── FastAPI APIRouters (`app/api/v1/endpoints/`)                           │
│  ├── Pydantic Request DTOs & Response DTOs                                 │
│  ├── Authentication & RBAC Dependencies (`get_current_user`, `require_role`)│
│  └── Response Serialization & Non-Diagnostic Header Middleware              │
│                                  │                                          │
│                                  │ Dispatches Commands & Queries            │
│                                  ▼                                          │
│  [ TIER 2: APPLICATION & SERVICE LAYER ]                                    │
│  ├── Command Handlers (Mutations, Workflows, Orchestration Coordination)    │
│  ├── Query Handlers (Read Projections, Doctor Queue Computations)           │
│  ├── Multi-Graph Synthesis Coordinators                                     │
│  └── Background Task Dispatchers (Asynchronous OCR/ASR Jobs)                │
│                                  │                                          │
│                                  │ Invokes Domain Rules & Adapters          │
│                                  ▼                                          │
│  [ TIER 3: DOMAIN LAYER (CLINICAL CORE) ]                                   │
│  ├── Domain Entities & Aggregate Roots (Case, Patient, EvidenceRecord)      │
│  ├── Deterministic Clinical Safety Services (NEWS2, Shock Index, Red Flags) │
│  ├── Epistemic State Machine & 27 Master Case States Engine                 │
│  ├── Provenance & Conflict Adjudication Logic                               │
│  └── Sufficiency & Zero-Imputation Mathematical Validators                  │
│                                  │                                          │
│                                  │ Calls Abstract Interfaces                │
│                                  ▼                                          │
│  [ TIER 4: INFRASTRUCTURE & ADAPTERS ]                                      │
│  ├── Relational Repositories (SQLAlchemy 2.0 Async Session)                 │
│  ├── Media Storage Adapters (Local Filesystem / Supabase Storage)           │
│  ├── AI & Model Adapters (Local SLM Qwen3, faster-whisper, PaddleOCR)       │
│  ├── Sync Journal Storage & Network Transport                               │
│  └── Cryptographic Audit Ledger (SHA-256 Merkle Chain Writer)               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CQRS & Operation Classification

To maintain high responsiveness and prevent read operations from being blocked by long-running transactions, the application layer distinguishes between **Commands** (mutations modifying state) and **Queries** (read-only projections):

| Operation Type | Architectural Role | Execution Characteristics | Example Services |
| :--- | :--- | :--- | :--- |
| **Command** | State mutation; creates events and updates entities | Executes inside an explicit `async with session.begin()` transaction; writes to `case_events` | `CreateCaseCommand`, `RecordVitalsCommand`, `ResolveConflictCommand`, `SignOffDecisionCommand` |
| **Query** | High-performance read projection | Read-only; bypasses complex business aggregates; evaluates dynamic projections at query time | `GetDoctorQueueQuery`, `GetCaseSummaryQuery`, `GetEvidenceLineageQuery`, `GetFacilityFreshnessQuery` |
| **Workflow** | Multi-step coordinator orchestrating several modules | Manages asynchronous transitions across external processes | `IntakeProcessingWorkflow` (Upload $\to$ OCR $\to$ Extraction $\to$ Verification) |
| **Safety Service** | Deterministic clinical evaluator | Pure function; zero I/O; 100% unit-testable without database or network | `NEWS2Evaluator`, `ShockIndexCalculator`, `RedFlagScanner`, `PediatricTriageRule` |
| **AI Adapter** | Statistical processing wrapper | Asynchronous external process call; strict timeout; non-fatal fallback | `SLMTextExtractor`, `WhisperTranscriber`, `PaddleOCRExtractor` |
| **Provenance Service** | Lineage and verification recorder | Manages spatial/acoustic pointers and RMP attestation records | `ProvenanceRecorder`, `ConflictDetector`, `DualReviewCoordinator` |
| **Audit Service** | Forensic compliance logger | Writes append-only cryptographically chained records complying with Section 63 BSA 2023 | `AuditLedgerWriter`, `MerkleTreeBuilder` |
| **Sync Service** | Offline delta synchronizer | Manages local journals and bi-directional push/pull replication | `SyncJournalReconciler`, `ConflictResolver` |

---

## 4. Deterministic Clinical Safety Layer: Complete LLM Decoupling

A foundational architectural requirement of CLINOVA AI is that **clinical safety logic must never depend on the LLM or any statistical AI model**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC SAFETY ENGINE BOUNDARY                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   INPUT: Standardized Clinical Observation Vector                           │
│   ├── Heart Rate (bpm): 128                                                 │
│   ├── Systolic BP (mmHg): 82                                                │
│   ├── Respiratory Rate (bpm): 28                                            │
│   ├── SpO2 (% on Room Air): 91                                              │
│   └── Consciousness: Voice (V)                                              │
│                                                                             │
│   DETERMINISTIC RULE EXECUTION (Zero AI Dependency / Pure Python):          │
│   ├── Shock Index = HR / SBP = 128 / 82 = 1.56 (Threshold > 0.9 => CRITICAL)│
│   ├── NEWS2 Calculation:                                                    │
│   │   • HR: 128 (+2)                                                        │
│   │   • SBP: 82 (+3)                                                        │
│   │   • RR: 28 (+3)                                                         │
│   │   • SpO2: 91 (+2)                                                       │
│   │   • AVPU: V (+3)                                                        │
│   │   └── TOTAL NEWS2 = 13 (Score >= 7 => RED FLAG EMERGENCY)               │
│   └── Red Flag Rule: Systolic BP < 90 + Altered Sensorium => Sepsis Alert   │
│                                                                             │
│   OUTPUT: Immutable Clinical Safety Assessment (Acuity: CRITICAL)           │
│   (Generated in < 2ms without invoking LLM, network, or external process)   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Safety Guarantees
1. **Crash Isolation:** If the local SLM runtime (Ollama/Qwen3) crashes or experiences an Out-Of-Memory (OOM) error, the deterministic safety engine continues to score vitals, trigger emergency red flags, and sort the doctor queue without interruption.
2. **Deterministic Reproducibility:** Given the identical set of clinical vitals, the deterministic safety engine produces the mathematically identical early warning score every single time ($P(\text{output}) = 1.0$), with zero stochastic variance or prompt drift.

---

## 5. Dependency Injection & Transaction Boundaries

FastAPI's dependency injection (`Depends`) is utilized to enforce clean lifecycle boundaries for database sessions and domain services:

```python
# Canonical Architectural Pattern for Dependency Injection and Transactions
@router.post("/cases/{case_id}/vitals", response_model=VitalsResponseDTO)
async def record_vitals(
    case_id: str,
    dto: RecordVitalsRequestDTO,
    current_user: User = Depends(require_role(["NURSE", "CLINICIAN"])),
    session: AsyncSession = Depends(get_db_session),
    vitals_service: VitalsService = Depends(get_vitals_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Atomic transaction boundary executing commands and audit logging."""
    async with session.begin():
        # 1. Execute deterministic domain command
        vital_reading, safety_alert = await vitals_service.record_and_evaluate(
            session=session,
            case_id=case_id,
            vitals_dto=dto,
            recorded_by=current_user.id
        )
        # 2. Append immutable audit event in the same atomic transaction
        await audit_service.log_event(
            session=session,
            actor_id=current_user.id,
            action="RECORD_VITALS",
            entity_type="CASE",
            entity_id=case_id,
            payload={"vitals": dto.model_dump(), "shock_index": vital_reading.shock_index}
        )
    return VitalsResponseDTO.from_orm(vital_reading, safety_alert)
```

---

## 6. Error Handling & Architectural Fallback Strategy

The backend enforces standard HTTP status codes combined with structured domain error envelopes:

```json
{
  "error_code": "CLINICAL_VALIDATION_FAILED",
  "message": "Systolic Blood Pressure (45 mmHg) is physiologically incompatible with stated alert consciousness without immediate verification.",
  "field": "systolic_bp",
  "remediation": "Check patient cuff placement or obtain immediate nursing re-measurement.",
  "is_fatal": false,
  "timestamp": "2026-10-08T10:30:00.000Z"
}
```

Whenever external subsystems (such as local OCR or speech transcription) fail, the backend degrades gracefully:
- OCR Failure: The document image is persisted with status `EXTRACTION_FAILED`; the UI displays the raw document image with manual data entry fields.
- ASR Failure: The audio recording is stored with status `TRANSCRIPTION_FAILED`; the UI allows direct audio playback for manual nurse transcription.
- The core clinical case is **never rejected or corrupted** due to secondary perceptual tool failures.
