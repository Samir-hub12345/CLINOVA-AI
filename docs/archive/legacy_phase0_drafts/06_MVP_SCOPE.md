# CLINOVA AI — MVP Scope & Boundary Specification

> **Document ID:** `DOC-06`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Scope Boundary Philosophy

The objective of the CLINOVA AI MVP is to deliver a **fully integrated, production-runnable clinical intelligence prototype** that proves the transition:
$$\text{From Isolated Triage} \longrightarrow \text{To Continuous Care Intelligence}$$

The MVP is not an exhaustive enterprise hospital information system (HIS) with billing, pharmacy inventory, and insurance claims. It is an **adaptive clinical care intelligence and navigation workstation** that demonstrates all 18 BPUT baseline requirements and all 4 CLINOVA innovation pillars operating in a continuous loop.

---

## 2. In-Scope for MVP

### 2.1 Baseline Ingestion & Safety Core
- Multimodal Intake:
  - Text symptom intake with clinical entity extraction.
  - Voice intake recording with local/API transcription and text fallback.
  - Medical report PDF/image upload with OCR parsing and structured extraction.
- Safety & Privacy:
  - Multilingual patient informed consent modal (English, Hindi, Odia).
  - PII scrubbing and automated synthetic pseudonym generation (`SYN-PT-XXXX`).
  - Configurable data retention and audit trail logging.
  - Non-diagnostic advisory headers and clinician sign-off gates.

### 2.2 CareGraph (Patient-Level Intelligence)
- Dynamic physiological state graph tracking symptoms, vitals, labs, and observations over time.
- Delta trajectory calculation ($\Delta R$) detecting rapid deterioration vs stability.
- Evidence provenance tracking (`PATIENT_REPORTED`, `VOICE_TRANSCRIBED`, `OCR_EXTRACTED`, `CLINICIAN_VERIFIED`).
- Evidence uncertainty score ($\mathcal{U}_t$) and protocol-based missing information detection.
- Targeted follow-up question generation to actively reduce uncertainty.

### 2.3 FacilityGraph (Care Feasibility Intelligence)
- Simulated regional network of 5 representative healthcare facilities:
  1. Rural Primary Health Center (Basic outpatient, no imaging, no ICU).
  2. Community Health Center (Basic X-ray, minor OT, 2 maternity beds).
  3. Sub-District Hospital (General surgery, blood storage, basic lab).
  4. District Headquarters Hospital (ICU, CT scan, blood bank, multi-specialty).
  5. Tertiary Medical College (Super-specialty, neurosurgery, cath lab).
- Real-time capacity modeling (bed occupancy, ED wait times, consumable shortages).
- Care feasibility matching matrix for required patient intervention bundles.
- Intelligent referral ranking identifying the safest reachable facility.
- Standardized SBAR referral letter generation.

### 2.4 SignalGraph (System Telemetry & Surge Intelligence)
- Aggregated real-time telemetry from simulated synthetic case encounters.
- Regional syndromic surge detection (e.g., respiratory cluster, acute febrile illness).
- Operational department backlog monitoring and referral pressure heatmap.
- Privacy-preserving aggregate broadcast without patient PII.

### 2.5 Orchestration Engine & Workstation
- Multi-dimensional cognitive synthesis: `CareGraph + Uncertainty + FacilityGraph + SignalGraph`.
- Candidate advisory action recommendations: `ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`.
- Clinician review workstation featuring one-click sign-off, structured override with rationale, and outcome tracking.

---

## 3. Explicit Out-of-Scope (Non-Goals)

To preserve architectural integrity and avoid mission creep, the following capabilities are strictly **out of scope for the MVP**:
- **Autonomous Medical Diagnosis:** No automated generation of authoritative ICD-10 diagnoses without clinician validation.
- **Direct Drug Prescription & Dispensing:** No prescription generation or automated pharmacy fulfillment.
- **Billing, Invoicing & Insurance Claims:** No revenue cycle management or insurance eligibility checking.
- **Hardware Telemetry Integration:** No direct Bluetooth/BLE driver pairing to physical bedside monitors (simulated vitals entry supported).
- **Production EHR Replacement:** No full replacement of legacy hospital EHR systems; operates as an intelligent advisory navigation layer.
- **Real Patient Health Records:** Zero usage of actual unanonymized patient records; 100% synthetic scenarios.

---

## 4. MVP Quality Gates & Acceptance Criteria

| Dimension | MVP Acceptance Threshold | Verification Method |
| :--- | :--- | :--- |
| **API Health & Resilience** | 100% endpoints return `< 200ms` for local queries; graceful fallback on external API failure. | Automated integration test suite (`pytest`) |
| **Frontend Stability** | Zero blocking console errors or unhandled hydration exceptions in Next.js 15. | Browser E2E verification & headless build |
| **Safety Compliance** | Non-diagnostic disclaimer header present on 100% of API responses and UI screens. | Automated header inspection |
| **Clinical Scenarios** | 17 synthetic scenarios (routine, urgent, critical, conflicting, referral, outbreak) execute end-to-end. | Scenario execution suite |
