# CLINOVA AI — Media Processing & Multimodal Pipeline Architecture

> **Document ID:** `RES-146`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Multimedia Systems, Computer Vision & Speech Processing Group  

---

## 1. Asynchronous Multimodal Architecture

Processing high-resolution camera photos of crumpled paper prescriptions and multi-minute audio recordings of rural dialect interviews can take several seconds on edge hardware.

**Architectural Law:** Media processing must be **asynchronous and non-blocking**. The user interface must never freeze or assume optimistic success while background perceptual jobs are running.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MULTIMODAL PROCESSING PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STAGE 1: UPLOAD & CHECKSUM VERIFICATION ]                                │
│  ├── Client transmits binary chunk via multipart/form-data                  │
│  ├── Server computes SHA-256 cryptographic digest in-flight:                │
│  │   H = SHA256(file_bytes)                                                 │
│  └── Rejects corrupted uploads or unsupported MIME types                    │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 2: STORAGE TIER PERSISTENCE ]                                      │
│  ├── Writes raw binary to Storage Abstraction (Local FS / Supabase Storage) │
│  ├── Emits immutable record to `raw_evidence_sources`                       │
│  └── Relational DB stores ONLY file path, SHA-256, byte size, and MIME type │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 3: BACKGROUND JOB DISPATCH ]                                       │
│  ├── Enqueues processing task in lightweight async queue (FastAPI Background│
│  │   Tasks / Redis Queue where available)                                   │
│  └── Returns immediate 202 Accepted response with job_id to client          │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 4: PERCEPTUAL EXECUTION (OCR / ASR) ]                              │
│  ├── Visual Track: PaddleOCR / Tesseract (Deskew, crop, OCR, bounding box)  │
│  └── Acoustic Track: faster-whisper (VAD, 16kHz resample, word alignment)   │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 5: EXTRACTION & NORMALIZATION ]                                    │
│  ├── Parses numbers, dates, test names; normalizes to LOINC / SNOMED CT     │
│  └── Calculates physical quality (Laplacian variance, Audio SNR in dB)      │
│                                  │                                          │
│                                  ▼                                          │
│  [ STAGE 6: PROVENANCE BINDING & REVIEW READINESS ]                         │
│  ├── Inserts extracted fields into `evidence_records` (Epistemic: INFERRED) │
│  ├── Updates job status: COMPLETED (or FAILED)                              │
│  └── Emits WebSocket / polling notification to Nurse/Doctor UI              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Storage Tier Abstraction Architecture

To maintain zero mandatory cloud costs while supporting cloud deployments seamlessly, the media storage layer implements an abstract `MediaStorage` interface:

```python
from abc import ABC, abstractmethod
from typing import BinaryIO

class MediaStorage(ABC):
    """Abstract interface decoupling media storage from local or cloud backends."""
    
    @abstractmethod
    async def save_media(
        self, file_data: bytes, filename: str, mime_type: str
    ) -> str:
        """Stores binary media and returns an immutable canonical URI."""
        pass

    @abstractmethod
    async def get_media(self, uri: str) -> bytes:
        """Retrieves raw media bytes by canonical URI."""
        pass

    @abstractmethod
    async def purge_media(self, uri: str) -> bool:
        """Permanently purges raw binary file under retention policies."""
        pass
```

### Implementations:
1. **`LocalStorageAdapter` (Edge / On-Premise):**
   - Stores files in dedicated directory: `/var/data/clinova/media/{case_id}/{file_hash}.{ext}`.
   - Zero external cloud bandwidth consumed; 100% offline edge operational.
2. **`SupabaseStorageAdapter` (Cloud Multi-Facility):**
   - Stores files in private Supabase Storage bucket (`clinova-medical-media`).
   - Uses presigned URLs with 15-minute expirations for client previews.

---

## 3. Safe Failure & Degradation Handling

Under real-world rural conditions, cameras produce blurred images and recordings capture diesel generator noise:

| Failure Mode | Perceptual Signal | System Fallback Behavior | Frontline Clinical Impact |
| :--- | :--- | :--- | :--- |
| **Severe Blur / Glare** | Laplacian Variance $< 100.0$ | Job completes with status `OCR_QUALITY_WARNING`; extracts text with low confidence ($C < 0.50$) | UI shows amber alert: *"Blurry scan. Verify against physical slip."* Doctor sees side-by-side slip image. |
| **Acoustic Noise / Distortion** | Audio SNR $< 12.0\text{ dB}$ | ASR skips low-confidence segments; tags transcript `ACOUSTICALLY_UNRELIABLE` | Audio player highlights noisy segment; prompts nurse to ask patient directly. |
| **OCR Engine Crash / OOM** | Subprocess terminates | Job caught; marks document `EXTRACTION_FAILED`; logs error without halting API | Master Case remains active; document thumbnail remains viewable for manual entry. |
| **Network Timeout During Upload**| HTTP 408 / Socket drop | Client caches audio chunk in browser IndexedDB; auto-retries when connection stabilizes | Zero loss of patient interview recording. |

---

## 4. UI Non-Assumption Invariant

**Invariant MP-1 (Asynchronous Honesty):** The frontend UI must never display an extracted value as verified or present until the background extraction job status transitions to `COMPLETED` and the record is stored in the database. While processing, the UI explicitly renders a progress skeleton: *"Processing Prescription (OCR)..."* and allows the user to proceed with manual entry without waiting.
