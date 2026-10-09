# CLINOVA AI — Provenance User Interface Conceptual Specification

> **Document ID:** `RES-124`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Ergonomic Vision & Phase Scope

In emergency medicine, intensive care, and rural outpatient practice, clinical cognitive bandwidth is extremely scarce. If inspecting the origin of a lab value requires navigating away from the active chart, opening multiple nested tabs, or waiting for complex network queries, clinicians simply will not inspect provenance. They will either guess blindly or bypass the system entirely.

Phase 7 specifies the **Conceptual Inspection Experience** for the CLINOVA Doctor Workbench and Frontline Nurse Intake Interfaces:
- **Phase Boundary:** This document specifies interaction patterns, information architecture, and visual hierarchy. It does **NOT** construct React/Flutter UI components or frontend code.
- **Empirical Rigor:** Avoids fabricated, unmeasured latency claims (e.g., *"renders in exactly 12ms"*). Instead, specifies architectural optimization principles (local SQLite edge indexing, client-side pre-fetching, pre-cropped image thumbnails) designed to achieve responsive, fluid bedside inspection.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL PROVENANCE INSPECTION FLOW                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FACT ──► SOURCE ──► ORIGINAL CONTENT ──► TRANSFORMATION ──► VERIFICATION  │
│                   ──► CONFLICTS ──► TIMESTAMPS ──► ACTOR                    │
│                                                                             │
│   A clinician must be able to verify any clinical datum's origin in one      │
│   gesture without losing context of the active patient chart.                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Seven Provenance UI Modalities

### 2.1 Modality 1: Optical Character Recognition (OCR) Bounding Box Overlay
- **Trigger:** Single-tap or mouse hover on any OCR-extracted observation (e.g., `Serum Creatinine: 2.8 mg/dL`).
- **Visual Presentation:** A non-modal floating inspection drawer slides in from the right pane.
- **Components:**
  - High-resolution cropped image of the physical paper slip bounded by $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$ highlighted in translucent amber.
  - Extracted text vs Raw OCR text side-by-side.
  - OCR Engine Name, Version, and Character Confidence Score.
  - One-click action buttons: `[Confirm Reading]`, `[Edit Number]`, `[Reject Snippet]`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ FACT: Serum Creatinine: 2.8 mg/dL                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ DOCUMENT IMAGE CROP PREVIEW ]                                             │
│ ┌──────────────────────────────────────────────┐                            │
│ │  S. Creatinine  :  2.8 mg/dL                 │  <-- Highlighted Bounding  │
│ │  Blood Urea     :  54 mg/dL                  │      Box [y:410, x:120]    │
│ └──────────────────────────────────────────────┘                            │
│ Engine: PaddleOCR-v4-Mobile (Confidence: 0.942)                             │
│ Captured: 10:18 AM by Staff Nurse Anita | Document: doc_a17c.jpg            │
│ ACTIONS: [✓ Confirm]  [Δ Correct Value]  [✕ Reject Extraction]              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Modality 2: Voice & Acoustic Snippet Player
- **Trigger:** Tapping an audio-extracted symptom or narrative finding (e.g., *"Severe retrosternal pain radiating to left arm"*).
- **Visual Presentation:** An inline micro-audio player appears directly beneath the text line.
- **Components:**
  - Interactive waveform visualization showing word-level timecode boundaries $[t_{\text{start}}, t_{\text{end}}]$.
  - Play button that streams the exact 3-second audio crop $[t_{\text{start}} - 500\text{ms}, \; t_{\text{end}} + 500\text{ms}]$.
  - Original vernacular transcript in Odia/Hindi alongside the English clinical translation.
  - Acoustic confidence indicator and speaker tag (`PATIENT` vs `CAREGIVER`).

---

### 2.3 Modality 3: Multi-Source Conflict Juxtaposition Card
- **Trigger:** System detects discordance between multiple sources (e.g., Patient stated BP $120/80$ vs Nurse measured BP $195/115$).
- **Visual Presentation:** A high-priority amber conflict banner at the top of the clinical summary card.
- **Components:**
  - Columnar side-by-side comparison displaying Source, Value, Actor, Time Elapsed, and Epistemic Status.
  - Variance Delta highlight ($+75\text{ mmHg}$ systolic difference).
  - Prominent safety tripwire notice: *"Pessimistic Safety Signal Active: 195 mmHg driving triage priority."*
  - Clinician resolution radio buttons: `[Accept Nurse Cuff]`, `[Accept Patient Report]`, `[Mark Both Valid Over Time]`, `[Manual Bedside Re-check]`.

---

### 2.4 Modality 4: Transformation Lineage Popover
- **Trigger:** Clicking a normalized diagnostic concept or converted unit (e.g., SNOMED CT `29857009` or Temperature $38.5^\circ\text{C}$).
- **Visual Presentation:** A compact vertical lineage tree modal.
- **Components:**
  - Step 1: Raw vernacular text (`"Garam laguchi, deha tharuchi"`).
  - Step 2: Language translation (`"Feeling hot, body shivering"`).
  - Step 3: Entity extraction (`Fever with chills`).
  - Step 4: Concept mapping (`SNOMED CT 386661006`).
  - Reversibility status badge (`PARTIALLY_REVERSIBLE`).

---

### 2.5 Modality 5: Acuity-Proportional Verification Badging
- **Visual Presentation:** Subtle, color-coded visual tokens attached to every clinical entity across the chart:
  - **`[UNVERIFIED]` (Hollow Grey Outline):** Raw OCR or patient kiosk entry; not yet checked by clinical staff.
  - **`[STAFF_VERIFIED]` (Solid Blue Badge):** Confirmed by nurse; operationally active for triage scoring.
  - **`[CLINICIAN_APPROVED]` (Solid Green Seal with Checkmark):** Attested by RMP; medico-legally binding.
  - **`[AI_INFERRED]` (Amber Watermark with Warning Icon):** Machine-generated advisory; displays model version and confidence on hover.

---

### 2.6 Modality 6: Multi-Clock Temporal Drawer
- **Trigger:** Clicking any timestamp displayed in the chart.
- **Visual Presentation:** Expands to show the five distinct temporal clocks:
  - Event Time (Biological occurrence): `06:30 AM`
  - Capture Time (Tablet entry): `07:15 AM`
  - Ingestion Time (Server sync): `08:45 AM`
  - Verification Time (Doctor sign-off): `08:52 AM`
  - Retrospective Lag Notice: `[!] Retrospective documentation: entered 45 minutes after physical event.`

---

### 2.7 Modality 7: Forensic Audit & Integrity Trail
- **Trigger:** Clicking the case security seal or selecting "Inspect Cryptographic Audit Ledger".
- **Visual Presentation:** A read-only chronological ledger displaying:
  - Event ID, Actor Legal Name, Role, Device UUID, IP Address.
  - Merkle Chain SHA-256 Hash $H_n = \text{SHA256}(H_{n-1} \parallel \dots)$.
  - Verification indicator: *"All 24 historical events cryptographically verified under Section 63 BSA 2023."*

---

## 3. Ergonomic Principles & Cognitive Safety

1. **Zero Context Loss:** Provenance inspection overlays (drawers, popovers, inline players) must never unmount or navigate away from the active clinical chart. Closing the drawer returns the doctor to the exact scroll position and cursor focus.
2. **One-Gesture Access:** Every provenance layer is accessible within a single tap or click. No nested menus or modal drilling.
3. **Pessimistic Safety Signaling:** Conflicts and unverified inferences are visually distinct from confirmed clinical facts, preventing perceptual automation bias and cognitive capture.
