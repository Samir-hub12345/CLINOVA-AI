# CLINOVA AI — Configuration Requirements & Statutory Traceability Matrix

> **Document ID:** `RES-190`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Regulatory Compliance, Verification Engineering & Traceability Group  

---

## 1. Traceability Architecture

Phase 9 ensures complete, unbroken bidirectional traceability between external statutory mandates (NMC, DPDP Act 2023, BSA 2023), academic hackathon specifications (BPUT Baseline `B01`–`B18`, Core Innovations `C01`–`C11`), and the concrete configuration variables and invariants defined in this phase.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BIDIRECTIONAL TRACEABILITY FLOW                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STATUTORY & PROBLEM REQUIREMENTS ]                                       │
│  ├── BPUT Baseline Specifications (`B01` - `B18`)                           │
│  ├── CLINOVA Core Innovations (`C01` - `C11`)                               │
│  ├── NMC RMP Regulations 2023 (Reg 27 & 28)                                 │
│  ├── Bharatiya Sakshya Adhiniyam 2023 (Section 63)                          │
│  └── Digital Personal Data Protection Act 2023                              │
│          │                                                                  │
│          ▼ Mapped To                                                        │
│  [ PHASE 9 CONFIGURATION SCHEMAS & INVARIANTS ]                             │
│  ├── Pydantic Settings (`RES-165`)                                          │
│  ├── Credential Taxonomy (`RES-166`)                                        │
│  ├── Frontend Boundary (`RES-167`)                                          │
│  ├── Deployment & Facility Profiles (`RES-168` - `RES-174`)                 │
│  └── Zero-Cost Economic Mandate (`RES-188`)                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Traceability Matrix

| Req ID | Requirement Description | Phase 9 Configuration Enforcer | Architectural Verification & Rule |
| :--- | :--- | :--- | :--- |
| **B01** | Multi-Modal Patient Intake | `FEATURE_VOICE=True`, `FEATURE_OCR=True`, `STORAGE_MODE` | Ingestion boundaries defined for audio, photo, text without cloud requirement. |
| **B02** | Vernacular Language Support | `FEATURE_TRANSLATION=True`, `default_languages` in profiles | Defaults to Odia/Hindi for rural PHC; English/Hindi for corporate. |
| **B03** | Deterministic Triage Scoring | `safety.py` (Non-flagged), `NEWS2` / `Shock Index` | Core physiological scoring is hardcoded; cannot be disabled by any flag. |
| **B04** | RMP Verification Gate | `NMC Reg 27 Gate` (Immutable Invariant) | System cannot auto-diagnose or prescribe; requires clinician session token. |
| **B05** | Offline Rural Capability | `APP_ENV=phc_edge`, `OFFLINE_MODE=True`, `LOCAL_FS` | Fanless Mini-PC runs autonomously on local SQLite WAL with zero WAN. |
| **B06** | Zero-Cost Infrastructure | `RES-188` Economic Model, `AI_PROVIDER=local_rules` | Zero mandatory paid APIs; all core features execute on open-source code. |
| **B07** | Data Privacy & Redaction | `CLINOVA_DATA_MODE=synthetic`, `PHI_LOGGING_POLICY` | Synthetic data default; regex redaction filters zero PHI in logs. |
| **B08** | Digital Legal Admissibility | `AUDIT_MODE=True`, `audit_events` Merkle chain | Section 63 BSA 2023 hash chaining enforced in all operational modes. |
| **B09** | Rapid Emergency Intake | `FEATURE_EMERGENCY_MODE=True`, `< 200ms` token flow | Bypasses non-essential forms during acute casualty arrivals. |
| **B10** | Facility Resource Awareness | `FEATURE_FACILITYGRAPH=True`, `FACILITY_PROFILES` | Capability matching prevents blind referrals to unavailable ICU beds. |
| **B11** | Trajectory Risk Visualization| `FEATURE_CAREGRAPH=True`, CSS Grid tokens | In-memory delta slope rendered using pure CSS variables and charts. |
| **B12** | Local Syndromic Monitoring | `FEATURE_SIGNALGRAPH=True`, facility anomaly score | Privacy-scrubbed z-score syndromic detection per environment profile. |
| **B13** | Multi-Graph Orchestration | `FEATURE_ORCHESTRATION=True`, candidate action vector | Synthesizes CareGraph, Facility, and Evidence into advisory actions. |
| **B14** | Perceptual Grounding | `PaddleOCR` bounding boxes $[0, 1000]^2$, audio timecodes | Side-by-side verification previews rendered via CSS Modules. |
| **B15** | Single Master Case Aggregate | `cases` table canonical designation, `case_id` UUID | Unified clinical episode coordinates all observations and vitals. |
| **B16** | Pure Standards Styling | CSS Variables, Flexbox/Grid, **Tailwind Rejection** | Reconciles Phase 8 styling; eliminates utility bloat in favor of native CSS. |
| **B17** | Secret Isolation Boundary | `Inv-FE-1`, `NEXT_PUBLIC_*` strictly restricted | Zero service-role keys or database passwords in client bundles. |
| **B18** | Fail-Closed Security | Pydantic boot validators, pre-flight write barriers | Process terminates (Exit 1) upon missing secrets or invalid config. |

---

## 3. Statutory Compliance Mapping

### 3.1 National Medical Commission (NMC) Regulations 2023
- **Regulation 27 (Physician Accountability):** System configuration enforces that all clinical suggestions are explicitly categorized as `AI_INFERRED` and require affirmative human RMP verification (`Inv-AI-2`).
- **Regulation 28 (Digital Prescription Standards):** Prescriptions are tied to the authenticated doctor's state medical council registration number; anonymous auto-prescribing is blocked.

### 3.2 Bharatiya Sakshya Adhiniyam, 2023 (Section 63)
- Modernizing Section 65B of the Indian Evidence Act, Section 63 requires proof of lawful computing custody and tamper-evident logging.
- Phase 9 mandates `AUDIT_MODE=True` across all live environments, producing immutable Merkle hash proofs ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$).

### 3.3 Digital Personal Data Protection (DPDP) Act, 2023
- **Sections 4 & 6 (Notice and Consent):** Triage workflow mandates consent capture before record persistence.
- **Section 8(7) (Storage Limitation):** Raw media retention is capped at 30 days (`MEDIA_RETENTION_POLICY_DAYS=30`), after which raw binary files are purged, retaining only cryptographic hashes.
