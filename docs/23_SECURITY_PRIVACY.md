# CLINOVA AI — Security, Privacy & Data Governance Specification

> **Document ID:** `DOC-23`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Compliance Framework & Foundational Mandates

CLINOVA AI complies with national and international health data protection frameworks:
- **India DPDP Act 2023** (Digital Personal Data Protection Act)
- **India DISHA Guidelines** (Digital Information Security in Healthcare Act)
- **HIPAA Security & Privacy Standards** (Health Insurance Portability and Accountability Act)

> **Core Foundational Mandates:**
> 1. **Synthetic / Public Data Only:** The system processes synthetic clinical records and simulated public samples exclusively. Absolutely zero real, identifiable patient records are ever collected, committed, or ingested.
> 2. **Zero Hardcoded Secrets:** Credentials, keys, and session tokens must never be committed to Git.
> 3. **Human-in-the-Loop Governance:** Autonomous AI actions with irreversible clinical consequences are barred at the architectural layer.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA SECURITY & PRIVACY GATES                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ GATE 1: INFORMED CONSENT CAPTURE ] ──> Explicit digital / verbal gate   │
│                   │                                                         │
│                   ▼                                                         │
│   [ GATE 2: PII SCRUBBING & PSEUDONYMIZATION ] ──> In-flight regex & NLP    │
│                   │                                                         │
│                   ▼                                                         │
│   [ GATE 3: ROLE-BASED ACCESS CONTROL (RBAC) ] ──> 8 Roles, JWT + Row-Level │
│                   │                                                         │
│                   ▼                                                         │
│   [ GATE 4: EPHEMERAL STORAGE & MINIMAL RETENTION ] ──> 24-Hour File Purge  │
│                   │                                                         │
│                   ▼                                                         │
│   [ GATE 5: IMMUTABLE AUDIT TRAIL ] ──> Cryptographic Tamper-Evident Ledger │
│                   │                                                         │
│                   ▼                                                         │
│   [ GATE 6: QUALIFIED CLINICIAN SIGN-OFF ] ──> Mandatory Human Gatekeeper   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Flight PII Minimization & Anonymization Engine

Before any raw patient narrative, audio transcript, or OCR text is processed by extraction algorithms or stored in persistent tables, it passes through the `AnonymizerService`:

### 2.1 PII Scrubbing Rules
- **Government Identifiers:** Indian Aadhaar (12 digits), PAN cards, voter IDs, and driving licenses are detected via regex and replaced with `[GOVT_ID_REDACTED]`.
- **Contact Details:** Phone numbers (+91 / 10 digits) and email addresses are scrubbed and replaced with `[PHONE_REDACTED]` and `[EMAIL_REDACTED]`.
- **Direct Names & Addresses:** Patient full names and home street addresses are stripped, and the record is mapped to a synthetic pseudonym:
  $$\text{Synthetic ID Format:}\ \mathbf{PT\text{-}XXXXXX}\quad (\text{e.g., } \text{PT-482910})$$

---

## 3. Minimal Data Retention & Ephemeral Storage Policy

Public healthcare clinics require zero long-term data liabilities for transient multimedia files.

### 3.1 24-Hour Ephemeral Disposal Protocol
- **Raw Audio Waves (.wav / .webm):** Retained in temporary ephemeral storage for 24 hours to allow clinical verification, after which the raw audio file is permanently shredded (`rm -P` / cryptographically wiped).
- **Uploaded Document Images & PDFs:** Original scans are purged after 24 hours. Only the extracted, clinician-verified structured discrete parameters and clinical entities are preserved in the permanent Master Case record.
- **Session Tokens:** Auth JWTs expire automatically after 60 minutes of inactivity.

---

## 4. Role-Based Access Control & Secret Separation

1. **Least-Privilege RBAC:** Enforced across all API endpoints using FastAPI dependency injection (`Depends(get_current_active_user)` and `Depends(require_role)`).
2. **Row-Level Security (RLS):** Enabled on PostgreSQL / Supabase tables ensuring patients can only query their own records, and clinicians can only query cases within their authorized facility.
3. **Secret Separation Invariant:**
   - Client-accessible variables must begin with `NEXT_PUBLIC_` and contain zero privileged secrets.
   - Database service-role keys and encryption master keys reside strictly on the server backend within environment variables.

---

## 5. Tamper-Evident Immutable Audit Logging

Every clinical event generates a structured audit log entry in the `audit_events` table:

```json
{
  "audit_id": "aud-6c12e84a-9b10",
  "timestamp": "2026-10-08T01:22:45Z",
  "case_id": "case-9418a0e2-77b3",
  "actor_id": "DOC-OD-4402",
  "actor_role": "ROLE_CLINICIAN",
  "action_type": "VERIFY_AND_MODIFY_PARAMETER",
  "details": {
    "field": "systolic_blood_pressure",
    "previous_value": 110,
    "new_value": 84,
    "justification": "Repeat manual auscultation confirmed severe hypotension"
  },
  "ip_address": "192.168.1.45",
  "hmac_signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

Audit records are append-only. No user, administrator, or database process possesses the authority to delete or modify historical audit rows.
