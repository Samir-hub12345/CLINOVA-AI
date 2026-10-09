# CLINOVA AI — Evidence & Epistemic Provenance Architecture

> **Document ID:** `RES-145`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Epistemic Engineering & Clinical Provenance Architecture Group  

---

## 1. Architectural Scope & The Epistemic Safety Layer

Evidence provenance in CLINOVA AI is not passive database metadata; it is an active **Clinical Safety Layer**. In high-pressure rural casualty wards, catastrophic errors occur when unverified rumors, transcription typos, or algorithmic deductions are mistaken for objective physical truths.

CLINOVA formalizes the epistemic chain through three foundational laws:
1. **Source Class $\neq$ Objective Truth:** Stating *who* entered data or *how* it was captured does not make it infallible; all data requires appropriate clinical verification.
2. **$\text{INFERRED} \neq \text{VERIFIED}$:** AI deductions are permanently categorized as `AI_INFERRED` ($w=0.50$, advisory) and can never transition to `VERIFIED` without an authenticated RMP attestation.
3. **Non-Destructive History:** Conflicting evidence records are never overwritten. Both contradictory values are preserved in `evidence_records` and linked in `evidence_conflicts` for clinician adjudication.

---

## 2. The Nine-Stage Provenance Lineage Pipeline

Every piece of clinical information traces an unbroken, auditable nine-stage chain of custody:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NINE-STAGE PROVENANCE LINEAGE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RAW SOURCE                                                              │
│     • Physical artifact captured (Audio WAV, Prescription JPEG, PDF)        │
│     • Stored on filesystem/object storage with immutable SHA-256 hash       │
│                                  │                                          │
│                                  ▼                                          │
│  2. INGESTION                                                               │
│     • Registered in `raw_evidence_sources` with mime type, bytes, timestamp │
│                                  │                                          │
│                                  ▼                                          │
│  3. TRANSFORMATION                                                          │
│     • Audio resampled to 16kHz mono; document contrast-enhanced & deskewed  │
│                                  │                                          │
│                                  ▼                                          │
│  4. EXTRACTION                                                              │
│     • Perceptual extraction running with coordinate tracking:               │
│       - OCR: 2D Spatial Bounding Box [ymin, xmin, ymax, xmax] in [0, 1000]  │
│       - ASR: Word-level acoustic timecodes [t_start, t_end] in seconds      │
│                                  │                                          │
│                                  ▼                                          │
│  5. NORMALIZATION                                                           │
│     • Vernacular entities mapped to LOINC / SNOMED CT concepts & SI units   │
│                                  │                                          │
│                                  ▼                                          │
│  6. VERIFICATION                                                            │
│     • Acuity-proportional review tier evaluated (Staff vs Clinician review) │
│     • Authenticated RMP records affirmative attestation or modification    │
│                                  │                                          │
│                                  ▼                                          │
│  7. CLINICAL USE                                                            │
│     • Informs CAREGRAPH trajectory, NEWS2 calculation, and gap audits       │
│                                  │                                          │
│                                  ▼                                          │
│  8. DECISION                                                                │
│     • Directly referenced in clinician prescription or referral orders      │
│                                  │                                          │
│                                  ▼                                          │
│  9. OUTCOME                                                                 │
│     • Linked to final patient discharge condition and clinical loop closure │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Eight Evidence Sources & Six Epistemic States

### 3.1 Eight Canonical Evidence Source Classes
1. `PATIENT_REPORTED` (Subjective narrative; $w=0.60$)
2. `VOICE_TRANSCRIBED` (Acoustic vernacular capture; $w=0.70$)
3. `OCR_EXTRACTED` (Optical scan / crop; $w=0.75$)
4. `CLINICIAN_VERIFIED` (RMP exam / order / signoff; $w=1.00$)
5. `STAFF_ENTERED` (Nurse / ANM calibrated measurement; $w=0.95$)
6. `AI_INFERRED` (Statistical model deduction; $w=0.50$, strictly advisory)
7. `SYSTEM_DERIVED` (Deterministic mathematical score; $w=1.00$)
8. `EXTERNAL_RECORD` (Historical ABDM / prior hospital summary; $w=0.80$)

### 3.2 Six Canonical Epistemic States
1. `KNOWN`: Fact actively present in chart with high reliability.
2. `UNKNOWN`: Information gap explicitly identified under Zero-Imputation Law.
3. `CONFLICTING`: Two or more contradictory values coexist awaiting RMP review.
4. `UNRELIABLE`: Low perceptual quality (SNR $< 12\text{dB}$, blurry scan $< 150\text{ DPI}$).
5. `VERIFIED`: Explicitly confirmed by a licensed human clinician.
6. `INFERRED`: Proposed by statistical AI model; advisory only.

---

## 4. Perceptual Grounding: Visual & Acoustic Pointers

To allow instant side-by-side verification on the Doctor Reviewer Workbench:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PERCEPTUAL GROUNDING ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ OPTICAL GROUNDING (OCR) ]                                               │
│   • Document Page: `document_ocr_pages`                                     │
│   • Normalized Bounding Box: [ymin, xmin, ymax, xmax] subset [0, 1000]^2   │
│   • Doctor clicks "Platelets: 42,000 /uL"                                   │
│     └──► Workbench displays instant cropped visual snippet of paper slip.   │
│                                                                             │
│   [ ACOUSTIC GROUNDING (SPEECH) ]                                           │
│   • Audio Recording: `audio_recordings` (WAV, 16kHz)                        │
│   • Word Alignment: [t_start = 14.2s, t_end = 17.1s]                       │
│   • Doctor clicks "Severe retrosternal pain radiating to left jaw"          │
│     └──► Workbench streams exact 3-second vernacular audio snippet.         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Non-Destructive Conflict Management Architecture

When contradictory measurements enter the chart (e.g. Patient states BP is normal, but nurse measures SBP 195 mmHg):
1. **Dual Persistence:** Both rows are inserted into `evidence_records` with their respective sources and timestamps.
2. **Conflict Linking:** A record is created in `evidence_conflicts`:
   ```sql
   INSERT INTO evidence_conflicts (
       id, case_id, evidence_id_a, evidence_id_b, parameter_name,
       severity, resolution_status, created_at
   ) VALUES (
       gen_random_uuid(), :case_id, :ev_a_id, :ev_b_id, 'systolic_bp',
       'CRITICAL_DISCORDANCE', 'PENDING_CLINICIAN_REVIEW', :now
   );
   ```
3. **Safety-Pessimistic Principle:** Downstream emergency triage engines temporarily use the **highest-acuity value** (SBP 195) to protect the patient from waiting-room deterioration, while flagging the value on the doctor's screen with a prominent amber `CONFLICTING` badge.
4. **Resolution:** The doctor selects `ACCEPTED_A`, `ACCEPTED_B`, `ACCEPTED_BOTH_TEMPORAL`, or `MANUAL_OVERRIDE`, writing an immutable `conflict_resolution_events` row.
