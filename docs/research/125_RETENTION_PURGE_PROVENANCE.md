# CLINOVA AI — Data Retention, Purge Provenance & Cryptographic Longevity Model

> **Document ID:** `RES-125`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Statutory Dilemma: Privacy vs Medical Record Preservation

Clinical data architecture operates under two competing statutory obligations in India:
1. **The Digital Personal Data Protection (DPDP) Act, 2023 (Section 8(7)):** Enforces the principle of **Storage Limitation** — personal data must not be retained beyond the period necessary to satisfy the purpose for which it was collected, requiring routine deletion of raw biometric, audio, and visual personal identifiers.
2. **National Medical Commission (RMP) Regulations, 2023 (Regulation 28) & IPHS Guidelines:** Mandates that every Registered Medical Practitioner must preserve outpatient medical records for a minimum of **3 years**, inpatient/surgical and Medico-Legal Case (MLC) records for **7 years**, and pediatric records until the patient reaches age **21**.

Furthermore, under Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (formerly Section 65B of the Indian Evidence Act), electronic medical records must maintain proof that their contents were not tampered with, even after years in storage.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL PURGE PROVENANCE INVARIANT                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│         PURGING RAW MEDIA MUST NEVER ERASE DERIVED HISTORICAL LINEAGE.      │
│                                                                             │
│   When raw audio recordings or high-resolution document scans are purged     │
│   under storage limitation policies, their cryptographic SHA-256 hashes,    │
│   extracted facts, and verification metadata must remain permanently.        │
│   Post-purge provenance must clearly state: MEDIA PURGED, HASH RETAINED.     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Five Canonical Media Lifecycle States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FIVE CANONICAL LIFECYCLE STATES                        │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Lifecycle State │ Physical & Epistemic Meaning                              │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ 1. ACTIVE       │ Raw media and structured facts fully accessible on disk.  │
│ 2. RETAINED     │ Case closed; media held in read-only immutable storage.   │
│ 3. ARCHIVED     │ Compressed cold storage (offline LTO tape or Glacier).    │
│ 4. HASH_ONLY    │ Raw media binary deleted; SHA-256 hash & facts preserved. │
│ 5. PURGED       │ Irreversible cryptographic wipe of media and identifiers. │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 3. Statutory Retention Schedules by Clinical Category

| Clinical Encounter Category | Statutory Basis | Minimum Retention Period | Purge Action at Expiry |
| :--- | :--- | :--- | :--- |
| **Outpatient Routine Consultation** | NMC Regulations 2023 (Reg 28) | **3 Years** from encounter date | Audio purged $\to$ `HASH_ONLY`; structured facts archived. |
| **Inpatient Ward Admission** | IPHS 2022 Guidelines / MoHFW | **5 Years** from discharge date | Raw media $\to$ `HASH_ONLY`; structured discharge pack held. |
| **Surgical Procedure / OT** | Consumer Protection Act / IPHS | **7 Years** from surgery date | Audio $\to$ `HASH_ONLY`; signed operative notes held 10 yrs. |
| **Medico-Legal Case (MLC)** | Police / Court Evidence Rules | **Permanent or 10+ Years** | Purge prohibited without explicit judicial magistrate order. |
| **Pediatric Minor (< 18 yrs)** | Limitations Act / DPDP Sec 9 | **Until Age 21** ($18 + 3\text{ yrs}$) | Retained until 21st birthday; then outpatient rules apply. |
| **Ephemeral Intake Audio** | DPDP Act (Purpose Limitation)| **90 Days** post-verification | Raw audio wiped $\to$ `HASH_ONLY`; verified transcript remains. |

---

## 4. The `HASH_ONLY` State Machine Transition

When the automated retention maintenance worker executes a purge on raw audio files after 90 days of successful clinician verification:

```
[1. Pre-Purge Validation]    System verifies: evidence_records.verification_status = 'CLINICIAN_APPROVED'
                             System verifies: case is NOT flagged as Medico-Legal Case (MLC)
         │
[2. Cryptographic Re-Check]  Worker reads raw /var/data/clinova/media/aud_89f1.wav
                             Computes SHA-256: matches database value e4b2...19a0 exactly
         │
[3. Binary Scrub]            Physical file securely wiped (NIST SP 800-88 single-pass overwrite)
                             File path unlinked from disk
         │
[4. Provenance Transition]   raw_evidence_sources.retention_class updated to 'HASH_ONLY'
                             storage_reference updated to 'PURGED_ON_2026-10-08_PER_DPDP_POLICY'
         │
[5. Audit Event Logged]      Immutable row committed to media_purge_audit_events
```

### Clinician Inspection Experience Post-Purge
If a physician reviews the case 2 years later:
- The UI displays:
  ```
  Symptom: Severe Retrosternal Chest Pain (SNOMED CT: 29857009)
  ├── Source: VOICE_TRANSCRIBED [Verified by Nurse Anita on 2026-10-08 10:25 AM]
  ├── Verified by Clinician: Dr. P. K. Patnaik, MD on 2026-10-08 10:30 AM
  ├── Audio Status: MEDIA PURGED (Storage Limitation Policy 90-Day Expiry)
  ├── Historical Integrity: SHA-256 (e4b2a3c7f9910d88b47219ac09214b7e88...) VERIFIED
  └── Audio Playback: UNAVAILABLE (Binary Scrubbed)
  ```
The system **never falsely implies that the audio is still playable**, yet **guarantees that the historical fact and its cryptographic origin are mathematically verified**.

---

## 5. Purge Provenance Relational Schema

```sql
CREATE TABLE media_purge_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_evidence_source_id UUID NOT NULL REFERENCES raw_evidence_sources(id) ON DELETE RESTRICT,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    purged_storage_reference VARCHAR(512) NOT NULL,
    pre_purge_sha256_hash CHAR(64) NOT NULL,
    pre_purge_file_size_bytes BIGINT NOT NULL,
    
    purge_reason VARCHAR(64) NOT NULL CHECK (purge_reason IN (
        'STATUTORY_EXPIRY_3_YEARS', 'STATUTORY_EXPIRY_7_YEARS', 
        'EPHEMERAL_AUDIO_POLICY_90_DAYS', 'DPDP_RIGHT_TO_ERASURE_APPROVED',
        'STORAGE_QUOTA_REDUCTION_POLICY'
    )),
    
    statutory_authority VARCHAR(64) NOT NULL, -- e.g. 'DPDP_ACT_2023_SEC_8_7'
    executed_by_actor_id UUID NOT NULL REFERENCES users(id), -- System Daemon or DPO
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    cryptographic_wipe_method VARCHAR(32) NOT NULL DEFAULT 'NIST_SP_800_88_OVERWRITE'
);

CREATE INDEX ix_purge_case ON media_purge_audit_events(case_id);
CREATE INDEX ix_purge_source ON media_purge_audit_events(raw_evidence_source_id);
CREATE INDEX ix_purge_hash ON media_purge_audit_events(pre_purge_sha256_hash);
```

This retention architecture achieves perfect harmony between privacy rights under the DPDP Act 2023 and medicolegal record obligations under NMC Regulations 2023.
