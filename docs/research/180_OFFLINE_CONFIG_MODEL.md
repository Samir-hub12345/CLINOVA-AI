# CLINOVA AI — Offline Configuration, Connectivity States & Edge Authority Model

> **Document ID:** `RES-180`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Distributed Systems, Offline-First Architecture & Resilient Networks Group  

---

## 1. The Offline Autonomy Principle

In rural and remote healthcare settings across India, internet outages are not edge cases—they are regular operational conditions lasting days or weeks.

**The Golden Law of Edge Persistence:**
$$\mathbf{Clinical\ Care\ Velocity} \perp \mathbf{WAN\ Connectivity}$$

A Primary Health Centre or Outreach Health Camp must never freeze, drop cases, or block a doctor from writing a prescription because the external internet link has failed. The **Local Clinic Server** (fanless Mini-PC hosting SQLite) is the **authoritative clinical source of truth** for all operations conducted within that facility.

---

## 2. Five Canonical Connectivity States

CLINOVA AI models system operational health across five discrete connectivity states:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FIVE CANONICAL CONNECTIVITY STATES                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STATE 1: ONLINE ]                                                        │
│  ├── Continuous high-speed WAN connection to District Hub / Cloud.          │
│  └── Real-time bi-directional telemetry and sync journals active.           │
│                                                                             │
│  [ STATE 2: OFFLINE ]                                                       │
│  ├── Zero WAN connectivity; complete cellular/fiber blackout.               │
│  └── 100% autonomous local operation. Zero clinical features disabled.     │
│                                                                             │
│  [ STATE 3: DEGRADED ]                                                      │
│  ├── Intermittent high-loss link or local AI hardware failure (OOM/CPU).     │
│  └── Falls back to deterministic rule sets; sync queue throttled.           │
│                                                                             │
│  [ STATE 4: SYNCING ]                                                       │
│  ├── Link restored; transmitting accumulated append-only sync journals.     │
│  └── Background non-blocking execution; zero UI freezing.                   │
│                                                                             │
│  [ STATE 5: SYNC_CONFLICT ]                                                 │
│  ├── Divergence detected between local edge state and central hub.          │
│  └── Deterministic safety-pessimistic resolution; audit flag raised.        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Thin-Client Frontline Architecture vs. Authoritative Local Server

A critical configuration distinction in CLINOVA AI is between the **Frontline Staff Tablets** and the **Local Clinic Server**:

1. **Frontline Staff Tablets (Thin Clients):**
   - Tablets held by nurses and registration clerks run browser sessions over local Wi-Fi.
   - They use browser `localStorage` or `IndexedDB` **strictly for transient draft caching** (auto-saving unsaved form keystrokes every 5s to prevent data loss if a browser tab is accidentally refreshed).
   - Tablets are **NOT** the authoritative database and do NOT maintain local sync journals.
2. **Local Clinic Server (Authoritative Edge Core):**
   - The fanless Mini-PC hosts the canonical FastAPI backend and SQLite WAL database.
   - All tablet submissions commit directly to SQLite over the local LAN.
   - The local server maintains the append-only `sync_journals` and manages reconciliation with the District Hospital.

---

## 4. Offline Configuration Schema

```python
# Offline & Sync Settings Model
class OfflineSyncSettings(BaseModel):
    OFFLINE_MODE: bool = Field(
        default=True,
        description="Enables autonomous local execution without internet",
    )
    SYNC_MODE: SyncMode = Field(
        default=SyncMode.OFFLINE_ONLY,
        description="Sync topology: OFFLINE_ONLY, BIDIRECTIONAL, or CLOUD_NATIVE",
    )
    SYNC_ENDPOINT: Optional[str] = Field(
        default=None,
        description="Fully qualified URL for district hospital sync gateway",
    )
    SYNC_BATCH_SIZE: int = Field(
        default=25,
        description="Maximum journal events per replication batch",
    )
    SYNC_POLL_INTERVAL_SECONDS: int = Field(
        default=300,
        description="Interval in seconds between WAN reachability probes",
    )
    MAX_UNSYNCED_EVENTS_ALERT: int = Field(
        default=5000,
        description="Threshold to alert technical officer of prolonged edge partition",
    )
```

---

## 5. Invariants Enforced in Offline Operation
1. **Inv-OFF-1 (Zero Network Blocking):** Under no circumstances may an HTTP request from a frontline tablet block on an external network DNS resolution or cloud ping.
2. **Inv-OFF-2 (Deterministic Conflict Adjudication):** If an inter-facility transfer update conflicts between edge and hub, the system resolves via **`CLINICIAN_WINS_WITH_AUDIT`** or **`SAFETY_PESSIMISTIC`** (assigning the higher acuity tier pending doctor re-verification).
3. **Inv-OFF-3 (Local Forensic Ledger):** Section 63 BSA cryptographic Merkle hash chains are computed and sealed locally on the edge node; admissibility does not depend on cloud timestamping.
