/**
 * CLINOVA AI — Client-Side Offline Synchronization Queue.
 * Continuous Care Intelligence System.
 * Phase 24: Offline / Low-Bandwidth / Sync Architecture (RES-99).
 * Phase 25: Security, Privacy & Local Storage Hardening.
 *
 * Implements persistent localStorage-backed queue for capturing patient intakes,
 * vital sign measurements, and clinical events while disconnected.
 * Automatically synchronizes with /api/v1/sync/push upon reconnection.
 *
 * SECURITY & PRIVACY CONTROLS (PHASE 25):
 * 1. Payload Sanitization: Strips credentials, auth tokens, passwords, and sensitive keys.
 * 2. User Scoping: Queued items are isolated per user_id to prevent cross-account leakage.
 * 3. Retention & TTL Pruning: Expired items (>7 days) and bounded capacity (max 500 items)
 *    are automatically pruned to prevent unbounded storage and stale PHI accumulation.
 * 4. User Clearing: clearUserQueue(userId) allows explicit purge upon logout or session end.
 *
 * RESIDUAL STORAGE RISK NOTICE:
 * Client-side browser storage (localStorage) is vulnerable to physical device access and
 * same-origin script execution (XSS). Do NOT store unencrypted passwords, authorization
 * bearer tokens, or non-anonymized high-risk patient secrets in this queue.
 */

export interface QueuedSyncItem {
  sync_id: string;
  node_id: string;
  user_id?: string;
  entity_type: string;
  entity_id: string;
  case_id?: string;
  operation: "INSERT" | "UPDATE" | "TOMBSTONE";
  local_version: number;
  conflict_strategy: "APPEND_ONLY" | "CLINICIAN_WINS" | "LAST_WRITE_WINS" | "MANUAL_GATE";
  payload_snapshot: Record<string, unknown>;
  created_at: string;
  status: "PENDING_UPLOAD" | "SYNCING" | "SYNCED" | "CONFLICT" | "FAILED";
  error_message?: string;
  conflict_id?: string;
}

const STORAGE_KEY = "clinova_offline_sync_queue";
const NODE_ID_KEY = "clinova_client_node_id";
const MAX_QUEUE_ITEMS = 500;
const MAX_ITEM_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days TTL

const FORBIDDEN_PAYLOAD_KEYS = new Set([
  "password",
  "secret",
  "token",
  "access_token",
  "refresh_token",
  "api_key",
  "authorization",
  "credentials",
  "private_key",
]);

const FORBIDDEN_SUBSTRINGS = [
  "password",
  "secret",
  "token",
  "credential",
  "api_key",
  "private_key",
];

/**
 * Sanitizes a payload object by stripping authentication keys and credentials.
 */
function sanitizePayload(obj: Record<string, unknown>): Record<string, unknown> {
  const sanitized: Record<string, unknown> = {};
  for (const [key, val] of Object.entries(obj)) {
    const lowerKey = key.toLowerCase();
    if (
      FORBIDDEN_PAYLOAD_KEYS.has(lowerKey) ||
      FORBIDDEN_SUBSTRINGS.some((sub) => lowerKey.includes(sub))
    ) {
      continue; // Strip credential
    }
    if (val && typeof val === "object" && !Array.isArray(val)) {
      sanitized[key] = sanitizePayload(val as Record<string, unknown>);
    } else {
      sanitized[key] = val;
    }
  }
  return sanitized;
}

export function getClientNodeId(): string {
  if (typeof window === "undefined") return "NODE-SERVER-SSR";
  let id = localStorage.getItem(NODE_ID_KEY);
  if (!id) {
    id = `NODE-WEB-${Math.random().toString(36).substring(2, 9).toUpperCase()}`;
    localStorage.setItem(NODE_ID_KEY, id);
  }
  return id;
}

/**
 * Retrieves the offline queue, applying TTL pruning and optional user isolation.
 */
export function getOfflineQueue(userId?: string): QueuedSyncItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const allItems: QueuedSyncItem[] = JSON.parse(raw);

    const now = Date.now();
    // Prune expired items (>7 days)
    const validItems = allItems.filter((item) => {
      const itemTime = new Date(item.created_at).getTime();
      return !isNaN(itemTime) && now - itemTime <= MAX_ITEM_AGE_MS;
    });

    if (validItems.length !== allItems.length) {
      saveOfflineQueue(validItems);
    }

    if (userId) {
      return validItems.filter((item) => !item.user_id || item.user_id === userId);
    }
    return validItems;
  } catch (err) {
    console.error("[OfflineQueue] Error reading queue from localStorage:", err);
    return [];
  }
}

/**
 * Saves the offline queue with sanitization and bounded size.
 */
function saveOfflineQueue(items: QueuedSyncItem[]): void {
  if (typeof window === "undefined") return;
  try {
    // Bound the queue size to MAX_QUEUE_ITEMS
    let trimmed = items;
    if (trimmed.length > MAX_QUEUE_ITEMS) {
      // Prioritize keeping pending items over already synced items
      const pending = trimmed.filter((i) => i.status === "PENDING_UPLOAD" || i.status === "FAILED");
      const others = trimmed.filter((i) => i.status !== "PENDING_UPLOAD" && i.status !== "FAILED");
      trimmed = [...others.slice(-(MAX_QUEUE_ITEMS - pending.length)), ...pending].slice(-MAX_QUEUE_ITEMS);
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    window.dispatchEvent(new CustomEvent("clinova:sync_queue_updated", { detail: { count: trimmed.length } }));
  } catch (err) {
    console.error("[OfflineQueue] Error writing queue to localStorage:", err);
  }
}

/**
 * Enqueues an offline item after sanitizing sensitive credentials from the payload.
 */
export function enqueueOfflineItem(
  item: Omit<QueuedSyncItem, "status"> & { status?: QueuedSyncItem["status"] }
): QueuedSyncItem {
  const allItems = getOfflineQueue();
  const sanitizedItem: QueuedSyncItem = {
    ...item,
    status: item.status || "PENDING_UPLOAD",
    payload_snapshot: sanitizePayload(item.payload_snapshot || {}),
  };

  // Avoid duplicates by sync_id
  const existingIdx = allItems.findIndex((q) => q.sync_id === sanitizedItem.sync_id);
  if (existingIdx >= 0) {
    allItems[existingIdx] = sanitizedItem;
  } else {
    allItems.push(sanitizedItem);
  }

  saveOfflineQueue(allItems);
  return sanitizedItem;
}

export function getPendingCount(userId?: string): number {
  return getOfflineQueue(userId).filter((q) => q.status === "PENDING_UPLOAD" || q.status === "FAILED").length;
}

export function clearSyncedItems(userId?: string): void {
  const allItems = getOfflineQueue();
  const remaining = allItems.filter((q) => {
    if (userId && q.user_id && q.user_id !== userId) return true; // Keep other users' items
    return q.status !== "SYNCED";
  });
  saveOfflineQueue(remaining);
}

/**
 * Clears all queue items for a specified user upon logout or session end.
 */
export function clearUserQueue(userId: string): void {
  if (!userId) return;
  const allItems = getOfflineQueue();
  const remaining = allItems.filter((q) => q.user_id !== userId);
  saveOfflineQueue(remaining);
}

export interface SyncPushItemPayload {
  sync_id: string;
  node_id: string;
  entity_type: string;
  entity_id: string;
  case_id?: string;
  operation: string;
  local_version: number;
  conflict_strategy: string;
  payload_snapshot: Record<string, unknown>;
  created_at: string;
}

export interface SyncPushResultItem {
  sync_id: string;
  entity_type: string;
  entity_id: string;
  case_id?: string;
  status: string;
  remote_version: number;
  conflict_id?: string;
  message: string;
}

export async function processOfflineSync(
  syncPushFn: (payload: { node_id: string; items: SyncPushItemPayload[] }) => Promise<{ results: SyncPushResultItem[] }>,
  userId?: string
): Promise<{ synced: number; conflicts: number; failed: number }> {
  const queue = getOfflineQueue(userId);
  const pending = queue.filter((q) => q.status === "PENDING_UPLOAD" || q.status === "FAILED");

  if (pending.length === 0) {
    return { synced: 0, conflicts: 0, failed: 0 };
  }

  const nodeId = getClientNodeId();
  const payloadItems: SyncPushItemPayload[] = pending.map((q) => ({
    sync_id: q.sync_id,
    node_id: nodeId,
    entity_type: q.entity_type,
    entity_id: q.entity_id,
    case_id: q.case_id,
    operation: q.operation,
    local_version: q.local_version,
    conflict_strategy: q.conflict_strategy,
    payload_snapshot: q.payload_snapshot,
    created_at: q.created_at,
  }));

  try {
    const response = await syncPushFn({ node_id: nodeId, items: payloadItems });
    let synced = 0;
    let conflicts = 0;
    let failed = 0;

    const resultMap = new Map<string, SyncPushResultItem>();
    for (const r of response.results || []) {
      resultMap.set(r.sync_id, r);
    }

    const allQueue = getOfflineQueue();
    const updatedQueue = allQueue.map((q) => {
      const res = resultMap.get(q.sync_id);
      if (!res) return q;

      if (res.status === "SYNCED" || res.status === "ALREADY_SYNCED") {
        synced++;
        return { ...q, status: "SYNCED" as const, conflict_id: undefined, error_message: undefined };
      } else if (res.status === "CONFLICT") {
        conflicts++;
        return { ...q, status: "CONFLICT" as const, conflict_id: res.conflict_id, error_message: res.message };
      } else {
        failed++;
        return { ...q, status: "FAILED" as const, error_message: res.message };
      }
    });

    saveOfflineQueue(updatedQueue);
    return { synced, conflicts, failed };
  } catch (err: unknown) {
    console.error("[OfflineQueue] Batch synchronization push failed:", err);
    return { synced: 0, conflicts: 0, failed: pending.length };
  }
}
