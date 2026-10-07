# CLINOVA AI — UI & WORKFLOW SCREENSHOT AUDIT PACK

**Audit Date:** 2026-10-06  
**Phase:** Phase 1 Foundation & UI Alignment  
**Framework:** Next.js 15.5.24 + Tailwind CSS + Lucide Icons  
**Reference Artifact:** `media_1791041522113.png` (Native Windows Orchestrator & UI Verification)  

---

## 1. UI Architecture & Role Surfaces

Clinova AI organizes patient and clinical workflows into strict, role-separated UI surfaces:

```text
                                  CLINOVA AI FRONTEND
                                           |
    +------------------+-------------------+-------------------+------------------+
    |                  |                   |                   |                  |
    v                  v                   v                   v                  v
PATIENT PORTAL    VOICE ASSISTANT     STAFF QUEUE       DOCTOR WORKSPACE     ADMIN CONSOLE
(/portal, /intake)   (Modal / Audio)    (/staff/queue)     (/doctor, /review)    (/admin)
```

---

## 2. Screen-by-Screen Audit Matrix

| Screen / Component | Route / File Path | Current Status | Clinical Authority Boundary | Multimodal & Case Alignment | Findings & Phase 1 Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Landing & Language Selection** | `frontend/src/app/page.tsx` | `CURRENT` (Working) | Clear disclaimer: Non-diagnostic triage assistant. | Supports English, Hindi, Odia, Bengali, Tamil, Telugu selection. | Aligned with Phase 1. Does not make diagnostic claims. |
| **Patient Multimodal Intake** | `frontend/src/app/patient/intake/page.tsx`<br>`frontend/src/app/portal/page.tsx` | `CURRENT` (Working) | Patient reported data only. Explicit consent checkbox enforced. | Accepts text, audio transcript, and document attachments. | Creates `TriageCase` via `/api/v1/cases`. Preserves patient provenance. |
| **Voice Assistant Modal** | `frontend/src/components/voice/VoiceAssistantModal.tsx` | `CURRENT` (Working) | Voice turn-taking state machine: `IDLE` -> `LISTENING` -> `USER_SPEAKING` -> `PROCESSING` -> `ASSISTANT_SPEAKING`. | Progressive real-time transcription, pause detection, interruptible playback. | Strictly patient-facing communication; does not autonomously prescribe or finalize case. |
| **Staff Verification Queue** | `frontend/src/app/staff/queue/page.tsx`<br>`frontend/src/app/nurse/page.tsx` | `CURRENT` (Working) | Staff/Nurse verifies patient intake and measures physical vitals. | Displays pending intake list; permits staff vitals entry. | Staff actions update case with `staff_entered` / `staff_verified` status. |
| **Doctor Clinical Review** | `frontend/src/app/doctor/workspace/page.tsx`<br>`frontend/src/app/doctor/queue/page.tsx`<br>`frontend/src/app/review/page.tsx` | `CURRENT` (Working) | Final clinical authority. Doctor reviews AI decision support note, overrides risk level, and writes final clinical orders. | Inspects raw symptoms, normalized summary, risk signals, timeline, and reports. | AI output is distinctly marked as decision support, never binding diagnosis. |
| **Admin System Governance** | `frontend/src/app/admin/page.tsx` | `CURRENT` (Working) | Administrative configuration, facility management, and audit log inspection. | Does not grant clinical override or patient case alteration authority. | Complies with server-side RBAC; separated from clinical paths. |

---

## 3. UI Evidence Verification

1. **Patient Consent & Disclaimer Gate**: Intake pages require explicit consent acknowledgment before dispatching cases to `/api/v1/cases`.
2. **AI Assistance Badging**: All AI triage summaries, risk signals, and timeline events render with explicit "AI-Assisted Decision Support — Not a Final Diagnosis" badges.
3. **Doctor Override Mechanism**: The doctor review UI provides editable override inputs for triage urgency, clinical notes, and destination department, ensuring the human clinician is the ultimate authority.
4. **Credential Isolation**: Zero API keys (Gemini, Sarvam, Groq, OCR) are bundled or referenced in `frontend/src/` or exposed via `NEXT_PUBLIC_*` variables.
