# CLINOVA AI — Clinical Documentation & Summarization Audit

> **Document ID:** `RES-04`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary

The clinical documentation technology landscape has expanded rapidly with the emergence of generative AI "ambient clinical scribes." Platforms such as **Nuance DAX Copilot (Microsoft)**, **Abridge**, **Ambience Healthcare**, **Suki AI**, and **Nabla Copilot** have demonstrated massive success in reducing physician administrative burden ("pajama time").

However, an adversarial architectural audit reveals that **over 90% of existing commercial AI scribes terminate at passive EHR documentation**. Their outputs are formatted text blobs (SOAP notes) designed for billing and medico-legal archival rather than active, executable state engines that drive downstream clinical actions, facility routing, or patient safety monitoring.

---

## 2. Comparative Audit of Clinical Documentation Systems

| Platform & Vendor | Primary Architecture | Ingestion Modalities | Primary Output | Evidence Provenance Depth | Uncertainty Representation | Downstream Action Triggering? | Resource / Facility Aware? | Outcome Tracking? | Licensing / Cost Model | Evidence Grade |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Nuance DAX Copilot** *(Microsoft)* | Ambient conversational speech-to-text + Azure OpenAI LLM summarization. | Conversational English/Spanish audio; microphone stream. | Structured SOAP note draft; patient after-visit summary. | **Low.** Generated text notes do not link back to exact acoustic timecodes for clinicians. | **None.** Produces polished narrative notes; omits unmentioned data without flagging gaps. | **Minimal.** Generates referral draft letters and ICD-10/CPT billing codes; no care orchestration. | **No.** Blind to live bed occupancy, staffing, or hospital queues. | **No.** Terminates upon note sign-off in Epic/Cerner. | Proprietary enterprise subscription ($300–$800 / physician / month). | **Grade B** (Microsoft Health Documentation, 2024) |
| **Abridge** | Proprietary clinical LLM trained on massive audio-note datasets. | Ambient physician-patient conversational audio. | Formatted clinical progress notes; patient-facing summaries. | **High (Direct Auditing).** Clicking generated note text highlights exact audio transcript snippet. | **Partial.** Flags conversational ambiguities, but lacks explicit clinical uncertainty state. | **Moderate.** Pushes structured note sections into EHR discrete fields; assists with coding. | **No.** Operates as an encounter-level documentation layer; no facility telemetry. | **No.** No post-encounter outcome tracking. | Proprietary enterprise contract with large health systems (Epic integration). | **Grade B** (Abridge Clinical Publications & KLAS, 2024) |
| **Ambience Healthcare** | "Chart-aware" LLM operating across historical records and real-time audio. | Ambient audio + historical EHR chart (prior labs, notes, problems). | Comprehensive specialty SOAP notes; after-visit summaries; referral letters. | **Moderate.** Surfaces historical chart references alongside ambient conversation. | **Low.** Focuses on maximizing documentation completeness for revenue integrity. | **Moderate.** Drafts orders and referrals, but requires physician to manually approve in EHR. | **No.** Does not evaluate real-time facility equipment, blood bank stock, or ICU capacity. | **No.** Terminates at encounter discharge. | Proprietary enterprise SaaS (Tiered per-clinician pricing). | **Grade B** (Ambience Healthcare Architecture Brief, 2024) |
| **Suki AI** | Voice assistant with ambient listening + EHR voice dictation. | Spoken commands, ambient conversation, dictation snippets. | Clinical progress notes, ICD-10 codes, EHR command execution. | **Low.** Standard conversational text-to-note mapping. | **None.** No formal uncertainty or missing-evidence quantification. | **Low.** Limited to executing basic voice commands inside EHR (e.g., "retrieve vitals"). | **No.** No awareness of facility resources or network capacity. | **No.** Terminates at note submission. | Proprietary subscription ($199–$399 / clinician / month). | **Grade B** (Suki AI Vendor Documentation, 2023) |
| **Nabla Copilot** | Lightweight ambient AI scribe operating in browser extension. | Ambient audio via web browser microphone. | Structured clinical notes; email summaries for patients. | **Low.** Text summary generated directly from ephemeral audio. | **None.** Summarizes what was spoken; does not analyze what critical tests were omitted. | **None.** Pure documentation generator; zero workflow integration. | **No.** Completely decoupled from hospital infrastructure. | **No.** Zero outcome connectivity. | Freemium / Paid SaaS ($119 / month). | **Grade B** (Nabla Product Architecture, 2023) |
| **AWS HealthScribe** | Managed generative AI service for healthcare speech-to-text and summarization. | Audio recordings of clinical dialogues via AWS SDK. | Transcript segments, clinical section summaries, concept extraction. | **High.** Provides two-way references linking summary text to raw transcript sentences. | **Low.** Leaves uncertainty interpretation to downstream developer applications. | **None (Developer SDK).** Pure infrastructure building block. | **No.** Developer must implement all facility and workflow logic. | **No.** No native outcome loops. | AWS usage-based API pricing ($0.05+ per audio minute). | **Grade B** (AWS Architecture Whitepaper, 2023) |

---

## 3. The Core Dilemma: Documentation vs Action

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 COMMERCIAL AI SCRIBES vs CLINOVA CAREGRAPH                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EXISTING AI SCRIBES (DAX, Abridge, Suki, Nabla):                           │
│  Ambient Audio ──> LLM Summarization ──> Static SOAP Note ──> EHR Archive    │
│  (The note sits passively in the chart. Nothing active happens.)            │
│                                                                             │
│  CLINOVA AI ARCHITECTURE:                                                   │
│  Multimodal Intake (Voice, OCR, Vitals)                                     │
│         │                                                                   │
│         ▼                                                                   │
│  Active State Engine (CAREGRAPH)                                            │
│         │                                                                   │
│         ├── Tracks Evidence Provenance & Confidence                         │
│         ├── Models Explicit Uncertainty (Known vs Unknown)                  │
│         ├── Synthesizes Facility Capability (FACILITYGRAPH)                 │
│         └── Drives Candidate Actions:                                       │
│             [ASK] ──> [VERIFY] ──> [CONTINUE] ──> [OBSERVE] ──> [REFER]     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Passive Documentation vs Active State
Existing systems treat documentation as an endpoint. Once the note is generated and signed, the AI's role terminates. If the patient sits in the hallway and deteriorates, the generated note provides zero alert.
- **CLINOVA Difference:** The intake summary is merely one projection of an active state machine (`CAREGRAPH`). The state persists, monitoring wait duration, serial vital trends, and capability gaps.

### 3.2 Evidence Provenance: The Black-Box Problem
While **Abridge** and **AWS HealthScribe** have introduced commendable audio-to-text phrase matching, they remain limited to acoustic audio. In Indian public healthcare, evidence arrives across multiple disjointed modalities: handwritten prescription slips, crumpled lab sheets, patient verbal complaints in regional dialects (Odia/Hindi), and bedside vital monitors.
- **CLINOVA Difference:** `EvidenceNode` tracks provenance across all modalities (`VOICE`, `OCR`, `PATIENT_REPORTED`, `CLINICIAN_VERIFIED`), storing bounding boxes, audio waveform segments, and source confidence.

### 3.3 The Missing Uncertainty Layer
Commercial scribes are prompt-engineered to generate fluent, authoritative SOAP notes. In doing so, they often commit **the sin of silent omission**: if the patient did not mention allergies, the AI simply omits the allergy section or writes "No allergies reported," creating dangerous false confidence.
- **CLINOVA Difference:** The system separates what is confirmed from what is unasked. Unrecorded critical qualifiers are explicitly categorized as `UNKNOWN`, preventing diagnostic premature closure.
