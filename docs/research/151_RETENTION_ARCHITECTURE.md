# CLINOVA AI — Data Retention, Purge Lifecycle & Daemon Authorization Architecture

> **Document ID:** `RES-151`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Legal Informatics, Data Governance & Security Engineering Group  

---

## 1. Statutory Foundations & Data Minimization Mandate

Under Indian public health law and digital personal data protection frameworks, clinical systems face two conflicting statutory mandates:

1. **Storage Limitation (DPDP Act 2023, Section 8(7)):** A data fiduciary must erase personal data upon purpose completion or retention expiry. Indefinitely storing raw audio recordings of intimate patient interviews or high-resolution camera photos of prescriptions on edge SSDs violates data minimization.
2. **Forensic Evidence Admissibility (NMC Reg 28 & Section 63 BSA 2023):** Registered Medical Practitioners must maintain medical records for a minimum of **3 years** (general cases) or **7 years** (Medico-Legal Cases - MLC). Furthermore, electronic records presented in legal proceedings require proof of uncorrupted custody.

---

## 2. The Four-Stage Retention Lifecycle: The `HASH_ONLY` State

CLINOVA AI resolves this statutory tension through the **`HASH_ONLY` Lifecycle Model**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATA RETENTION LIFECYCLE STAGES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STAGE 1: ACTIVE CLINICAL EPISODE ]                                       │
│  ├── Raw binary media (WAV audio, JPEG prescription) accessible on disk     │
│  ├── Full playback and high-resolution zooming enabled on Doctor Workbench  │
│  └── Storage State: `ACTIVE`                                                │
│                                  │                                          │
│                                  ▼ (Patient Discharged / Outcome Finalized) │
│  [ STAGE 2: MANDATORY RETENTION WINDOW ]                                    │
│  ├── Raw media retained for operational grace period:                       │
│  │   • General Outpatient Media: 30 days                                    │
│  │   • Inpatient / Emergency Media: 90 days                                 │
│  │   • Structured Clinical Data: 3 years (NMC Reg 28)                       │
│  │   • Medico-Legal Records (MLC): 7 years (IPHS Standards)                 │
│  └── Storage State: `RETENTION_PENDING`                                     │
│                                  │                                          │
│                                  ▼ (Retention Period Expires)               │
│  [ STAGE 3: CRYPTOGRAPHIC PURGE & DISPOSAL ]                                │
│  ├── Automated Retention Daemon unlinks and securely zeroes raw binary file │
│  │   from disk / object storage (NIST SP 800-88 Rev 1 compliant overwrite) │
│  └── Storage State: `PURGED`                                                │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 4: `HASH_ONLY` FORENSIC PRESERVATION ]                             │
│  ├── Relational record in `raw_evidence_sources` remains intact:            │
│  │   • SHA-256 Checksum preserved permanently                               │
│  │   • Normalized clinical text & LOINC extractions preserved permanently   │
│  │   • RMP verification attestations preserved permanently                  │
│  │   • Binary file path set to NULL                                         │
│  │   • Purge Certificate Hash & Timestamp appended                          │
│  └── Storage State: `HASH_ONLY`                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Forensic Integrity Invariant
**Invariant RET-1:** Even after raw binary media is purged, the legal proof of custody under Section 63 BSA 2023 remains mathematically intact. Anyone challenging an extracted clinical fact can verify that the original document SHA-256 hash matches the historical Merkle ledger chain.

---

## 3. Resolving the Retention Daemon Database Trigger Exception

### 3.1 The Architectural Conflict
- In Phase 7 and Phase 6, database triggers were architected to enforce immutability on `evidence_records`, `raw_evidence_sources`, and audit tables by raising an exception on any `UPDATE` or `DELETE` statement.
- When the retention window expires, the background **Retention Daemon** must transition `storage_state` from `ACTIVE` to `HASH_ONLY`, set `file_uri = NULL`, and write `purged_at = :utc_now`.
- If the database trigger blindly prohibits all updates, the retention daemon crashes with a permission denied error, creating a deadlock between data minimization law and immutability rules.

### 3.2 Definitive Architectural Resolution
CLINOVA implements an **Authorized Daemon Bypass Mechanism** via session-scoped transaction configuration or dedicated database role:

```sql
-- Architectural PostgreSQL Trigger Implementation for Authorized Retention Transitions
CREATE OR REPLACE FUNCTION trg_enforce_evidence_immutability()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if current transaction is an explicitly authorized retention daemon
    IF current_setting('clinova.retention_daemon_active', true) = 'true' THEN
        -- Allow ONLY retention-state and purge metadata modifications:
        IF (NEW.id = OLD.id AND
            NEW.case_id = OLD.case_id AND
            NEW.file_hash = OLD.file_hash AND
            NEW.created_at = OLD.created_at AND
            NEW.storage_state = 'HASH_ONLY' AND
            NEW.file_uri IS NULL) THEN
            RETURN NEW; -- Authorized purge transition permitted
        ELSE
            RAISE EXCEPTION 'Retention daemon attempted unauthorized modification of clinical payload';
        END IF;
    END IF;

    -- Block all standard user UPDATE and DELETE operations
    RAISE EXCEPTION 'Clinical evidence records are immutable. Direct updates and deletes are prohibited.';
END;
$$ LANGUAGE plpgsql;
```

### In SQLite Edge WAL Mode:
In local SQLite environments, the application layer encapsulates the purge operation inside a dedicated `RetentionService` that verifies daemon credentials and logs an explicit `PURGE_EVENT` into `audit_logs` within the same atomic transaction.

**Non-Implementation Rule:** In accordance with the Phase 8 atomic phase rule, the retention daemon background service is **NOT implemented now**. This specification establishes the authoritative database architecture for Phase 9 implementation.
