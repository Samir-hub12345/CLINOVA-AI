# CLINOVA AI — Evidence Reliability, Quality & Confidence Model

> **Document ID:** `RES-115`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Fallacy of the Monolithic Confidence Score

In machine learning and clinical informatics, a pervasive anti-pattern is the collapse of distinct epistemic dimensions into a single scalar "confidence score" (e.g. `confidence: 0.87`). 

When an engineer or system collapses signal fidelity, model uncertainty, human trust, and institutional origin into a single number, critical distinctions vanish:
- A perfectly sharp 600 DPI scan ($Q=0.98$) of an illegible cursive signature ($C=0.12$) is mashed into $0.55$.
- A noisy audio snippet ($Q=0.30$) where a patient repeatedly and clearly screams *"chest pain"* ($C=0.95$) is mashed into $0.62$.
- A high-confidence hallucination by a language model ($C=0.99$) is conflated with an attested clinical verification by a senior physician ($V=\text{VERIFIED}$).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE FIVE-AXIS DECOUPLING LAW OF EVIDENCE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  DO NOT COLLAPSE SOURCE, PROVENANCE,                        │
│             CONFIDENCE, QUALITY, AND VERIFICATION INTO ONE.                 │
│                                                                             │
│   Clinical reliability is an emergent property of five orthogonal axes.     │
│   Each axis must be measured, stored, and audited independently.            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Five Orthogonal Evidence Dimensions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE FIVE ORTHOGONAL EVIDENCE AXES                       │
├──────────────────┬──────────────────────────────────────────────────────────┤
│ 1. SOURCE        │ Where did the datum originate? (Modality & Actor Class)  │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 2. PROVENANCE    │ What is the unbroken audit lineage back to raw media?    │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 3. QUALITY       │ What is the physical signal fidelity of the raw medium?  │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 4. CONFIDENCE    │ What is the calibrated statistical certainty of the model│
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 5. VERIFICATION  │ Has an authenticated human clinician legally attested it?│
└──────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Axis Specifications

### 3.1 Axis 1: Source Class ($\mathcal{S}$)
- **Domain:** Discrete 8-member enumeration:
  $$\mathcal{S} \in \{\text{PATIENT\_REPORTED}, \text{VOICE\_TRANSCRIBED}, \text{OCR\_EXTRACTED}, \text{CLINICIAN\_VERIFIED}, \text{STAFF\_ENTERED}, \text{AI\_INFERRED}, \text{SYSTEM\_DERIVED}, \text{EXTERNAL\_RECORD}\}$$
- **Role:** Governs statutory legal scope, default trust tier, and downstream procedural authority.

### 3.2 Axis 2: Provenance Lineage ($\mathcal{P}$)
- **Domain:** Cryptographic DAG of foreign key pointers, SHA-256 media hashes, hardware device IDs, and spatial/acoustic offsets $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$ or $[t_{\text{start}}, t_{\text{end}}]$.
- **Role:** Enables instant one-click physical grounding on the clinician workbench.

### 3.3 Axis 3: Physical Signal Quality ($Q \in [0.00, 1.00]$)
- **Domain:** Objective, non-probabilistic measurement of raw signal integrity.
- **Audio Quality Metrics:**
  - Spectral Signal-to-Noise Ratio: $\text{SNR}_{\text{dB}} = 10 \log_{10}(P_{\text{signal}} / P_{\text{noise}})$
  - Mapping: $Q_{\text{audio}} = \min(1.0, \max(0.0, (\text{SNR}_{\text{dB}} - 5) / 25))$
- **Image Quality Metrics:**
  - Laplacian Blur Variance: $\sigma^2_{\text{Laplace}} = \text{Var}(\nabla^2 I)$
  - Resolution (DPI): Evaluated against minimum 150 DPI clinical readability baseline.
  - Mapping: $Q_{\text{image}} = \min(1.0, \max(0.0, \sigma^2_{\text{Laplace}} / 500))$
- **Sensor Quality Metrics:**
  - Plethysmograph perfusion index (PI) for pulse oximetry ($Q \ge 0.80$ if $\text{PI} \ge 1.0\%$).

### 3.4 Axis 4: Calibrated Statistical Confidence ($C \in [0.00, 1.00]$)
- **Domain:** Calibrated probability that the extracted textual token or entity matches ground truth.
- **Strict Prohibition:** **No Fabricated Probability Claims.** Raw Softmax probabilities from uncalibrated neural networks or LLMs are notoriously overconfident and cannot be stored directly.
- **Calibration Requirement:** Model probabilities must be calibrated using **Temperature Scaling** or **Isotonic Regression** evaluated on empirical medical benchmarks:
  $$\hat{P}(Y = y | X) = \frac{\exp(z_y / T)}{\sum_j \exp(z_j / T)}$$
  Where temperature $T$ is tuned to minimize the Expected Calibration Error (ECE):
  $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right| < 0.05$$
- **Interpretation Guidelines:**
  - $C \ge 0.90$: High statistical reliability; eligible for automated draft pre-fill.
  - $0.70 \le C < 0.90$: Moderate confidence; flagged for explicit staff review.
  - $C < 0.70$: Low confidence; tagged `UNRELIABLE`, suppressed from automatic pre-fill.

### 3.5 Axis 5: Human Verification Status ($\mathcal{V}$)
- **Domain:** Discrete attestation state:
  $$\mathcal{V} \in \{\text{UNVERIFIED}, \text{STAFF\_VERIFIED}, \text{CLINICIAN\_APPROVED}, \text{DISPUTED}, \text{REJECTED}\}$$
- **Role:** Sole legal determinant of clinical validity under NMC Regulations 2023.

---

## 4. Multi-Axis Interaction Matrix

To demonstrate why collapsing these dimensions is dangerous, consider four clinical real-world combinations:

| Clinical Scenario | Source ($\mathcal{S}$) | Quality ($Q$) | Confidence ($C$) | Verification ($\mathcal{V}$) | Safe System Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Clean Printed Lab** | `OCR_EXTRACTED` | **0.98** (Sharp scan) | **0.96** (Crisp print) | `UNVERIFIED` | Surfaces draft value; 1-click nurse confirmation required. |
| **B. Illegible Doctor Note** | `OCR_EXTRACTED` | **0.95** (Sharp scan) | **0.18** (Garbled cursive)| `UNRELIABLE` | Displays raw image crop; forces manual human transcription. |
| **C. Faint Thermal Printout**| `OCR_EXTRACTED` | **0.35** (Faded receipt)| **0.92** (Clear digits) | `UNRELIABLE` | Alerts nurse: *"Low image quality — please confirm digits visually."* |
| **D. Noisy Rural Audio** | `VOICE_TRANSCRIBED`| **0.25** (Generator noise)| **0.40** (Muffled speech)| `UNRELIABLE` | Hard-blocks automated entity extraction; prompts re-recording. |

---

## 5. Relational Schema Representation

```sql
-- Schema embedding independent dimensions in evidence_records
ALTER TABLE evidence_records
ADD COLUMN source_quality_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 
    CHECK (source_quality_score >= 0.0 AND source_quality_score <= 1.0),
ADD COLUMN confidence_score NUMERIC(4,3) NOT NULL DEFAULT 1.000 
    CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
ADD COLUMN confidence_calibration_method VARCHAR(32) DEFAULT 'PLATT_SCALING' 
    CHECK (confidence_calibration_method IS NULL OR confidence_calibration_method IN (
        'PLATT_SCALING', 'ISOTONIC_REGRESSION', 'ENSEMBLE_VARIANCE', 'DETERMINISTIC_DIRECT'
    ));

-- Check constraint: AI_INFERRED records MUST specify a non-trivial confidence score
ALTER TABLE evidence_records
ADD CONSTRAINT chk_ai_confidence_bounded
CHECK (
    source_type != 'AI_INFERRED' OR (confidence_score >= 0.0 AND confidence_score <= 1.0)
);
```

By decoupling these five vectors, CLINOVA AI provides clinicians with complete epistemological transparency: doctors can see whether a datum was clear or degraded, whether a model was certain or guessing, and whether a colleague has verified it.
