/**
 * Clinova AI — Speech Recognition & Transcript Pipeline Verification
 * Verifies script identification, transcript combination, and language locale mapping.
 */

const assert = require("assert");

// Test functions mirroring frontend/src/lib/speech-recognition.ts
function detectScriptFromText(text) {
  if (!text || !text.trim()) {
    return { code: "unknown", label: "No speech text" };
  }
  if (/[\u0900-\u097F]/.test(text)) return { code: "hi", label: "हिन्दी (Hindi - Devanagari)" };
  if (/[\u0B00-\u0B7F]/.test(text)) return { code: "or", label: "ଓଡ଼ିଆ (Odia)" };
  if (/[\u0980-\u09FF]/.test(text)) return { code: "bn", label: "বাংলা (Bengali)" };
  if (/[\u0B80-\u0BFF]/.test(text)) return { code: "ta", label: "தமிழ் (Tamil)" };
  if (/[\u0C00-\u0C7F]/.test(text)) return { code: "te", label: "తెలుగు (Telugu)" };
  if (/[a-zA-Z]/.test(text)) return { code: "en", label: "English" };
  return { code: "unknown", label: "Undetermined Script" };
}

function combineTranscripts(existingText, newText, mode = "append") {
  const cleanNew = (newText || "").trim();
  if (!cleanNew) return existingText || "";
  if (mode === "replace" || !existingText || !existingText.trim()) {
    return cleanNew;
  }
  const cleanExisting = existingText.trim();
  if (cleanExisting.endsWith(cleanNew)) {
    return cleanExisting;
  }
  const endsWithPunct = /[.!?।,;:]$/.test(cleanExisting);
  return endsWithPunct ? `${cleanExisting} ${cleanNew}` : `${cleanExisting}. ${cleanNew}`;
}

const SPEECH_LANGUAGES = [
  { code: "auto", locale: "en-IN" },
  { code: "en", locale: "en-IN" },
  { code: "hi", locale: "hi-IN" },
  { code: "or", locale: "or-IN" },
  { code: "bn", locale: "bn-IN" },
  { code: "ta", locale: "ta-IN" },
  { code: "te", locale: "te-IN" },
];

console.log("=================================================");
console.log("CLINOVA AI — SPEECH TRANSCRIPTION TEST SUITE");
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

// 1. Script Detection Tests
runTest("Detects Hindi Devanagari script accurately", () => {
  const res = detectScriptFromText("मुझे पिछले दो दिनों से बहुत तेज बुखार है");
  assert.strictEqual(res.code, "hi");
});

runTest("Detects Odia script accurately", () => {
  const res = detectScriptFromText("ମୋତେ ୩ ଦିନ ଧରି ମୁଣ୍ଡ ବିନ୍ଧା ହେଉଛି");
  assert.strictEqual(res.code, "or");
});

runTest("Detects English script accurately", () => {
  const res = detectScriptFromText("Patient has difficulty breathing and chest tightness");
  assert.strictEqual(res.code, "en");
});

runTest("Detects Bengali script accurately", () => {
  const res = detectScriptFromText("আমার মাথায় প্রচণ্ড যন্ত্রণা হচ্ছে");
  assert.strictEqual(res.code, "bn");
});

runTest("Detects Tamil script accurately", () => {
  const res = detectScriptFromText("எனக்கு மூன்று நாட்களாக காய்ச்சல் உள்ளது");
  assert.strictEqual(res.code, "ta");
});

runTest("Detects Telugu script accurately", () => {
  const res = detectScriptFromText("నాకు రెండు రోజులుగా తీవ్రమైన జ్వరం ఉంది");
  assert.strictEqual(res.code, "te");
});

runTest("Handles empty and non-alphabetic inputs gracefully", () => {
  assert.strictEqual(detectScriptFromText("").code, "unknown");
  assert.strictEqual(detectScriptFromText("   ").code, "unknown");
  assert.strictEqual(detectScriptFromText("12345 !@#$%^").code, "unknown");
});

// 2. Transcript Combination & Review Tests
runTest("Combines with period when existing text lacks punctuation", () => {
  const combined = combineTranscripts("High fever for three days", "Severe dry cough at night", "append");
  assert.strictEqual(combined, "High fever for three days. Severe dry cough at night");
});

runTest("Combines with space when existing text ends with period", () => {
  const combined = combineTranscripts("High fever for three days.", "Severe dry cough at night", "append");
  assert.strictEqual(combined, "High fever for three days. Severe dry cough at night");
});

runTest("Supports Hindi purna viram (।) boundary joining", () => {
  const combined = combineTranscripts("तेज बुखार है।", "सांस लेने में तकलीफ है", "append");
  assert.strictEqual(combined, "तेज बुखार है। सांस लेने में तकलीफ है");
});

runTest("Replaces existing text cleanly in replace mode", () => {
  const replaced = combineTranscripts("Old erroneous symptom note", "Corrected revised symptoms", "replace");
  assert.strictEqual(replaced, "Corrected revised symptoms");
});

runTest("Prevents duplicate appending if transcript already present", () => {
  const text = "Patient has high fever and chills";
  const duplicate = combineTranscripts(text, "chills", "append");
  assert.strictEqual(duplicate, text);
});

// 3. Language Locale Coverage Tests
runTest("Ensures supported Indic recognition locales exist", () => {
  const codes = SPEECH_LANGUAGES.map((l) => l.code);
  assert.ok(codes.includes("en"));
  assert.ok(codes.includes("hi"));
  assert.ok(codes.includes("or"));
  assert.ok(codes.includes("auto"));

  const hiLang = SPEECH_LANGUAGES.find((l) => l.code === "hi");
  assert.strictEqual(hiLang.locale, "hi-IN");

  const orLang = SPEECH_LANGUAGES.find((l) => l.code === "or");
  assert.strictEqual(orLang.locale, "or-IN");
});

console.log("-------------------------------------------------");
console.log(`Results: ${passed} / ${total} tests passed (${Math.round((passed / total) * 100)}%)`);
console.log("=================================================");

if (passed !== total) {
  process.exit(1);
}
