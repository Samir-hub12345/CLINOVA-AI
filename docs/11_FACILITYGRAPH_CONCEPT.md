# CLINOVA AI — FACILITYGRAPH Concept & Care Feasibility Model

> **Document ID:** `DOC-11`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. What is FACILITYGRAPH?

> **Core Definition:** FACILITYGRAPH is the real-time resource and capability intelligence layer of CLINOVA AI.
>
> Conventional triage calculates what a patient needs in theory, but remains completely blind to what the healthcare facility can actually execute in reality. FACILITYGRAPH models physical capabilities, equipment states, bed availability, and staffing to answer the paramount operational question:
> $$\mathbf{CAN\ THE\ REQUIRED\ CARE\ ACTUALLY\ BE\ DELIVERED\ HERE,}$$
> $$\mathbf{AND\ WHERE\ ELSE\ IN\ THE\ REGIONAL\ NETWORK\ CAN\ IT\ SAFELY\ HAPPEN?}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FACILITYGRAPH ENGINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [ FACILITY RESOURCE TOPOLOGY ]                                            │
│   • Emergency Resuscitation Capabilities (Airway, Defib, Suction, Chest Tube)│
│   • Specialty Services (Pediatrics, OB-GYN, General Surgery, Orthopedics)   │
│   • Diagnostic Services (24x7 Lab, X-Ray, Ultrasound, CT, Blood Bank)      │
│   • Operational Capacity (ICU Beds, Emergency Beds, Ward Beds, Ventilators) │
│   • Active Queue Pressure & Average Physician Wait Times                   │
│   • On-Duty Medical Officer & Specialist Rosters                            │
│   • Geographic Coordinates & Regional Network Interconnects                 │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│   [ EVALUATION FUNCTION ]                                                   │
│   Patient Requirements + Urgency + Local Capability + Capacity + Distance   │
│                                                                             │
│                                     │                                       │
│                                     ▼                                       │
│   [ CARE FEASIBILITY OUTCOMES ]                                             │
│   ├── 1. SUITABLE HERE (Local care fully executable on-site)                │
│   ├── 2. SUITABLE WITH CONDITIONS (Manage locally under close observation)  │
│   ├── 3. CURRENT FACILITY INSUFFICIENT (Immediate capability deficit)       │
│   ├── 4. ALTERNATIVE FACILITY RECOMMENDED (Optimal destination identified)  │
│   └── 5. URGENT TRANSFER PATHWAY (Emergency golden-hour bypass transfer)    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Facility Capability Modeling

FACILITYGRAPH models healthcare institutions as active capability nodes across five standardized resource tiers:

### 2.1 Capability Inventory Dimensions
1. **Emergency & Resuscitation Capability:**
   - Level 0 (None): First-aid only.
   - Level 1 (Basic): Bag-valve-mask, oxygen cylinder, basic IV fluids, oral rehydration.
   - Level 2 (Advanced): Endotracheal intubation, mechanical ventilator, multiparameter monitors, defibrillator, emergency vasopressors.
   - Level 3 (Comprehensive Tertiary): 24/7 dedicated trauma resuscitation team, arterial lines, ECMO capability.
2. **Specialist & Human Resource Availability:**
   - Live roster tracking on-duty presence: General Medicine, General Surgery, Pediatrics, Obstetrics & Gynecology, Orthopedics, Anesthesia, Critical Care.
3. **Diagnostic Infrastructure:**
   - Laboratory: Point-of-care rapid tests (malaria, dengue NS1, urine dipstick) vs. automated hematology (CBC, PT/INR) vs. arterial blood gas (ABG).
   - Imaging: None vs. Portable Ultrasound / FAST vs. Plain Radiography vs. 24/7 Contrast CT / MRI.
   - Blood Products: None vs. Blood storage unit (PRBC only) vs. Full licensed blood bank with component separation (Platelets, FFP, Cryoprecipitate).
4. **Bed Capacity & Occupancy Pressure:**
   - Total beds vs. Occupied beds across: Emergency Resuscitation, Intensive Care Unit (ICU), High Dependency Unit (HDU), General Male/Female Wards.
   - Real-time occupancy percentage ($> 90\%$ triggers capacity alert).

---

## 3. Care Feasibility Synthesis

Care Feasibility determines whether the clinical requirements dictated by CAREGRAPH match the operational reality of the facility:

$$\mathbf{Care\ Feasibility} = \mathcal{F}\Big(\text{Req}(\text{CareGraph}),\ \text{Cap}(\text{Facility}),\ \text{QueuePressure},\ \text{GeoDist}\Big)$$

### 3.1 The Five Feasibility Outcomes
1. `SUITABLE_HERE`:
   - The current facility possesses all necessary diagnostics, medications, beds, and specialists required to safely manage the patient.
   - Action: Proceed with on-site consultation and treatment.
2. `SUITABLE_WITH_CONDITIONS`:
   - The facility can initiate stabilization and manage the patient, provided serial monitoring is maintained and contingency transfer protocols are placed on standby.
   - Action: Retain for structured observation in the short-stay ward.
3. `CURRENT_FACILITY_INSUFFICIENT`:
   - The patient exhibits critical needs that exceed local capabilities (e.g., patient with acute subdural hematoma presents at a rural PHC lacking neurosurgery and CT imaging).
   - Action: Halt non-essential intake steps; initiate immediate stabilization and prepare referral pack.
4. `ALTERNATIVE_FACILITY_RECOMMENDED`:
   - The patient is clinically stable but requires elective or semi-urgent specialized evaluation available at an interconnected network facility.
   - Action: Generate non-emergency referral documentation and appointment booking.
5. `URGENT_TRANSFER_PATHWAY`:
   - Severe physiological instability requiring emergency transfer to the nearest tertiary center equipped with open ICU beds and active surgical suites.
   - Action: Trigger ambulance dispatch, alert receiving trauma team, and transmit the Emergency Transfer Pack.

---

## 4. Zero-Cost Geospatial & Mapping Strategy

CLINOVA AI strictly avoids expensive, proprietary map APIs (e.g., Google Maps Platform, Mapbox) to ensure long-term sustainability across resource-limited public health environments.

### 4.1 Architecture of the Zero-Cost Mapping Stack
- **Mapping Engine:** [Leaflet.js](https://leafletjs.com/) (Open-source interactive map renderer).
- **Tile Server:** [OpenStreetMap](https://www.openstreetmap.org/) (OSM) public free tile layers (`tile.openstreetmap.org`).
- **Geospatial Distance Engine:** Client-side and server-side local **Haversine formula** computing great-circle distances:
  $$d = 2r \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
- **Travel Time Heuristic:** Local road terrain travel velocity models (e.g., rural unpaved roads: 30 km/h; national highway: 60 km/h; urban congestion: 20 km/h) yielding realistic transit estimations without paid routing API dependencies.
- **Synthetic Facility Coordinates:** The prototype utilizes synthetic latitude/longitude coordinates simulating regional health networks across Odisha and India. All simulated facility capacity and telemetry are explicitly flagged as `SIMULATED_SAMPLE_DATA`.

---

## 5. UI Representation of Feasibility

The FACILITYGRAPH UI moves beyond simple lists of hospital names:
1. **Feasibility Radar / Badge:** Immediate color-coded status badge (`SUITABLE HERE` vs. `CAPABILITY DEFICIT`).
2. **Capability Matching Matrix:** Side-by-side comparison table matching patient requirements against facility resources:
   - *Required: Blood Platelet Transfusion* ──> *Local Status: ❌ No Platelet Agitator (Nearest: Capital Hospital, 18 km)*
   - *Required: Mechanical Ventilation* ──> *Local Status: ⚠️ 2/2 ICU Ventilators Currently Occupied*
3. **Interactive Network Map:** Clean Leaflet view showing the patient's current location, nearby facilities, real-time bed availability indicators, and verified transit distance.
4. **Referral Destination Recommender:** Ranked list of target facilities sorted by composite feasibility score:
   $$\text{Score} = w_1 \text{CapabilityMatch} + w_2 \text{OpenBeds} + w_3 (1 / \text{Distance})$$
