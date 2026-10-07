# CLINOVA AI — Security & Privacy Architecture

> **Document ID:** `DOC-15`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Compliance Standard & Privacy By Design

CLINOVA AI adheres to the highest international and clinical software privacy benchmarks:
- **HIPAA Security Rule § 164.312** (Technical Safeguards: Access Control, Audit Controls, Integrity, Person Authentication, Transmission Security).
- **ISO 27001 & ISO 27799** (Health Informatics Information Security Management).
- **Digital Personal Data Protection (DPDP) Act & GDPR Principle of Data Minimization.**

---

## 2. Privacy Safeguards: 100% Synthetic Data & PII Minimization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PII SCRUBBING & PSEUDONYMIZATION                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ Raw Intake Stream ]                                                     │
│   "Patient Ramesh Kumar, 58/M, Phone 9876543210, Aadhaar 1234-5678-9012"    │
│            │                                                                │
│            ▼                                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      IN-MEMORY SANITIZER GATE                       │   │
│   │  1. Match Regex: Names, Phone numbers, National IDs, Exact Addresses│   │
│   │  2. Map Exact Age (58) -> Age Bracket ("50-59")                     │   │
│   │  3. Issue Cryptographic Pseudonym -> "SYN-PT-8821"                  │   │
│   │  4. Zero raw PII written to database or transmitted to LLM          │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│   [ Sanitized Clinical Record ]                                             │
│   "Patient SYN-PT-8821, Age 50-59, Male, Severe Chest Pain x 2 hours"       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Zero Real Patient Data:** The prototype operates strictly on curated synthetic test profiles. Real patient protected health information (PHI) is never loaded or processed.
2. **Deterministic Pseudonymization:** All case identifiers are generated as opaque synthetic tokens (`SYN-PT-XXXX`).
3. **Data Retention & Disposal Policy:**
   - Active encounter data is retained only for the duration of the clinical episode or demonstration cycle (default: 24-hour TTL in development).
   - Inactive/closed encounters are securely archived or purged with all ephemeral voice and OCR cache buffers destroyed.

---

## 3. Role-Based Access Control (RBAC) Matrix

| User Role | Intake Form | CareGraph Review | Clinician Sign-off | Referral Dispatch | SignalGraph | Audit Logs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Patient / Caregiver** | Read/Submit (Own) | No | No | No | No | No |
| **Triage Nurse** | Full Access | View Only | No | Prepare Only | No | No |
| **Medical Officer / Doctor** | View/Amend | Full Access | **Authorize & Override** | Authorize | View Only | View Own |
| **Referral Coordinator** | View Summary | View Summary | No | **Dispatch & Accept** | View Network | View Transfers |
| **Hospital Administrator** | No Clinical | No Clinical | No | View Capacity | **Full Access** | **Full Audit Access** |

---

## 4. Input Validation & Defense-in-Depth

### 4.1 File Upload Security
- **MIME & Magic Byte Inspection:** Client-reported file extensions and MIME headers are untrusted. Incoming files are inspected for magic bytes (`%PDF`, `\x89PNG`, `\xFF\xD8\xFF`) to prevent executable uploads (`MZ`, `ELF`).
- **File Size Caps:** Strict limits enforced at reverse proxy and application level (Max 10MB per document; Max 20MB per voice recording).

### 4.2 Secrets Management
- Zero API keys, passwords, or database credentials are committed to version control.
- All configuration is resolved through `.env` loaded via Pydantic `BaseSettings`.
- Frontend code exposes zero backend secrets (only public URLs prefixed with `NEXT_PUBLIC_`).

---

## 5. Tamper-Evident Audit Logging

Every mutating action generates an immutable audit entry containing:
- ISO 8601 UTC timestamp.
- User UUID and authenticated clinical role.
- Action verb (`INTAKE_SUBMITTED`, `NODE_VERIFIED`, `DECISION_AUTHORIZED`, `OVERRIDE_RECORDED`).
- Entity ID and cryptographic SHA-256 hash of the modified payload.
