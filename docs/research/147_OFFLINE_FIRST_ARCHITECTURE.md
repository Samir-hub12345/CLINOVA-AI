# CLINOVA AI — Offline-First Architecture & Edge Topology

> **Document ID:** `RES-147`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Distributed Systems Architecture & Offline Resilience Engineering Group  

---

## 1. The Offline Edge Mandate

Primary Health Centres (PHCs) and community outreach health camps in rural Odisha, tribal districts, and hilly regions operate under chronic infrastructure fragility:
- Daily cellular and broadband blackouts lasting 4 to 48 hours.
- Generator-powered electrical grids with voltage spikes.
- Low-bandwidth (2G/3G) intermittent connectivity.

**Architectural Law:** CLINOVA AI is **Offline-First by Design**. All core clinical workflows (patient intake, speech recording, vital sign acquisition, NEWS2 scoring, doctor consultation, prescription drafting, and local thermal slip printing) must execute with **zero network connectivity to the internet or cloud**.

---

## 2. Three-Tier Offline Edge Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THREE-TIER EDGE TOPOLOGY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ TIER 1: FRONTLINE CLIENT DEVICES ]                                       │
│  ├── Nurse Android Tablets & Doctor Laptops on Local Clinic Wi-Fi LAN       │
│  ├── Next.js Web App loaded into browser cache (Service Worker PWA)         │
│  └── Client Caching: IndexedDB holds transient drafts (NOT canonical DB)    │
│                                  │                                          │
│                                  │ Local Wi-Fi / Ethernet (No Internet Req) │
│                                  ▼                                          │
│  [ TIER 2: LOCAL CLINIC EDGE SERVER ] (The Authoritative Local Hub)         │
│  ├── Single low-cost fanless Mini-PC (e.g. Celeron N5105 / 8GB RAM / 128GB) │
│  ├── Runs FastAPI Modular Monolith + SQLite 3.45+ in WAL Mode               │
│  ├── Local AI Inference: faster-whisper (CPU) + PaddleOCR (CPU)             │
│  ├── Stores canonical edge relational state & raw media files on local SSD  │
│  └── Writes append-only mutations to local `sync_journals`                  │
│                                  │                                          │
│                                  │ Intermittent Cellular / WAN Link         │
│                                  ▼ (When Internet Becomes Available)        │
│  [ TIER 3: CENTRAL CLOUD / DISTRICT HOSPITAL HUB ]                          │
│  ├── PostgreSQL 15+ / Supabase Central Repository                           │
│  ├── Cross-facility referral routing & district-level SIGNALGRAPH           │
│  └── ABDM national health exchange synchronization                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Clear Division of Persistence Responsibility

A critical architectural pitfall in web applications is making the browser client (IndexedDB) the authoritative database. In a clinical facility with multiple staff, if a nurse records vitals on Tablet A and a doctor reviews on Laptop B, a browser-authoritative database leads to fragmented data silos.

### Definitive Persistence Boundaries
1. **The Browser Client is NOT the Authoritative Database:**
   - Frontline tablets and browser clients act as **smart terminals**.
   - IndexedDB is used strictly for transient input drafting (protecting against accidental tab closures or local Wi-Fi drops) and static asset caching.
2. **The Local Clinic Server is the Authoritative Edge Hub:**
   - The Local Mini-PC hosts the single canonical edge database (`clinova-edge.db`) running SQLite in Write-Ahead Logging (`WAL`) mode with `PRAGMA foreign_keys = ON`.
   - Every staff tablet on the local Wi-Fi communicates directly with this Local Clinic Server over LAN HTTP/WebSocket.
   - When the nurse records vitals, the data is immediately visible on the doctor's screen across the local clinic network, even if external internet is completely severed.
3. **The Central Cloud is the Regional Aggregator:**
   - The central cloud acts as a synchronization target for inter-facility transfers, regional reporting, and cloud backups.

---

## 4. Network Partition Recovery & Resilient Synchronization

When the external internet goes down:
1. **Detection:** The Local Clinic Server attempts periodic lightweight ping probes (`HEAD /api/v1/hub/health`) every 30 seconds. Upon 3 consecutive failures, the sync worker enters `OFFLINE_AUTONOMOUS` mode.
2. **Autonomous Edge Operation:** The local clinic operates indefinitely without cloud access. All cases, vitals, prescriptions, and cryptographic audit hashes accumulate safely in the local SQLite database and `sync_journals`.
3. **Re-Connection & Push Replication:** When external internet is restored:
   - The sync daemon authenticates with the Central Hub via mutual TLS (mTLS) or JWT.
   - Pushes all un-synchronized journal entries in deterministic sequential order (`device_seq`).
   - Pulls updated regional hospital bed availability and incoming referral notices.
4. **Idempotency Guarantee:** Sync payloads are keyed by unique RFC 4122 UUIDv4 identifiers. Re-transmitting a sync batch after a network drop produces zero duplicate clinical records or duplicate billing slips.
