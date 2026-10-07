# CLINOVA AI — CAREGRAPH Detailed Technical Specification

> **Document ID:** `DOC-08`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Architectural Role & Core Purpose

**CareGraph** is the patient-level clinical intelligence engine of CLINOVA AI. It models the patient's physiological trajectory over time as a directed, typed, multi-attribute knowledge graph.

CareGraph answers the fundamental clinical question:
$$\mathbf{What\ is\ happening\ to\ this\ patient\ right\ now?}$$

Unlike electronic health records (EHRs) that store discrete tables of historical encounters, CareGraph computes active clinical states, detects physiological deterioration in real time, quantifies diagnostic uncertainty, and exposes the exact evidentiary provenance of every clinical observation.

---

## 2. Graph Schema & Node Typology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CAREGRAPH NODE & EDGE SCHEMA                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│               [ PatientProfile Node ]                                       │
│                         │                                                   │
│                         │ (HAS_EPISODE)                                     │
│                         ▼                                                   │
│                  [ Encounter Node ] ──(AT_TIME)──> [ Timeline Node ]        │
│                   │         │                             ▲                 │
│         (REPORTS) │         │ (EXHIBITS)                  │ (RECORDED_AT)   │
│                   ▼         ▼                             │                 │
│         [ Symptom Node ]  [ VitalSign Node ] ─────────────┘                 │
│                 │                 │                                         │
│   (EXTRACTED_BY)│                 │ (DERIVED_FROM)                          │
│                 ▼                 ▼                                         │
│            [ Evidence / Document / Audio Node ]                             │
│                         ▲                                                   │
│                         │ (VERIFIED_BY)                                     │
│            [ Clinician Verification Node ]                                  │
│                         │                                                   │
│                         ▼ (AUTHORIZES)                                      │
│                [ Clinical Decision Node ]                                   │
│                         │                                                   │
│                         ▼ (YIELDS)                                          │
│                 [ Care Action & Outcome Node ]                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Node Definitions

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class ProvenanceType(str, Enum):
    PATIENT_REPORTED = "PATIENT_REPORTED"
    VOICE_TRANSCRIBED = "VOICE_TRANSCRIBED"
    OCR_EXTRACTED = "OCR_EXTRACTED"
    CLINICIAN_VERIFIED = "CLINICIAN_VERIFIED"
    AI_INFERRED = "AI_INFERRED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"

class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    CONFIRMED = "CONFIRMED"
    MODIFIED = "MODIFIED"
    DISPUTED = "DISPUTED"

class CareGraphNode(BaseModel):
    node_id: str
    node_type: str # 'PATIENT', 'SYMPTOM', 'VITAL', 'LAB', 'TIMELINE', 'EVIDENCE', 'DECISION'
    timestamp: datetime
    data: Dict[str, Any]
    provenance: ProvenanceType
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by: Optional[str] = None
```

---

## 3. Dynamic Trajectory & Deterioration Engine

CareGraph evaluates physiological trajectory whenever new vitals or symptoms are appended:

### 3.1 Acuity Score Formulation ($R_t$)
The composite acuity score is grounded in the standardized **National Early Warning Score 2 (NEWS2)** framework adapted for emergency triage:
$$R_t = \sum_{i} \text{Weight}(v_i) + \sum_{j} \text{RedFlagPenalty}(r_j)$$
Where physiological parameters ($v_i$) include:
- Respiration Rate (bpm)
- SpO2 Oxygen Saturation ($\%$) and Supplemental Oxygen requirement
- Systolic Blood Pressure (mmHg)
- Pulse Rate (bpm)
- Level of Consciousness (AVPU / GCS)
- Temperature ($^\circ\text{C}$)

### 3.2 Dynamic Trajectory Slope ($\Delta R$)
$$\Delta R = \frac{R(t_2) - R(t_1)}{t_2 - t_1} \quad \left[\text{points / hour}\right]$$
- **Rapid Deterioration ($\Delta R \ge +1.5/\text{hr}$):** Generates high-priority audible/visual alert; triggers immediate `ESCALATE` recommendation.
- **Gradual Deterioration ($0.5 \le \Delta R < 1.5/\text{hr}$):** Recommends scheduled serial observation (`OBSERVE` at 15-minute intervals).
- **Physiologically Stable ($-0.5 < \Delta R < 0.5/\text{hr}$):** Recommends maintenance on current pathway (`CONTINUE`).
- **Improving ($\Delta R \le -0.5/\text{hr}$):** Confirms positive clinical response to interventions.

---

## 4. Evidence Uncertainty Engine ($\mathcal{U}_t$)

Uncertainty is treated as an active clinical parameter rather than missing telemetry:
$$\mathcal{U}_t = 1.0 - \left( 0.40 \cdot \mathcal{C}_{\text{data}} + 0.35 \cdot \overline{\mathcal{Q}}_{\text{evidence}} + 0.25 \cdot \mathcal{V}_{\text{clinician}} \right)$$

1. **Protocol Completeness ($\mathcal{C}_{\text{data}}$):**
   $$\mathcal{C}_{\text{data}} = \frac{|\text{CapturedProtocolParameters}|}{|\text{RequiredProtocolParameters}|}$$
   Example: If a patient presents with acute chest pain, the required protocol includes: *onset duration, radiation, character, SpO2, BP, heart rate, ECG, troponin*. If only chest pain and SpO2 are present, $\mathcal{C}_{\text{data}} = 2/8 = 0.25$.

2. **Evidence Quality ($\overline{\mathcal{Q}}_{\text{evidence}}$):**
   Mean cryptographic and extraction confidence of raw data sources (OCR text recognition score, speech transcription confidence).

3. **Clinician Verification Ratio ($\mathcal{V}_{\text{clinician}}$):**
   $$\mathcal{V}_{\text{clinician}} = \frac{|\text{ClinicianVerifiedNodes}|}{|\text{TotalNodes}|}$$

### 4.1 Missing Information & Conflict Resolution
When $\mathcal{U}_t > 0.40$, CareGraph generates:
- **Missing Information Chips:** Highlighting critical absent parameters (e.g., "Missing: Allergy Status", "Missing: Chest Pain Duration").
- **Targeted Follow-Up Questions:** Specific prompts to be answered by the triage worker or patient.
- **Conflict Badges:** Generated when two nodes contradict (e.g., Patient reported "no fever" but vital sign thermometer reading is $39.4^\circ\text{C}$).

---

## 5. Downstream Integration

CareGraph outputs a clean, immutable state snapshot to the **Orchestration Engine** at every state change, enabling context-aware decision support that evolves with the patient.
