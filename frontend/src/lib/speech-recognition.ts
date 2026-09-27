/**
 * Shared Speech Recognition Utilities & Types
 * Clinova AI — Unified Speech-to-Text Architecture
 *
 * Provides shared language definitions, script detection across Indian languages,
 * browser capability verification, and transcript concatenation helpers.
 */

export interface SpeechLanguage {
  code: string;
  name: string;
  nativeName: string;
  locale: string;
}

export const SPEECH_LANGUAGES: SpeechLanguage[] = [
  { code: "auto", name: "Auto-Detect", nativeName: "Auto-Detect (Multilingual)", locale: "en-IN" },
  { code: "en", name: "English", nativeName: "English (India)", locale: "en-IN" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी (Hindi)", locale: "hi-IN" },
  { code: "or", name: "Odia", nativeName: "ଓଡ଼ିଆ (Odia)", locale: "or-IN" },
  { code: "bn", name: "Bengali", nativeName: "বাংলা (Bengali)", locale: "bn-IN" },
  { code: "ta", name: "Tamil", nativeName: "தமிழ் (Tamil)", locale: "ta-IN" },
  { code: "te", name: "Telugu", nativeName: "తెలుగు (Telugu)", locale: "te-IN" },
];

/**
 * Verifies if Web Speech API is supported in the current browser environment.
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
}

/**
 * Detects the script of the transcribed text using Unicode block ranges.
 * Distinguishes native Indic scripts (Devanagari, Odia, Bengali, Tamil, Telugu) from Latin/English.
 */
export function detectScriptFromText(text: string): { code: string; label: string } {
  if (!text || !text.trim()) {
    return { code: "unknown", label: "No speech text" };
  }

  // Devanagari Unicode: \u0900 - \u097F
  if (/[\u0900-\u097F]/.test(text)) {
    return { code: "hi", label: "हिन्दी (Hindi - Devanagari)" };
  }
  // Odia Unicode: \u0B00 - \u0B7F
  if (/[\u0B00-\u0B7F]/.test(text)) {
    return { code: "or", label: "ଓଡ଼ିଆ (Odia)" };
  }
  // Bengali Unicode: \u0980 - \u09FF
  if (/[\u0980-\u09FF]/.test(text)) {
    return { code: "bn", label: "বাংলা (Bengali)" };
  }
  // Tamil Unicode: \u0B80 - \u0BFF
  if (/[\u0B80-\u0BFF]/.test(text)) {
    return { code: "ta", label: "தமிழ் (Tamil)" };
  }
  // Telugu Unicode: \u0C00 - \u0C7F
  if (/[\u0C00-\u0C7F]/.test(text)) {
    return { code: "te", label: "తెలుగు (Telugu)" };
  }
  // English / Latin
  if (/[a-zA-Z]/.test(text)) {
    return { code: "en", label: "English" };
  }

  return { code: "unknown", label: "Undetermined Script" };
}

/**
 * Safely merges a finalized speech transcript into existing symptom text.
 * Prevents unintended duplication and preserves punctuation boundaries.
 */
export function combineTranscripts(
  existingText: string,
  newText: string,
  mode: "replace" | "append" = "append"
): string {
  const cleanNew = (newText || "").trim();
  if (!cleanNew) return existingText || "";
  if (mode === "replace" || !existingText || !existingText.trim()) {
    return cleanNew;
  }
  const cleanExisting = existingText.trim();
  // Prevent duplicate append if already present at the end
  if (cleanExisting.endsWith(cleanNew)) {
    return cleanExisting;
  }
  // Separate by period or space depending on terminal punctuation
  const endsWithPunct = /[.!?।,;:]$/.test(cleanExisting);
  return endsWithPunct ? `${cleanExisting} ${cleanNew}` : `${cleanExisting}. ${cleanNew}`;
}
