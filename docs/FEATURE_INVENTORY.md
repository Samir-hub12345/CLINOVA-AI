# CLINOVA AI — Comprehensive Feature Inventory & Verification Matrix

> **Document ID:** `DOC-FEAT-INV`  
> **Status:** APPROVED & LOCKED  
> **Phase:** Phase 1 — Product Definition & Documentation Source of Truth  
> **Version:** 2.0.0  

---

## 1. Feature Governance Matrix

Every functional requirement across the **BPUT Baseline (`B01`–`B18`)** and the **CLINOVA Continuous Care Intelligence Core (`C01`–`C11`)** is tracked against eleven engineering dimensions:
1. **Requirement & Purpose**
2. **Responsible Actor**
3. **Workflow Association**
4. **UI Screen Linkage**
5. **Data Model Entity**
6. **Backend / API Endpoint**
7. **Integration Touchpoint**
8. **Failure & Exception Handling**
9. **Automated Test Specification**
10. **Browser Verification Standard**
11. **Implementation Status**

---

## 2. BPUT Baseline Capabilities (`B01`–`B18`)

| ID | Requirement | Actor | Workflow | UI Screen | Data Model | Backend / API | Integration | Failure Handling | Tests | Browser Verification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B01** | **Text Intake** | Patient, Nurse | Regular & Camp Intake | Screen 06 (`/encounter/intake`) | `MasterCase.raw_symptom_narrative` | `POST /api/v1/intake/text` | Feeds NLP normalization engine | Rejects empty strings; sanitizes inputs | `test_text_intake_validation` | Interactive textarea renders and submits | Phase 1 Contract Approved |
| **B02** | **Voice Intake** | Patient, Nurse | Vernacular Speech Intake | Screen 07 (`/encounter/voice`) | `MasterCase.voice_recordings` | `POST /api/v1/intake/speech` | Local Whisper / faster-whisper | Audio failure falls back to typed text input | `test_voice_upload_transcribe` | Audio recording timer and waveform render | Phase 1 Contract Approved |
| **B03** | **Report Upload** | Patient, Nurse | Point-of-Care Ingestion | Screen 08 (`/encounter/upload`) | `MasterCase.uploaded_documents` | `POST /api/v1/intake/upload` | Multipart file ingestion to ephemeral storage | Validates MIME types (PDF, PNG, JPG); reject corrupt files | `test_document_upload_mimetypes`| File dropzone with progress indicator | Phase 1 Contract Approved |
| **B04** | **Optical Character Recognition (OCR)** | System, Nurse | Lab Extraction Pipeline | Screen 09 (`/encounter/extraction`) | `MasterCase.ocr_raw_text` | `POST /api/v1/intake/ocr` | Local PaddleOCR / Tesseract pipeline | Low-confidence OCR tagged UNRELIABLE; prompt manual edit | `test_paddleocr_cbc_parser` | Bounding-box snippet viewer with zoom | Phase 1 Contract Approved |
| **B05** | **Extraction & Structuring** | System, Reviewer | Intake Entity Resolution | Screen 09 (`/encounter/extraction`) | `MasterCase.extracted_entities` | `POST /api/v1/ai/extract` | Local Qwen3-4B + Pydantic schema validation | Model offline falls back to regex entity matcher | `test_entity_extraction_schema` | Side-by-side entity vs. source snippet card | Phase 1 Contract Approved |
| **B06** | **Timeline Summarization** | Nurse, Doctor | Longitudinal Progression | Screen 10 (`/encounter/timeline`) | `MasterCase.timeline_events` | `GET /api/v1/cases/{id}/timeline`| Chronological normalizer from dates/vitals | Handles missing timestamps; sorts by intake sequence | `test_timeline_chronological_sort`| Horizontal/vertical milestone swimlane | Phase 1 Contract Approved |
| **B07** | **Missing Information Audit** | Nurse, Doctor | Triage Safety Audit | Screen 11 (`/encounter/audit`) | `CareGraph.uncertainty_vector` | `GET /api/v1/cases/{id}/audit` | Evaluates completeness against red-flag checklists | Explicitly flags gaps as UNKNOWN (no imputation) | `test_missing_data_rule_engine` | Color-coded status badges (Known/Unknown/Conflict) | Phase 1 Contract Approved |
| **B08** | **Follow-up Questions** | Patient, Nurse | Dynamic Gap Closure | Screen 12 (`/encounter/follow-up`)| `MasterCase.qa_sessions` | `POST /api/v1/ai/follow-up` | Next-Best Information engine | Max 3 questions; skips to nurse path if unanswered | `test_nbi_question_generation` | Multiple-choice radio cards with submit action | Phase 1 Contract Approved |
| **B09** | **Language Translation** | Patient, Nurse | Vernacular Normalization | Global Language Selector | `TranslationEntity` | `POST /api/v1/intake/translate` | Local MarianMT / clinical dictionary | Fallback returns native script verbatim with notice | `test_odia_hindi_translation` | Seamless language switcher updates UI strings | Phase 1 Contract Approved |
| **B10** | **Risk Category Support** | System, Doctor | Clinical Stratification | Screen 17 (`/case/:id/trajectory`)| `MasterCase.risk_level` | `POST /api/v1/risk/evaluate` | Deterministic MEWS & shock index rules | Out-of-bounds vitals force manual confirmation | `test_mews_shock_index_rules` | High-contrast risk badge (Red/Amber/Yellow/Green) | Phase 1 Contract Approved |
| **B11** | **Queue Prioritization** | Doctor, Nurse | Clinic Worklist Management | Screen 21 (`/doctor/queue`) | `QueueOrderVector` | `GET /api/v1/doctor/queue` | Dynamic sorting (Risk + Trajectory + Wait time) | Decompensating cases dynamically jump to top | `test_queue_reorder_on_escalation`| Sortable table with live wait-time tickers | Phase 1 Contract Approved |
| **B12** | **Reviewer Dashboard** | Doctor, Reviewer | Clinical Review Workstation| Screen 22 (`/doctor/case/:id`) | `MasterCase` (Unified Read) | `GET /api/v1/cases/{id}/full` | Unified aggregate query loading complete state | Graceful empty-state if sub-reports pending | `test_doctor_workbench_payload` | Multi-panel responsive clinical workbench | Phase 1 Contract Approved |
| **B13** | **Referral Preparation** | Doctor, Referral Staff| Inter-Facility Transfer | Screen 25 (`/facilities/compare`) | `ReferralRecord` | `POST /api/v1/referrals/create` | FACILITYGRAPH capability matcher | Receiving hospital full triggers alternate destination | `test_referral_pack_generation` | Printable referral dossier with Leaflet route | Phase 1 Contract Approved |
| **B14** | **Consent Capture** | Patient, Nurse | Intake Gatekeeper | Screen 06 (`/encounter/intake`) | `MasterCase.consent_recorded` | `POST /api/v1/intake/consent` | Middleware gate blocking unconsented persistence | Unconsented cases rejected; emergency waiver logged | `test_consent_middleware_block` | Mandatory consent modal with digital sign checkbox | Phase 1 Contract Approved |
| **B15** | **Privacy & Anonymization**| System | In-Flight Data Scrubbing | Pipeline Middleware | `AnonymizedRecord` | `POST /api/v1/intake/anonymize` | Regex and NLP PII scrubbing service | Preserves clinical numbers while stripping Aadhaar/phone | `test_anonymizer_aadhaar_phone` | Verify [REDACTED] tokens in network inspector | Phase 1 Contract Approved |
| **B16** | **Auditability** | System Admin | Medicolegal Compliance | Screen 40 (`/admin/audit-logs`)| `AuditEvent` | `GET /api/v1/admin/audit-logs` | Cryptographically linked append-only ledger | Audit failure blocks write transaction | `test_immutable_audit_append` | Paginated tamper-evident log viewer | Phase 1 Contract Approved |
| **B17** | **Human Handoff** | Doctor, Nurse | Inpatient / Transfer Care | Screen 31 (`/case/:id/handoff`) | `HandoffRecord` | `POST /api/v1/cases/handoff` | Dual-signature sign-off protocol | Handoff incomplete blocks patient discharge | `test_dual_signature_handoff` | Two-party signature confirmation modal | Phase 1 Contract Approved |
| **B18** | **Non-Diagnostic Behavior**| System | Safety Enforcement Layer | Global System Middleware | Global Safety Headers | ASGI Middleware: `X-Clinical-Safety` | Global disclaimer injected into every UI header | Rejects unverified autonomous discharge attempts | `test_safety_headers_present` | Visible non-diagnostic disclaimer on every page | Phase 1 Contract Approved |

---

## 3. CLINOVA Continuous Care Intelligence Innovations (`C01`–`C11`)

| ID | Requirement | Actor | Workflow | UI Screen | Data Model | Backend / API | Integration | Failure Handling | Tests | Browser Verification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | **CAREGRAPH Engine** | Doctor, Reviewer | Dynamic State Tracking | Screen 16 (`/case/:id/caregraph`) | `CareGraphState` | `GET /api/v1/caregraph/{id}` | Reactive state graph recomputing on vitals delta | Graph error defaults to tabular clinical summary | `test_caregraph_state_transition`| Interactive physiological state visualization | Phase 1 Contract Approved |
| **C02** | **Evidence Intelligence** | Doctor, Reviewer | Provenance Inspection | Screen 18 (`/case/:id/evidence`) | `EvidenceNode` | `GET /api/v1/evidence/{id}` | Binds parameters to source snippets & confidence | Missing source flagged as UNVERIFIED | `test_evidence_provenance_linkage`| Provenance inspection drawer on value click | Phase 1 Contract Approved |
| **C03** | **Uncertainty Quantification**| Doctor, Reviewer | Clinical Gap Analysis | Screen 18 (`/case/:id/evidence`) | `UncertaintyVector` | `GET /api/v1/uncertainty/{id}` | Computes Known/Unknown/Conflict metrics | Extreme uncertainty prevents routine discharge | `test_uncertainty_score_calc` | High-contrast gap alert callout panel | Phase 1 Contract Approved |
| **C04** | **Next-Best Information** | Patient, Nurse | Targeted Gap Closure | Screen 12 (`/encounter/follow-up`)| `NBITarget` | `POST /api/v1/ai/nbi` | Clinical Value-of-Information (VOI) ranking | VOI tie-break defaults to non-invasive vitals | `test_nbi_voi_ranking_algorithm`| Top-ranked question card with clear explanation | Phase 1 Contract Approved |
| **C05** | **FACILITYGRAPH Engine** | Doctor, Admin | Resource Modeling | Screen 24 (`/facilities/capability`)| `FacilityNode` | `GET /api/v1/facilities/{id}` | Real-time capability, bed & specialist state model | Stale facility telemetry flagged with warning | `test_facilitygraph_capability` | Capability radar matrix with bed count badges | Phase 1 Contract Approved |
| **C06** | **Care Feasibility Engine** | Doctor, Referral Staff| Capability-Matched Routing | Screen 25 (`/facilities/compare`) | `CareFeasibilityReport` | `POST /api/v1/facilities/match`| Matches CAREGRAPH need against network facilities | Local deficit automatically suggests nearest CHC | `test_care_feasibility_matrix` | Side-by-side hospital suitability comparison | Phase 1 Contract Approved |
| **C07** | **SIGNALGRAPH Telemetry** | System Admin, Officer | Epidemiological Telemetry | Screen 38 (`/signals/surveillance`)| `SignalTelemetry` | `GET /api/v1/signals/feed` | Rolling z-score syndromic anomaly detector | Zero-event periods display baseline telemetry | `test_signalgraph_zscore_detector`| Regional syndromic surge heatmap on Leaflet map| Phase 1 Contract Approved |
| **C08** | **ORCHESTRATION Synthesis** | Doctor, Reviewer | Care Decision Synthesis | Screen 26 (`/case/:id/orchestrate`)| `OrchestrationPlan` | `POST /api/v1/orchestrate` | Multi-graph synthesis (Care + Facility + Signals) | Ambiguous synthesis prompts OBSERVE or VERIFY | `test_orchestration_synthesis` | Explainable candidate action card with rationale | Phase 1 Contract Approved |
| **C09** | **Safest Achievable Pathway**| Doctor, Reviewer | Clinical Disposition | Screen 26 (`/case/:id/orchestrate`)| `SafestPathway` | `GET /api/v1/pathway/{id}` | Framed as resource-grounded advisory guidance | Requires doctor acceptance before execution | `test_safest_pathway_advisory` | Prominent advisory recommendation card | Phase 1 Contract Approved |
| **C10** | **Continuity & Outcome Loop**| Doctor, Nurse | Post-Disposition Tracking | Screen 37 (`/case/:id/outcome`) | `LongitudinalOutcome` | `POST /api/v1/cases/{id}/outcome`| Updates CAREGRAPH and feeds SIGNALGRAPH telemetry| Lost to follow-up logged as UNRESOLVED | `test_outcome_feedback_mutation`| Real-world endpoint selector & recovery log | Phase 1 Contract Approved |
| **C11** | **Clinician Learning Signals**| Researcher, Admin | Evaluation Calibration | Screen 40 (`/admin/audit-logs`) | `ClinicianOverrideSignal` | `GET /api/v1/evaluation/signals`| Aggregates doctor overrides against AI guidance | Overrides never alter live clinical rules autonomously| `test_override_calibration_signal`| Calibration concordance chart for researchers | Phase 1 Contract Approved |
