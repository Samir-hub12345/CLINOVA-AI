# CLINOVA AI — Provenance Security, Tamper Resistance & Evidentiary Integrity Model

> **Document ID:** `RES-127`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Medicolegal Evidentiary Mandate & Statutory Modernization

In clinical malpractice litigation, criminal coroner inquiries, and regulatory medical audits in India, hospital electronic records are subject to strict evidentiary standards. 

### Modern Indian Legal Framework
This specification formally updates and reconciles statutory citations with modern Indian legislation:
- **Bharatiya Sakshya Adhiniyam (BSA), 2023 (Section 63):** Replaces Section 65B of the Indian Evidence Act, 1872. Governs the admissibility of electronic records in court, requiring proof of computer system integrity, uncorrupted data transmission, and certified custody logs.
- **Digital Personal Data Protection (DPDP) Act, 2023 (Sections 4, 6, 8, 9):** Governs data fiduciary obligations, reasonable security safeguards against unauthorized access or tampering, and parental consent audit trails for minors.
- **National Medical Commission (RMP) Regulations, 2023 (Regulation 28):** Establishes personal physician liability for the preservation and authenticity of medical records.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL TAMPER RESISTANCE INVARIANT                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  EVIDENCE PROVENANCE CANNOT BE SILENTLY                     │
│                           ALTERED OR DETACHED.                              │
│                                                                             │
│   Historical evidence records, actor attributions, and timestamps are       │
│   append-only. Database triggers and cryptographic hash chains prohibit     │
│   physical UPDATE and DELETE queries. Any attempt to modify historical      │
│   provenance breaks the Merkle hash chain and triggers a security alert.    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Six Conceptual Security & Tamper-Resistance Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SIX TAMPER-RESISTANCE PILLARS                          │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Content Hashing   │ Cryptographic SHA-256 fingerprints of all raw media  │
│ 2. Immutable UUIDs   │ RFC 4122 globally unique identifiers                 │
│ 3. Append-Only DB    │ Engine triggers blocking in-place UPDATE and DELETE  │
│ 4. Merkle Chaining   │ H(n) = SHA256( H(n-1) || event_id || payload )       │
│ 5. Concurrency Locks │ Atomic compare-and-swap on monotonic state_version   │
│ 6. Runtime Auditing  │ Scheduled background daemon checking hash consistency│
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 3. Cryptographic Merkle Hash Chaining Specification

Every clinical, administrative, or algorithmic event within a case is appended to the `case_events` ledger. Each event $n$ is cryptographically chained to its predecessor event $n-1$:

$$H_0 = \text{SHA256}(\text{case\_id} \parallel \text{created\_at} \parallel \text{"GENESIS"})$$
$$H_n = \text{SHA256}\Big( H_{n-1} \parallel \text{event\_id} \parallel \text{actor\_id} \parallel \text{timestamp} \parallel \text{CanonicalJSON}(\text{payload}) \Big)$$

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│   Event 1    │          │   Event 2    │          │   Event 3    │
│  (Intake)    │          │   (Vitals)   │          │  (Review)    │
│  Hash: H_1   │ ───────► │  Hash: H_2   │ ───────► │  Hash: H_3   │
│  Prev: H_0   │          │  Prev: H_1   │          │  Prev: H_2   │
└──────────────┘          └──────────────┘          └──────────────┘
```

### Forensic Proof of Non-Tampering (Section 63 BSA 2023)
If a malicious database administrator executes an unauthorized `UPDATE` on Event 2 (e.g. changing an allergy or altering an injected drug dosage):
1. The hash of Event 2 ceases to match $\text{SHA256}(H_1 \parallel \dots)$.
2. When Event 3 is inspected, its stored `previous_hash` ($H_2$) fails to validate against the modified row.
3. The Merkle chain is broken; the fraud is instantly detectable by forensic examiners.

---

## 4. Database-Level Immobility Enforcement (Triggers)

To guarantee that application bugs or rogue SQL queries cannot overwrite clinical history, database-level triggers enforce immutability at the engine layer in both PostgreSQL and SQLite:

### 4.1 PostgreSQL Immutability Trigger
```sql
CREATE OR REPLACE FUNCTION trg_enforce_evidence_immutability()
RETURNS TRIGGER AS $$
BEGIN
    -- Prohibit physical deletion
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'CRITICAL SECURITY VIOLATION: Physical deletion of evidence records is prohibited under Section 63 BSA 2023.';
    END IF;
    
    -- Prohibit alteration of core provenance attributes
    IF TG_OP = 'UPDATE' THEN
        IF NEW.id != OLD.id OR 
           NEW.case_id != OLD.case_id OR 
           NEW.source_type != OLD.source_type OR 
           NEW.recorded_by_actor_id != OLD.recorded_by_actor_id OR 
           NEW.recorded_at != OLD.recorded_at THEN
            RAISE EXCEPTION 'CRITICAL SECURITY VIOLATION: Provenance metadata is strictly immutable.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_evidence_records
BEFORE UPDATE OR DELETE ON evidence_records
FOR EACH ROW EXECUTE FUNCTION trg_enforce_evidence_immutability();
```

### 4.2 SQLite Dialect Trigger
```sql
CREATE TRIGGER trg_no_delete_evidence_sqlite
BEFORE DELETE ON evidence_records
BEGIN
    SELECT RAISE(FAIL, 'SECURITY ERROR: Deletion of evidence records prohibited.');
END;
```

---

## 5. Runtime Integrity Verification Daemon

CLINOVA edge and cloud daemons run periodic, non-blocking integrity audits:
1. **Media Integrity Check:** Verifies that physical audio and document files on disk match the `file_checksum_sha256` recorded in `raw_evidence_sources`.
2. **Chain Verification Query:** Traverses `case_events` from genesis to the active leaf, recomputing $H_n$ iteratively.
3. **Anomaly Reporting:** Any mismatch immediately isolates the case record, logs a high-severity alert in `security_tamper_audit_logs`, and marks the case status as `INTEGRITY_DISPUTED`.

---

## 6. Security Relational Schema

```sql
CREATE TABLE security_tamper_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    incident_type VARCHAR(32) NOT NULL CHECK (incident_type IN (
        'HASH_MISMATCH_ON_DISK', 'MERKLE_CHAIN_BROKEN', 'UNAUTHORIZED_MUTATION_ATTEMPT', 
        'CLOCK_DRIFT_ANOMALY', 'ACTOR_CREDENTIAL_SUSPECT'
    )),
    
    target_table_name VARCHAR(64) NOT NULL,
    target_record_id UUID NOT NULL,
    expected_hash CHAR(64),
    computed_hash CHAR(64),
    
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    detection_daemon_version VARCHAR(32) NOT NULL,
    is_investigated BOOLEAN NOT NULL DEFAULT FALSE,
    investigated_by_security_officer_id UUID REFERENCES users(id),
    resolution_notes TEXT
);

CREATE INDEX ix_sec_case ON security_tamper_audit_logs(case_id);
CREATE INDEX ix_sec_type ON security_tamper_audit_logs(incident_type);
```

By substituting obsolete legal references with Section 63 of the Bharatiya Sakshya Adhiniyam, 2023, and enforcing database-level cryptographic hash chaining, CLINOVA AI provides ironclad medicolegal and clinical tamper resistance.
