# CLINOVA AI — Media & Document Extraction Data Model

> **Document ID:** `RES-84`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Visual & Acoustic Grounding

In resource-constrained frontline clinics across India, patient intake heavily relies on:
1. **Vernacular Speech:** Spoken Odia, Hindi, or conversational regional dialects.
2. **Physical Documents:** Handwritten crumpled doctor prescription slips, government diagnostic lab printouts, and referral slips.

If an AI system extracts entities (e.g. `Metformin 500mg BID`) into structured JSON without retaining exact spatial bounding boxes on the original image, or transcribes symptoms without audio playback timestamps, clinicians cannot verify accuracy under high OPD pressure.

CLINOVA AI enforces **Bi-directional Visual & Acoustic Grounding**:
Every extracted clinical fact maintains an immutable relational pointer to:
- The exact audio recording, duration offset, and word confidence score.
- The exact document page, bounding box coordinates $[y_{\min}, x_{\min}, y_{\max}, x_{\max}]$, and raw OCR text crop.

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MULTIMODAL EXTRACTION SCHEMA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── audio_recordings (audio_id PK, case_id FK)                           │
│    │     └── audio_transcripts (transcript_id PK, audio_id FK)              │
│    │           └── word_alignment_spans (word_id PK, transcript_id FK)      │
│    │                                                                        │
│    └── documents (document_id PK, case_id FK)                               │
│          └── document_ocr_pages (page_id PK, document_id FK)                │
│                └── ocr_extracted_snippets (snippet_id PK, page_id FK)       │
│                      └── Bound to evidence_records (field_name, value)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 Audio Recordings & Transcripts

```sql
CREATE TABLE audio_recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    file_path VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64) NOT NULL, -- SHA-256
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(64) NOT NULL DEFAULT 'audio/webm',
    duration_seconds NUMERIC(6,2) NOT NULL,
    sample_rate_hz INTEGER NOT NULL DEFAULT 16000,
    recorded_by_actor_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audio_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    audio_id UUID NOT NULL REFERENCES audio_recordings(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    whisper_model VARCHAR(64) NOT NULL, -- e.g., 'faster-whisper-small-int8'
    detected_language VARCHAR(16) NOT NULL, -- 'or', 'hi', 'en'
    language_probability NUMERIC(4,3) NOT NULL,
    raw_transcript_native TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    transcription_latency_ms INTEGER NOT NULL,
    confidence_score NUMERIC(4,3) NOT NULL,
    word_timestamps JSONB NOT NULL DEFAULT '[]'::jsonb,
    review_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED'
        CHECK (review_status IN ('UNVERIFIED', 'CONFIRMED', 'EDITED', 'REJECTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.2 Documents, OCR Pages & Extracted Snippets

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    document_type VARCHAR(32) NOT NULL CHECK (document_type IN (
        'PRESCRIPTION_SLIP', 'LAB_REPORT', 'DISCHARGE_SUMMARY', 
        'REFERRAL_NOTE', 'RADIOLOGY_REPORT', 'IDENTITY_CARD', 'OTHER'
    )),
    file_path VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64) NOT NULL, -- SHA-256 of image/PDF
    mime_type VARCHAR(64) NOT NULL, -- 'image/jpeg', 'application/pdf'
    file_size_bytes BIGINT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 1,
    uploaded_by_actor_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_ocr_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    page_number INTEGER NOT NULL DEFAULT 1,
    ocr_engine VARCHAR(64) NOT NULL, -- 'paddleocr-v4-quantized', 'tesseract-5'
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,
    ocr_raw_text TEXT NOT NULL,
    mean_confidence NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_doc_page UNIQUE (document_id, page_number)
);

CREATE TABLE ocr_extracted_snippets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES document_ocr_pages(id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    bounding_box JSONB NOT NULL, -- [ymin, xmin, ymax, xmax] normalized [0, 1000]
    raw_snippet_text TEXT NOT NULL,
    confidence_score NUMERIC(4,3) NOT NULL,
    target_field VARCHAR(64) NOT NULL, -- e.g., 'medication_name', 'fasting_blood_sugar'
    normalized_value JSONB NOT NULL,   -- { "drug": "Metformin", "dose": 500, "unit": "mg" }
    review_status VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED'
        CHECK (review_status IN ('UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'REJECTED')),
    reviewed_by_actor_id UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_snippets_case_field ON ocr_extracted_snippets(case_id, target_field);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE audio_recordings (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL DEFAULT 'audio/webm',
    duration_seconds REAL NOT NULL,
    sample_rate_hz INTEGER NOT NULL DEFAULT 16000,
    recorded_by_actor_id TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE TABLE audio_transcripts (
    id TEXT PRIMARY KEY NOT NULL,
    audio_id TEXT NOT NULL REFERENCES audio_recordings(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    whisper_model TEXT NOT NULL,
    detected_language TEXT NOT NULL,
    language_probability REAL NOT NULL,
    raw_transcript_native TEXT NOT NULL,
    english_translation TEXT NOT NULL,
    transcription_latency_ms INTEGER NOT NULL,
    confidence_score REAL NOT NULL,
    word_timestamps TEXT NOT NULL DEFAULT '[]', -- JSON string
    review_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (review_status IN ('UNVERIFIED', 'CONFIRMED', 'EDITED', 'REJECTED')),
    created_at TEXT NOT NULL
);

CREATE TABLE documents (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    document_type TEXT NOT NULL CHECK (document_type IN (
        'PRESCRIPTION_SLIP', 'LAB_REPORT', 'DISCHARGE_SUMMARY', 
        'REFERRAL_NOTE', 'RADIOLOGY_REPORT', 'IDENTITY_CARD', 'OTHER'
    )),
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 1,
    uploaded_by_actor_id TEXT NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE TABLE document_ocr_pages (
    id TEXT PRIMARY KEY NOT NULL,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    page_number INTEGER NOT NULL DEFAULT 1,
    ocr_engine TEXT NOT NULL,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,
    ocr_raw_text TEXT NOT NULL,
    mean_confidence REAL NOT NULL,
    created_at TEXT NOT NULL,
    CONSTRAINT uq_doc_page UNIQUE (document_id, page_number)
);

CREATE TABLE ocr_extracted_snippets (
    id TEXT PRIMARY KEY NOT NULL,
    page_id TEXT NOT NULL REFERENCES document_ocr_pages(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    bounding_box TEXT NOT NULL, -- JSON string: [ymin, xmin, ymax, xmax]
    raw_snippet_text TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    target_field TEXT NOT NULL,
    normalized_value TEXT NOT NULL, -- JSON string
    review_status TEXT NOT NULL DEFAULT 'UNVERIFIED' CHECK (review_status IN ('UNVERIFIED', 'CONFIRMED', 'MODIFIED', 'REJECTED')),
    reviewed_by_actor_id TEXT REFERENCES users(id),
    reviewed_at TEXT,
    created_at TEXT NOT NULL
);
```

---

## 5. Invariants Governing Media & Extraction

$$\begin{aligned}
\mathbf{Inv\ MEDIA\text{-}1} &: \quad \forall s \in \text{ExtractedSnippets}, \quad s.\text{case\_id} = \text{DocumentPages}(s.\text{page\_id}).\text{case\_id} \\
\mathbf{Inv\ MEDIA\text{-}2} &: \quad \forall d \in \text{Documents}, \quad d.\text{file\_hash} = \text{SHA256}(\text{BlobBytes}(d.\text{file\_path})) \\
\mathbf{Inv\ MEDIA\text{-}3} &: \quad \forall s \in \text{ExtractedSnippets}, \quad s.\text{bounding\_box} = [y_1, x_1, y_2, x_2] \implies (0 \le y_1 < y_2 \le 1000) \land (0 \le x_1 < x_2 \le 1000) \\
\mathbf{Inv\ MEDIA\text{-}4} &: \quad \text{Any extraction displayed on Doctor Workbench MUST expose clickable URI to parent crop / audio.}
\end{aligned}$$
