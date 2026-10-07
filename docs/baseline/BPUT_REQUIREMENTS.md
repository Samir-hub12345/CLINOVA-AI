# CLINOVA AI — Baseline Operational Requirements (BPUT Standard)

## 1. Executive Summary
While the primary architectural innovation of CLINOVA AI is **Continuous Care Intelligence** (CareGraph, FacilityGraph, SignalGraph, and the Orchestration Engine), the application integrates all mandatory baseline operational capabilities to support field clinical operations.

---

## 2. Baseline Requirement Mapping

| # | Requirement | Specification & Purpose | Continuous Care Mapping |
|:---|:---|:---|:---|
| 1 | **Text Symptom Intake** | Structured patient narrative entry with autosizing textarea, clinical symptom tagging, and duration capture. | Ingests into `CareGraph` as self-reported observations. |
| 2 | **Voice Symptom Intake** | Speech audio capture with multi-state recording interface (idle, recording, transcribing, verified). | Audio converted to transcript and stored as provenance source in `CareGraph`. |
| 3 | **Medical Report Extraction** | Automated parsing of laboratory documents (e.g. Complete Blood Count - CBC: Hb, TLC, Platelets). | Discrete lab parameters populate quantitative nodes in `CareGraph`. |
| 4 | **Timeline Summarization** | Chronological ordering of symptom onset, peak, previous interventions, and current acuity. | Provides temporal context in `CareGraph` longitudinal views. |
| 5 | **Missing-Information Detection** | Algorithmic scanning for missing critical inputs (e.g. pain radiation, fever duration, allergy history). | Exposed as evidence uncertainty metrics within `CareGraph`. |
| 6 | **Follow-up Questions** | Generation of focused clarifying questions to close identified clinical information gaps. | Orchestration Engine generates gap-closure prompts. |
| 7 | **Optical Character Recognition (OCR)** | Computer vision extraction of printed and scanned medical records and prescription slips. | Ingestion adapter feeding report extraction pipeline. |
| 8 | **Language / Translation Support** | Vernacular support (Odia, Hindi, English) with bi-directional normalization. | Normalizes regional idioms into standardized clinical descriptors. |
| 9 | **Risk-Category Support** | Transparent risk bands: Emergency / Red Flag, Urgent Priority, Routine Assessment. | Informs Orchestration Engine priority calculations. |
| 10 | **Queue Prioritization** | Dynamic facility queue ordering based on clinical risk score and wait duration. | Integrated with `FacilityGraph` capacity and operational queue metrics. |
| 11 | **Referral Preparation** | Automated synthesis of structured inter-facility transfer documentation with capability justification. | Prepared by Orchestration Engine when `FacilityGraph` feasibility fails. |
| 12 | **Reviewer Dashboard** | One-screen clinical review workstation displaying synthesized notes, provenance, and override controls. | Primary clinician interface for human-in-the-loop validation. |
| 13 | **Consent Capture** | Explicit digital/verbal consent recorded prior to intake and data processing. | Gatekeeper for all case ingestion pipelines. |
| 14 | **Anonymization Layer** | Regex & NLP scrubbing of phone numbers, emails, government IDs, and direct identifiers. | Assigns synthetic identifiers before any analytical processing. |
| 15 | **Minimal Data Retention** | Automated 24-hour retention policy with secure ephemeral disposal of transient files. | Compliance safeguard ensuring zero long-term data liability. |
| 16 | **Auditability** | Tamper-evident logging of intake timestamps, rule evaluations, model inferences, and clinician overrides. | Persistent audit trail for medicolegal governance. |
| 17 | **Qualified Human Handoff** | Enforced clinical sign-off gate blocking any autonomous routing or discharge without clinician confirmation. | Non-negotiable architectural invariant. |
