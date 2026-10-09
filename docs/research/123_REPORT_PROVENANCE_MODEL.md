# CLINOVA AI — Clinical Report Provenance & Artifact Lineage Model

> **Document ID:** `RES-123`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Peril of Detached Medical Reports

In conventional hospital operations, generated clinical documents (discharge summaries, referral letters, police injury reports, SBAR transit handoffs) frequently become **detached snapshots**. Once exported as a PDF or printed on paper:
- All hyperlinks back to the underlying vitals, audio recordings, or OCR crops are severed.
- The receiving clinician cannot tell whether a listed diagnosis was verified by a physician or merely suggested by an AI triage algorithm.
- If a late laboratory result arrives after the report was generated (e.g., blood cultures showing Methicillin-Resistant *S. aureus*), the static PDF in the patient's hand continues to circulate as if it were the active truth.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL REPORT PROVENANCE INVARIANT                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              REPORTS MUST NEVER BECOME DETACHED SNAPSHOTS                   │
│                        WITH NO SOURCE LINEAGE.                              │
│                                                                             │
│   Every generated clinical report, PDF, and FHIR export must carry an       │
│   embedded, tamper-evident cryptographic provenance manifest.               │
│   Verified and inferred values must be visually and semantically decoupled.│
│   Post-generation mutations must explicitly watermark prior revisions       │
│   as SUPERSEDED.                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Seven Invariant Report Provenance Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SEVEN REPORT PROVENANCE PILLARS                        │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Master Case Root  │ Immutable binding to canonical case_id (UUIDv4)      │
│ 2. Evidence Manifest │ Exact inventory of included evidence record UUIDs    │
│ 3. Epistemic Labels  │ Explicit "Verified" vs "AI-Inferred" section badges  │
│ 4. Generation Clock  │ Microsecond generation timestamp and sequence        │
│ 5. Engine Version    │ Software version, template ID, and git commit hash   │
│ 6. Clinician Signoff │ Attending RMP name, NMR number, cryptographic token  │
│ 7. Post-Gen History  │ Revisions, addenda, and "SUPERSEDED" watermarking    │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 3. Epistemic Separation in Generated Documents

Whether exported as an ABDM-compliant FHIR Discharge Summary Bundle, an SBAR Referral Document, or a printed PDF, the report layout strictly isolates verified facts from unverified inferences:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CLINOVA CLINICAL SBAR REFERRAL SUMMARY                      │
│                 Case ID: f81d4fae-7dec-11d0-a765-00a0c91e6bf6               │
├─────────────────────────────────────────────────────────────────────────────┤
│ SECTION 1: VERIFIED CLINICAL FACTS (Physician Attested)                     │
│ [V] Confirmed Diagnosis: Acute Anterior Wall STEMI (ICD-11: BA41.0)         │
│ [V] Blood Pressure: 88/54 mmHg | Heart Rate: 114 bpm | SpO2: 91% (10:24 AM) │
│ [V] Attending Clinician: Dr. P. K. Patnaik, MD (NMR #78412)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ SECTION 2: REPORTED NARRATIVE (Unverified Subjective History)               │
│ [?] Chest Pain Onset: 06:30 AM (Reported by Patient Spouse)                 │
│ [?] Known Allergy: "Believed to be allergic to Penicillin"                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ SECTION 3: DECISION SUPPORT TELEMETRY (Advisory / Inferred)                 │
│ [AI] NEWS2 Score: 8 (High Acuity) | Shock Index: 1.30 (Severe Shock)        │
│ [AI] Recommended Action: Immediate Primary PCI Transfer (SCB Cuttack)       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Integrity Hash: SHA-256 e4b2...19a0 | Generated: 2026-10-08 10:35:12 UTC    │
│ Scan QR Code to Verify Live Electronic State on CLINOVA Network             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Post-Generation Revision & Supersession Dynamics

If new evidence is captured or a clinician amends an order after Report Rev 1 has been issued:
1. **Report Rev 1 is NEVER modified in place.**
2. A new `Report Rev 2` is compiled and signed.
3. `Report Rev 1` status is transitioned to `SUPERSEDED`.
4. If anyone attempts to view or download `Report Rev 1`, the PDF rendering engine embeds a prominent diagonal red watermark across all pages:
   $$\text{\Large \textbf{SUPERSEDED BY REVISION 2 ON 2026-10-08 11:15 UTC}}$$
5. The digital QR code printed on the physical document routes the mobile scanner to an active warning page alerting the receiving hospital that a newer clinical summary exists.

---

## 5. Canonical Report Relational Schema

```sql
CREATE TABLE clinical_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    report_type VARCHAR(32) NOT NULL CHECK (report_type IN (
        'SBAR_REFERRAL_SUMMARY', 'INPATIENT_DISCHARGE_SUMMARY', 
        'EMERGENCY_TRIAGE_NOTE', 'SURGICAL_OPERATIVE_NOTE', 'ABDM_FHIR_BUNDLE'
    )),
    revision_number INTEGER NOT NULL DEFAULT 1 CHECK (revision_number >= 1),
    
    -- Engine and Template Provenance
    template_identifier VARCHAR(64) NOT NULL,
    template_version_hash CHAR(64) NOT NULL,
    generator_engine_version VARCHAR(32) NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Content and Cryptographic Seals
    rendered_payload_json JSONB NOT NULL,
    rendered_document_pdf_path VARCHAR(512),
    document_sha256_hash CHAR(64) NOT NULL,
    
    -- RMP Attestation
    attesting_clinician_id UUID NOT NULL REFERENCES users(id),
    nmr_registration_number VARCHAR(64) NOT NULL,
    digital_signature_token TEXT NOT NULL,
    attested_at TIMESTAMPTZ NOT NULL,
    
    -- Lifecycle and Supersession Tracking
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE' CHECK (lifecycle_status IN (
        'ACTIVE', 'SUPERSEDED', 'RETRACTED', 'ARCHIVED'
    )),
    superseded_by_report_id UUID REFERENCES clinical_reports(id),
    superseded_at TIMESTAMPTZ,
    supersession_reason TEXT
);

-- Manifest of every evidence record frozen into this report
CREATE TABLE report_evidence_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES clinical_reports(id) ON DELETE CASCADE,
    evidence_record_id UUID NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    frozen_value_snapshot JSONB NOT NULL,
    frozen_epistemic_status VARCHAR(16) NOT NULL,
    frozen_source_type VARCHAR(32) NOT NULL
);

CREATE INDEX ix_rep_case ON clinical_reports(case_id);
CREATE INDEX ix_rep_status ON clinical_reports(lifecycle_status);
CREATE INDEX ix_rep_hash ON clinical_reports(document_sha256_hash);
CREATE INDEX ix_rep_man_rep ON report_evidence_manifests(report_id);
```

By binding every document to an immutable evidence manifest and QR-verifiable web anchor, CLINOVA AI eliminates detached medical snapshots and prevents communication breakdowns during critical patient handoffs.
