/**
 * CLINOVA AI — Authentication & Session Stability Test Suite
 * Validates non-looping auth state, role persistence, session clearing,
 * unauthenticated null handling, and event dispatch stability.
 */

import assert from "node:assert";

// 1. Setup mock Web Storage & DOM environment
class MockStorage {
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

globalThis.sessionStorage = new MockStorage();
globalThis.localStorage = new MockStorage();

const dispatchedEvents = [];
globalThis.window = {
  dispatchEvent: (event) => {
    dispatchedEvents.push(event);
  },
  addEventListener: () => {},
  removeEventListener: () => {},
};

globalThis.CustomEvent = class CustomEvent {
  constructor(name, opts) {
    this.name = name;
    this.detail = opts?.detail;
  }
};

// 2. Import API module
const {
  getAuthToken,
  getStoredUser,
  setAuthToken,
  clearAuthToken,
  login,
  logout,
  getCurrentUser,
  switchPersona,
  getPersonas,
} = await import("../src/lib/api.ts");

console.log("--- Starting CLINOVA Authentication & Stability Test Suite ---");

// Test 1: Unauthenticated state returns null cleanly without network loops
{
  clearAuthToken();
  dispatchedEvents.length = 0;

  assert.strictEqual(getAuthToken(), null, "Initial token must be null");
  assert.strictEqual(getStoredUser(), null, "Initial stored user must be null");

  const currentUser = await getCurrentUser();
  assert.strictEqual(currentUser, null, "Unauthenticated user must be null");
  assert.strictEqual(dispatchedEvents.length, 0, "No events should be dispatched for unauthenticated check");

  console.log("✓ Test 1: Unauthenticated state returns null cleanly without event loops passed");
}

// Test 2: Login as Nurse sets token and preserves Nurse persona
{
  dispatchedEvents.length = 0;
  const loginRes = await login("nurse", "ClinovaDemo2026!");

  assert.ok(loginRes.access_token, "Access token must be returned");
  assert.strictEqual(loginRes.user.role, "NURSE", "Logged in role must be NURSE");
  assert.strictEqual(loginRes.user.full_name, "Ananya Patel, RN", "Expected Ananya Patel, RN");

  assert.strictEqual(getAuthToken(), loginRes.access_token, "Token must be saved in storage");
  const stored = getStoredUser();
  assert.strictEqual(stored?.role, "NURSE", "Stored user role must be NURSE");

  const current = await getCurrentUser();
  assert.strictEqual(current?.role, "NURSE", "getCurrentUser must return NURSE (not Clinician)");
  assert.strictEqual(current?.full_name, "Ananya Patel, RN");

  // Verify auth event was dispatched once
  const authEvents = dispatchedEvents.filter((e) => e.name === "clinova_auth_changed");
  assert.strictEqual(authEvents.length, 1, "Exactly one auth_changed event should be dispatched");

  console.log("✓ Test 2: Login as Nurse preserves correct role and session identity passed");
}

// Test 3: Switching persona to Receptionist updates identity cleanly
{
  dispatchedEvents.length = 0;
  const switched = await switchPersona("receptionist");

  assert.strictEqual(switched.role, "RECEPTIONIST", "Role must be RECEPTIONIST");
  assert.strictEqual(switched.full_name, "Tunde Olawale", "Expected Tunde Olawale");

  const current = await getCurrentUser();
  assert.strictEqual(current?.role, "RECEPTIONIST", "getCurrentUser must return RECEPTIONIST");

  const stored = getStoredUser();
  assert.strictEqual(stored?.role, "RECEPTIONIST", "Stored user must be updated to RECEPTIONIST");

  console.log("✓ Test 3: Switch persona to Receptionist updates session identity passed");
}

// Test 4: Switching persona to System Admin updates identity cleanly
{
  const switched = await switchPersona("sysadmin");
  assert.strictEqual(switched.role, "SYSTEM_ADMIN", "Role must be SYSTEM_ADMIN");

  const current = await getCurrentUser();
  assert.strictEqual(current?.role, "SYSTEM_ADMIN", "getCurrentUser must return SYSTEM_ADMIN");

  console.log("✓ Test 4: Switch persona to System Administrator passed");
}

// Test 5: Idempotent setAuthToken does NOT dispatch duplicate events
{
  dispatchedEvents.length = 0;
  const currentToken = getAuthToken();

  // Call setAuthToken with identical token and user undefined
  setAuthToken(currentToken);
  assert.strictEqual(dispatchedEvents.length, 0, "No duplicate event should fire when token is unchanged");

  console.log("✓ Test 5: Idempotent token check prevents redundant event storms passed");
}

// Test 6: Logout cleanly revokes session and clears stored identity
{
  dispatchedEvents.length = 0;
  const logoutRes = await logout();

  assert.strictEqual(logoutRes.status, "revoked");
  assert.strictEqual(getAuthToken(), null, "Token must be null after logout");
  assert.strictEqual(getStoredUser(), null, "Stored user must be null after logout");

  const current = await getCurrentUser();
  assert.strictEqual(current, null, "User must be null after logout");

  const expiredEvents = dispatchedEvents.filter((e) => e.name === "clinova_session_expired");
  assert.strictEqual(expiredEvents.length, 1, "Session expired event should fire on logout");

  console.log("✓ Test 6: Logout cleanly clears credentials and transitions to unauthenticated passed");
}

// Test 7: Calling clearAuthToken when already logged out does NOT fire duplicate expired events
{
  dispatchedEvents.length = 0;
  clearAuthToken();
  assert.strictEqual(dispatchedEvents.length, 0, "clearAuthToken on already-empty session must not fire events");

  console.log("✓ Test 7: Redundant clearAuthToken avoids spurious expired events passed");
}

// Test 8: clinova_auth_changed event carries user persona payload in detail
{
  dispatchedEvents.length = 0;
  const loginRes = await login("clinician", "ClinovaDemo2026!");

  assert.strictEqual(loginRes.user.role, "CLINICIAN");
  const authEvents = dispatchedEvents.filter((e) => e.name === "clinova_auth_changed");
  assert.strictEqual(authEvents.length, 1, "Exactly one auth event fired");
  assert.strictEqual(authEvents[0].detail?.user?.role, "CLINICIAN", "Event detail must contain user object");
  assert.strictEqual(authEvents[0].detail?.user?.full_name, "Dr. Priya Sharma", "Event detail user must match Priya Sharma");

  console.log("✓ Test 8: Event detail delivers full persona payload for synchronous hydration passed");
}

// Test 9: Rapid multi-role switching across all clinical roles preserves exact stored role
{
  const roles = [
    { id: "nurse", expectedRole: "NURSE" },
    { id: "receptionist", expectedRole: "RECEPTIONIST" },
    { id: "facility_admin", expectedRole: "FACILITY_ADMIN" },
    { id: "sysadmin", expectedRole: "SYSTEM_ADMIN" },
    { id: "clinician", expectedRole: "CLINICIAN" },
  ];

  for (const r of roles) {
    const switched = await switchPersona(r.id);
    assert.strictEqual(switched.role, r.expectedRole, `Role for ${r.id} must be ${r.expectedRole}`);
    assert.strictEqual(getStoredUser()?.role, r.expectedRole, `Stored role must match ${r.expectedRole}`);
  }

  console.log("✓ Test 9: Rapid multi-role switching preserves exact session identity across all roles passed");
}

// Test 10: getStoredUser resolves synchronously without requiring async microtask delays
{
  const stored = getStoredUser();
  assert.ok(stored, "Stored user must be immediately readable from session storage");
  assert.strictEqual(stored.role, "CLINICIAN", "Stored user must be CLINICIAN without awaiting promise");

  console.log("✓ Test 10: Synchronous session storage reads guarantee zero-delay RoleGuard mount passed");
}

console.log("--- All Authentication Stability Tests Passed (10/10) ---");
