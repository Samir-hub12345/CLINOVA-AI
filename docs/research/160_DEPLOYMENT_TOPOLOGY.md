# CLINOVA AI — Deployment Topology & Infrastructure Architecture

> **Document ID:** `RES-160`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Infrastructure Architecture, DevOps & Distributed Systems Group  

---

## 1. Five Approved Deployment Topologies

To accommodate real-world infrastructure constraints ranging from standalone hackathon testing on a developer laptop to multi-facility district healthcare networks, CLINOVA AI defines five discrete deployment topologies:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FIVE DEPLOYMENT TOPOLOGIES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. `TOPOLOGY_DEV`          ──► Local Developer Machine (Windows/Mac/Linux) │
│  2. `TOPOLOGY_LOCAL_DEMO`   ──► Single Standalone Laptop (All-in-One Demo)  │
│  3. `TOPOLOGY_PHC_EDGE`     ──► Rural Primary Health Centre (Mini-PC + LAN) │
│  4. `TOPOLOGY_DISTRICT_HOSP`──► District Hospital On-Premise Linux Server   │
│  5. `TOPOLOGY_OPTIONAL_CLOUD`─► Regional Multi-Facility Cloud Network       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Topology Comparison & What Runs Where

| Topology | Target Environment | Host Hardware | Relational Persistence | Media Storage | AI & Perceptual Runtime | Synchronization Scope |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`TOPOLOGY_DEV`** | Developer Workstation | Windows / macOS / Linux PC | SQLite (`clinova-dev.db`) | Local directory (`backend/media/`) | Mock adapters or local Ollama/Whisper | None (Standalone development) |
| **`TOPOLOGY_LOCAL_DEMO`** | Hackathon Evaluation / Booth | Single Laptop (e.g. Core i5, 16GB) | SQLite WAL mode | Local directory | CPU faster-whisper + PaddleOCR + Qwen3-4B | None (Self-contained presentation) |
| **`TOPOLOGY_PHC_EDGE`** | Rural Health Centre / Camp | Fanless Mini-PC + Local Wi-Fi Router | SQLite WAL mode (`PRAGMA foreign_keys=ON`) | Local SSD (`/var/data/clinova/media/`) | CPU faster-whisper + PaddleOCR | Bi-directional push/pull journals to District Hub |
| **`TOPOLOGY_DISTRICT_HOSP`**| District Hospital (DH / SDH) | Dedicated Server (e.g. Xeon/EPYC, 32GB) | PostgreSQL 15+ (On-Premise) | Local NAS / MinIO Object Storage | Local GPU / CPU Whisper + PaddleOCR | Serves 50+ hospital LAN terminals; syncs with PHCs |
| **`TOPOLOGY_OPTIONAL_CLOUD`**| State Health Department Cluster | Cloud VPS / Supabase / Vercel | Supabase PostgreSQL + RLS | Supabase Storage (S3 API) | Cloud container / Edge offload | Aggregates all district referral networks |

---

## 3. Data Residency & The Local Infrastructure Boundary

In accordance with patient confidentiality and national medical data regulations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA BOUNDARIES & RESIDENCY POLICIES                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WHAT NEVER LEAVES LOCAL INFRASTRUCTURE (Air-Gapped / Strictly Local):     │
│   • Raw unredacted patient audio recordings (Spoken vernacular interviews)  │
│   • High-resolution camera photos of physical prescription slips            │
│   • Full unredacted demographic identifiers (Direct names, phone numbers)   │
│   • Local operational system logs                                           │
│                                                                             │
│   WHAT SYNCHRONIZES WITH DISTRICT / CLOUD HUBS (When Link is Available):    │
│   • Anonymized Master Case records & Acuity Tiers (`cases`)                 │
│   • Normalized clinical vital signs & LOINC discrete extractions            │
│   • Cryptographic SHA-256 hashes of original raw documents                  │
│   • Clinician verification attestations & override justifications           │
│   • Inter-facility referral transfer requests & SBAR packets                │
│   • De-identified syndromic telemetry counts (SIGNALGRAPH aggregates)       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Air-Gapped Media Invariant
**Invariant DEP-1:** Heavy raw media files (audio recordings, image scans) are retained and purged on local edge storage; only cryptographic SHA-256 digests and normalized clinical concepts are transmitted across bandwidth-constrained rural uplinks to central hospital hubs.

---

## 4. Disaster Recovery & Zero-Data-Loss Invariant

On rural edge Mini-PCs, sudden power cuts from local grid collapses are frequent:
1. **SQLite WAL Durability:** SQLite running with `PRAGMA synchronous = NORMAL` and Write-Ahead Logging guarantees that in-flight transactions either commit atomically or roll back completely upon power restoration. Zero database file corruption occurs.
2. **Crash-Safe Boot Watchdog:** Upon reboot, `systemd` restarts the FastAPI service automatically in $< 5\text{s}$, verifies database integrity via `PRAGMA quick_check;`, and resumes local clinic serving immediately.
3. **Hardware Battery Buffering:** Edge Mini-PCs are paired with a standard 12V 7Ah DC battery backup (providing 4–6 hours of run-time), ensuring uninterrupted clinical workflows during power outages.
