# CLINOVA AI — UI/UX Design Direction & Visual Language

> **Document ID:** `DOC-24`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Design Philosophy: Clinical, Calm, Trustworthy

CLINOVA AI is a safety-critical clinical platform designed for high-stress emergency rooms, crowded outpatient departments, and rural clinics across India.

The user interface must convey **institutional credibility, clinical precision, calm authority, and absolute data clarity**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UI/UX DESIGN MANDATES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT WE EXCLUSIVELY USE                  WHAT IS STRICTLY FORBIDDEN       │
│   ──────────────────────────────────       ───────────────────────────────  │
│   ✅ Clean, high-legibility typography      ❌ NO generic AI SaaS neon cards │
│   ✅ Professional Lucide clinical icons    ❌ NO emojis as interface icons   │
│   ✅ High-contrast evidence badges         ❌ NO purple/pink gradient text   │
│   ✅ Purposeful, subtle motion (<200ms)    ❌ NO gratuitous bouncing motion  │
│   ✅ Clear clinical hierarchy & asymmetry  ❌ NO repetitive identical cards  │
│   ✅ Generous whitespace for focus         ❌ NO decorative AI brain graphics│
│   ✅ Full WCAG 2.1 AA accessibility        ❌ NO low-contrast gray-on-gray   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Color Palette & Clinical Semantic Tokens

The visual palette is anchored in medical calm, utilizing precise semantic color tokens to communicate clinical urgency without inducing alarm:

### 2.1 Primary & Neutral Foundations
- **Canvas / Background:** Crisp, sterile whites and calm slates (`#F8FAFC` to `#FFFFFF`).
- **Surface Elevation:** Subtle bordered panels with soft natural shadows (`border-slate-200`, `shadow-sm`).
- **Primary Clinical Blue:** Authoritative navy and medical slate (`#0F172A`, `#1E293B`, `#2563EB`) representing institutional reliability.
- **Body Typography:** High-contrast slate text (`#0F172A` headings, `#334155` body) ensuring optimal readability on hospital LCD monitors.

### 2.2 Clinical Semantic Urgency Colors
- 🔴 **Emergency Red (`#DC2626` / `#EF4444`):** Reserved **strictly** for acute life threats, physiological shock, red-flag alerts, and emergency ward routing.
- 🟠 **Urgent Amber (`#D97706` / `#F59E0B`):** Reserved for high-priority cases, worsening physiological trajectories, and critical missing vital signs.
- 🟡 **Observation Yellow (`#CA8A04` / `#EAB308`):** Indicates intermediate risk, borderline observations, and active monitoring states.
- 🟢 **Routine Green (`#16A34A` / `#22C55E`):** Denotes stable parameters, verified findings, routine discharge, and full recoveries.
- 🟣 **Evidence Purple (`#7C3AED` / `#9333EA`):** Denotes lab reports, OCR extracts, and diagnostic panels.

---

## 3. Typography & Information Hierarchy

- **Primary Font Family:** Clean, legible sans-serif with distinct numeral glyphs (`Inter`, `Geist Sans`, or system `-apple-system, BlinkMacSystemFont, "Segoe UI"`).
- **Monospace Family:** Distinct tabular figures (`JetBrains Mono`, `Roboto Mono`) for all physiological vitals, lab values, timestamps, and case IDs to ensure zero visual misalignment in data columns.
- **Visual Weight Rules:**
  - Clear structural headings (`text-xl font-semibold text-slate-900`) separating clinical sections.
  - Subdued metadata labels (`text-xs font-medium uppercase tracking-wider text-slate-500`).
  - Prominent numerical callouts for vital signs (`text-2xl font-bold font-mono`).

---

## 4. Visualization Invariants

### 4.1 Evidence & Provenance Visual Badges
Every piece of data displays a clear, legible badge denoting its source:
- `[DOCTOR VERIFIED]` — Solid green badge with check icon.
- `[PATIENT REPORTED]` — Crisp blue outline badge.
- `[OCR EXTRACTED]` — Subtle purple badge with direct link to view source snippet.
- `[AI INFERRED]` — Dotted amber border with hover tooltip explaining model inference.
- `[CONFLICT DETECTED]` — High-contrast alert badge showing conflicting data points.

### 4.2 CAREGRAPH & FACILITYGRAPH Visualizations
- Graphs must be structured and readable. No unreadable, floating "spaghetti" node-link networks.
- Graphs are rendered as organized clinical swimlanes, interactive radar matrices, or geographic Leaflet overlays with clear legends.

---

## 5. Accessibility & Responsive Touch Targets

1. **Accessibility Standards:** Full compliance with **WCAG 2.1 AA** standards across all screens (minimum contrast ratio of 4.5:1 for body text and 3:1 for large headings).
2. **Field Tablet & Mobile Optimization:**
   - Minimum touch target size of **48x48 pixels** for all buttons, checkboxes, and interactive controls to facilitate one-handed operation on tablets by nurses wearing gloves.
   - Fluid responsive layouts that collapse gracefully from 3-column desktop doctor workbenches into structured single-column vertical flows on mobile devices.
3. **High-Stress Scannability:** Emergency fast-track screens use oversized typography and prominent contrast, allowing vital signs and red flags to be comprehended from a distance of 2 meters across an emergency bay.
