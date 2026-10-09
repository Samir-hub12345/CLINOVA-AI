# CLINOVA AI — Storage Configuration & Media Persistence Model

> **Document ID:** `RES-177`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Storage Systems, Media Processing & Privacy Engineering Group  

---

## 1. Architectural Storage Foundation & Abstraction

Clinical intake in CLINOVA AI is inherently multi-modal, capturing:
1. **Paper Prescriptions & Prior Lab Slips:** High-resolution digital photographs (JPEG/PNG) or multi-page PDF documents.
2. **Vernacular Patient Audio:** 15–60 second press-and-talk voice recordings in WAV or Opus/WebM formats.

To support both air-gapped rural clinics and cloud sandboxes, CLINOVA AI abstracts storage persistence behind a unified storage interface supporting two distinct engines:
- **`LOCAL_FS` (Local Filesystem):** Mandatory for `PHC_EDGE`, `LOCAL_DEMO`, `DISTRICT_HOSPITAL`, and `DEV`.
- **`SUPABASE_STORAGE` (Cloud Object Storage):** Used exclusively in `CLOUD_PREVIEW`.

---

## 2. Inviolable Security Invariant: No Public Directory Fallback

**The Core Privacy Law:**
$$\mathbf{Raw\ Patient\ Media} \cap \mathbf{Public\ Static\ Web\ Root} = \emptyset$$

Under no circumstances may raw audio recordings or patient document images be saved to a web-accessible public directory (such as `frontend/public/` or an unauthenticated Nginx web root). If local filesystem paths cannot be created or secured, the upload request terminates immediately with an error rather than falling back to an insecure public folder.

---

## 3. Storage Engine Specifications

### 3.1 Local Filesystem Engine (`LOCAL_FS`)
- **Directory Structure:**
  ```
  STORAGE_PATH/
  ├── prescriptions/      # Processed prescription images (JPEG/PNG)
  ├── lab_slips/          # Laboratory report images and PDFs
  ├── voice_recordings/   # Audio intake recordings (WAV/WebM)
  └── tmp/                # Transient chunks and temporary OCR crop buffers
  ```
- **Filesystem Permissions:** On Linux edge nodes (`PHC_EDGE` and `DISTRICT_HOSPITAL`), directory permissions must be strictly set to `0750` owned by `clinova:clinova`.
- **Pre-Flight Write Barrier:** During server boot, the application writes a transient `.clinova_storage_probe` file to `STORAGE_PATH` and deletes it. If write access fails, server startup halts with a fatal exit.

### 3.2 Supabase Storage Engine (`SUPABASE_STORAGE`)
- **Private Bucket Configuration:** Buckets (`clinova-preview-media`) must be marked **Private** with public read access disabled.
- **Signed URL Access:** The frontend never receives permanent public URLs. When a clinician views a slip crop or listens to an audio snippet, the backend generates an ephemeral signed URL with a **strict 15-minute time-to-live (TTL)**.
- **Row Level Security (RLS):** Supabase storage policies enforce that authenticated tokens can only access objects belonging to their active clinical facility.

---

## 4. Ingestion Constraints & Retention Policies

| Parameter | Default Value | District Hospital Value | Enforced Rule |
| :--- | :--- | :--- | :--- |
| **Allowed MIME Types** | `image/jpeg`, `image/png`, `application/pdf`, `audio/wav`, `audio/webm` | Same | Executable (`.exe`, `.sh`, `.js`) or unapproved MIME types rejected with HTTP 415. |
| **Max File Upload Size** | 15 MB (`15,728,640 bytes`) | 25 MB (`26,214,400 bytes`) | Enforced at HTTP body parser layer before buffering to disk. |
| **Media Retention Class**| 30 Days (DPDP Act) | 90 Days (Hospital Policy) | After expiration, automated retention daemon purges raw binary, leaving only cryptographic SHA-256 hash. |
| **Temp Buffer Cleanup** | Auto-purged every 60 min | Auto-purged every 60 min | Unfinished uploads or crashed audio streams in `tmp/` deleted. |

---

## 5. Storage Configuration Schema

```python
# Storage Settings Model
class StorageSettings(BaseModel):
    STORAGE_MODE: StorageMode = StorageMode.LOCAL_FS
    STORAGE_PATH: Path = Path("./data/storage")
    STORAGE_TEMP_PATH: Path = Path("./data/storage/tmp")
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024
    ALLOWED_MIME_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "application/pdf",
        "audio/wav",
        "audio/webm",
    ]
    MEDIA_RETENTION_POLICY_DAYS: int = 30
    SUPABASE_BUCKET_NAME: str = "clinova-media-private"
    SIGNED_URL_EXPIRATION_SECONDS: int = 900  # 15 minutes
```
