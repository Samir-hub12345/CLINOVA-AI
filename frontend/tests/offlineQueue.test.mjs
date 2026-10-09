/**
 * CLINOVA AI — Client Offline Sync Queue Test Suite (RES-99 / Phase 24-26)
 * Validates local queue lifecycle, privacy credential sanitization,
 * TTL retention pruning, multi-user isolation, and sync reconciliation.
 */

import assert from "node:assert";

// 1. Setup mock DOM / Web Storage environment for Node
class MockLocalStorage {
  constructor() {
    this.store = new Map();
  }
  getItem(key) {
    return this.store.has(key) ? this.store.get(key) : null;
  }
  setItem(key, value) {
    this.store.set(key, String(value));
  }
  removeItem(key) {
    this.store.delete(key);
  }
  clear() {
    this.store.clear();
  }
}

globalThis.localStorage = new MockLocalStorage();
const dispatchedEvents = [];
globalThis.window = {
  dispatchEvent: (event) => {
    dispatchedEvents.push(event);
  },
};
globalThis.CustomEvent = class CustomEvent {
  constructor(name, detail) {
    this.name = name;
    this.detail = detail;
  }
};

// 2. Import module under test
const {
  getClientNodeId,
  getOfflineQueue,
  enqueueOfflineItem,
  getPendingCount,
  clearSyncedItems,
  clearUserQueue,
  processOfflineSync,
} = await import("../src/lib/offlineQueue.ts");

console.log("--- Starting CLINOVA Client Offline Queue Test Suite ---");

// Test 1: Node ID generation and persistence
{
  localStorage.clear();
  const id1 = getClientNodeId();
  assert.ok(id1.startsWith("NODE-WEB-"), "Expected client node ID prefix NODE-WEB-");
  const id2 = getClientNodeId();
  assert.strictEqual(id1, id2, "Client node ID should be cached in storage");
  console.log("✓ Test 1: Node ID generation and caching passed");
}

// Test 2: Payload sanitization (stripping credentials and tokens)
{
  localStorage.clear();
  const rawItem = {
    sync_id: "sync-item-001",
    node_id: getClientNodeId(),
    user_id: "usr-nurse-01",
    entity_type: "INTAKE",
    entity_id: "intake-999",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: new Date().toISOString(),
    payload_snapshot: {
      patient_name: "Rahul Verma",
      chief_complaint: "Persistent dry cough",
      vitals: {
        heart_rate: 88,
        nested_secret: "super_secret_token_123",
      },
      password: "PlainTextPassword123!",
      auth_token: "jwt.bearer.token.abc",
      api_key: "key-xyz-789",
      authorization: "Bearer secret-bearer",
    },
  };

  const enqueued = enqueueOfflineItem(rawItem);
  const queue = getOfflineQueue("usr-nurse-01");
  assert.strictEqual(queue.length, 1);
  const storedPayload = queue[0].payload_snapshot;

  // Verify clinical fields preserved
  assert.strictEqual(storedPayload.patient_name, "Rahul Verma");
  assert.strictEqual(storedPayload.chief_complaint, "Persistent dry cough");
  assert.strictEqual(storedPayload.vitals.heart_rate, 88);

  // Verify sensitive auth fields stripped
  assert.strictEqual(storedPayload.password, undefined);
  assert.strictEqual(storedPayload.auth_token, undefined);
  assert.strictEqual(storedPayload.api_key, undefined);
  assert.strictEqual(storedPayload.authorization, undefined);
  assert.strictEqual(storedPayload.vitals.nested_secret, undefined);
  console.log("✓ Test 2: Payload credential sanitization passed");
}

// Test 3: User scoping & multi-account isolation
{
  localStorage.clear();
  enqueueOfflineItem({
    sync_id: "sync-u1",
    node_id: "NODE-1",
    user_id: "usr-patient-01",
    entity_type: "INTAKE",
    entity_id: "e-1",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: new Date().toISOString(),
    payload_snapshot: { case: "User 1 data" },
  });

  enqueueOfflineItem({
    sync_id: "sync-u2",
    node_id: "NODE-1",
    user_id: "usr-patient-02",
    entity_type: "INTAKE",
    entity_id: "e-2",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: new Date().toISOString(),
    payload_snapshot: { case: "User 2 data" },
  });

  // User 1 sees only user 1
  const u1Queue = getOfflineQueue("usr-patient-01");
  assert.strictEqual(u1Queue.length, 1);
  assert.strictEqual(u1Queue[0].user_id, "usr-patient-01");

  // User 2 sees only user 2
  const u2Queue = getOfflineQueue("usr-patient-02");
  assert.strictEqual(u2Queue.length, 1);
  assert.strictEqual(u2Queue[0].user_id, "usr-patient-02");

  // Global query sees both
  const allQueue = getOfflineQueue();
  assert.strictEqual(allQueue.length, 2);
  console.log("✓ Test 3: User scoping and isolation passed");
}

// Test 4: TTL Retention Pruning (>7 days)
{
  localStorage.clear();
  const eightDaysAgo = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString();
  const now = new Date().toISOString();

  // Enqueue fresh item
  enqueueOfflineItem({
    sync_id: "sync-fresh",
    node_id: "NODE-1",
    entity_type: "VITALS",
    entity_id: "v-fresh",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: now,
    payload_snapshot: { hr: 75 },
  });

  // Manually insert stale item into raw storage
  const rawItems = JSON.parse(localStorage.getItem("clinova_offline_sync_queue") || "[]");
  rawItems.push({
    sync_id: "sync-stale",
    node_id: "NODE-1",
    entity_type: "VITALS",
    entity_id: "v-stale",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: eightDaysAgo,
    status: "PENDING_UPLOAD",
    payload_snapshot: { hr: 99 },
  });
  localStorage.setItem("clinova_offline_sync_queue", JSON.stringify(rawItems));

  // getOfflineQueue should prune stale item
  const validQueue = getOfflineQueue();
  assert.strictEqual(validQueue.length, 1);
  assert.strictEqual(validQueue[0].sync_id, "sync-fresh");
  console.log("✓ Test 4: TTL retention pruning (>7 days) passed");
}

// Test 5: User Queue Purge on Logout (`clearUserQueue`)
{
  localStorage.clear();
  enqueueOfflineItem({
    sync_id: "sync-purge-01",
    node_id: "NODE-1",
    user_id: "usr-patient-01",
    entity_type: "INTAKE",
    entity_id: "intake-p1",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: new Date().toISOString(),
    payload_snapshot: { data: "p1" },
  });
  enqueueOfflineItem({
    sync_id: "sync-purge-02",
    node_id: "NODE-1",
    user_id: "usr-patient-02",
    entity_type: "INTAKE",
    entity_id: "intake-p2",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "APPEND_ONLY",
    created_at: new Date().toISOString(),
    payload_snapshot: { data: "p2" },
  });

  clearUserQueue("usr-patient-01");
  const p1Queue = getOfflineQueue("usr-patient-01");
  const p2Queue = getOfflineQueue("usr-patient-02");
  assert.strictEqual(p1Queue.length, 0);
  assert.strictEqual(p2Queue.length, 1);
  assert.strictEqual(p2Queue[0].sync_id, "sync-purge-02");
  console.log("✓ Test 5: User queue clearing on session logout passed");
}

// Test 6: Sync Reconciliation Push (`processOfflineSync`)
{
  localStorage.clear();
  enqueueOfflineItem({
    sync_id: "sync-sync-01",
    node_id: getClientNodeId(),
    user_id: "usr-doc-01",
    entity_type: "DECISION",
    entity_id: "d-01",
    operation: "INSERT",
    local_version: 1,
    conflict_strategy: "CLINICIAN_WINS",
    created_at: new Date().toISOString(),
    payload_snapshot: { action: "OBSERVE" },
  });
  enqueueOfflineItem({
    sync_id: "sync-conflict-01",
    node_id: getClientNodeId(),
    user_id: "usr-doc-01",
    entity_type: "INTAKE",
    entity_id: "in-01",
    operation: "UPDATE",
    local_version: 1,
    conflict_strategy: "MANUAL_GATE",
    created_at: new Date().toISOString(),
    payload_snapshot: { severity: "HIGH" },
  });

  // Mock server syncPush response
  const mockSyncPush = async ({ items }) => {
    assert.strictEqual(items.length, 2);
    return {
      results: [
        {
          sync_id: "sync-sync-01",
          entity_type: "DECISION",
          entity_id: "d-01",
          status: "SYNCED",
          remote_version: 2,
          message: "Saved successfully",
        },
        {
          sync_id: "sync-conflict-01",
          entity_type: "INTAKE",
          entity_id: "in-01",
          status: "CONFLICT",
          remote_version: 3,
          conflict_id: "cnf-999-abc",
          message: "Conflict detected: Remote version ahead",
        },
      ],
    };
  };

  const syncResult = await processOfflineSync(mockSyncPush, "usr-doc-01");
  assert.strictEqual(syncResult.synced, 1);
  assert.strictEqual(syncResult.conflicts, 1);
  assert.strictEqual(syncResult.failed, 0);

  const updatedQueue = getOfflineQueue("usr-doc-01");
  const syncedItem = updatedQueue.find((i) => i.sync_id === "sync-sync-01");
  const conflictItem = updatedQueue.find((i) => i.sync_id === "sync-conflict-01");
  assert.strictEqual(syncedItem.status, "SYNCED");
  assert.strictEqual(conflictItem.status, "CONFLICT");
  assert.strictEqual(conflictItem.conflict_id, "cnf-999-abc");

  // Test clearSyncedItems
  clearSyncedItems("usr-doc-01");
  const afterClear = getOfflineQueue("usr-doc-01");
  assert.strictEqual(afterClear.length, 1);
  assert.strictEqual(afterClear[0].sync_id, "sync-conflict-01");
  console.log("✓ Test 6: Sync reconciliation and conflict tracking passed");
}

console.log("--- All Offline Queue Tests Passed Successfully ---");
