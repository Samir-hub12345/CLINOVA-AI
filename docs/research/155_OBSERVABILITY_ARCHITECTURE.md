# CLINOVA AI — Clinical Observability & Telemetry Architecture

> **Document ID:** `RES-155`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Site Reliability Engineering, Observability & Medical Privacy Systems Group  

---

## 1. The Clinical Observability Paradox & Privacy Invariant

In standard distributed applications, debugging encourages verbose logging of incoming request bodies and database payloads. In a healthcare system, blindly logging request payloads causes severe privacy violations: personal health information (patient names, HIV status, intimate domestic trauma histories) leaks into plaintext log files, Elasticsearch clusters, and developer terminals.

**The Foundational Privacy Invariant:**
$$\mathbf{Inv\ OBS\text{-}1} \quad (\text{Zero PHI in Logs}): \quad \forall l \in \text{SystemLogs}, \quad l \cap \text{PHI\_FIELDS} = \emptyset$$

CLINOVA AI enforces structured logging with **in-flight PHI masking**. Operational logs capture performance metrics, error stack traces, execution durations, and correlation UUIDs, but **never raw patient text, audio recordings, or clinical narratives**.

---

## 2. Structured Logging Schema & Correlation Tracing

All backend services emit structured JSON logs via Python's standard `logging` library configured with a custom JSON formatter:

```json
{
  "timestamp": "2026-10-08T10:45:12.345Z",
  "level": "ERROR",
  "service": "clinova-backend",
  "module": "app.domain.multimodal_media.ocr_service",
  "request_id": "req-884a20b1-419b-43d2-a720-bc56e189d201",
  "case_id": "cas-2026-001042",
  "actor_id": "usr-nurse-priya-01",
  "event_type": "OCR_PROCESSING_FAILED",
  "error_code": "IMAGE_DECODE_ERROR",
  "duration_ms": 342.5,
  "context": {
    "file_mime": "image/jpeg",
    "file_size_bytes": 4512030,
    "laplacian_variance": 42.1,
    "quality_status": "UNREADABLE_BLUR"
  },
  "message": "PaddleOCR processing failed due to severe image blur; fallback triggered."
}
```

### Traceability without Privacy Leakage
Notice that while the log captures the technical failure (`IMAGE_DECODE_ERROR`), the image file size, and the correlation `case_id`, it contains **zero patient demographic data or transcribed clinical text**.

---

## 3. Subsystem Health Probes & Monitoring Matrix

CLINOVA exposes standardized health endpoints for container orchestrators (Docker, Kubernetes) and local edge monitoring daemons:

| Probe Endpoint | Purpose | Subsystems Checked | Failure Response |
| :--- | :--- | :--- | :--- |
| **`GET /health`** | Liveness Probe | Uvicorn process responsiveness | 503 if event loop is blocked |
| **`GET /health/ready`** | Readiness Probe | Database connection, Disk space ($> 1\text{GB}$), Local SLM socket | 503 if DB unreachable |
| **`GET /health/ai`** | AI Subsystem Probe | Ollama/Qwen3 socket, faster-whisper model loaded, PaddleOCR initialized | 200 with degraded status if AI down |
| **`GET /health/sync`** | Sync Subsystem Probe | Pending sync queue depth, last successful sync timestamp, network link | 200 with `sync_status: OFFLINE` |

---

## 4. Key Performance & Safety Metrics (Prometheus / OpenTelemetry)

The backend exposes internal operational counters and histograms at `/metrics`:

```
# Core Queue & Triage Metrics
clinova_doctor_queue_depth{facility="DH-KORAPUT-01", acuity="CRITICAL"} 2
clinova_doctor_queue_depth{facility="DH-KORAPUT-01", acuity="URGENT"} 8
clinova_doctor_queue_wait_seconds_bucket{le="300"} 45
clinova_doctor_queue_wait_seconds_bucket{le="900"} 82

# Perceptual Processing Latency Histograms
clinova_ocr_processing_duration_seconds_bucket{model="paddleocr", le="5.0"} 120
clinova_asr_processing_duration_seconds_bucket{model="faster_whisper", le="4.0"} 98

# Subsystem Failure Counters
clinova_ai_inference_failures_total{model="qwen3_4b", reason="timeout"} 3
clinova_deterministic_fallbacks_total{trigger="ai_unreachable"} 3
clinova_sync_push_failures_total{reason="network_unreachable"} 14

# Epistemic & Freshness Metrics
clinova_active_evidence_conflicts_total{facility="DH-KORAPUT-01"} 1
clinova_stale_facility_capabilities_total{threshold="4h"} 0
```

---

## 5. Audit Log Forensics vs. Operational Observability

It is critical to distinguish between **Operational Logs** (transient debugging text) and **Audit Logs** (permanent forensic records):
- **Operational Logs:** Retained for 14 to 30 days in circular ring buffers; used for debugging performance, latency spikes, and system crashes.
- **Forensic Audit Logs (`audit_logs` table):** Retained for 3 to 7 years in the relational database; cryptographically linked with SHA-256 Merkle hash chaining; forensic compliance under Section 63 Bharatiya Sakshya Adhiniyam 2023.
