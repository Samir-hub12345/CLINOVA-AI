# CLINOVA AI — Optical Character Recognition (OCR) Provenance Model

> **Document ID:** `RES-110`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Perceptual OCR Reality & The Safety Invariant

In Indian healthcare settings (Public Health Centres, Community Health Centres, District Hospitals, and Industrial Health Outposts), the vast majority of prior medical records exist as **physical paper**: carbon-copy OPD cards, hand-scribbled referral slips, dot-matrix biochemistry lab printouts, and thermal-paper ECG strips.

Automated OCR is an invaluable tool for eliminating hours of manual data entry, but it is fundamentally an **imperfect perceptual projection**, not a source of truth. A crumpled receipt can turn `$15\text{ mg}$` into `$150\text{ mg}$`; a poor scan can invert `1.1` into `11`; a doctor's hurried cursive can render `Norflox` as `Norpace`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE CANONICAL OCR SAFETY INVARIANT                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│               NO OCR VALUE IS AUTOMATICALLY CLINICALLY VERIFIED.            │
│                                                                             │
│   Every value extracted by an optical engine enters the system tagged       │
│   as OCR_EXTRACTED with epistemic state INFERRED or UNRELIABLE.             │
│   Under no operational circumstance may OCR text update active baseline     │
│   physiology or clinical orders without human visual review.                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Spatial Provenance & The Bounding Box Architecture

To allow instant, friction-free verification by clinicians and nurses, every extracted datum must point back to its exact **spatial coordinates** on the source document.

### 2.1 Coordinate Normalization
Coordinates are stored as normalized bounding boxes within $[0, 1000]$ integer space to remain invariant across image downscaling, mobile screens, or high-DPI desktop monitors:
$$\mathbf{B} = [y_{\min}, x_{\min}, y_{\max}, x_{\max}] \quad \text{where } 0 \le y_{\min} < y_{\max} \le 1000, \quad 0 \le x_{\min} < x_{\max} \le 1000$$

When a clinician hovers over or taps any extracted lab parameter (e.g., `Serum Creatinine: 2.4 mg/dL`), the Doctor Workbench instantaneously displays a high-resolution, side-by-side cropped preview of the physical document image corresponding to bounding box $\mathbf{B}$.

---

## 3. Comprehensive Handling of Real-World OCR Edge Cases

| Real-World Scenario | Optical Phenomenon | System Detection Mechanism | Operational & Epistemic Response |
| :--- | :--- | :--- | :--- |
| **1. Clean Printed OCR** | Crisp 300 DPI lab report, standard fonts, high contrast. | Character confidence $> 0.92$, orientation angle $< 1.0^\circ$. | Tagged `KNOWN`. Populates draft intake form; highlighted for rapid 1-click confirmation. |
| **2. Partial OCR** | Half the page torn or obscured by shadow/thumb. | Segment detection indicates cropped table boundaries. | Unextracted fields remain `UNKNOWN` (Zero-Imputation); partial fields extracted with warning. |
| **3. Smudged Document** | Oil stain, water damage, or faint thermal printer ink. | Low character confidence ($C \in [0.40, 0.69]$), low local contrast. | Tagged `UNRELIABLE`. Bounding box highlighted with yellow warning: *"Smudged print — verify visually."* |
| **4. Rotated / Skewed Image** | Photo taken upside down or at a $45^\circ$ angle via mobile camera. | Orientation angle classifier detects skew $\theta$. | Automatic lossless deskew transform applied; original unrotated image hash preserved. |
| **5. Multiple Ambiguous Values** | Multi-column table where heading aligns with two numbers. | Spatial disambiguation assigns multiple candidate hypotheses $\{v_1, v_2\}$. | System surfaces multi-choice selector: *"Did the lab report Hb 11.2 or 14.1?"* Clinician selects. |
| **6. Erroneous OCR** | Confusion between characters (e.g. `O` vs `0`, `S` vs `5`, `mg` vs `mL`). | Regex validator detects clinical impossibility (e.g., Blood Glucose = 5000 mg/dL). | Hard-blocked by clinical boundary checks; flagged for mandatory manual re-entry. |
| **7. Duplicate OCR** | Same test reported twice on same page (repeat run). | Exact concept match with different values in same scan. | Instantiates `evidence_conflicts` with resolution prompt on doctor review screen. |
| **8. Handwritten Text** | Freehand cursive clinical notes by OPD physician. | Handwriting detector triggers; recognition confidence $< 0.50$. | Tagged `UNRELIABLE / INFERRED`. Raw bounding box displayed with prompt: *"Handwritten note — staff transcription needed."* |

---

## 4. OCR Provenance Schema Architecture

The OCR provenance layer binds `documents`, `document_ocr_pages`, `ocr_extracted_snippets`, and `evidence_records`:

```
┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
│    documents    │ 1───* │  document_ocr_pages  │ 1───* │ ocr_extracted_snippets │
│  (Raw Scan/PDF) │       │  (Page Deskew/Text)  │       │ (Bounding Box Entities)│
└─────────────────┘       └──────────────────────┘       └───────────┬────────────┘
                                                                     │ 1
                                                                     │
                                                                     │ 1
                                                              ┌──────▼─────────────┐
                                                              │  evidence_records  │
                                                              │  (Clinical State)  │
                                                              └────────────────────┘
```

### 4.1 Table Definition: `ocr_extracted_snippets`

```sql
CREATE TABLE ocr_extracted_snippets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
    page_number INTEGER NOT NULL CHECK (page_number >= 1),
    
    -- Spatial Bounding Box in Normalized 1000x1000 Grid
    bbox_ymin INTEGER NOT NULL CHECK (bbox_ymin >= 0 AND bbox_ymin <= 1000),
    bbox_xmin INTEGER NOT NULL CHECK (bbox_xmin >= 0 AND bbox_xmin <= 1000),
    bbox_ymax INTEGER NOT NULL CHECK (bbox_ymax >= bbox_ymin AND bbox_ymax <= 1000),
    bbox_xmax INTEGER NOT NULL CHECK (bbox_xmax >= bbox_xmin AND bbox_xmax <= 1000),
    
    raw_extracted_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    canonical_concept VARCHAR(64), -- LOINC or SNOMED CT code
    detected_numeric_value NUMERIC(10,3),
    detected_unit VARCHAR(32),
    
    -- Perceptual Engine Metadata
    ocr_engine_name VARCHAR(64) NOT NULL,    -- e.g., 'PaddleOCR-v4-Mobile'
    ocr_engine_version VARCHAR(32) NOT NULL, -- e.g., '4.1.2'
    character_confidence NUMERIC(4,3) NOT NULL CHECK (character_confidence >= 0.0 AND character_confidence <= 1.0),
    is_handwritten BOOLEAN NOT NULL DEFAULT FALSE,
    extraction_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Review and Verification Tracking
    review_status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (review_status IN (
        'PENDING', 'ACCEPTED', 'CORRECTED', 'REJECTED'
    )),
    reviewed_by_user_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    correction_delta JSONB -- Stores { "original": "15 mg", "corrected": "15 mL" }
);

CREATE INDEX ix_ocr_snip_case ON ocr_extracted_snippets(case_id);
CREATE INDEX ix_ocr_snip_doc ON ocr_extracted_snippets(document_id, page_number);
CREATE INDEX ix_ocr_snip_status ON ocr_extracted_snippets(review_status);
```

---

## 5. Visual Inspection Workflow on the Doctor Workbench

When an extracted snippet is presented on the user interface:
1. **Interactive Highlight:** The extracted field is rendered in a clean table alongside other clinical observations.
2. **One-Click Grounding Preview:** Clicking on the value opens an inline popover displaying the exact image crop bounded by $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$.
3. **Ergonomic Verification Actions:**
   - **Accept ($\checkmark$):** Single keystroke/click approves the reading. Links `evidence_records.verification_status = 'CONFIRMED'`.
   - **Correct ($\Delta$):** User edits the number in place. System records original OCR text, corrected value, and user ID in `correction_delta`.
   - **Reject ($\times$):** User dismisses the snippet as artifact or invalid noise.
4. **Audit Trail Preservation:** Rejection or correction does NOT delete the snippet row. It updates `review_status`, preserving complete historical transparency for forensic and quality audits.
