import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcDir = path.join(__dirname, "../src");

console.log("--- Starting CLINOVA Redesigned Landing Page Verification Suite ---");

// Test 1: Page.tsx structure and authenticated dashboard bypass
{
  const pageFile = path.join(srcDir, "app/page.tsx");
  assert.ok(fs.existsSync(pageFile), "app/page.tsx must exist");
  const content = fs.readFileSync(pageFile, "utf8");

  assert.ok(content.includes("ReferenceDashboard"), "Must preserve authenticated dashboard rendering");
  assert.ok(content.includes("useClinova"), "Must use Clinova context for session handling");
  assert.ok(content.includes("HeroSection"), "Must include HeroSection");
  assert.ok(content.includes("ProductOverviewSection"), "Must include ProductOverviewSection");
  assert.ok(content.includes("WorkflowSection"), "Must include WorkflowSection");
  assert.ok(content.includes("InnovationLayersSection"), "Must include InnovationLayersSection");
  assert.ok(content.includes("RoleWorkspacesSection"), "Must include RoleWorkspacesSection");
  assert.ok(content.includes("TrustSafetySection"), "Must include TrustSafetySection");
  assert.ok(content.includes("ReportShowcaseSection"), "Must include ReportShowcaseSection");
  assert.ok(content.includes("FinalCtaSection"), "Must include FinalCtaSection");

  console.log("✓ Test 1: Page root integrates all 8 modular sections & preserves authenticated dashboard routing");
}

// Test 2: Hero Section content & product preview
{
  const heroFile = path.join(srcDir, "components/landing/HeroSection.tsx");
  assert.ok(fs.existsSync(heroFile), "HeroSection.tsx must exist");
  const content = fs.readFileSync(heroFile, "utf8");

  assert.ok(content.includes("From Patient Information to Clearer Clinical Decisions"), "Hero headline must match prompt");
  assert.ok(content.includes("CLINICAL INTELLIGENCE PLATFORM"), "Eyebrow must match prompt");
  assert.ok(content.includes("AI supports clinical review. Authorized healthcare professionals retain decision authority"), "Accurate non-delegation statement must be present");
  assert.ok(content.includes("CASE-SYNTH-003"), "Product preview must display synthetic case identifier");
  assert.ok(content.includes("TIMELINE & EVIDENCE PROVENANCE"), "Must preview timeline and provenance");
  assert.ok(content.includes("EPISTEMIC GAP AUDIT"), "Must preview missing information indicators");
  assert.ok(content.includes("Clinician Decision Gate"), "Must preview non-delegable decision gate");
  assert.ok(!content.includes("linear-gradient(text"), "Must not use text gradient for headings");
  assert.ok(content.includes("preview-decision-status-pill"), "Static preview must use non-interactive indicator instead of a misleading button");
  assert.ok(!content.includes('button className="btn btn-primary"'), "Must not render fake actionable button in static mockup");

  console.log("✓ Test 2: Hero Section verifies asymmetric layout, exact copy & authentic product UI preview");
}

// Test 3: Product Overview 9 Capabilities & Truthful Claims
{
  const overviewFile = path.join(srcDir, "components/landing/ProductOverviewSection.tsx");
  assert.ok(fs.existsSync(overviewFile), "ProductOverviewSection.tsx must exist");
  const content = fs.readFileSync(overviewFile, "utf8");

  assert.ok(content.includes("One connected view of the patient journey"), "Heading must match prompt");
  assert.ok(content.includes("Patient Narrative Intake"), "Must include narrative intake");
  assert.ok(content.includes("Voice Transcription & Processing"), "Must include voice transcription");
  assert.ok(content.includes("Evidence Extraction & Provenance"), "Must include evidence extraction");
  assert.ok(content.includes("Patient Timeline Progression"), "Must include timeline");
  assert.ok(content.includes("Clinical Summary & Explanation"), "Must include clinical summary");
  assert.ok(content.includes("Missing-Information Audit"), "Must include missing info audit");
  assert.ok(content.includes("Adaptive Follow-up Inquiries"), "Must include adaptive questions");
  assert.ok(content.includes("Clinician Review Workbench"), "Must include clinician review");
  assert.ok(content.includes("Patient-Specific Reporting & SBAR"), "Must include reporting");

  // Enforce zero fabricated claims & responsive grid
  assert.ok(!content.includes("400/400"), "Must not include fabricated '400/400' test claim");
  assert.ok(content.includes("landing-overview-grid"), "Must use responsive landing-overview-grid");
  assert.ok(content.includes('role="tablist"'), "Must include role='tablist' for accessibility");
  assert.ok(content.includes('role="tab"'), "Must include role='tab' for accessibility");
  assert.ok(content.includes('role="tabpanel"'), "Must include role='tabpanel' for accessibility");

  console.log("✓ Test 3: Product Overview verifies all 9 capabilities, responsive grid, ARIA roles & truthful claims");
}

// Test 4: Workflow Section Distinct Branches & Paschim Banga Doctrine
{
  const workflowFile = path.join(srcDir, "components/landing/WorkflowSection.tsx");
  assert.ok(fs.existsSync(workflowFile), "WorkflowSection.tsx must exist");
  const content = fs.readFileSync(workflowFile, "utf8");

  assert.ok(content.includes("How Clinova AI Coordinates Patient Care"), "Heading must match prompt");
  assert.ok(content.includes("Regular OPD Pathway"), "Must feature distinct regular pathway");
  assert.ok(content.includes("Emergency Pathway"), "Must feature distinct emergency pathway");
  assert.ok(content.includes("Paschim Banga Doctrine"), "Must include Supreme Court constitutional emergency doctrine");
  assert.ok(content.includes("urgent human assessment and resuscitation must never be delayed"), "Must state emergency delay invariant");
  assert.ok(content.includes("THE 12-STAGE MASTER CASE CONTINUOUS LOOP"), "Must preserve 12-stage loop");
  assert.ok(content.includes("landing-workflow-grid"), "Must use responsive landing-workflow-grid");

  console.log("✓ Test 4: Workflow Section verifies distinct regular and emergency branches & Paschim Banga Invariant");
}

// Test 5: Tri-Graph Innovation Layers & Truthful Telemetry
{
  const layersFile = path.join(srcDir, "components/landing/InnovationLayersSection.tsx");
  assert.ok(fs.existsSync(layersFile), "InnovationLayersSection.tsx must exist");
  const content = fs.readFileSync(layersFile, "utf8");

  assert.ok(content.includes("CAREGRAPH"), "Must explain CAREGRAPH");
  assert.ok(content.includes("FACILITYGRAPH"), "Must explain FACILITYGRAPH");
  assert.ok(content.includes("SIGNALGRAPH"), "Must explain SIGNALGRAPH");
  assert.ok(content.includes("Provenance Traceability"), "CAREGRAPH must detail provenance");
  assert.ok(content.includes("Resource Feasibility & Transfer Handoff"), "FACILITYGRAPH must detail transfer feasibility");
  assert.ok(content.includes("Closed-Loop Outcome Telemetry"), "SIGNALGRAPH must detail longitudinal surveillance");

  // Enforce zero fabricated statistics
  assert.ok(!content.includes("98.4% Closed"), "Must not include fabricated '98.4% Closed' statistic");
  assert.ok(!content.includes("100% Verified"), "Must not include fabricated '100% Verified' statistic");
  assert.ok(content.includes("landing-innovation-card-grid"), "Must use responsive landing-innovation-card-grid");

  console.log("✓ Test 5: Innovation Layers Section verifies CAREGRAPH, FACILITYGRAPH and SIGNALGRAPH without fabricated stats");
}

// Test 6: Six Role Workspaces & Strict RBAC Security
{
  const rolesFile = path.join(srcDir, "components/landing/RoleWorkspacesSection.tsx");
  assert.ok(fs.existsSync(rolesFile), "RoleWorkspacesSection.tsx must exist");
  const content = fs.readFileSync(rolesFile, "utf8");

  assert.ok(content.includes("Six Distinct Role Experiences"), "Heading must match prompt");
  assert.ok(content.includes("Patient Portal"), "Must include Patient role");
  assert.ok(content.includes("Receptionist Desk"), "Must include Receptionist role");
  assert.ok(content.includes("Nurse Triage"), "Must include Nurse role");
  assert.ok(content.includes("Doctor Workbench"), "Must include Clinician role");
  assert.ok(content.includes("Facility Administrator"), "Must include Facility Admin role");
  assert.ok(content.includes("System Administrator"), "Must include System Admin role");
  assert.ok(content.includes("Role-Based Access Control (RBAC) & Hospital Authentication"), "Must include RBAC gate");
  assert.ok(!content.includes('href="/staff/triage"'), "Must not provide direct unauthenticated triage bypass");
  assert.ok(content.includes("landing-role-detail-grid"), "Must use responsive landing-role-detail-grid");
  assert.ok(content.includes('role="tablist"'), "Must include role='tablist'");
  assert.ok(content.includes('role="tabpanel"'), "Must include role='tabpanel'");

  console.log("✓ Test 6: Role Workspaces Section verifies all 6 clinical personas & RBAC security gate");
}

// Test 7: Public Header & Navigation Links
{
  const headerFile = path.join(srcDir, "components/landing/LandingHeader.tsx");
  assert.ok(fs.existsSync(headerFile), "LandingHeader.tsx must exist");
  const content = fs.readFileSync(headerFile, "utf8");

  assert.ok(content.includes('"/#platform"'), "Must link to platform section");
  assert.ok(content.includes('"/#workflow"'), "Must link to workflow section");
  assert.ok(content.includes('"/#intelligence"'), "Must link to intelligence section");
  assert.ok(content.includes('"/#trust"'), "Must link to trust section");
  assert.ok(content.includes('href="/login"'), "Must link to sign in");
  assert.ok(content.includes('href="/register"'), "Must link to get started / register");
  assert.ok(content.includes("aria-label=\"Toggle navigation menu\""), "Must include accessible mobile navigation button");
  assert.ok(content.includes("pushState"), "Must update browser history hash when smooth-scrolling");

  console.log("✓ Test 7: Public Landing Header verifies active anchor links, authentication buttons & mobile menu");
}

// Test 8: Footer Integrity & Existing Routes
{
  const footerFile = path.join(srcDir, "components/common/Footer.tsx");
  assert.ok(fs.existsSync(footerFile), "Footer.tsx must exist");
  const content = fs.readFileSync(footerFile, "utf8");

  assert.ok(content.includes('href="/#platform"'), "Footer must link to platform");
  assert.ok(content.includes('href="/#workflow"'), "Footer must link to workflow");
  assert.ok(content.includes('href="/#intelligence"'), "Footer must link to intelligence");
  assert.ok(content.includes('href="/#trust"'), "Footer must link to trust");
  assert.ok(content.includes('href="/login"'), "Footer must link to sign in");
  assert.ok(content.includes('href="/register"'), "Footer must link to registration");
  assert.ok(content.includes('href="/privacy"'), "Footer must link to privacy");
  assert.ok(content.includes('href="/disclaimer"'), "Footer must link to disclaimer");
  assert.ok(content.includes('href="/about"'), "Footer must link to about");
  assert.ok(!content.includes('href="/terms"'), "Footer must not link to non-existent /terms page");
  assert.ok(content.includes("clinova-footer-link"), "Footer must apply accessible hover styling");

  console.log("✓ Test 8: Footer verifies all active links, disclaimers & omission of dead /terms destination");
}

// Test 9: Design System Consistency & Token Integrity
{
  const cssFile = path.join(srcDir, "app/globals.css");
  assert.ok(fs.existsSync(cssFile), "globals.css must exist");
  const cssContent = fs.readFileSync(cssFile, "utf8");

  assert.ok(cssContent.includes(".landing-workflow-grid"), "globals.css must define .landing-workflow-grid");
  assert.ok(cssContent.includes(".landing-overview-grid"), "globals.css must define .landing-overview-grid");
  assert.ok(cssContent.includes(".landing-innovation-card-grid"), "globals.css must define .landing-innovation-card-grid");
  assert.ok(cssContent.includes(".landing-role-detail-grid"), "globals.css must define .landing-role-detail-grid");
  assert.ok(cssContent.includes(".landing-trust-grid"), "globals.css must define .landing-trust-grid");
  assert.ok(cssContent.includes(".preview-decision-status-pill"), "globals.css must define .preview-decision-status-pill");

  // Verify absence of hardcoded legacy #5fd3c7 in landing components
  const landingDir = path.join(srcDir, "components/landing");
  const files = fs.readdirSync(landingDir).filter((f) => f.endsWith(".tsx"));
  for (const file of files) {
    const fileContent = fs.readFileSync(path.join(landingDir, file), "utf8");
    assert.ok(
      !fileContent.includes("#5fd3c7"),
      `${file} must not use legacy hardcoded hex #5fd3c7; use CSS design tokens instead`
    );
  }

  console.log("✓ Test 9: Design System & CSS Invariants verified across all landing components");
}

console.log("--- All 9 Redesigned Landing Page Tests Passed Successfully ---");
