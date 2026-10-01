/**
 * Clinova AI — Voice State Machine Transition & Guard Unit Tests
 */

const assert = require("assert");

// Mirror transition definitions
const VALID_VOICE_TRANSITIONS = {
  CLOSED: ["REQUESTING_MIC", "CONNECTING", "IDLE", "ERROR"],
  IDLE: ["REQUESTING_MIC", "CONNECTING", "LISTENING", "CLOSED", "ERROR"],
  REQUESTING_MIC: ["CONNECTING", "LISTENING", "ERROR", "CLOSED"],
  CONNECTING: ["LISTENING", "ASSISTANT_SPEAKING", "ERROR", "CLOSED"],
  LISTENING: ["USER_SPEAKING", "PROCESSING", "ASSISTANT_THINKING", "INTERRUPTED", "ERROR", "CLOSED", "IDLE"],
  USER_SPEAKING: ["PROCESSING", "ASSISTANT_THINKING", "LISTENING", "INTERRUPTED", "ERROR", "CLOSED"],
  PROCESSING: ["ASSISTANT_THINKING", "ASSISTANT_SPEAKING", "LISTENING", "ERROR", "CLOSED"],
  ASSISTANT_THINKING: ["ASSISTANT_SPEAKING", "LISTENING", "ERROR", "CLOSED"],
  ASSISTANT_SPEAKING: ["LISTENING", "USER_SPEAKING", "INTERRUPTED", "ERROR", "CLOSED", "IDLE"],
  INTERRUPTED: ["LISTENING", "USER_SPEAKING", "PROCESSING", "ERROR", "CLOSED"],
  ERROR: ["REQUESTING_MIC", "CONNECTING", "LISTENING", "IDLE", "CLOSED"],
};

function isValidVoiceTransition(current, target) {
  if (current === target) return true;
  const allowed = VALID_VOICE_TRANSITIONS[current];
  return Boolean(allowed && allowed.includes(target));
}

function hasSentenceTerminalPunctuation(text) {
  if (!text) return false;
  const trimmed = text.trim();
  return /[.!?।॥]$/.test(trimmed);
}

console.log("=================================================");
console.log("CLINOVA AI — VOICE STATE MACHINE TEST SUITE");
console.log("=================================================");

let passed = 0;
let total = 0;

function runTest(name, fn) {
  total++;
  try {
    fn();
    console.log(`  ✓ [PASS] ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ [FAIL] ${name}: ${err.message}`);
  }
}

// 1. Initial State Transitions
runTest("Allows CLOSED to REQUESTING_MIC and CONNECTING", () => {
  assert.strictEqual(isValidVoiceTransition("CLOSED", "REQUESTING_MIC"), true);
  assert.strictEqual(isValidVoiceTransition("CLOSED", "CONNECTING"), true);
  assert.strictEqual(isValidVoiceTransition("CLOSED", "ASSISTANT_SPEAKING"), false);
});

// 2. Normal Conversation Loop Transitions
runTest("Allows full standard conversation loop", () => {
  assert.strictEqual(isValidVoiceTransition("REQUESTING_MIC", "CONNECTING"), true);
  assert.strictEqual(isValidVoiceTransition("CONNECTING", "LISTENING"), true);
  assert.strictEqual(isValidVoiceTransition("LISTENING", "USER_SPEAKING"), true);
  assert.strictEqual(isValidVoiceTransition("USER_SPEAKING", "PROCESSING"), true);
  assert.strictEqual(isValidVoiceTransition("PROCESSING", "ASSISTANT_SPEAKING"), true);
  assert.strictEqual(isValidVoiceTransition("ASSISTANT_SPEAKING", "LISTENING"), true);
});

// 3. Barge-In Interruption Transitions
runTest("Allows Interruption from ASSISTANT_SPEAKING", () => {
  assert.strictEqual(isValidVoiceTransition("ASSISTANT_SPEAKING", "INTERRUPTED"), true);
  assert.strictEqual(isValidVoiceTransition("INTERRUPTED", "LISTENING"), true);
  assert.strictEqual(isValidVoiceTransition("INTERRUPTED", "USER_SPEAKING"), true);
});

// 4. Safe Close from Any State
runTest("Allows CLOSED from any active state", () => {
  const allStates = Object.keys(VALID_VOICE_TRANSITIONS);
  for (const st of allStates) {
    if (st !== "CLOSED") {
      assert.strictEqual(isValidVoiceTransition(st, "CLOSED"), true, `Failed for ${st}`);
    }
  }
});

// 5. Prevents Impossible Concurrent States
runTest("Rejects invalid jumps like CLOSED to USER_SPEAKING", () => {
  assert.strictEqual(isValidVoiceTransition("CLOSED", "USER_SPEAKING"), false);
  assert.strictEqual(isValidVoiceTransition("REQUESTING_MIC", "PROCESSING"), false);
});

// 6. Sentence Terminal Punctuation Detection
runTest("Detects Latin and Indic terminal punctuation correctly", () => {
  assert.strictEqual(hasSentenceTerminalPunctuation("I have a fever."), true);
  assert.strictEqual(hasSentenceTerminalPunctuation("How bad is it?"), true);
  assert.strictEqual(hasSentenceTerminalPunctuation("Please help!"), true);
  assert.strictEqual(hasSentenceTerminalPunctuation("मुझे सिरदर्द है।"), true);
  assert.strictEqual(hasSentenceTerminalPunctuation("I have a fever"), false);
  assert.strictEqual(hasSentenceTerminalPunctuation("मुझे सिरदर्द है"), false);
  assert.strictEqual(hasSentenceTerminalPunctuation(""), false);
});

console.log("-------------------------------------------------");
console.log(`Results: ${passed} / ${total} tests passed (${Math.round((passed / total) * 100)}%)`);
console.log("=================================================");
if (passed !== total) process.exit(1);
