/**
 * CLINOVA AI — Patient Intake Subsystem Audit Test Suite
 *
 * Verifies:
 * 1. Absence of visible language selection step from the intake wizard sequence.
 * 2. Background language processing and vernacular presets preserved.
 * 3. Extraction Results Screen rendered with primary syndrome, care bundle,
 *    discrete entities with source provenance, epistemic uncertainty,
 *    and missing-information protocol audit (clarified as non-negative).
 * 4. Pathway modification and emergency handoff API client methods.
 * 5. Master Case patient view display of pathway and care bundle badges.
 */

import fs from "node:fs";
import path from "node:path";
import assert from "node:assert";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(testDir, "..");

console.log("--- Starting Patient Intake Subsystem Audit Test Suite ---");

// Test 1: Verify absence of visible LANGUAGE step in PatientIntakeWizard.tsx
const wizardPath = path.join(frontendDir, "src", "components", "patient", "PatientIntakeWizard.tsx");
assert(fs.existsSync(wizardPath), "PatientIntakeWizard.tsx must exist");
const wizardSource = fs.readFileSync(wizardPath, "utf-8");

// Verify WizardStep type definition does NOT have "LANGUAGE"
assert(
  !wizardSource.includes('"REGISTRATION" | "CONSENT" | "LANGUAGE"'),
  "WizardStep must not include visible LANGUAGE step in sequence"
);

// Verify stepList does NOT contain a Language step
assert(
  !wizardSource.includes('{ id: "LANGUAGE", label: "Language" }'),
  "stepList must not present a visible Language selection step"
);

// Verify transition from INPUT_MODE goes directly to ADAPTIVE_QUESTIONS
assert(
  wizardSource.includes('"INPUT_MODE",\n    "ADAPTIVE_QUESTIONS",') ||
  wizardSource.includes('"INPUT_MODE",\r\n    "ADAPTIVE_QUESTIONS",'),
  "Wizard stepList must transition directly from INPUT_MODE to ADAPTIVE_QUESTIONS without LANGUAGE"
);

console.log("✓ Test 1: Visible language-selection step completely removed from intake wizard sequence");

// Test 2: Verify background language support and vernacular presets are preserved
assert(
  wizardSource.includes('preferred_language: "en"'),
  "Background default preferred language must be preserved in state"
);
assert(
  wizardSource.includes("Quick Vernacular Voice Presets") && wizardSource.includes("Hindi") && wizardSource.includes("Odia"),
  "Vernacular audio / dialect presets must be preserved for clinical accessibility"
);
console.log("✓ Test 2: Internal vernacular processing and dialect presets preserved in background");

// Test 3: Verify Extraction Results Screen components
assert(
  wizardSource.includes("Extraction & Clinical Findings"),
  "Extraction results screen must display extraction and clinical findings heading"
);
assert(
  wizardSource.includes("CRITICAL CLINICAL RED FLAG DETECTED — AUTOMATIC EMERGENCY ESCALATION"),
  "Extraction results screen must include emergency escalation banner"
);
assert(
  wizardSource.includes("SYNDROME:") && wizardSource.includes("BUNDLE:"),
  "Extraction results screen must render primary syndrome and required care bundle"
);
assert(
  wizardSource.includes("Discrete Clinical Findings & Provenance"),
  "Extraction results screen must render discrete extracted symptoms and source provenance"
);
assert(
  wizardSource.includes("Missing Protocol Parameters Audit"),
  "Extraction results screen must render missing information protocol audit chips"
);
assert(
  wizardSource.includes("NOT</strong> treated as negative clinical findings"),
  "Protocol gap notice must clarify missing info is not a negative finding"
);
assert(
  wizardSource.includes("Epistemic Uncertainty Score"),
  "Extraction results screen must render epistemic uncertainty score"
);
console.log("✓ Test 3: Extraction Results Screen comprehensively displays syndrome, bundle, provenance & gaps");

// Test 4: Verify API client extensions in src/lib/api.ts
const apiPath = path.join(frontendDir, "src", "lib", "api.ts");
assert(fs.existsSync(apiPath), "api.ts must exist");
const apiSource = fs.readFileSync(apiPath, "utf-8");

assert(apiSource.includes("export async function changeCasePathway"), "changeCasePathway must be exported");
assert(apiSource.includes("export async function recordEmergencyHandoff"), "recordEmergencyHandoff must be exported");
assert(apiSource.includes("export async function answerFollowUpQuestion"), "answerFollowUpQuestion must be exported");
assert(apiSource.includes("primary_syndrome?: string;"), "IntakeResult must contain primary_syndrome");
assert(apiSource.includes("required_bundle?: string;"), "IntakeResult must contain required_bundle");
assert(apiSource.includes("extracted_entities?:"), "IntakeResult must contain extracted_entities");
assert(apiSource.includes("missing_parameters?: string[];"), "IntakeResult must contain missing_parameters");
console.log("✓ Test 4: API client methods for pathway transition and emergency handoff verified");

// Test 5: Verify Patient Case page displays clinical care classification
const casePagePath = path.join(frontendDir, "src", "app", "patient", "case", "[caseId]", "page.tsx");
assert(fs.existsSync(casePagePath), "Patient case page must exist");
const casePageSource = fs.readFileSync(casePagePath, "utf-8");

assert(casePageSource.includes("Clinical Care Classification"), "Patient case page must display clinical care classification");
assert(casePageSource.includes("Care Bundle"), "Patient case page must display care bundle");
console.log("✓ Test 5: Patient Case page displays Care Classification and Care Bundle");

console.log("--- All 5 Intake Subsystem Audit Tests Passed Successfully ---");
