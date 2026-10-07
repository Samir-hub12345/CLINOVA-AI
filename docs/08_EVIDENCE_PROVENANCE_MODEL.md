# CLINOVA AI — Evidence Provenance & Quality Model

> **Document ID:** `DOC-08`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. The Evidence Provenance Mandate

In safety-critical clinical environments, an isolated numerical or categorical value (e.g., `Heart Rate: 130 bpm`) is dangerous if the clinician cannot see **how** that value was obtained, **who** recorded it, **what tool** extracted it, and **how confident** the system is in its accuracy.

CLINOVA AI establishes a strict **Evidence Provenance & Verification Model**. Every piece of clinical information within CAREGRAPH carries an immutable provenance ledger tracking:
1. **Source Modality** (Voice, OCR, typed text, device, clinical examination)
2. **Confidence / Quality Score** (Algorithmic or measurement certainty)
3. **Temporal Validity** (Exact timestamp and latency)
4. **Verification State** (Unverified AI inference vs. human clinician sign-off)
5. **Responsible Actor** (Patient, nurse, medical officer, system process)
6. **Downstream Decision Linkage** (Which clinical recommendation relied on this value)

---

## 2. Six Supported Evidence Sources

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA EVIDENCE SOURCES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. PATIENT_REPORTED   ──> Subjective narrative entered by patient/caregiver│
│  2. VOICE_TRANSCRIBED  ──> Audio speech processed by local Whisper model     │
│  3. OCR_EXTRACTED      ──> Document text parsed by PaddleOCR / Tesseract    │
│  4. CLINICIAN_VERIFIED ──> Physical exam or confirmed data signed by doctor │
│  5. AI_INFERRED        ──> Extracted entity or clinical signal derived by SLM│
│  6. SYSTEM_DERIVED     ──> Deterministic physiological score (MEWS, shock)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. `PATIENT_REPORTED`:
   - Data origin: Self-entered text or structured questionnaire answers from patient or caregiver.
   - Clinical weight: High subjective importance; requires objective vital sign correlation.
2. `VOICE_TRANSCRIBED`:
   - Data origin: Audio stream recorded at intake and transcribed into text via local Whisper.
   - Clinical weight: Rich conversational context; preserves verbatim patient phrasing; carries acoustic confidence metrics.
3. `OCR_EXTRACTED`:
   - Data origin: Printed lab report, handwritten prescription slip, or discharge summary parsed by local PaddleOCR / Tesseract.
   - Clinical weight: Objective prior documentation; carries character/bounding-box confidence metrics.
4. `CLINICIAN_VERIFIED`:
   - Data origin: Bedside physical examination, verified auscultation, or formal confirmation by a licensed medical officer.
   - Clinical weight: Highest clinical validity; supersedes AI inferences and unverified self-reports.
5. `AI_INFERRED`:
   - Data origin: Clinical concepts, normalized entities, or risk categories inferred by local Qwen3-4B runtime.
   - Clinical weight: Advisory decision-support candidate; strictly unverified until confirmed by clinician.
6. `SYSTEM_DERIVED`:
   - Data origin: Deterministic algorithmic calculations (e.g., Shock Index = HR / SBP, MEWS calculation, wait duration).
   - Clinical weight: Mathematically reproducible; fully deterministic.

---

## 3. Six Evidence States

Every clinical parameter resides in one of six mutually exclusive evidence states:

| Evidence State | Definition | Clinical Implication | Action Required |
| :--- | :--- | :--- | :--- |
| `KNOWN` | High-confidence, verified parameter present in record. | High certainty; eligible for clinical scoring. | Proceed with standard evaluation. |
| `UNKNOWN` | Parameter completely absent or unmeasured. | Clinical gap; could conceal hidden risk. | Flag in uncertainty audit; ask follow-up. |
| `CONFLICTING` | Mutually incompatible values present across sources (e.g., reported duration = 2 days; clinic slip = 2 weeks). | Evidential dissonance; danger of misdiagnosis. | Surface conflict in UI; prompt clinician resolution. |
| `UNRELIABLE` | Value extracted with low algorithmic confidence (< 0.70) or from degraded audio/image. | Cannot be trusted for critical scoring. | Require human re-entry or manual measurement. |
| `VERIFIED` | Value explicitly reviewed and confirmed by licensed doctor. | Medicolegally binding evidence. | Unlocks final disposition sign-off. |
| `INFERRED` | Algorithmic entity candidate derived by AI model. | Advisory only; non-binding. | Highlight in doctor review workspace. |

---

## 4. Evidence Node Data Structure

Every discrete clinical data point is stored as an `EvidenceNode`:

```json
{
  "node_id": "ev-8f92b1a0-4c3e",
  "parameter_name": "systolic_blood_pressure",
  "value": 84,
  "unit": "mmHg",
  "source": "CLINICIAN_VERIFIED",
  "status": "VERIFIED",
  "timestamp": "2026-10-08T01:15:30Z",
  "confidence_score": 1.0,
  "actor": {
    "actor_id": "DOC-OD-4402",
    "role": "ROLE_CLINICIAN",
    "name": "Dr. S. Mohapatra, MO"
  },
  "raw_provenance": {
    "source_modality": "DIGITAL_SPHYGMO",
    "device_model": "Omron Healthcare HBP-1300",
    "previous_value": 90,
    "modification_reason": "Manual repeat verification confirmed severe hypotension"
  },
  "downstream_impact": {
    "affects_risk": true,
    "triggered_alert": "ALERT_HYPOTENSIVE_SHOCK",
    "orchestration_action_generated": "ESCALATE_RESUSCITATION"
  }
}
```

---

## 5. Provenance UI Visualization Invariants

1. **Visual Source Badges:** In all user interfaces, values display clear visual badges denoting their source:
   - 🟢 `[VERIFIED]` — Green border, solid checkmark (Doctor verified)
   - 🔵 `[PATIENT]` — Blue badge (Self-reported)
   - 🟣 `[OCR]` — Purple badge with click-to-view snippet
   - 🟡 `[AI INFERRED]` — Dotted amber border with hover explanation
   - 🔴 `[CONFLICT]` — High-contrast alert badge showing both conflicting values
2. **Provenance Drawer / Hover Card:** Clicking any value immediately opens an evidence inspection drawer displaying:
   - Exact source document image snippet or audio waveform playback.
   - Extraction timestamp and responsible actor.
   - Historical modification log if the value was altered.
3. **Audit Immutability:** No value can be overwritten without preserving the previous value, timestamp, actor ID, and stated modification rationale in the immutable audit log.
