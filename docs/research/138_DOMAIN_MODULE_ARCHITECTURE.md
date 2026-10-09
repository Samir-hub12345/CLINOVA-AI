# CLINOVA AI — Domain Module Architecture & Boundary Specification

> **Document ID:** `RES-138`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Domain-Driven Design & Clinical Systems Architecture Group  

---

## 1. Domain Module Boundary Principles

In accordance with Domain-Driven Design (DDD) principles and the **Modular Monolith** pattern, CLINOVA AI partitions its clinical and operational logic into explicit, bounded domain packages within `backend/app/domain/`.

### 1.1 Cohesion & Merging Decisions
To prevent excessive file fragmentation while upholding strict single-responsibility boundaries, twenty-eight conceptual functional areas are organized into **eleven highly cohesive domain modules**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLINOVA DOMAIN MODULE MAP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. `case_aggregate`       ──► Merges `case`, `encounter`, `lifecycle`      │
│  2. `identity_registry`    ──► Merges `identity`, `deduplication`, `merge`   │
│  3. `intake_stream`        ──► Merges `intake`, `consent`                   │
│  4. `multimodal_media`     ──► Merges `media`, `documents`, `ocr`, `asr`    │
│  5. `evidence_provenance`  ──► Merges `evidence`, `provenance`, `conflict`  │
│  6. `clinical_observations`──► Merges `observations`, `timeline`, `vitals`  │
│  7. `gap_resolution`       ──► Merges `missing_information`, `followup_nbi` │
│  8. `triage_review`        ──► Merges `triage`, `clinical_review`, `queue`  │
│  9. `continuous_graphs`    ──► Merges `caregraph`, `facilitygraph`,         │
│                                `signalgraph`, `orchestration`               │
│  10. `care_pathways`       ──► Merges `referral`, `ward`, `ot`,             │
│                                `appointments`, `outcomes`                   │
│  11. `governance_sync`     ──► Merges `audit`, `retention`, `sync`          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Definitive Domain Module Specifications

---

### Module 1: `case_aggregate` (Master Case Core)
- **Conceptual Responsibilities:** Coordinates the entire clinical episode, root case identity, lifecycle progression across 27 canonical states, and Optimistic Concurrency Control (`state_version`).
- **Primary Entities:** `Case`, `Encounter`, `CaseStateTransition`.
- **Inbound Commands:** `InitializeCaseCommand`, `TransitionStateCommand`, `CloseCaseCommand`.
- **Outbound Events:** `CaseCreatedEvent`, `CaseStateChangedEvent`, `CaseClosedEvent`.
- **Boundary Rule:** Owns the primary key `cases.id`. All other clinical records link to this module via foreign key. No module may alter `cases.status` directly; transitions must invoke `CaseStateMachineService`.

---

### Module 2: `identity_registry` (Patient Identity & Linking)
- **Conceptual Responsibilities:** Resolves patient demographic identity, manages ABHA/MRN identifiers, generates instant emergency tokens (`EMG-YYYYMMDD-XXXX`), identifies duplicate candidate records, and manages non-destructive profile merges.
- **Primary Entities:** `Patient`, `PatientIdentifier`, `IdentityLinkEvent`, `PatientMerge`.
- **Inbound Commands:** `RegisterPatientCommand`, `CreateEmergencyTokenCommand`, `MergePatientProfilesCommand`.
- **Outbound Events:** `PatientIdentifiedEvent`, `PatientMergedEvent`.
- **Boundary Rule:** Strictly decoupled from `cases`. A patient may have multiple historical cases; an emergency case can be created with an anonymous token before demographic identity is known.

---

### Module 3: `intake_stream` (Multimodal Ingestion & Consent)
- **Conceptual Responsibilities:** Captures free-text complaints, handles audio recording uploads and paper slip submissions, captures mandatory digital/verbal consent under DPDP Act 2023, and runs in-flight de-identification regexes.
- **Primary Entities:** `IntakeSubmission`, `ConsentRecord`, `AnonymizationAudit`.
- **Inbound Commands:** `SubmitIntakeCommand`, `RecordConsentCommand`.
- **Outbound Events:** `IntakeSubmittedEvent`, `ConsentGrantedEvent`.
- **Boundary Rule:** If consent is revoked or refused, intake processing halts immediately; raw inputs are blocked from persistence.

---

### Module 4: `multimodal_media` (Media, OCR & Speech Processing)
- **Conceptual Responsibilities:** Manages binary storage for audio WAV files and document scans; runs asynchronous PaddleOCR / Tesseract optical recognition; executes faster-whisper speech-to-text; extracts normalized 2D spatial bounding boxes $[0, 1000]^2$ and word-level acoustic timecodes $[t_{\text{start}}, t_{\text{end}}]$.
- **Primary Entities:** `MediaFile`, `AudioTranscript`, `DocumentOCRPage`, `ExtractedSnippet`.
- **Inbound Commands:** `UploadMediaCommand`, `ProcessOCRJobCommand`, `ProcessASRJobCommand`.
- **Outbound Events:** `MediaUploadedEvent`, `OCRCompletedEvent`, `ASRCompletedEvent`.
- **Boundary Rule:** Stores zero binary BLOBs in the relational database. Files reside on filesystem/object storage; this module manages file paths, SHA-256 hashes, and perceptual coordinate metadata.

---

### Module 5: `evidence_provenance` (Epistemic Safety Layer)
- **Conceptual Responsibilities:** Governs the 8 evidence source classes and 6 epistemic states; enforces the 9-stage provenance lineage; records contradictory clinical measurements in `evidence_conflicts`; manages RMP verification attestations; prevents automated self-verification ($\text{INFERRED} \neq \text{VERIFIED}$).
- **Primary Entities:** `EvidenceRecord`, `EvidenceConflict`, `VerificationEvent`, `ProvenanceChainNode`.
- **Inbound Commands:** `AssertEvidenceCommand`, `RecordConflictCommand`, `AttestVerificationCommand`.
- **Outbound Events:** `EvidenceAssertedEvent`, `ConflictDetectedEvent`, `VerificationRecordedEvent`.
- **Boundary Rule:** Enforces non-destructive history. An edit to a clinical value never overwrites the earlier record; a new `EvidenceRecord` is appended, linked to its predecessor.

---

### Module 6: `clinical_observations` (Vitals & Symptom Timelines)
- **Conceptual Responsibilities:** Captures serial vital signs (HR, SBP, DBP, SpO2, RR, Temp, AVPU); calculates deterministic indices (Shock Index, NEWS2); normalizes discrete lab tests to LOINC/SNOMED CT; tracks symptom onset times and trajectory classifications (`IMPROVING`, `STABLE`, `WORSENING`).
- **Primary Entities:** `VitalReading`, `ClinicalObservation`, `SymptomTimeline`, `SymptomProgressionEvent`.
- **Inbound Commands:** `RecordVitalsCommand`, `LogObservationCommand`, `UpdateSymptomTimelineCommand`.
- **Outbound Events:** `VitalsRecordedEvent`, `VitalAbnormalityDetectedEvent`.
- **Boundary Rule:** Pure deterministic logic. Calculations are 100% reproducible and execute without AI models.

---

### Module 7: `gap_resolution` (Missing Data & Next-Best Information)
- **Conceptual Responsibilities:** Enforces the Zero-Imputation Law; detects missing critical qualifiers and unmeasured vitals; calculates mathematical information sufficiency $S \ge 0.85$; generates 1–3 high-yield Next-Best Information (NBI) clarifying questions to reduce case uncertainty.
- **Primary Entities:** `MissingInformationItem`, `FollowupQuestionSession`, `FollowupQuestion`, `FollowupAnswer`.
- **Inbound Commands:** `ScanGapsCommand`, `GenerateNBIQuestionsCommand`, `SubmitAnswerCommand`.
- **Outbound Events:** `GapIdentifiedEvent`, `SufficiencyThresholdAchievedEvent`.
- **Boundary Rule:** If Tier 1 critical vitals are missing, this module blocks automatic queue promotion, routing the patient to the Nurse Missing-Data Worklist.

---

### Module 8: `triage_review` (Queue Prioritization & Clinical Review)
- **Conceptual Responsibilities:** Computes multi-dimensional doctor queue rankings at query time; surfaces the Doctor Workbench summary; provides override and sign-off controls under NMC Regulation 27; tracks physician review time and diagnostic notes.
- **Primary Entities:** `TriageEvaluation`, `DoctorQueueItem`, `ClinicianDecision`, `ClinicianOverride`.
- **Inbound Commands:** `EvaluateTriageCommand`, `AcceptRecommendationCommand`, `OverrideRecommendationCommand`.
- **Outbound Events:** `TriageEvaluatedEvent`, `DecisionSignedOffEvent`.
- **Boundary Rule:** Only Registered Medical Practitioners (RMPs) holding a valid registration number may issue binding clinical dispositions or sign-offs.

---

### Module 9: `continuous_graphs` (CareGraph, FacilityGraph, SignalGraph & Orchestration)
- **Conceptual Responsibilities:**
  - *CareGraph:* Projects longitudinal physiological trajectory and epistemic uncertainty ($U_t$).
  - *FacilityGraph:* Models facility capabilities, bed availability, and telemetry freshness.
  - *SignalGraph:* Aggregates de-identified syndromic trends and operational bottlenecks.
  - *Orchestration:* Synthesizes all graphs into advisory candidate actions (`ASK`, `VERIFY`, `CONTINUE`, `OBSERVE`, `ESCALATE`, `REFER`).
- **Primary Entities:** `CareGraphState`, `FacilityCapability`, `SignalAggregate`, `OrchestrationAdvisory`.
- **Inbound Commands:** `ComputeCareGraphProjectionCommand`, `UpdateFacilityTelemetryCommand`, `SynthesizeOrchestrationCommand`.
- **Outbound Events:** `CareTrajectoryShiftedEvent`, `OrchestrationSynthesizedEvent`.
- **Boundary Rule:** Strictly advisory. Candidate actions require explicit clinician review before any physical action is ordered.

---

### Module 10: `care_pathways` (Post-Disposition Pathways & Continuity)
- **Conceptual Responsibilities:** Manages post-doctor clinical paths: inter-facility referral preparation (capability-matched SBAR notes), inpatient ward admission requests, Emergency Operating Theatre (OT) surgical handoffs, routine discharge instructions, and outcome recording.
- **Primary Entities:** `ReferralRequest`, `WardAdmission`, `OTHandoff`, `AppointmentBooking`, `CaseOutcome`.
- **Inbound Commands:** `CreateReferralCommand`, `RequestWardAdmissionCommand`, `AuthorizeOTHandoffCommand`, `RecordOutcomeCommand`.
- **Outbound Events:** `ReferralDispatchedEvent`, `PatientAdmittedEvent`, `CaseOutcomeRecordedEvent`.
- **Boundary Rule:** Implements the Anti-Blind Referral Invariant. No referral request may be dispatched unless FACILITYGRAPH verifies that the destination facility currently possesses the required clinical capabilities.

---

### Module 11: `governance_sync` (Audit, Retention & Offline Sync)
- **Conceptual Responsibilities:** Writes append-only cryptographically linked audit ledgers ($H_n = \text{SHA256}(H_{n-1} \parallel \dots)$) under Section 63 BSA 2023; manages data retention and post-purge transitions to `HASH_ONLY` state; coordinates bi-directional push/pull replication journals between offline edge nodes and central hubs.
- **Primary Entities:** `AuditLog`, `MerkleNode`, `RetentionPolicy`, `SyncJournalItem`.
- **Inbound Commands:** `LogAuditEventCommand`, `ExecuteRetentionPurgeCommand`, `ReconcileSyncJournalCommand`.
- **Outbound Events:** `AuditAppendedEvent`, `RetentionPurgedEvent`, `SyncCompletedEvent`.
- **Boundary Rule:** Database triggers prohibit `UPDATE` and `DELETE` queries on audit and event tables; only authorized retention daemons can execute state purges under strict audit logging.
