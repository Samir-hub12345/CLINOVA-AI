# CLINOVA AI — Synthetic Data Default & Protected Health Information Safety Model

> **Document ID:** `RES-181`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Privacy, Healthcare Compliance & Data Governance Group  

---

## 1. The Synthetic Data Default Law

Under the **Digital Personal Data Protection (DPDP) Act, 2023**, processing of Protected Health Information (PHI) without unambiguous purpose limitation, explicit consent, or statutory medical necessity carries severe statutory penalties (up to ₹250 crore per breach).

**The Inviolable Synthetic Default Principle:**
$$\mathbf{Default\ Data\ Mode} = \mathbf{SYNTHETIC} \quad \forall \text{ non-certified deployments}$$

By default, any freshly cloned or booted instance of CLINOVA AI starts in **`CLINOVA_DATA_MODE=synthetic`**. It is strictly impossible for a developer, student, evaluator, or conference presenter to accidentally ingest, process, or leak real patient records during software development, automated testing, or demonstration.

---

## 2. The `CLINOVA_DATA_MODE` Configuration Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATA MODE SAFETY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ MODE 1: SYNTHETIC (Default) ]                                            │
│  ├── Required in: `DEV`, `LOCAL_DEMO`, `CLOUD_PREVIEW`, `TEST`.             │
│  ├── Uses pre-generated synthetic Master Cases (STEMI, Shock, COPD).        │
│  ├── Ingestion of real Aadhaar/ABHA credentials triggers immediate block.   │
│  └── Prominent UI banner: "SYNTHETIC MEDICAL DATA ONLY".                   │
│                                                                             │
│  [ MODE 2: LIVE (Clinical Operations) ]                                     │
│  ├── Permitted ONLY in: `DISTRICT_HOSPITAL` and `PHC_EDGE`.                 │
│  ├── Requires affirmative multi-key cryptographic authorization.            │
│  ├── Full 18-identifier DPDP/HIPAA de-identification active in memory.      │
│  └── Immutable Merkle audit logging permanently enabled.                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Quadruple-Check Validation Barrier for `LIVE` Mode

To switch an instance to `CLINOVA_DATA_MODE=live`, the backend startup validator enforces four mandatory prerequisites. If ANY check fails, the application refuses to start:

```python
# Startup Validation Barrier for Live Data Mode
@model_validator(mode="after")
def validate_live_data_authorization(self) -> "Settings":
    if self.CLINOVA_DATA_MODE == ClinovaDataMode.LIVE:
        # Check 1: Forbidden environment check
        if self.APP_ENV in [AppEnv.DEV, AppEnv.LOCAL_DEMO, AppEnv.TEST, AppEnv.CLOUD_PREVIEW]:
            raise ValueError(
                f"FATAL PRIVACY SAFETY VIOLATION: CLINOVA_DATA_MODE=live is strictly forbidden "
                f"in environment '{self.APP_ENV}'! Only certified physical facilities may run live data."
            )
            
        # Check 2: Affirmative production confirmation flag
        if not getattr(self, "CLINOVA_PRODUCTION_LIVE_CONFIRMED", False):
            raise ValueError(
                "FATAL PRIVACY SAFETY VIOLATION: Live patient data mode requires explicit "
                "CLINOVA_PRODUCTION_LIVE_CONFIRMED=true in configuration!"
            )
            
        # Check 3: Cryptographic secret key length
        if len(self.SECRET_KEY.get_secret_value()) < 64:
            raise ValueError(
                "FATAL PRIVACY SAFETY VIOLATION: Operating in live patient mode requires a "
                "production-grade SECRET_KEY of at least 64 characters!"
            )
            
        # Check 4: Audit mode must be strictly active
        if not self.AUDIT_MODE:
            raise ValueError(
                "FATAL COMPLIANCE VIOLATION: AUDIT_MODE=True is mandatory when running in live patient mode!"
            )

    return self
```

---

## 4. Synthetic Patient Case Bundles

In synthetic mode, the system bundles four clinically authentic, fully de-identified synthetic test episodes matching the Phase 6 Master Case specifications:
1. **Case STEMI-01 (Acute Coronary Syndrome):** 54-year-old male with radiating retrosternal chest pain, diaphoresis, and synthetic ECG slip showing ST-elevation.
2. **Case PED-02 (Pediatric Dehydration & Shock):** 3-year-old female with 4-day acute watery diarrhea, lethargy, capillary refill $> 3\text{s}$, and tachycardia.
3. **Case MAT-03 (Severe Pre-Eclampsia / Maternal):** 26-year-old primigravida at 34 weeks gestation with severe frontal headache, BP 170/110 mmHg, and trace pedal edema.
4. **Case TRAUMA-04 (Blunt Thoracoabdominal Trauma):** 32-year-old female motor-vehicle collision victim with tachypnea, fractured ribs, and sub-capsular hematoma.

Each synthetic case includes synthetic audio recordings, synthetic lab slips with pre-calculated bounding boxes, and multi-tier vitals trajectories.
