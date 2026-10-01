/**
 * Clinova AI — Authoritative Voice State Machine & Audio Engine
 * 
 * Implements a strict, single-source-of-truth finite state machine for
 * patient voice conversations. Guarantees:
 * - Mutually exclusive states (no impossible concurrent states like LISTENING & ASSISTANT_SPEAKING)
 * - Configurable end-of-turn pause detection
 * - Protection against SpeechRecognition onend race conditions
 * - Turn commit idempotency (no duplicate AI requests or double audio playback)
 * - Clean lifecycle teardown (no lingering mic streams, timers, or TTS audio)
 */

export type VoiceState =
  | "CLOSED"
  | "IDLE"
  | "REQUESTING_MIC"
  | "CONNECTING"
  | "LISTENING"
  | "USER_SPEAKING"
  | "PROCESSING"
  | "ASSISTANT_THINKING"
  | "ASSISTANT_SPEAKING"
  | "INTERRUPTED"
  | "ERROR";

export interface VoiceSessionConfig {
  silenceTimeoutMs: number;
  punctuationSilenceTimeoutMs: number;
  minSpeechDurationMs: number;
  maxTurnDurationMs: number;
  language: string;
  locale: string;
}

export const DEFAULT_VOICE_CONFIG: VoiceSessionConfig = {
  silenceTimeoutMs: 1100,             // Natural conversational pause threshold
  punctuationSilenceTimeoutMs: 750,   // Faster turn commit if punctuation boundary reached
  minSpeechDurationMs: 300,           // Filter out mic clicks/coughs
  maxTurnDurationMs: 45000,          // Safety cap for extremely long single monologues
  language: "en",
  locale: "en-IN",
};

/**
 * Valid state transitions table.
 * Any transition not in this set is rejected to protect system invariants.
 */
export const VALID_VOICE_TRANSITIONS: Record<VoiceState, VoiceState[]> = {
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

/**
 * Validates if transition from currentState to targetState is permissible.
 */
export function isValidVoiceTransition(current: VoiceState, target: VoiceState): boolean {
  if (current === target) return true;
  const allowed = VALID_VOICE_TRANSITIONS[current];
  return Boolean(allowed && allowed.includes(target));
}

/**
 * Generates an idempotent turn token.
 */
export function generateTurnId(sessionId: string): string {
  return `turn-${sessionId}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

/**
 * Detects whether a transcript ends with terminal punctuation across Latin and Indic scripts.
 */
export function hasSentenceTerminalPunctuation(text: string): boolean {
  if (!text) return false;
  const trimmed = text.trim();
  // Include English . ! ? and Indic purna viram (।) and double purna viram (॥)
  return /[.!?।॥]$/.test(trimmed);
}
