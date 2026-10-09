# CLINOVA AI — Inter-Facility Referral & Transfer Pathway Specification

> **Document ID:** `RES-69`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 5 — Master Patient Journey & End-to-End Care Pathway Specification  
> **Version:** 5.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Overview & The Anti-Blind-Transfer Doctrine

In peripheral primary health centres (PHCs), community health centres (CHCs), and rural sub-divisional hospitals, diagnostic and therapeutic capabilities are fundamentally bounded by statutory resource constraints (IPHS 2022). When a patient's clinical needs exceed on-site capabilities—such as requiring computed tomography, intensive mechanical ventilation, emergent hemodialysis, or specialist surgical subspecialties—safe navigation requires **Pathway D: Inter-Facility Referral & Transfer**.

CLINOVA's Referral Pathway is governed by the **Anti-Blind-Transfer Doctrine**:
> **Core Mandate:** No patient shall be dispatched on an uncoordinated "blind transfer" without verified destination capability, pre-arrival clinical packet transmission, confirmed bed readiness, and continuous en-route risk management.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTER-FACILITY REFERRAL PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1 ] CLINICAL REFERRAL NEED IDENTIFIED                               │
│       │     (Deficit detected: on-site capability exceeded)                 │
│       ▼                                                                     │
│  [ STEP 2 ] FACILITYGRAPH CARE FEASIBILITY & MATCHING                       │
│       │     (Multi-criteria search: capability, distance, beds, traffic)    │
│       ▼                                                                     │
│  [ STEP 3 ] DESTINATION SELECTION & CLINICIAN APPROVAL                      │
│       │     (Doctor selects verified capable receiving hospital)            │
│       ▼                                                                     │
│  [ STEP 4 ] DIGITAL REFERRAL PACK GENERATION (Report Type 2)                │
│       │     (Comprehensive pre-arrival dossier & CAREGRAPH payload)         │
│       ▼                                                                     │
│  [ STEP 5 ] RECEIVING FACILITY CONFIRMATION & BED HOLD                      │
│       │     (Digital accept / telephone verification protocol)              │
│       ▼                                                                     │
│  [ STEP 6 ] TRANSPORT / AMBULANCE DISPATCH & HANDOFF                        │
│       │     (BLS / ALS ambulance matched; departure vitals recorded)        │
│       ▼                                                                     │
│  [ STEP 7 ] EN-ROUTE MONITORING & ARRIVAL HANDOFF                           │
│       │     (Real-time in-transit telemetry; receiving hospital intake)      │
│       ▼                                                                     │
│  [ STEP 8 ] TRANSFER OUTCOME RESOLUTION & CONTINUITY                        │
│       │     (Destination admission confirmed; SIGNALGRAPH feedback logged)  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Step-by-Step Referral Execution

### Step 1: Clinical Referral Need Identified
- **Actor:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **Data State:** `STATE_ORCHESTRATION_PENDING` $\to$ `STATE_REFERRAL_PENDING`.
- **System Action:**
  - Clinician or system detects that patient requirements exceed local capabilities ($\Phi_{\text{local}} = 0.0$).
  - System captures specific clinical deficits (e.g., `DEFICIT: NEURO_SURGERY`, `DEFICIT: ICU_VENTILATOR`, `DEFICIT: BLOOD_BANK_PRBC`).
  - Clinician initiates referral protocol.

### Step 2: FACILITYGRAPH Care Feasibility & Destination Matching
- **Engine:** $\text{FACILITYGRAPH}$ executes real-time regional network matching:
  - Filters facilities within 100km corridor possessing verified matching capabilities.
  - Computes dynamic ranking score:
    $$\text{Score}(\text{Fac}_j) = 0.40 \cdot \text{CapabilityMatch} + 0.30 \cdot \text{BedAvailability} - 0.20 \cdot \text{TransitTime} - 0.10 \cdot \text{StalenessPenalty}$$
  - Ranks candidate hospitals (e.g., District Headquarters Hospital, Government Medical College, Regional Trauma Centre).

### Step 3: Destination Hospital Selection & Clinician Approval
- **Actor:** Attending Medical Officer (`ROLE_CLINICIAN`).
- **System Action:**
  - Workbench displays top candidate facilities with real-time bed census, travel distance, estimated transit time, and contact telephone numbers.
  - Clinician selects the destination hospital and specifies transport urgency (STAT / Within 1 hour / Non-urgent elective).

### Step 4: Digital Referral Pack Generation (Report Type 2)
- **Artifact:** Generates the **Digital Referral Dossier (`Report Type 2`)**:
  - Patient demographics and synthetic ID (`PT-XXXXXX`).
  - Verified clinical timeline and physical examination findings.
  - Complete vital signs progression and trajectory vector.
  - Administered pre-transfer medications and stabilization fluids.
  - Exact clinical indication for transfer.
  - Serialized CAREGRAPH payload and scannable high-density QR code.

### Step 5: Receiving Facility Confirmation & Bed Reservation
- **Protocol:**
  - *Digital Interoperability (ABDM / State Portal):* Pre-arrival notification pushed to receiving facility emergency intake queue.
  - *Telephonic Verification Gate:* In environments with intermittent cloud connectivity, referral coordinator executes statutory telephone confirmation:
    > *"District Hospital Casualty confirming transfer of PT-49102; 45yo male, acute abdomen, arriving via 108 ALS Ambulance in 40 minutes. Surgical bed held."*
  - Confirmation status set to `CONFIRMED`.

### Step 6: Transport / Ambulance Dispatch & Departure Handoff
- **Actor:** Referral Coordinator (`ROLE_ADMIN` / `ROLE_NURSE`) & Paramedic.
- **Data State:** `STATE_REFERRAL_PENDING` $\to$ `STATE_TRANSFER_IN_TRANSIT`.
- **System Action:**
  - Matches required transport tier:
    - *Basic Life Support (BLS):* Stable patients requiring non-monitored transit.
    - *Advanced Life Support (ALS):* Unstable / critical patients requiring en-route oxygen, cardiac monitor, and escort paramedic.
  - Paramedic receives physical or digital Referral Pack.
  - Records departure vital signs and UTC departure timestamp.

### Step 7: En-Route Monitoring & Destination Intake Handoff
- **In-Transit Protocol:**
  - Paramedic monitors patient during transit; records serial vitals if condition changes.
  - If acute decompensation occurs en route, ambulance staff initiates emergency resuscitation bundle.
- **Arrival at Destination:**
  - Receiving casualty team scans patient QR code, instantly loading the full Master Case history on their local terminal.
  - Dual-party intake sign-off executed between transport paramedic and receiving triage doctor.

### Step 8: Transfer Outcome Resolution & Loop Closure
- **Data State:** `STATE_OUTCOME_PENDING` $\to$ `STATE_RESOLVED`.
- **System Action:**
  - Originating facility console updates: *"Transfer successfully admitted at District Hospital (Bed ICU-02)."*
  - Originating encounter marks clinical endpoint as `REFERRED_HIGHER`.
  - Referral duration, transit time, and acceptance metrics feed $\text{SIGNALGRAPH}$ to continuously optimize future regional referral recommendations.

---

## 3. Comprehensive Exception & Failure Handling

Real-world inter-facility transfers face severe logistical and clinical hazards. The Referral Pathway enforces six mandatory failure recovery protocols:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REFERRAL EXCEPTION WORKFLOWS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ EXCEPTION 1: REFERRAL REJECTED ] ────────────────> Fallback rerouting to │
│  Receiving hospital suddenly reports bed saturation.  next capable facility.│
│                                                                             │
│  [ EXCEPTION 2: NO DESTINATION FOUND ] ─────────────> Maximum on-site       │
│  No facility within transit radius has open beds.     stabilization & tele- │
│                                                       consultation protocol.│
│                                                                             │
│  [ EXCEPTION 3: DESTINATION BECOMES UNAVAILABLE ] ──> Dynamic in-transit    │
│  Catastrophic fire/failure at receiving hospital.     ambulance diversion.  │
│                                                                             │
│  [ EXCEPTION 4: TRANSPORT UNAVAILABLE ] ────────────> Emergency 108 mutual  │
│  No government ALS ambulance available.               aid / private voucher.│
│                                                                             │
│  [ EXCEPTION 5: TRANSFER INTERRUPTED ] ─────────────> En-route diversion to │
│  Patient collapses or ambulance breaks down en route. nearest emergency bay.│
│                                                                             │
│  [ EXCEPTION 6: PATIENT REFUSES TRANSFER ] ─────────> Statutory AMA consent │
│  Family refuses transfer due to distance/cost.        & home care fallback. │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Failure Response Protocols:

1. **Referral Rejected by Receiving Hospital:**
   - *Detection:* Receiving hospital dispatcher logs rejection flag (e.g., *"Casualty ICU at 100% capacity due to multi-casualty bus accident"*).
   - *System Action:* Instantly removes rejected facility from active corridor; $\text{FACILITYGRAPH}$ automatically queries the 2nd-ranked facility; generates updated referral transmission.
   - *Safety Guardrail:* Case never enters indefinite queue; doctor notified within 60 seconds.

2. **No Capable Destination Found within Transit Radius:**
   - *Detection:* All regional facilities report capability deficit or zero available beds.
   - *System Action:* Triggers the **Maximum Safe On-Site Stabilization Protocol**:
     - Alerts senior medical officer on-site.
     - Initiates statutory Tele-Consultation bridge with state medical college specialist (eSanjeevani / ABDM tele-link).
     - Renders conservative medical management bundle (parenteral antibiotics, fluid titrations) while holding in observation.

3. **Destination Becomes Unavailable While In-Transit:**
   - *Detection:* Emergency radio broadcast or alert from receiving hospital while ambulance is on the highway.
   - *System Action:* Generates an emergency **In-Transit Diversion Beacon**; alerts ambulance GPS / mobile tablet with alternate destination coordinates and pre-arrival notification.

4. **Transport Unavailable (Ambulance Gridlock):**
   - *Detection:* State emergency dispatch (108) reports $> 90$-minute wait for government ALS ambulance.
   - *System Action:* Prompts hospital administration to execute the **Emergency Transport Voucher Protocol** (contracted private ambulance or inter-district emergency mutual aid).

5. **Transfer Interrupted by Clinical Decompensation En Route:**
   - *Detection:* Paramedic flags acute respiratory arrest or shock index $> 1.4$ during highway transit.
   - *System Action:* System recalculates route to the **Nearest Stabilization Facility** (even if lower tier) to perform emergency endotracheal intubation or CPR before resuming tertiary transit.

6. **Patient / Family Refuses Transfer (Against Medical Advice - AMA):**
   - *Detection:* Family cites financial inability to afford stay in district city, cultural fears, or preference for home care.
   - *System Action:* Enforces strict medico-legal compliance:
     - Generates structured vernacular **High-Risk Transfer Refusal Consent Form**.
     - Requires dual signatures (attending doctor + family representative).
     - Provides best-available take-home oral medication regimen and explicit warning signs.
     - Logs `PATIENT_REFUSED_TRANSFER` to immutable audit trail.
