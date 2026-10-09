# CLINOVA AI — Provenance Permission & Access Control Model

> **Document ID:** `RES-128`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Scope & DPDP Act Privacy Governance

Access to clinical provenance data is governed by strict statutory, professional, and ethical boundaries in India:
- **Digital Personal Data Protection (DPDP) Act, 2023:** Enforces the principle of **Purpose Limitation** and data minimization. Patients (Data Principals) have the right to access their processed personal data, but non-clinical users must not have unrestricted access to raw audio or sensitive clinical diagnostic hypotheses.
- **National Medical Commission (RMP) Regulations, 2023 (Regulation 27):** Restricts the legal authority to diagnose, verify clinical conditions, and adjudicate medical conflicts exclusively to Registered Medical Practitioners.

### Architectural Boundary Condition
This document formalizes the **Conceptual Permission & Access Control Matrix**. It does **NOT** implement role-based access control (RBAC) middleware, OAuth policies, or backend authorization code in `backend/app`.

---

## 2. Ten Canonical Provenance Permission Actions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   TEN CANONICAL PROVENANCE ACTIONS                          │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ Action Key           │ Semantic Scope & Operational Capability              │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ 1. VIEW_SOURCE       │ View origin metadata, actor, timestamp, device       │
│ 2. VIEW_EXTRACTED    │ Read structured clinical observations, vitals, labs  │
│ 3. EDIT_EXTRACTED    │ Correct unverified OCR text or audio transcripts     │
│ 4. VERIFY            │ Attest datum as STAFF_VERIFIED or CLINICIAN_APPROVED │
│ 5. REJECT            │ Dismiss erroneous OCR boxes or AI inferences         │
│ 6. RESOLVE_CONFLICT  │ Adjudicate discordant values (e.g. SBP 120 vs 195)   │
│ 7. VIEW_AI_INFERENCE │ View advisory differential hypotheses & red-flags    │
│ 8. VIEW_RAW_MEDIA    │ Listen to raw audio files; view high-res scans       │
│ 9. EXPORT_PROVENANCE │ Export Section 63 BSA legal audit certificate bundle │
│ 10. VIEW_AUDIT       │ Inspect cryptographic Merkle hash ledger & logs      │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 3. Nine Canonical Actor Roles

1. **Patient:** The individual receiving care (Data Principal under DPDP Act).
2. **Caregiver:** Authorized family proxy or guardian managing patient affairs.
3. **Nurse:** Licensed Staff Nurse or Auxiliary Nurse Midwife (ANM).
4. **Health Worker:** Accredited Social Health Activist (ASHA) or community volunteer.
5. **Clinician (RMP):** Licensed physician registered on the National Medical Register.
6. **Referral Staff:** Ambulance paramedic or inter-facility transfer coordinator.
7. **Facility Admin:** Hospital Medical Records Officer (MRO) or Medical Superintendent.
8. **System Admin:** Platform infrastructure engineer managing edge nodes and cloud hubs.
9. **Researcher:** Academic epidemiologist conducting public health surveillance.

---

## 4. Comprehensive Provenance Permission Matrix

| Role | `VIEW_SOURCE` | `VIEW_EXTRACTED` | `EDIT_EXTRACTED` | `VERIFY` | `REJECT` | `RESOLVE_CONFLICT` | `VIEW_AI_INFERENCE` | `VIEW_RAW_MEDIA` | `EXPORT_PROVENANCE` | `VIEW_AUDIT` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Patient** | Allowed (Self) | Allowed (Self) | Prohibited | Prohibited | Prohibited | Prohibited | Prohibited (1) | Allowed (Self) | Allowed (Self) | Prohibited |
| **Caregiver** | Allowed (Proxy)| Allowed (Proxy)| Prohibited | Prohibited | Prohibited | Prohibited | Prohibited (1) | Allowed (Proxy)| Allowed (Proxy)| Prohibited |
| **Health Worker (ASHA)**| Allowed | Allowed | Allowed (Draft)| Prohibited | Prohibited | Prohibited | Advisory Only | Allowed | Prohibited | Prohibited |
| **Staff Nurse** | Allowed | Allowed | Allowed (Triage)| Staff Tier | Allowed (OCR) | Prohibited (2) | Advisory Only | Allowed | Prohibited | Prohibited |
| **Clinician (RMP)**| **FULL** | **FULL** | **FULL** | **FULL** | **FULL** | **EXCLUSIVE** | **FULL** | **FULL** | **FULL** | Allowed |
| **Referral Staff** | Allowed | Allowed | Prohibited | Prohibited | Prohibited | Prohibited | SBAR Summary | Transit Media | SBAR Export | Prohibited |
| **Facility Admin** | Metadata Only | Summary Only | Prohibited | Prohibited | Prohibited | Prohibited | Prohibited | Redacted PII | Court Pack Only| Allowed |
| **System Admin** | System Logs | Prohibited (3) | Prohibited | Prohibited | Prohibited | Prohibited | Prohibited | Prohibited (3) | Technical Hash | **FULL** |
| **Researcher** | De-identified | De-identified | Prohibited | Prohibited | Prohibited | Prohibited | De-identified | Prohibited (4) | De-identified | Prohibited |

### Critical Matrix Annotations:
1. **Patient / Caregiver AI Suppression:** Patients see verified clinician instructions and finalized discharge summaries; raw probabilistic AI differential hypotheses (e.g. *"Candidate 1: Pancreatic Adenocarcinoma (22%)"*) are suppressed to prevent ungrounded catastrophic panic before physician counseling.
2. **Nurse Conflict Resolution Prohibition:** Frontline nurses cannot resolve conflicting physiological measurements; only an RMP holds statutory authority to choose the active clinical value.
3. **System Admin Privacy Wall:** System administrators maintain technical database performance but are air-gapped from viewing unencrypted raw clinical media or patient health payloads (DPDP Act compliance).
4. **Researcher Media Prohibition:** De-identified epidemiological research datasets contain structured codes (LOINC, SNOMED CT) but strictly exclude raw vernacular audio or facial document scans to prevent biometric re-identification.

---

## 5. Emergency Break-Glass Access Controls

In acute resuscitation scenarios (Phase 5 State $S22: \text{STATE\_EMERGENCY\_ACTIVE}$):
- If an unconscious trauma victim arrives without registered identity or pre-existing consent, an attending emergency clinician or triage nurse may trigger **Emergency Break-Glass Access**.
- **Operational Effect:** Instantly unlocks `VIEW_EXTRACTED` and `VIEW_RAW_MEDIA` for all historical regional records linked to biometric or emergency tokens.
- **Audit Requirement:** The action is permanently logged in `privacy_break_glass_audits` capturing the clinician’s identity, exact timestamp, and mandatory statutory justification citing Section 7 of the DPDP Act, 2023 (Medical Emergency Implied Consent Exception).

This permission model ensures that clinical care flows without life-threatening delays while safeguarding legal compliance, professional monopolies, and patient privacy.
