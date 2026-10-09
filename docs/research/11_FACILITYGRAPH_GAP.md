# CLINOVA AI — FACILITYGRAPH Gap Audit & Defensibility Analysis

> **Document ID:** `RES-11`  
> **Status:** COMPLETED & AUDITED  
> **Phase:** Phase 2 — Research, Existing-Solution & Innovation-Gap Audit  
> **Version:** 2.0.0  
> **Date:** October 2026  

---

## 1. Executive Summary & Audit Objective

This audit investigates the defensibility of **FACILITYGRAPH** by testing the exact multi-factor care feasibility combination proposed in Phase 1:

$$\mathbf{FEASIBILITY} = \mathcal{F}\Big(\text{Patient Requirement},\ \text{Facility Capability},\ \text{Bed Capacity},\ \text{Specialist Availability},\ \text{Geography},\ \text{Referral Destination}\Big)$$

We search globally across emergency medical dispatch systems, trauma transfer networks, patient placement software, and Indian emergency portals to identify:
1. Whether any existing commercial or government system executes this exact multi-factor synthesis.
2. What remains genuinely broken in existing implementations.
3. The smallest, bulletproof defensible CLINOVA contribution.

---

## 2. Adversarial Mapping: How Close are Existing Systems?

| Existing Solution Category | Representative Systems | What They Actually Model | What They Silently Omit | How Close to FACILITYGRAPH? | Novelty Classification |
|:---|:---|:---|:---|:---|:---|
| **Commercial Transfer Center Software** | TeleTracking Transfer Center, Central Logic (Access TeleCare), Epic Transfer Center. | Patient demographic, referring facility, receiving facility, requested bed type (ICU/Floor), transport method. | **Granular capability verification.** Assumes receiving nurse manually phones the on-duty surgeon to verify operating room readiness. | **Close functionally, but relies on human call center agents.** Software is an administrative ticketing system, not an algorithmic feasibility engine. | **Category B** (Existing capability with manual call-center workflow) |
| **Emergency Medical Dispatch (EMD)** | ProQA (Priority Dispatch), FirstWatch, Deccan 108 Emergency Ambulance Dispatch. | Caller location, MPDS emergency code, nearest available ambulance vehicle GPS. | **Hospital internal resource states.** Dispatches ambulance to nearest general hospital without knowing if that hospital's ICU is full or if CT is broken. | **Moderate.** Solves the geographic routing of the vehicle, but **blind to receiving hospital clinical capability**. | **Category C** (Integration target: combining ambulance dispatch with hospital readiness) |
| **State Bed Portals (India)** | Delhi Corona Portal, WB Health COVID Dashboard, Odisha Bed Tracking. | Static tallies of general, oxygen, and ICU beds reported by hospital data clerks. | **Specialist on-duty rosters, functioning equipment, patient clinical requirements.** Completely decoupled from individual patient vitals. | **Distant.** A public informational website; cannot compute patient-specific feasibility. | **Category B** (Static manual reporting vs dynamic algorithmic matching) |
| **Discharge & Post-Acute Placement** | CarePort Health, LeanTaaS iQueue, Qventus. | Inpatient stay milestones, insurance pre-authorization, post-acute nursing home availability. | **Acute emergency resuscitation capability.** Designed for non-emergency post-acute discharge coordination. | **Distant.** Operates at discharge from tertiary hospital, not at initial intake/referral. | **Category A / B** (Established in post-acute; absent in acute emergency triage) |

---

## 3. The Grill: Can a Judge Say "This Already Exists"?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FACILITYGRAPH ADVERSARIAL GRILL                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  JUDGE'S CHALLENGE:                                                         │
│  "Large hospital systems in the US and UK already have Transfer Centers     │
│   (like TeleTracking or Epic) that route patients based on bed capacity     │
│   and specialty. Why is FACILITYGRAPH different?"                           │
│                                                                             │
│  THE HONEST REALITY:                                                        │
│  In Western enterprise health systems, transfer center routing DOES exist,   │
│  BUT it costs millions of dollars, requires dedicated teams of 20+ nurses   │
│  answering phones 24/7, and runs on closed proprietary EHR software.        │
│                                                                             │
│  In Indian public healthcare (PHCs, CHCs, District Hospitals):              │
│  • There are ZERO automated transfer centers.                               │
│  • A rural doctor writes "Refer to SCB Medical College" on a paper slip.    │
│  • The patient travels 3 hours in an ambulance only to find that all 12     │
│    ventilators are occupied and no neurosurgeon is available.               │
│  • The patient is turned away at the door ("Refused Admission").            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 The Granular Capability Deficit in Real Transfers
Commercial transfer software treats a hospital as having generic "ICU beds." 
However, real clinical care feasibility requires satisfying **hierarchical prerequisite dependencies**:
$$\begin{aligned}
\text{Care Feasible} \iff &\ (\text{ICU Bed Available}) \land (\text{Functioning Ventilator Available}) \\
&\land (\text{On-Duty Specialist Logged On}) \land (\text{Blood Bank Has Matched Component}) \\
&\land (\text{Travel Time} \le \text{Golden Hour Window})
\end{aligned}$$

If any single term in this conjunction evaluates to false, the referral will fail. No existing lightweight public health software in India evaluates this logical conjunction at the point of frontline intake.

---

## 4. The Smallest Defensible CLINOVA Contribution

Based on this audit, we must **narrow the innovation claim**:
- **Do NOT claim:** Uniqueness of "hospital capacity tracking" or "geospatial referral routing."
- **Defensible Claim:** 
  > **A lightweight, ₹0 open-source Care Feasibility Engine that evaluates multi-tier institutional capabilities, on-duty specialist rosters, blood component stocks, and Haversine transit times against individual physiological urgency at the point of primary care intake.**

### Classification Summary
- **Capability:** Multi-tier resource feasibility matching.
- **Category:** **CATEGORY C (Meaningful Combination)** + **CATEGORY E (CLINOVA Contribution in Low-Resource Public Health Context)**.
- **Evidence Quality:** **Grade A** (RHS 2022 specialist shortfall data; ICMR Trauma Referral Audits 2023).
