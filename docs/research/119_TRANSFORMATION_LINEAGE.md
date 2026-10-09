# CLINOVA AI — Data Transformation Lineage & Reversibility Model

> **Document ID:** `RES-119`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Transformation Opacity Risk

In modern clinical AI architectures, raw sensory inputs undergo intense, multi-stage data processing pipelines before reaching the physician. An acoustic wave spoken in rural Odia is decoded into vernacular text, translated into English, parsed into symptoms, mapped to SNOMED CT concepts, and synthesized into a summary note.

If these transformations occur within an opaque "black box", disastrous epistemic hazards emerge:
- A mistranslation changes *"I feel lightheaded when standing"* into *"Vertigo"*, misdirecting the workup from orthostatic hypotension to vestibular neuritis.
- A unit conversion failure multiplies a pediatric drug dose by $1000$ ($0.5\text{ mg}$ converted erroneously to $500\text{ mg}$).
- An LLM summarization silently drops an allergy to Penicillin because it occurred in a secondary clause.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               THE CANONICAL TRANSFORMATION LINEAGE INVARIANT                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│               NEVER LET TRANSFORMED TEXT HIDE THE ORIGINAL SOURCE.          │
│                                                                             │
│   Every transformation step must maintain an explicit, tamper-evident audit │
│   linkage recording input, output, transformer engine, version, and         │
│   reversibility. The physician must always be able to inspect the original  │
│   pre-transformation source in one click.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Eight Canonical Transformation Operations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EIGHT CANONICAL TRANSFORMATION TYPES                    │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Transformation Type      │ Operational Role & Mathematical Function         │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 1. SPEECH_TO_TEXT        │ Acoustic wave decoding -> vernacular tokens      │
│ 2. TRANSLATION           │ Vernacular language (Odia/Hindi) -> English      │
│ 3. OCR_LAYOUT_ANALYSIS   │ Visual document pixel crop -> ASCII text         │
│ 4. STRING_NORMALIZATION  │ Regex parsing of messy numbers ("120 / 80")      │
│ 5. UNIT_CONVERSION       │ Metric/Imperial math ($F \to C, \text{mg/dL} \to \text{mmol/L}$)   │
│ 6. CONCEPT_MAPPING       │ Text phrase -> Standard SNOMED CT / LOINC code   │
│ 7. DERIVED_CALCULATION   │ Multi-vital input vector -> NEWS2 composite score│
│ 8. CLINICAL_SUMMARIZATION│ Longitudinal narrative -> Structured SBAR summary│
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 3. Transformation Rigor Specifications

For every single transformation executed across the platform, eight mandatory invariant attributes are captured:

| Transformation Attribute | Semantic Definition | Concrete Exemplar |
| :--- | :--- | :--- |
| **1. Input Reference** | Foreign key pointer to source record or input blob. | `raw_text = "B.P: 190 / 110 mmHg"` |
| **2. Output Artefact** | Transformed payload or newly generated entity. | `json = { "sbp": 190, "dbp": 110, "unit": "mmHg" }` |
| **3. Transformer Engine** | Exact software library, model, or rule script. | `PaddleOCR-v4-Layout` or `clinova-unit-converter` |
| **4. Engine / Model Version**| Semantic version or checkpoint hash. | `v4.1.0-sha256:d89e...` |
| **5. Execution Timestamp**| Microsecond server time of execution. | `2026-10-08T10:14:22.184Z` |
| **6. Transformation Confidence**| Calibrated accuracy metric of transformation. | `0.984` (Rule-based: `1.000`) |
| **7. Reversibility Class** | Whether original input can be mathematically recovered. | `FULLY_REVERSIBLE` vs `LOSSY_ONE_WAY` |
| **8. Parent Source Link** | Pointer to root physical source media. | FK to `documents.id` or `audio_recordings.id` |

---

## 4. Reversibility Taxonomy

Not all transformations can be inverted. CLINOVA AI classifies transformations into three distinct **Reversibility Classes**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REVERSIBILITY TAXONOMY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. FULLY_REVERSIBLE (Bijective):                                            │
│    • Unit Conversions: °F <--> °C, lbs <--> kg                              │
│    • Lossless Audio Compression: FLAC <--> WAV                              │
│    • Original value is mathematically recoverable from output.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. PARTIALLY_REVERSIBLE (Lossy with State Anchor):                          │
│    • Translation: Odia <--> English (semantic nuances shift)                 │
│    • Concept Mapping: "Chest ache" --> SNOMED CT 29857009 (loses phrasing)  │
│    • Reversible ONLY by retaining original text side-by-side.                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. IRREVERSIBLE (Purely One-Way Reductive):                                 │
│    • Derived Scores: NEWS2 = 7 (Cannot reconstruct original BP, RR, SpO2)   │
│    • Clinical Summarization: SBAR (Drops narrative conversational nuances)  │
│    • Mandatory Rule: Input snapshot must be immutably stored in lineage.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Canonical Transformation Relational Schema

```sql
CREATE TABLE transformation_lineage_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    
    transformation_type VARCHAR(32) NOT NULL CHECK (transformation_type IN (
        'SPEECH_TO_TEXT', 'TRANSLATION', 'OCR_LAYOUT_ANALYSIS', 
        'STRING_NORMALIZATION', 'UNIT_CONVERSION', 'CONCEPT_MAPPING', 
        'DERIVED_CALCULATION', 'CLINICAL_SUMMARIZATION'
    )),
    
    -- Input & Output Linkages
    input_entity_type VARCHAR(32) NOT NULL, -- e.g. 'audio_recordings', 'raw_ocr_box'
    input_entity_id UUID NOT NULL,
    input_payload_snapshot JSONB NOT NULL,
    
    output_entity_type VARCHAR(32) NOT NULL, -- e.g. 'evidence_records', 'symptoms'
    output_entity_id UUID NOT NULL,
    output_payload_snapshot JSONB NOT NULL,
    
    -- Engine and Algorithmic Provenance
    transformer_name VARCHAR(64) NOT NULL,
    transformer_version VARCHAR(32) NOT NULL,
    prompt_or_rule_version_hash CHAR(64), -- SHA-256 of prompt template or regex script
    execution_time_ms INTEGER NOT NULL CHECK (execution_time_ms >= 0),
    transformed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Fidelity & Reversibility
    transformation_confidence NUMERIC(4,3) NOT NULL DEFAULT 1.000 
        CHECK (transformation_confidence >= 0.0 AND transformation_confidence <= 1.0),
    reversibility_class VARCHAR(24) NOT NULL CHECK (reversibility_class IN (
        'FULLY_REVERSIBLE', 'PARTIALLY_REVERSIBLE', 'IRREVERSIBLE'
    )),
    
    root_source_media_id UUID REFERENCES raw_evidence_sources(id) ON DELETE RESTRICT
);

CREATE INDEX ix_trans_case ON transformation_lineage_events(case_id);
CREATE INDEX ix_trans_input ON transformation_lineage_events(input_entity_id);
CREATE INDEX ix_trans_output ON transformation_lineage_events(output_entity_id);
CREATE INDEX ix_trans_root ON transformation_lineage_events(root_source_media_id);
```

---

## 6. Doctor Workbench Grounding Experience

When an extracted concept is rendered on screen:
1. Hovering over the concept displays a tooltip:
   ```
   SNOMED CT: 29857009 (Chest Pain)
   ├── Extracted by: clinova-multilingual-extract-v2.1
   ├── Translated from: "ମୋ ଛାତିରେ ଭୀଷଣ କଷ୍ଟ ହେଉଛି" (Odia)
   ├── Source: Audio Recording #aud_89f1 [00:01.2 - 00:04.5]
   └── View Raw Audio [Play]
   ```
2. The physician is never forced to trust an algorithmic black box. The entire transformation chain is transparent, reversible, and auditable in real time.
