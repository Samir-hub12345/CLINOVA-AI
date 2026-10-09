# CLINOVA AI — Offline Availability & Safe Degradation Architecture

> **Document ID:** `RES-208`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** AI Systems Engineering, Clinical Reliability & Fault Tolerance Group  

---

## 1. Tri-State AI Operational Model

The local AI runtime operates within three discrete availability tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TRI-STATE AVAILABILITY MODEL                          │
├────────────────────┬────────────────────────────────────────────────────────┤
│ 1. AI_AVAILABLE    │ Local model loaded, healthy, and responsive (<5s).     │
│                    │ Full AI-assisted extraction and drafting active.       │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 2. AI_DEGRADED     │ Model loaded but experiencing queue pressure or high   │
│                    │ latency. AI advisory tasks deferred; lightweight       │
│                    │ extraction prioritized.                                │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 3. AI_UNAVAILABLE  │ Daemon crashed, offline, or disabled. Zero generative  │
│                    │ processing. Pure deterministic clinical operations.    │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Inviolable Guarantees During `AI_UNAVAILABLE`

$$\mathbf{THE\ GOLDEN\ LAW:\ NEVER\ FABRICATE\ WHEN\ OFFLINE}$$

When the local AI runtime is unavailable (e.g. during daemon crash, missing GGUF weights, or low RAM eviction):

1. **Deterministic Care Continues 100%:**
   - Vital sign recording, Shock Index calculation, and NEWS2 early warning scoring function without interruption.
   - Emergency Red Flags (`TRIAGE-R01` to `TRIAGE-R06`) trigger with zero delay.
   - Doctor Queue prioritization based on physiological risk remains operational.
2. **Manual Input Unlocked:**
   - Text boxes for chief complaint, history of present illness, and clinical notes remain open for direct typing by nurses and doctors.
3. **Existing Verified Data Preserved:**
   - All previously verified observations, lab results, and clinician orders remain visible and uncorrupted.
4. **Transparent Clinical UI Notification:**
   - An amber, non-blocking status indicator is displayed in the navigation header:
     > ℹ️ *AI Assistant Offline — Operating on Deterministic Clinical Rules. Manual data entry enabled.*
5. **Zero Synthetic Hallucinations:**
   - Under no circumstances does the backend fabricate synthetic AI extractions, fake lab values, or canned diagnostic text to "pretend" the AI is functioning.
6. **Immutable Audit Recording:**
   - System failure events are recorded in operational logs and forensic audit ledgers for administrative review.
