# CLINOVA AI — AI Result Lifecycle & Clinician Modification Ledger

> **Document ID:** `RES-213`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Medicolegal Systems & Governance Group  

---

## 1. The Eight Canonical Lifecycle States

An AI-generated clinical artifact exists within an immutable eight-stage lifecycle. Under no circumstance does an inference transition to clinical truth without explicit physician sign-off.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AI ARTIFACT LIFECYCLE STATES                          │
├────────────────────┬────────────────────────────────────────────────────────┤
│ 1. GENERATED       │ Raw completion emitted by local language model.        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 2. VALIDATED       │ Passed all deterministic schema, range, and action     │
│                    │ validation checks. Safe for UI rendering.              │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 3. REVIEW_PENDING  │ Rendered on Doctor Workbench with advisory badge.      │
│                    │ Awaiting human physician review.                       │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 4. ACCEPTED        │ Clinician reviewed and approved the suggestion as-is.  │
│                    │ Promoted to formal draft clinical order/note.          │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 5. MODIFIED        │ Clinician edited or adjusted the suggestion. Both      │
│                    │ original AI text and doctor's edits preserved.         │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 6. REJECTED        │ Clinician explicitly dismissed the suggestion. Removed │
│                    │ from primary clinical flow; preserved for audit.       │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 7. SUPERSEDED      │ Replaced by a more recent inference due to fresh case   │
│                    │ evidence arrivals.                                     │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 8. EXPIRED         │ Stale inference whose time-to-live expired without     │
│                    │ human action.                                          │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. State Transition Dynamics

```
      [ LOCAL MODEL ]
            │
            ▼
      [ GENERATED ] ──(Fails Validation)──► [ REJECTED (Automated) ]
            │
      (Passes Validation)
            ▼
      [ VALIDATED ]
            │
            ▼
      [ REVIEW_PENDING ] ──(Evidence Changes)──► [ SUPERSEDED ]
            │
            ├────────────── Clinician Accepts As-Is ────────► [ ACCEPTED ]
            │
            ├────────────── Clinician Overrides/Edits ──────► [ MODIFIED ]
            │
            └────────────── Clinician Dismisses ────────────► [ REJECTED (Human) ]
```

---

## 3. The Clinician Modification Ledger Principle

$$\mathbf{NEVER\ OVERWRITE\ OR\ DELETE\ ORIGINAL\ AI\ RECOMMENDATIONS}$$

When a Registered Medical Practitioner (RMP) overrides, edits, or rejects an AI recommendation:
1. The original AI payload, confidence score, and prompt version are **NEVER deleted or updated in-place**.
2. An immutable ledger entry is written to `clinician_modifications`:
   - `original_ai_payload`: The exact machine suggestion.
   - `clinician_replacement_value`: The actual order/diagnosis written by the doctor.
   - `override_reason`: Structured clinical rationale.
   - `clinician_id`: Attending physician's UUID and National Medical Register (NMR) ID.
   - `timestamp`: UTC timestamp of the override.

```python
class ClinicianOverrideRecord(BaseModel):
    original_ai_payload: Dict[str, Any]
    clinician_replacement_value: Optional[Dict[str, Any]]
    action: AIResultLifecycle           # ACCEPTED, MODIFIED, or REJECTED
    override_reason: str
    clinician_id: str
    recorded_at: str                    # ISO-8601 UTC
```

This ledger provides complete medicolegal protection for both clinicians and healthcare facilities, proving that human clinical judgment remained the sole decisive authority.
