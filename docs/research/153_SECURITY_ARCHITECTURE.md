# CLINOVA AI — Security, Privacy & Zero-Trust Architecture

> **Document ID:** `RES-153`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Cybersecurity, Information Governance & Medical Data Protection Group  

---

## 1. Zero-Trust Healthcare Security Principles

CLINOVA AI is designed according to **Zero-Trust Security Principles** tailored for clinical environments:
1. **Never Trust, Always Verify:** Every HTTP request, whether originating from a local clinic tablet over Wi-Fi or a remote district server, must be explicitly authenticated and authorized.
2. **Least Privilege Enforcement:** Users and internal services operate with the minimal permissions required for their specific clinical role.
3. **Defense in Depth:** Security is enforced across client validation, API gateways, service boundaries, database constraints, and cryptographic ledgers.
4. **Separation of Medical Truth from Administrative Power:** System administrators have zero clinical authority to alter medical facts or sign off on patient care.

---

## 2. Authentication & Session Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AUTHENTICATION & SESSION TOPOLOGY                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ CLOUD / REGIONAL CLUSTER ]                  [ OFFLINE RURAL EDGE NODE ]  │
│  • Supabase Auth (Free Tier)                   • Local JWT Cryptographic Hub│
│  • OAuth 2.0 / Passwordless Email Magic Link   • Offline HMAC-SHA256 Signing│
│  • RS256 Asymmetric Signed JWT                 • Locally Cached Public Keys │
│  • 15-Minute Access Tokens                     • Shift-Based 8-Hour Tokens  │
│  • Secure HTTP-Only Refresh Cookies            • Local PIN / PIN + Card Auth│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### JSON Web Token (JWT) Clinical Claims Structure
Every authenticated session token carries standardized clinical identity claims:
```json
{
  "sub": "usr-550e8400-e29b-41d4-a716-446655440000",
  "email": "dr.patnaik@odishahealth.gov.in",
  "role": "CLINICIAN",
  "facility_id": "fac-dh-koraput-01",
  "nmr_registration_no": "OR-MC-2018-04821",
  "environment": "ENV_GOV_HOSPITAL",
  "iat": 1791456000,
  "exp": 1791459600
}
```

---

## 3. Role-Based Access Control (RBAC) Matrix

CLINOVA enforces four distinct clinical and administrative roles matching the Indian statutory landscape:

| Role Identifier | Real-World Personnel | Allowed Actions | Strictly Blocked Actions |
| :--- | :--- | :--- | :--- |
| **`PATIENT`** | Patient, Caregiver | Submit intake narrative, upload past records, view self triage status, grant/revoke consent | View other patients, modify vitals, access doctor queue |
| **`NURSE`** | Staff Nurse, ANM, ASHA | Record serial vitals, resolve missing data, triage scoring, administer verified orders | Issue medical diagnosis, prescribe drugs, discharge patient, authorize surgery |
| **`CLINICIAN`** | Registered Medical Practitioner (RMP) | Full clinical chart access, conflict adjudication, diagnosis, prescription, admission, discharge | Delete audit logs, bypass retention triggers |
| **`ADMIN`** | Facility IT / Hospital Administrator | Manage facility beds/equipment, configure users, inspect audit integrity | View un-anonymized clinical notes, modify medical dispositions |

### Administrator Clinical Boundary Invariant
**Invariant SEC-1 (No Admin Clinical Authority):** A user with `ADMIN` role can NEVER perform clinical sign-offs, write prescriptions, or override a doctor's decision. System administration is strictly decoupled from medical authority under NMC Regulations 2023.

---

## 4. Secret Management & Browser Key Isolation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECRET BOUNDARY & KEY ISOLATION RULES                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ALLOWED IN BROWSER / CLIENT BUNDLE:                                       │
│   ✅ NEXT_PUBLIC_SUPABASE_ANON_KEY (Public anonymous client key)            │
│   ✅ NEXT_PUBLIC_API_BASE_URL (URL pointing to FastAPI backend)             │
│   ✅ Active user session JWT (Stored in memory / Secure HTTP-Only Cookie)   │
│                                                                             │
│   STRICTLY FORBIDDEN IN BROWSER / CLIENT BUNDLE (Non-Negotiable):           │
│   ❌ SUPABASE_SERVICE_ROLE_KEY (Bypasses all RLS security policies)         │
│   ❌ DATABASE_URL / Master Postgres / SQLite connection strings            │
│   ❌ JWT Secret signing keys (HMAC secrets / Private PEM keys)              │
│   ❌ Local AI model API tokens or administrative passwords                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rule:** Next.js Server Components and backend FastAPI endpoints act as security firewalls. Any operation requiring elevated permissions executes on the server; service-role credentials NEVER cross the network to client browsers.

---

## 5. PII / PHI Isolation & In-Flight Redaction Proxy

To ensure patient privacy during intake and AI processing:
1. **Synthetic Tokenization:** As soon as an intake is submitted, direct identifiers (name, phone, government IDs) are tokenized into a synthetic anonymous identifier (`SYN-PT-1042`).
2. **In-Flight Regex Redaction:** Before any unstructured narrative text is sent to the local SLM adapter, the text passes through the `InFlightRedactionService`:
   - Redacts 10-digit Indian mobile numbers (`r"\b[6-9]\d{9}\b"` $\to$ `[PHONE_REDACTED]`)
   - Redacts 12-digit Aadhaar patterns (`r"\b\d{4}\s\d{4}\s\d{4}\b"` $\to$ `[ID_REDACTED]`)
   - Redacts personal email addresses (`r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"` $\to$ `[EMAIL_REDACTED]`)
3. **No External AI Leakage:** Because the SLM (Qwen3-4B) runs on the local clinic server via loopback IPC (`127.0.0.1`), zero patient telemetry or clinical notes ever leave the clinic perimeter to external third-party cloud providers.

---

## 6. Break-Glass Protocol: Emergency Access with Forensic Auditing

In acute trauma resuscitation, an unconscious patient may arrive without consent, or an emergency clinician may need urgent access to a patient record registered under another department or facility.

### The Break-Glass Architectural Flow
1. **Trigger:** The clinician clicks the `BREAK-GLASS EMERGENCY ACCESS` button on the Doctor Workbench.
2. **Immediate Unblocking:** Access to the patient's full clinical history and past medical records is granted immediately without administrative delay (*Paschim Banga* doctrine compliance).
3. **Cryptographic Logging:** In the same database transaction:
   - Writes a high-priority row to `audit_logs` capturing `actor_id`, `patient_id`, `timestamp`, `ip_address`, and mandatory clinician rationale.
   - Computes Section 63 BSA cryptographic Merkle hash chaining.
   - Emits an automated security alert notification to the Hospital Information Security Officer (HISO) for post-access verification within 24 hours.
