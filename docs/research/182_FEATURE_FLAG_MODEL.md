# CLINOVA AI — Declarative Feature Flag Architecture & Safety Boundaries

> **Document ID:** `RES-182`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Feature Architecture, Clinical Risk Management & Systems Engineering Group  

---

## 1. Architectural Feature Flag Philosophy

Feature flags allow CLINOVA AI to gracefully toggle auxiliary capabilities (such as heavy optical character recognition, voice processing, or experimental multi-facility sync) based on hardware capacity, battery power, or network conditions.

However, in healthcare software, **feature flags can become fatal trapdoors** if an operator can disable critical safety guardrails to "speed up triage."

**The Golden Law of Feature Boundaries:**
$$\mathbf{Tunable\ Feature\ Flags} \cap \mathbf{Core\ Safety\ Invariants} = \emptyset$$

Core clinical safety guardrails are **hardcoded immutable laws** compiled into the application core and can **NEVER be disabled by any feature flag**.

---

## 2. The Nine Approved Declarative Feature Flags

| Feature Flag | Operational Capability | Default in `PHC_EDGE` | Default in `DEV` | Default in Low-RAM Mode |
| :--- | :--- | :--- | :--- | :--- |
| `FEATURE_VOICE` | Vernacular voice capture and faster-whisper transcription. | `True` | `True` | `False` (Saves 500MB RAM) |
| `FEATURE_OCR` | Paper slip upload and PaddleOCR text extraction. | `True` | `True` | `False` (Saves 400MB RAM) |
| `FEATURE_TRANSLATION` | Vernacular language translation (Odia/Hindi to English). | `True` | `True` | `True` (Fast lookup) |
| `FEATURE_CAREGRAPH` | Continuous risk trajectory slope ($\Delta R / \Delta t$) rendering. | `True` | `True` | `True` (In-memory $<2\text{ms}$) |
| `FEATURE_FACILITYGRAPH`| Facility capability checking and anti-blind referral gating. | `True` | `True` | `True` |
| `FEATURE_SIGNALGRAPH` | Local facility syndromic anomaly z-score alerts. | `True` | `True` | `True` |
| `FEATURE_ORCHESTRATION`| Advisory clinical action synthesis (`ASK`, `VERIFY`, etc.). | `True` | `True` | `True` |
| `FEATURE_OFFLINE_SYNC` | Background sync journal push/pull replication. | `True` | `False` | `True` |
| `FEATURE_EMERGENCY_MODE`| Instant $< 200\text{ms}$ anonymous casualty token generation. | `True` | `True` | `True` |

---

## 3. The Seven Inviolable Invariants (Flag-Immune Guardrails)

The following seven mechanisms **DO NOT HAVE FEATURE FLAGS** and are architecturally protected from being toggled off:

1. **RMP Verification Gate:** The system CANNOT be configured to autonomously approve prescriptions, discharge patients, or finalize diagnoses without doctor sign-off. (Mandated by NMC Regulation 27).
2. **Deterministic NEWS2 & Shock Index Scoring:** Physiological risk calculation is permanent; no flag can disable early warning score calculation on acquired vitals.
3. **Forensic Provenance Chaining:** Every mutation creates an immutable event in the hash-chained ledger; audit logging cannot be suppressed.
4. **Zero-Imputation Enforcement:** Missing vital signs remain explicitly tagged `MISSING`; no flag can enable "AI guess missing heart rate."
5. **Epistemic State Attribution:** AI suggestions are permanently tagged `AI_INFERRED`; no flag can reclassify unverified AI text as `VERIFIED`.
6. **Side-by-Side Verification Views:** The Doctor Workbench permanently provides access to raw source slip bounding boxes and audio snippets.
7. **Patient Informed Consent Gate:** Triage intake permanently requires affirmative consent recording (verbal or digital).

---

## 4. Feature Flag Schema & Startup Validation

```python
# Feature Flags Model
class FeatureFlagsSettings(BaseModel):
    FEATURE_VOICE: bool = Field(default=True, description="Enable voice capture & ASR")
    FEATURE_OCR: bool = Field(default=True, description="Enable slip photo upload & OCR")
    FEATURE_TRANSLATION: bool = Field(default=True, description="Enable language translation")
    FEATURE_CAREGRAPH: bool = Field(default=True, description="Enable trajectory risk calculation")
    FEATURE_FACILITYGRAPH: bool = Field(default=True, description="Enable facility resource gating")
    FEATURE_SIGNALGRAPH: bool = Field(default=True, description="Enable syndromic anomaly alerts")
    FEATURE_ORCHESTRATION: bool = Field(default=True, description="Enable action synthesis")
    FEATURE_OFFLINE_SYNC: bool = Field(default=False, description="Enable background sync replication")
    FEATURE_EMERGENCY_MODE: bool = Field(default=True, description="Enable rapid casualty bypass")

    # Anti-Tampering Check: Rejects any attempt to pass forbidden bypass flags
    @model_validator(mode="before")
    @classmethod
    def reject_forbidden_flags(cls, values: dict) -> dict:
        forbidden = [
            "DISABLE_DOCTOR_VERIFICATION",
            "DISABLE_NEWS2",
            "DISABLE_AUDIT_LOG",
            "ENABLE_AUTO_PRESCRIBE",
            "ENABLE_VITAL_IMPUTATION",
            "DISABLE_CONSENT_GATE",
        ]
        for key in forbidden:
            if key in values:
                raise ValueError(
                    f"FATAL SECURITY VIOLATION: Forbidden safety bypass flag '{key}' detected in configuration!"
                )
        return values
```
