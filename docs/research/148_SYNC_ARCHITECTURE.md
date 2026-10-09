# CLINOVA AI — Synchronization & Event Journal Architecture

> **Document ID:** `RES-148`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Distributed Systems Architecture & Event Synchronization Group  

---

## 1. Architectural Rejection of Blind Last-Write-Wins

In standard consumer applications, offline synchronization commonly uses **Last-Write-Wins (LWW)** based on wall-clock timestamps.

**In Clinical Systems, Blind Last-Write-Wins is Fatal:**
- If an offline tablet with an unsynchronized or drifting clock records a normal blood pressure reading at 10:00 AM, and an online casualty nurse records a life-threatening hypotensive crisis (SBP 60 mmHg) at 10:05 AM, a blind LWW engine might overwrite the crisis data with the older normal reading based on a corrupted timestamp.
- **Architectural Law:** CLINOVA AI **strictly prohibits blind Last-Write-Wins** for clinically meaningful data. Synchronization relies on **Append-Only Event Journals**, explicit identity schemas, and deterministic clinical reconciliation strategies.

---

## 2. Synchronization Data Model & Journal Schema

Every mutation originating on an edge node is recorded in an immutable local ledger table named `sync_journals`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SYNC JOURNAL RECORD SCHEMA                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  • journal_id:        UUIDv4 (Primary Key)                                  │
│  • entity_type:       "CASE" | "VITALS" | "EVIDENCE" | "DECISION"           │
│  • entity_id:         UUIDv4 (Canonical ID of affected entity)              │
│  • event_id:          UUIDv4 (Immutable ID of the clinical event)          │
│  • device_id:         "EDGE-PHC-KORAPUT-01" (Originating hardware node)     │
│  • device_seq:        64-bit Monotonic Integer (1, 2, 3... per device)      │
│  • server_seq:        64-bit Monotonic Integer (Assigned upon Hub ingest)   │
│  • recorded_at:       ISO-8601 UTC Timestamp (Physical event time)          │
│  • sync_status:       "PENDING" | "IN_FLIGHT" | "COMMITTED" | "CONFLICT"    │
│  • conflict_state:    "NONE" | "RESOLVED_AUTO" | "REQUIRES_CLINICIAN_REVIEW"│
│  • payload_json:      Canonical JSON of mutation snapshot                   │
│  • payload_hash:      SHA-256 Digest of Canonical JSON                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Monotonic Identity Invariant
$$\mathbf{Inv\ SYNC\text{-}1}: \quad \forall d \in \text{Devices}, \quad \text{device\_seq}_{n} = \text{device\_seq}_{n-1} + 1$$

Logical sequence counters guarantee that mutations from a device are processed in exact causal order, completely immunizing the sync engine against hardware Real-Time Clock (RTC) drift on rural edge Mini-PCs.

---

## 3. Two-Phase Synchronization Protocol (Push / Pull)

Synchronization between edge nodes and the central cloud hub executes via an idempotent two-phase protocol:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TWO-PHASE PUSH / PULL PROTOCOL                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   EDGE NODE (Mini-PC)                               CENTRAL CLOUD HUB       │
│   ───────────────────                               ─────────────────       │
│                                                                             │
│   [ PHASE 1: PUSH EDGE MUTATIONS ]                                          │
│   1. Read batch of 50 `PENDING` journals                                    │
│   2. Transmit: `POST /api/v1/sync/push` ───────► 3. Validate mTLS & payload │
│                                                  4. Insert into central DB   │
│                                                  5. Assign `server_seq`     │
│      6. Receive 200 OK + ACK list   ◄─────────── 7. Return commit receipt   │
│   8. Mark local journals `COMMITTED`                                        │
│                                                                             │
│   [ PHASE 2: PULL HUB DELTAS ]                                              │
│   9. Request: `GET /api/v1/sync/pull?since_server_seq=N` ────────►          │
│                                                  10. Query server_seq > N   │
│      12. Receive regional delta batch ◄───────── 11. Return delta bundle    │
│   13. Apply deltas to local SQLite                                          │
│   14. Update local `last_pulled_server_seq`                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deterministic Clinical Conflict Resolution Strategies

When concurrent mutations collide during offline synchronization, CLINOVA applies four deterministic strategies based on entity type:

| Entity Category | Collision Scenario | Resolution Strategy | Algorithmic Behavior |
| :--- | :--- | :--- | :--- |
| **Vital Signs & Labs** | Nurse A records HR 110 offline; Nurse B records HR 115 on hub | **`APPEND_ONLY`** | Both vital readings are preserved as separate serial snapshots with their respective device IDs. Zero data loss. |
| **Master Case Status** | Doctor moves case to `STATE_DOCTOR_REVIEWING`; Nurse enters triage note | **`STATE_MACHINE_CAS`** | Compare-and-Swap on `state_version`. Transitions follow valid DAG edges; non-conflicting field updates merge. |
| **Prescription & Diagnosis** | Two clinicians modify treatment simultaneously | **`CLINICIAN_WINS_WITH_AUDIT`** | The latest RMP signature designates primary treatment; superseded order is archived in `clinician_modifications`. |
| **Conflicting Observations** | Patient states allergy absent offline; relative reports allergy online | **`SAFETY_PESSIMISTIC`** | Allergy is flagged as `ACTIVE_CONFLICT` with safety status `SUSPECTED_ALLERGY` until bedside RMP verifies. |

### The Safety-Pessimistic Invariant
**Invariant SYNC-2:** When physiological observations collide during synchronization, the system always adopts the **higher acuity interpretation** for safety monitoring purposes, preventing patient decompensation while human review is pending.
