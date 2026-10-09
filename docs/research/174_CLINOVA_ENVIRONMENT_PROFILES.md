# CLINOVA AI — Declarative Facility Environment Profiles Specification

> **Document ID:** `RES-174`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Health Informatics & Policy Group  

---

## 1. Architectural Law: Declarative Profiles vs. Inviolable Invariants

CLINOVA AI operates across six diverse healthcare operational contexts. To avoid maintaining separate codebases or branches, the entire system adapts its operational behaviors via **declarative environment configuration profiles** identified by `CLINOVA_ENVIRONMENT_ID`.

**The Inviolable Invariant Law:**
$$\mathbf{Operational\ Profile\ Configuration} \not\subset \mathbf{Clinical\ Safety\ Invariants}$$

Configuration profiles govern workflows, intake interfaces, queue depths, and hardware assumptions, but **under no circumstances can any profile alter, relax, or disable**:
1. **Human Clinical Control:** RMP monopoly over diagnosis, prescription, admission, and discharge (NMC Regulation 27).
2. **Forensic Evidence Provenance:** Cryptographic hash chaining and Section 63 BSA legal admissibility.
3. **Auditability:** Tamper-evident append-only event logging.
4. **Zero-Imputation:** Missing clinical observations remain explicitly marked `MISSING`; zero algorithmic hallucination of missing vitals.
5. **AI Advisory-Only Boundary:** Statistical outputs are tagged `AI_INFERRED` and require affirmative human verification (`INFERRED \neq VERIFIED`).
6. **Deterministic Safety Guardrails:** NEWS2 scores, Shock Index, and red-flag rules remain pure deterministic evaluators.

---

## 2. Comparative Matrix: The Six Operational Profiles

| Profile Dimension | `ENV_GOV_HOSPITAL` | `ENV_PHC` | `ENV_PUBLIC_CAMP` | `ENV_COMPANY_CLINIC` | `ENV_INDUSTRIAL_HEALTH` | `ENV_CAMPUS_HEALTH` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Facility Tier** | IPHS Level 4 (District) | IPHS Level 1 (PHC) | Temporary Outreach | Corporate OHC | Industrial / Mining | Campus Health Centre |
| **Primary Intake Mode** | Kiosk + Staff Triage | ASHA / Nurse Assisted | Batch Paper + Mobile | Employee Self-Intake | Kiosk + Shift Nurse | Student App / Kiosk |
| **Default Languages** | English, Hindi, Odia | Odia, Hindi, English | Odia, Vernacular Dialects| English, Hindi | Hindi, Odia, English | English, Hindi |
| **Device Assumptions** | Multi-monitor PC + Tablets| Fanless Mini-PC + Tablets| Rugged Laptops + Tablets| Desktops + Mobile Web | Industrial Kiosks + Tablets| Laptops + Smartphones |
| **Connectivity Baseline**| High-speed Hospital LAN | Intermittent 2G/3G / None | **100% Offline Autonomy** | Enterprise WAN (1 Gbps) | Factory On-Premise LAN | University Wi-Fi (WAN) |
| **Facility Capabilities**| ICU, Blood Bank, CT, OT | Observation Beds, Day OPD | First Aid, Screening Only | Basic First Aid, Rest Bay | Trauma Bay, Burn Station | Outpatient Clinic, Infir. |
| **Queue Depth Alert** | 150 patients | 40 patients | 200 patients | 15 patients | 30 patients | 50 patients |
| **Wait Acceleration $\alpha$**| 5.0 (Standard ED) | 3.0 (Rural OPD) | 2.0 (Mass Outreach) | 1.5 (Corporate) | 6.0 (High Emergency Hazard)| 2.5 (Campus OPD) |
| **Specialist Routing** | **Yes** (Cardio, Ortho, etc.)| No (Referral Gateway) | No (Referral Gateway) | No (Teleconsult Option)| **Yes** (Industrial MO) | No (General MO) |
| **Hazard Screening** | No | No | No | Ergonomics, VDT strain | **Yes** (Silica, Gas, Toxic) | Sports injuries, Mental health |
| **Single-Doctor Exemption**| **Blocked** (Full Staff) | **Enabled** (Night Shift) | **Enabled** (Camp MO) | **Blocked** | **Blocked** | **Blocked** |
| **Signal Aggregation** | District syndromic trends | Sub-district cluster | Camp community cluster | Workplace absenteeism | Factory hazard cluster | Dormitory infection cluster |

---

## 3. Detailed Profile Specifications

### 3.1 `ENV_GOV_HOSPITAL` (Government District Hospital)
- **Context:** High-throughput urban/sub-divisional public hospital experiencing severe casualty surges.
- **Workflow:** High-volume patient registration $\to$ rapid two-tier nurse triage $\to$ prioritized doctor workbench with dynamic wait-time escalation.
- **Referral:** Acts as a **Destination Hub**; receives inbound transfer dossiers from peripheral PHCs.

### 3.2 `ENV_PHC` (Rural Primary Health Centre)
- **Context:** 24x7 rural primary care facility staffed by 1 Medical Officer, 2 Staff Nurses, and peripheral ASHAs.
- **Workflow:** Vernacular voice intake in Odia/Hindi $\to$ paper prescription slip photo capture $\to$ single-doctor review queue.
- **Referral:** Acts as a **Source Facility**; generates SBAR transfer dossiers and checks destination capabilities via FACILITYGRAPH.

### 3.3 `ENV_PUBLIC_CAMP` (Outreach Health Camp / Disaster Relief Site)
- **Context:** Mobile health camps in remote panchayats, flood relief centers, or tribal outreach zones.
- **Workflow:** High-speed batch token intake $\to$ physical examination $\to$ offline synchronization queuing.
- **Storage:** Local laptop filesystem with encrypted SQLite; zero reliance on cloud or cellular uplink.

### 3.4 `ENV_COMPANY_CLINIC` (Corporate Occupational Health Centre)
- **Context:** On-site occupational medical clinic at an enterprise office complex.
- **Workflow:** Employee check-in with corporate ID $\to$ ergonomic and chronic lifestyle screening $\to$ return-to-work fitness certification.
- **Privacy:** Strict corporate-versus-clinical data fencing; HR receives fitness certificates only, zero diagnostic details.

### 3.5 `ENV_INDUSTRIAL_HEALTH` (High-Hazard Factory / Mining Health Unit)
- **Context:** Heavy industrial manufacturing, chemical processing, or mining site with acute toxic and mechanical hazards.
- **Workflow:** Mandatory industrial exposure logging (silica dust, toxic fumes, caustic chemicals) $\to$ rapid trauma bay resuscitation.
- **Safety Rule:** Acceleration factor $\alpha = 6.0$ rapidly elevates chemical exposure cases to the head of the medical queue.

### 3.6 `ENV_CAMPUS_HEALTH` (University Student & Residential Clinic)
- **Context:** Academic campus health center serving university students, faculty, and resident staff.
- **Workflow:** Student ID integration $\to$ sports injury, infectious outbreak (dengue, influenza), and mental health distress triage.
- **Privacy:** Confidential student health records separated from academic and disciplinary registries.

---

## 4. Declarative Pydantic Profile Registry

```python
# backend/app/core/profiles.py - Phase 9 Facility Profile Definitions

from typing import Dict
from pydantic import BaseModel

class FacilityProfileConfig(BaseModel):
    environment_id: str
    display_name: str
    facility_tier: str
    max_queue_depth_alert: int
    wait_time_acceleration_alpha: float
    enable_specialist_routing: bool
    enable_hazard_screening: bool
    allow_single_doctor_override: bool
    default_intake_mode: str
    default_languages: list[str]

FACILITY_PROFILES: Dict[str, FacilityProfileConfig] = {
    "ENV_GOV_HOSPITAL": FacilityProfileConfig(
        environment_id="ENV_GOV_HOSPITAL",
        display_name="Government District Hospital",
        facility_tier="LEVEL_4_DH",
        max_queue_depth_alert=150,
        wait_time_acceleration_alpha=5.0,
        enable_specialist_routing=True,
        enable_hazard_screening=False,
        allow_single_doctor_override=False,
        default_intake_mode="KIOSK_AND_STAFF",
        default_languages=["en", "hi", "or"],
    ),
    "ENV_PHC": FacilityProfileConfig(
        environment_id="ENV_PHC",
        display_name="Rural Primary Health Centre",
        facility_tier="LEVEL_1_PHC",
        max_queue_depth_alert=40,
        wait_time_acceleration_alpha=3.0,
        enable_specialist_routing=False,
        enable_hazard_screening=False,
        allow_single_doctor_override=True,
        default_intake_mode="ASHA_ASSISTED",
        default_languages=["or", "hi", "en"],
    ),
    "ENV_PUBLIC_CAMP": FacilityProfileConfig(
        environment_id="ENV_PUBLIC_CAMP",
        display_name="Outreach Public Health Camp",
        facility_tier="TEMPORARY_CAMP",
        max_queue_depth_alert=200,
        wait_time_acceleration_alpha=2.0,
        enable_specialist_routing=False,
        enable_hazard_screening=False,
        allow_single_doctor_override=True,
        default_intake_mode="BATCH_PAPER_MOBILE",
        default_languages=["or", "hi", "en"],
    ),
    "ENV_COMPANY_CLINIC": FacilityProfileConfig(
        environment_id="ENV_COMPANY_CLINIC",
        display_name="Corporate Occupational Health Centre",
        facility_tier="OCCUPATIONAL_L1",
        max_queue_depth_alert=15,
        wait_time_acceleration_alpha=1.5,
        enable_specialist_routing=False,
        enable_hazard_screening=True,
        allow_single_doctor_override=False,
        default_intake_mode="EMPLOYEE_SELF_SERVICE",
        default_languages=["en", "hi"],
    ),
    "ENV_INDUSTRIAL_HEALTH": FacilityProfileConfig(
        environment_id="ENV_INDUSTRIAL_HEALTH",
        display_name="Industrial / Mining Health Centre",
        facility_tier="OCCUPATIONAL_L2",
        max_queue_depth_alert=30,
        wait_time_acceleration_alpha=6.0,
        enable_specialist_routing=True,
        enable_hazard_screening=True,
        allow_single_doctor_override=False,
        default_intake_mode="SHIFT_NURSE_TRAUMA",
        default_languages=["hi", "or", "en"],
    ),
    "ENV_CAMPUS_HEALTH": FacilityProfileConfig(
        environment_id="ENV_CAMPUS_HEALTH",
        display_name="University Campus Health Centre",
        facility_tier="CAMPUS_CLINIC",
        max_queue_depth_alert=50,
        wait_time_acceleration_alpha=2.5,
        enable_specialist_routing=False,
        enable_hazard_screening=False,
        allow_single_doctor_override=False,
        default_intake_mode="STUDENT_PORTAL_KIOSK",
        default_languages=["en", "hi"],
    ),
}
```
