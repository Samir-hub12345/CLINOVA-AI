# CLINOVA AI — Offline Edge Provenance & Decentralized Synchronization Model

> **Document ID:** `RES-126`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. The Offline Reality of Rural Health Delivery

In rural Primary Health Centres (PHCs), sub-centres, village outreach camps, and transit ambulances across developing regions, continuous broadband connectivity is a fiction. Internet connectivity fails for hours or days at a time.

If a clinical system cannot operate 100% offline, care halts. However, if offline data synchronization is engineered naively:
1. **Primary Key Collisions:** Auto-incrementing integer IDs ($1, 2, 3\dots$) generated on separate offline tablets collide during cloud synchronization, interleaving different patients' vital signs.
2. **Provenance Detachment:** When an offline record is pushed to the cloud, the central server overwrites the original physical capture time with the current network sync time, corrupting clinical timelines.
3. **Silent Overwrite Races:** A nurse entering vitals offline accidentally clobbers a doctor's concurrent orders placed on a connected desktop.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE CANONICAL OFFLINE PROVENANCE INVARIANT                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                  A SYNCHRONIZATION EVENT MUST NEVER MAKE                    │
│                          PROVENANCE AMBIGUOUS.                              │
│                                                                             │
│   Records generated on offline edge devices retain their local device ID,   │
│   local monotonic sequence, and offline capture timestamps permanently.      │
│   Cloud ingestion appends synchronization telemetry without mutating        │
│   the originating edge provenance ledger.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Four Pillars of Offline Provenance Integrity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FOUR OFFLINE PROVENANCE PILLARS                        │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Global UUIDv4     │ RFC 4122 collision-free identifiers generated locally│
│ 2. Device Identity   │ Hardware MAC/IMEI, Client App ID, and Ed25519 PubKey │
│ 3. Monotonic Logic   │ Local device sequence counter (device_seq)           │
│ 4. Sync Journal      │ Append-only sync ledger tracking network transitions │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 3. Decentralized Synchronization States

Every evidence record generated on an edge node transitions across four sync states:

```
┌─────────────────┐       Wi-Fi / Cellular        ┌──────────────────┐       Server ACK       ┌──────────────────────┐
│  OFFLINE_LOCAL  │ ────────────────────────────► │   PENDING_SYNC   │ ─────────────────────► │  SYNCED_TO_CENTRAL   │
│  (Edge SQLite)  │          Detected             │ (Outbox Enqueued)│                        │   (Postgres Hub)     │
└─────────────────┘                               └──────────────────┘                        └──────────────────────┘
                                                           │
                                                           │ Conflict Detected
                                                           ▼
                                                  ┌──────────────────┐
                                                  │  SYNC_CONFLICT   │ (Diverted to RMP Gate)
                                                  └──────────────────┘
```

- **`OFFLINE_LOCAL`:** Committed to local edge SQLite WAL database. Fully active for local edge triage, risk scoring, and clinical workflows.
- **`PENDING_SYNC`:** Enqueued in the persistent edge synchronization outbox queue.
- **`SYNCED_TO_CENTRAL`:** Received, validated, and cryptographically acknowledged by the central PostgreSQL hub.
- **`SYNC_CONFLICT`:** Server detects a concurrent modification to the same clinical entity; locked pending human reconciliation.

---

## 4. Conflict Resolution Strategies During Edge Merging

When disconnected nodes synchronize with the central hub, four conflict resolution policies govern reconciliation:

| Conflict Strategy | Clinical Domain | Algorithmic Mechanism | Safety Justification |
| :--- | :--- | :--- | :--- |
| **`APPEND_ONLY` (Default)**| Vitals, Symptoms, Audio, OCR, Events | Both offline and central records preserved in `evidence_records`. | **Zero Data Loss.** Clinical history is cumulative; both entries remain visible. |
| **`CLINICIAN_WINS`** | Conflicting Diagnoses, Treatment Dispositions | Clinician's central order takes precedence over offline nurse draft. | RMP statutory authority under NMC Regulations 2023. |
| **`LAST_WRITE_WINS`** | Non-Clinical Demographics, Patient Phone # | Record with latest calibrated `capture_time` survives. | Acceptable strictly for non-clinical administrative metadata. |
| **`MANUAL_GATE`** | Disagreeing Critical Labs (e.g. Potassium $3.1$ vs $6.2$) | Record flagged as `CONFLICTING`; doctor must resolve before discharge. | Prevents silent clinical error under high physiological stakes. |

---

## 5. Offline Sync Journal Relational Schema

### Edge SQLite & Central PostgreSQL Sync Journal

```sql
CREATE TABLE sync_journals (
    id TEXT PRIMARY KEY NOT NULL, -- UUID string
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    evidence_record_id TEXT NOT NULL REFERENCES evidence_records(id) ON DELETE RESTRICT,
    
    originating_device_id TEXT NOT NULL,
    originating_app_version TEXT NOT NULL,
    device_local_sequence INTEGER NOT NULL CHECK (device_local_sequence >= 1),
    
    sync_status TEXT NOT NULL DEFAULT 'OFFLINE_LOCAL' CHECK (sync_status IN (
        'OFFLINE_LOCAL', 'PENDING_SYNC', 'SYNCED_TO_CENTRAL', 'SYNC_CONFLICT'
    )),
    
    local_created_at TEXT NOT NULL, -- ISO-8601 UTC timestamp from local hardware clock
    synced_to_server_at TEXT,       -- Populated when acknowledged by cloud hub
    sync_latency_seconds INTEGER,
    
    has_conflict INTEGER NOT NULL DEFAULT 0 CHECK (has_conflict IN (0, 1)),
    conflict_resolution_strategy TEXT CHECK (conflict_resolution_strategy IS NULL OR conflict_resolution_strategy IN (
        'APPEND_ONLY', 'CLINICIAN_WINS', 'LAST_WRITE_WINS', 'MANUAL_GATE'
    )),
    server_ack_signature TEXT
);

CREATE INDEX ix_sync_status ON sync_journals(sync_status);
CREATE INDEX ix_sync_device ON sync_journals(originating_device_id, device_local_sequence);
```

---

## 6. Guarantee of Unbroken Provenance During Reconnection

When a tablet synchronizes 50 offline records after an 8-hour outage:
1. The cloud database ingests every record with its original `recorded_at = 09:30 AM` preserved in `capture_timestamp`.
2. The server sets `ingestion_timestamp = 05:30 PM` (current cloud clock).
3. The originating device ID, local sequence, and offline batch ID are committed to `sync_journals`.
4. Downstream clinical graphs plot the patient’s morning vitals at 9:30 AM, NOT at 5:30 PM.

This guarantees that rural edge healthcare workers can document patient care in total isolation without sacrificing forensic integrity or clinical accuracy.
