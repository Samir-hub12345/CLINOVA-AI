# CLINOVA AI — Consent, Privacy & DPDP Compliance Data Model

> **Document ID:** `RES-97`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Statutory Foundations: India DPDP Act 2023 & Emergency Exceptions

The collection and processing of health data in India is governed by the **Digital Personal Data Protection (DPDP) Act, 2023**:
1. **Section 6 (Notice and Explicit Consent):** Data fiduciaries must present clear, vernacular notice and capture unbundled, unambiguous consent before processing personal data.
2. **Section 9 (Processing of Children's Data):** Verifiable parental or legal guardian consent is mandatory for minors ($< 18$ years of age).
3. **Section 7 (Certain Legitimate Uses / Emergency Medical Waiver):** Processing personal data is legally permitted without prior consent in situations of medical emergency involving a threat to the life or immediate health of the individual.

CLINOVA AI formalizes the **Consent & Privacy Model**, providing a strict air-gap between identifiable administrative demographics and clinical AI processing, alongside auditable break-glass emergency consent.

---

## 2. Five Canonical Consent Types & Granular Scope

| Consent Type | Processing Scope | Allowed Grantors | Revocation Behavior |
| :--- | :--- | :--- | :--- |
| `INTAKE` | Basic demographic registration and vital sign measurement. | `PATIENT`, `CAREGIVER`, `EMERGENCY_IMPLIED` | Stops encounter immediately. |
| `DATA_PROCESSING` | SLM transcription, entity extraction, and clinical decision support. | `PATIENT`, `CAREGIVER`, `EMERGENCY_IMPLIED` | Restricts system to manual non-AI mode. |
| `TELECONSULT` | Transmission of clinical data to remote tele-consultant. | `PATIENT`, `CAREGIVER` | Limits care to local staff. |
| `REFERRAL` | Transmission of digital SBAR referral dossier to external hospital. | `PATIENT`, `CAREGIVER`, `EMERGENCY_IMPLIED` | Prevents digital dossier dispatch. |
| `PROCEDURE` | High-risk invasive procedure or Operation Theatre surgical consent. | `PATIENT`, `LEGAL_GUARDIAN` | Hard-blocks surgical booking. |

---

## 3. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONSENT & PRIVACY SCHEMA                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── patient_consents (consent_id PK, case_id FK)                         │
│    │     └── [Consent Type, Granted By, Language, Break-Glass Flag, Digital]│
│    │                                                                        │
│    └── privacy_break_glass_audits (audit_id PK, case_id FK)                 │
│          └── [Clinician ID, Emergency Justification, Timestamp, Terminal IP]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Relational DDL Specification (PostgreSQL / Supabase)

### 4.1 `patient_consents` Table

```sql
CREATE TABLE patient_consents (
    consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    patient_id UUID REFERENCES patients(id) ON DELETE RESTRICT,
    consent_type VARCHAR(32) NOT NULL CHECK (consent_type IN (
        'INTAKE', 'DATA_PROCESSING', 'TELECONSULT', 'REFERRAL', 'PROCEDURE'
    )),
    granted_by VARCHAR(32) NOT NULL CHECK (granted_by IN (
        'PATIENT', 'CAREGIVER', 'LEGAL_GUARDIAN', 'EMERGENCY_IMPLIED'
    )),
    grantor_name VARCHAR(128),
    grantor_relationship VARCHAR(64), -- 'SELF', 'FATHER', 'SPOUSE', 'ATTENDING_PHYSICIAN'
    notice_language VARCHAR(16) NOT NULL DEFAULT 'or', -- Odia, Hindi, English
    signature_mode VARCHAR(32) NOT NULL DEFAULT 'DIGITAL_CHECKBOX'
        CHECK (signature_mode IN ('DIGITAL_CHECKBOX', 'BIOMETRIC', 'VERBAL_WITNESSED', 'EMERGENCY_STATUTORY')),
    witness_name VARCHAR(128),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,
    emergency_break_glass_flag BOOLEAN NOT NULL DEFAULT FALSE,
    emergency_justification TEXT,
    CONSTRAINT uq_case_consent_type UNIQUE (case_id, consent_type)
);

CREATE INDEX ix_consents_case ON patient_consents(case_id);
```

### 4.2 `privacy_break_glass_audits` Table

```sql
CREATE TABLE privacy_break_glass_audits (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    actor_id UUID NOT NULL REFERENCES users(id),
    actor_role VARCHAR(32) NOT NULL,
    emergency_justification TEXT NOT NULL,
    patient_presenting_condition VARCHAR(128) NOT NULL, -- e.g., 'CARDIAC_ARREST_UNRESPONSIVE'
    terminal_ip_address VARCHAR(45) NOT NULL,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_break_glass_case ON privacy_break_glass_audits(case_id);
```

---

## 5. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE patient_consents (
    consent_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    patient_id TEXT REFERENCES patients(id) ON DELETE RESTRICT,
    consent_type TEXT NOT NULL CHECK (consent_type IN ('INTAKE', 'DATA_PROCESSING', 'TELECONSULT', 'REFERRAL', 'PROCEDURE')),
    granted_by TEXT NOT NULL CHECK (granted_by IN ('PATIENT', 'CAREGIVER', 'LEGAL_GUARDIAN', 'EMERGENCY_IMPLIED')),
    grantor_name TEXT,
    grantor_relationship TEXT,
    notice_language TEXT NOT NULL DEFAULT 'or',
    signature_mode TEXT NOT NULL DEFAULT 'DIGITAL_CHECKBOX' CHECK (signature_mode IN ('DIGITAL_CHECKBOX', 'BIOMETRIC', 'VERBAL_WITNESSED', 'EMERGENCY_STATUTORY')),
    witness_name TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    granted_at TEXT NOT NULL,
    revoked_at TEXT,
    revocation_reason TEXT,
    emergency_break_glass_flag INTEGER NOT NULL DEFAULT 0 CHECK (emergency_break_glass_flag IN (0, 1)),
    emergency_justification TEXT,
    CONSTRAINT uq_case_consent_type UNIQUE (case_id, consent_type)
);

CREATE TABLE privacy_break_glass_audits (
    audit_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    actor_id TEXT NOT NULL REFERENCES users(id),
    actor_role TEXT NOT NULL,
    emergency_justification TEXT NOT NULL,
    patient_presenting_condition TEXT NOT NULL,
    terminal_ip_address TEXT NOT NULL,
    triggered_at TEXT NOT NULL
);
```

---

## 6. Invariants Governing Consent & Privacy

$$\begin{aligned}
\mathbf{Inv\ CONS\text{-}1} &: \quad \forall c \in \text{Cases}, \quad \text{Cases}(c).\text{intake\_mode} = \text{'REGULAR'} \\
& \quad \implies \exists s \in \text{Consents}(c) \text{ s.t. } (s.\text{consent\_type} = \text{'INTAKE'} \land s.\text{is\_active} = \text{TRUE}) \\
\mathbf{Inv\ CONS\text{-}2} &: \quad s.\text{emergency\_break\_glass\_flag} = \text{TRUE} \\
& \quad \implies \left( s.\text{granted\_by} = \text{'EMERGENCY\_IMPLIED'} \land s.\text{emergency\_justification} \neq \text{NULL} \right) \\
\mathbf{Inv\ CONS\text{-}3} &: \quad \text{DPDP Demographic Air-Gap: AI inferencing payloads must NOT include direct patient identifiers.}
\end{aligned}$$
