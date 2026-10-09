# CLINOVA AI — Evidence Failure & Exception Matrix (25 Clinical Failure Cases)

> **Document ID:** `RES-129`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 7 — Evidence, Provenance, Verification & Uncertainty Foundation  
> **Version:** 7.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture, Safety Informatics & Epistemic Engineering Group  

---

## 1. Safety Failure Analysis Methodology

In safety-critical clinical engineering, resilience is defined by how a platform behaves when assumptions break. Systems that assume infallible sensors, error-free users, and zero-defect AI models inevitably cause iatrogenic patient harm.

This matrix analyzes **Twenty-Five Concrete Clinical Failure Modes**. Each failure is subjected to an exhaustive 8-point causal investigation:

$$\mathbf{Failure} \longrightarrow \mathbf{Safety\ Risk} \longrightarrow \mathbf{Detection} \longrightarrow \mathbf{System\ Response} \longrightarrow \mathbf{Human\ Response} \longrightarrow \mathbf{Data\ State} \longrightarrow \mathbf{Audit\ Event} \longrightarrow \mathbf{Recovery}$$

---

## 2. Exhaustive 25-Failure Exception Matrix

---

### Failure 1: OCR Wrong Value (Character Misread)
- **Failure:** OCR engine misreads printed lab value: parses `Potassium: 3.1 mEq/L` as `8.1 mEq/L`.
- **Safety Risk:** Severe false hyperkalemia alert leading to inappropriate calcium gluconate/insulin infusion causing lethal hypoglycemia or cardiac arrest.
- **Detection:** Physiological range validator triggers outlier flag ($8.1 > 7.0\text{ mEq/L}$); character confidence $C = 0.62$.
- **System Response:** Tags record `UNRELIABLE`; suppresses automated orders; opens Doctor Workbench with red popover and cropped image of bounding box.
- **Human Response:** Clinician inspects bounding box, sees `"3.1"`, clicks `"Correct Value"` and types `3.1`.
- **Data State:** `evidence_records` updated via append-only amendment; original OCR string preserved in `ocr_extracted_snippets.correction_delta`.
- **Audit Event:** `EVENT_OCR_MANUAL_CORRECTION` written to `case_events` with clinician UUID.
- **Recovery:** Physiological score recalculated; false alert cleared; model telemetry logs misread token for fine-tuning.

---

### Failure 2: OCR Missing Value (Omitted Table Row)
- **Failure:** OCR layout analyzer misses bottom row of printed complete blood count (Platelet count omitted).
- **Safety Risk:** Severe occult thrombocytopenia overlooked prior to emergency surgery, risking uncontrolled hemorrhage.
- **Detection:** Epistemic missing-data audit (`RES-87`) detects mandatory hematology profile incomplete; Sufficiency Score $S$ drops.
- **System Response:** Sets `Platelet Count` to `UNKNOWN` (Zero-Imputation); generates Nurse Worklist task: *"Platelet value missing from scanned CBC"*.
- **Human Response:** Triage nurse checks paper report, enters platelet count manually from keyboard.
- **Data State:** New record inserted with `source_type = 'STAFF_ENTERED'`, `epistemic_status = 'KNOWN'`.
- **Audit Event:** `EVENT_MISSING_DATA_MANUALLY_RESOLVED`.
- **Recovery:** Surgical safety checklist unblocks; hematology profile verified complete.

---

### Failure 3: Voice Mistranscription (Negation Omission)
- **Failure:** Edge speech-to-text drops vernacular negation: *"I do NOT have chest pain"* transcribed as *"I have chest pain"*.
- **Safety Risk:** Inappropriate cardiac emergency workup, diversion of scarce ECG/ICU resources, severe patient anxiety.
- **Detection:** Negation acoustic confidence $c_{\text{neg}} < 0.70$; contradiction with patient triage questionnaire.
- **System Response:** Tags extracted symptom `UNRELIABLE`; flags clinical card: *"Acoustic ambiguity detected in chest pain statement."*
- **Human Response:** Doctor taps inline audio player, listens to 3-second vernacular audio clip, hears clear negation, clicks `"Dismiss Symptom"`.
- **Data State:** Transcript marked `has_human_correction = TRUE`; symptom entity set to `REJECTED`.
- **Audit Event:** `EVENT_TRANSCRIPT_CORRECTION` logged in `audio_transcript_corrections`.
- **Recovery:** Case priority returns to routine OPD queue; acoustic model logs audio clip for dialect re-training.

---

### Failure 4: Dialect Mismatch (Unrecognized Vernacular Phrasing)
- **Failure:** Patient speaks Sambalpuri dialect phrase (*"Chhati bitha heuchhe"*), unrecognized by standard Odia vocabulary.
- **Safety Risk:** Red-flag symptom dropped during intake, delaying recognition of acute coronary syndrome.
- **Detection:** Out-of-vocabulary (OOV) perplexity spike $> 45.0$; language identification confidence drops $< 0.50$.
- **System Response:** Tags entire audio segment `AMBIGUOUS_DIALECT`; alerts nurse: *"Local dialect detected — audio review needed."*
- **Human Response:** Frontline bilingual ASHA/ANM worker listens to audio, types standard Odia/English translation into intake card.
- **Data State:** Raw audio preserved; manual translation linked as child of original transcript.
- **Audit Event:** `EVENT_DIALECT_MANUAL_TRANSLATION`.
- **Recovery:** Triage queue receives normalized symptom; Sambalpuri audio added to vernacular adaptation library.

---

### Failure 5: Poor Audio Quality (Severe Background Noise)
- **Failure:** Ambient diesel generator hum at rural PHC drops audio Signal-to-Noise Ratio to $\text{SNR} = 6\text{ dB}$.
- **Safety Risk:** Muffled audio leads to garbled hallucinated text extractions.
- **Detection:** Audio quality engine computes $Q_{\text{audio}} = 0.22 < 0.50$.
- **System Response:** Hard-blocks automated entity extraction; displays UI banner: *"Audio too noisy for automated intake — please use structured form or re-record."*
- **Human Response:** Nurse moves phone closer to patient or types directly into standard checkbox form.
- **Data State:** Audio saved as `retention_class = 'PURGED_EARLY'`; zero corrupt entities written to `evidence_records`.
- **Audit Event:** `EVENT_AUDIO_QUALITY_REJECTED`.
- **Recovery:** Intake proceeds via structured digital forms without contaminated clinical data.

---

### Failure 6: Conflicting Patient vs Caregiver Reports
- **Failure:** Elderly patient states seizure lasted *"2 minutes"*; panicked daughter states *"he shook for 30 minutes"*.
- **Safety Risk:** Misdiagnosing status epilepticus (requiring emergency intubation) vs self-terminating seizure.
- **Detection:** Dynamic conflict detector identifies $|\Delta t| = 28\text{ minutes}$ across concurrent seizure duration entries.
- **System Response:** Instantiates row in `evidence_conflicts`; surfaces side-by-side juxtaposition card to clinician.
- **Human Response:** Doctor reviews both statements, explains post-ictal confusion to daughter, records estimated duration of 5 minutes with 25 minutes post-ictal sleep.
- **Data State:** Both statements preserved; resolution event committed with strategy `ACCEPTED_BOTH_TEMPORAL`.
- **Audit Event:** `EVENT_CONFLICT_RESOLVED` with doctor's clinical rationale.
- **Recovery:** Safe clinical care: patient observed without premature invasive airway intervention.

---

### Failure 7: Conflicting Nurse vs Doctor Vital Readings
- **Failure:** Triage nurse enters BP $190/110\text{ mmHg}$ at 10:00 AM; doctor re-checks at 10:15 AM and enters $130/85\text{ mmHg}$.
- **Safety Risk:** Over-treatment of transient white-coat hypertension with aggressive IV antihypertensives causing cerebral hypoperfusion.
- **Detection:** Conflict detector triggers on $|\Delta\text{SBP}| = 60\text{ mmHg}$ within 15-minute window.
- **System Response:** Surfaces conflict banner; displays both readings chronologically.
- **Human Response:** Doctor confirms patient had acute anxiety during nurse triage which resolved after resting in quiet room; documents resolution note.
- **Data State:** Both records retained in `evidence_records`; doctor's reading selected as active baseline.
- **Audit Event:** `EVENT_PHYSIOLOGICAL_VARIANCE_RESOLVED`.
- **Recovery:** Patient managed conservatively; avoids dangerous acute hypotension.

---

### Failure 8: Stale External Record Treated as Current
- **Failure:** External ABDM FHIR summary from 6 months ago indicates *"Patient on Metformin 500mg"*; patient stopped drug 3 months ago due to severe renal impairment.
- **Safety Risk:** Inadvertent re-initiation of Metformin in severe renal failure risking fatal lactic acidosis.
- **Detection:** Freshness evaluator (`RES-117`) checks capture timestamp; marks record `STALE` ($\Delta t > 90\text{ days}$).
- **System Response:** Prompts mandatory medication reconciliation badge: *"Historical medication > 90 days old — confirm current adherence."*
- **Human Response:** Nurse asks patient, confirms drug was discontinued; marks Metformin as `DISCONTINUED`.
- **Data State:** External record remains in historical archive; active case medication list reflects zero Metformin.
- **Audit Event:** `EVENT_MEDICATION_RECONCILIATION_COMPLETED`.
- **Recovery:** Patient protected from medication error; active renal failure recorded.

---

### Failure 9: Duplicate Evidence Upload
- **Failure:** Anxious family member uploads the same PDF laboratory report twice from their phone.
- **Safety Risk:** Artificially inflating test counts or generating duplicate conflicting rows.
- **Detection:** Ingestion hash check detects identical `file_checksum_sha256` within same `case_id`.
- **System Response:** Blocks second upload; surfaces message: *"Document already ingested on 2026-10-08 09:15 AM."*
- **Human Response:** User acknowledges alert; duplicate upload discarded.
- **Data State:** Database remains clean; zero duplicate rows in `documents`.
- **Audit Event:** `EVENT_DUPLICATE_INGESTION_BLOCKED`.
- **Recovery:** Record integrity preserved; storage space conserved.

---

### Failure 10: Evidence Uploaded to Wrong Patient Case
- **Failure:** Triage nurse accidentally photographs Patient B's discharge card while active chart is set to Patient A.
- **Safety Risk:** Cross-contamination of medical history; Patient A given wrong blood type or inappropriate medications.
- **Detection:** OCR demographic validator detects Name / Age on scanned document contradicts active patient profile.
- **System Response:** Flags demographic mismatch warning; halts automatic extraction; locks document in quarantine.
- **Human Response:** Nurse realizes mistake, clicks `"Detach from Case & Reassign"`, enters correct Patient B MRN.
- **Data State:** Document unlinked from Case A; audit event records severance; linked cleanly to Case B.
- **Audit Event:** `EVENT_EVIDENCE_REASSIGNMENT_CROSS_CASE`.
- **Recovery:** Patient A's chart cleansed of foreign data; Patient B receives their document.

---

### Failure 11: Accidental Attempted Deletion of Evidence
- **Failure:** Frontline user accidentally clicks delete or rogue SQL script executes `DELETE FROM evidence_records`.
- **Safety Risk:** Destruction of medicolegal audit trail and vital clinical history.
- **Detection:** Database trigger `trg_protect_evidence_records` intercepts query at engine layer.
- **System Response:** Aborts transaction with `EXCEPTION: Physical deletion prohibited under Section 63 BSA 2023`.
- **Human Response:** Application surfaces error: *"Clinical records cannot be deleted. Use formal retraction if invalid."*
- **Data State:** Record remains $100\%$ intact on disk.
- **Audit Event:** `EVENT_UNAUTHORIZED_DELETE_BLOCKED` in `security_tamper_audit_logs`.
- **Recovery:** Database integrity unharmed; malicious or accidental deletion defeated.

---

### Failure 12: Evidence Inaccessible During Edge Outage
- **Failure:** Rural PHC loses internet and local Wi-Fi router power supply; tablet cannot reach local mini-PC server.
- **Safety Risk:** Inability to access historical patient allergies or vitals during acute consultation.
- **Detection:** Client app network monitor detects server timeout $> 1000\text{ms}$.
- **System Response:** Seamlessly switches to local embedded SQLite database on tablet storage; displays `"Offline Mode Active"`.
- **Human Response:** Health worker continues clinical intake and vitals capture on tablet uninterrupted.
- **Data State:** New records committed to local SQLite WAL journal with `sync_status = 'OFFLINE_LOCAL'`.
- **Audit Event:** `EVENT_EDGE_OFFLINE_FAILOVER`.
- **Recovery:** Care proceeds without delay; tablet syncs automatically when power/network restores.

---

### Failure 13: Offline Device Provenance Collision
- **Failure:** Two disconnected tablets in separate outreach tents register emergency patients simultaneously.
- **Safety Risk:** Identifier collision overwriting patient records during end-of-day synchronization.
- **Detection:** Ingestion pipeline validates primary keys are RFC 4122 UUIDv4 ($2^{122}$ collision space).
- **System Response:** Ingests both records without primary key conflict; local sequence numbers mapped to unique device namespaces.
- **Human Response:** Zero human intervention required.
- **Data State:** Both cases exist independently in cloud PostgreSQL database.
- **Audit Event:** `EVENT_OFFLINE_SYNC_SUCCESS` for both devices.
- **Recovery:** Mathematical collision probability is effectively zero; seamless decentralized scale.

---

### Failure 14: Concurrent Synchronization Modification Conflict
- **Failure:** Tablet A edits patient address while offline; Reception desk updates phone number centrally.
- **Safety Risk:** Data clobbering or corrupted contact information.
- **Detection:** Central sync engine detects mismatch between `state_version` and base sync version.
- **System Response:** Applies `LAST_WRITE_WINS` policy for non-clinical demographic fields.
- **Human Response:** None required.
- **Data State:** Both edits merged into demographic record; audit trail logs dual sources.
- **Audit Event:** `EVENT_CONCURRENT_SYNC_MERGED`.
- **Recovery:** Zero clinical impact; contact record unified.

---

### Failure 15: AI Hallucinated Entity Extraction
- **Failure:** Language model hallucinates a non-existent diagnosis: extracts *"History of Chronic Kidney Disease"* from a narrative that mentioned *"Patient's father had kidney stones"*.
- **Safety Risk:** Inappropriate drug dose adjustments or unnecessary nephrology consultations.
- **Detection:** Epistemic grounding validator searches input transcript; fails to find direct semantic support ($C_{\text{ground}} < 0.30$).
- **System Response:** Flags extraction as `UNGROUNDED_MODEL_ASSERTION`; marks epistemic status `UNRELIABLE`.
- **Human Response:** Clinician inspects grounding tooltip, sees family history was misattributed, clicks `"Reject"`.
- **Data State:** Entity marked `review_status = 'REJECTED'`; suppressed from active problem list.
- **Audit Event:** `EVENT_AI_HALLUCINATION_REJECTED`.
- **Recovery:** Active chart protected from erroneous diagnosis; prompt telemetry updated.

---

### Failure 16: AI Inference Presented as Confirmed Fact
- **Failure:** Client UI bug attempts to display AI-suggested Pulmonary Embolism as a finalized diagnosis.
- **Safety Risk:** Automation bias: junior doctor accepts AI suggestion without ordering CT pulmonary angiogram.
- **Detection:** View rendering engine checks `epistemic_status == 'INFERRED'` and `verified_by_actor_id IS NULL`.
- **System Response:** Enforces mandatory amber watermark and disclaimer: *"AI Advisory — Requires Physician Verification"*; blocks automated prescription panel.
- **Human Response:** Resident doctor realizes suggestion requires objective testing, orders D-Dimer and CTPA.
- **Data State:** Diagnostic state remains `INFERRED` until confirmed by CT scan and consultant review.
- **Audit Event:** `EVENT_AI_ADVISORY_RENDERED`.
- **Recovery:** Clinical protocol upheld; diagnostic safety maintained.

---

### Failure 17: Frontline Reviewer Verification Mistake
- **Failure:** Busy triage nurse accidentally confirms an erroneous blood pressure ($290/110$ instead of $120/110$).
- **Safety Risk:** False diagnosis of extreme hypertensive emergency, triggering unnecessary ICU bed hold.
- **Detection:** Plausibility engine flags SBP $> 250\text{ mmHg}$; attending doctor notes discrepancy upon examining calm patient.
- **System Response:** Doctor Workbench displays abnormal vital reading with nurse attribution.
- **Human Response:** Doctor performs manual bedside re-measurement ($122/82\text{ mmHg}$), clicks `"Correct Reading"`.
- **Data State:** Original nurse entry retained; new doctor measurement committed as active `CLINICIAN_VERIFIED`.
- **Audit Event:** `EVENT_CLINICIAN_AMENDMENT` with reason `STAFF_VERIFICATION_ERROR`.
- **Recovery:** Emergency ICU hold cancelled; patient managed calmly.

---

### Failure 18: Clinician Retrospective Correction
- **Failure:** Doctor documents initial impression of *"Acute Gastroenteritis"*; 2 hours later, abdominal rigidity develops, proving *"Perforated Peptic Ulcer"*.
- **Safety Risk:** Confusion in surgical handoff if prior notes contradict emergent surgical booking.
- **Detection:** Doctor initiates diagnostic revision on workbench.
- **System Response:** Prompts mandatory clinical reason for change; links new diagnosis to evolving physical signs.
- **Human Response:** Doctor selects `SUBSEQUENT_CLINICAL_EVOLUTION`, enters operative diagnosis.
- **Data State:** Initial impression archived as superseded; new diagnosis becomes active; both visible in timeline.
- **Audit Event:** `EVENT_DIAGNOSIS_AMENDED` in `clinician_modifications`.
- **Recovery:** Operative team receives clear timeline showing evolving surgical abdomen; patient rushed to OT.

---

### Failure 19: Raw Media Purge Expiry
- **Failure:** 90-day retention policy expires for raw audio consultation file; file is wiped by automated cron worker.
- **Safety Risk:** Clinician or auditor opens case and encounters a broken file link or crash.
- **Detection:** Provenance loader checks `retention_class == 'HASH_ONLY'`.
- **System Response:** UI disables audio play button, displaying: *"Media purged per DPDP retention schedule on 2026-10-08; SHA-256 integrity hash preserved."*
- **Human Response:** User reviews verified transcript and clinician notes; understands raw audio is intentionally scrubbed.
- **Data State:** Relational records intact; disk storage reclaimed; legal compliance maintained.
- **Audit Event:** `EVENT_MEDIA_PURGE_EXECUTED`.
- **Recovery:** Zero system crash; seamless compliance with Indian data protection laws.

---

### Failure 20: Broken Source Media Reference
- **Failure:** Storage disk path moved or cloud bucket permissions altered, causing `404 Not Found` on document image.
- **Safety Risk:** Doctor unable to inspect original paper scan during critical clinical review.
- **Detection:** Pre-fetch daemon detects missing storage object; sets `media_accessibility = 'UNAVAILABLE'`.
- **System Response:** Surfaces graceful fallback UI: displays cached text extraction and OCR confidence; alerts IT operations.
- **Human Response:** Doctor relies on physical paper slip in patient's hand or requests fresh scan from nursing desk.
- **Data State:** Case marked `SOURCE_MEDIA_OFFLINE`; case uncertainty $U_t$ penalized.
- **Audit Event:** `EVENT_STORAGE_REFERENCE_BROKEN`.
- **Recovery:** IT resolves storage mount; media access restored without data corruption.

---

### Failure 21: Corrupted Media File on Disk
- **Failure:** Bit rot or bad sectors corrupt a stored audio file `/var/data/clinova/media/aud_89f1.wav`.
- **Safety Risk:** Inaudible noise or application crash upon attempting playback.
- **Detection:** Media stream loader catches audio decode error; flags corrupted container.
- **System Response:** Prevents audio player crash; surfaces warning: *"Audio file container damaged; reviewing verified transcript."*
- **Human Response:** Clinician relies on verified transcript text signed off by triage nurse.
- **Data State:** Raw source record flagged `IS_CORRUPTED = TRUE`.
- **Audit Event:** `EVENT_MEDIA_CORRUPTION_DETECTED`.
- **Recovery:** Redundant edge backup restored from cloud sync vault if available.

---

### Failure 22: Cryptographic Checksum Mismatch
- **Failure:** SHA-256 hash of document image on disk does NOT match `file_checksum_sha256` recorded in database.
- **Safety Risk:** Malicious tampering or undetected disk corruption compromising legal evidence admissibility.
- **Detection:** Scheduled security audit daemon recalculates hash; detects mismatch.
- **System Response:** Immediately isolates file; marks case `INTEGRITY_DISPUTED`; alerts Chief Information Security Officer (CISO).
- **Human Response:** Hospital legal and IT team investigate potential filesystem tampering.
- **Data State:** Document extraction quarantined; excluded from legal report exports.
- **Audit Event:** `EVENT_SECURITY_HASH_MISMATCH` in `security_tamper_audit_logs`.
- **Recovery:** Forensic examination determines cause; clean signed copy restored from write-once audit archive.

---

### Failure 23: Unauthorized Access Attempt to Sensitive Source Media
- **Failure:** Hospital billing clerk attempts to access psychiatric consultation audio recording.
- **Safety Risk:** Severe breach of patient mental health privacy under Mental Healthcare Act, 2017 and DPDP Act, 2023.
- **Detection:** Provenance access control gate checks role (`FACILITY_ADMINISTRATOR`) against `VIEW_RAW_MEDIA` permission.
- **System Response:** Denies request (`403 Forbidden`); suppresses audio player; logs security incident.
- **Human Response:** Clerk receives notice: *"Access Restricted: Clinical credential required."*
- **Data State:** Zero unauthorized data exposed.
- **Audit Event:** `EVENT_UNAUTHORIZED_ACCESS_DENIED`.
- **Recovery:** Confidentiality preserved; privacy audit log updated for Data Protection Officer (DPO).

---

### Failure 24: Erroneous Hardware Timestamp / Clock Drift
- **Failure:** Rural edge tablet hardware clock drifted by 3 days into the future due to dead CMOS battery.
- **Safety Risk:** Future-dated records breaking clinical time-series models and timeline ordering.
- **Detection:** Ingestion temporal validator compares `capture_timestamp` against central NTP server: detects drift $> 24\text{ hours}$.
- **System Response:** Flags clock anomaly; normalizes logical event ordering via monotonic sequence counters; prompts edge calibration.
- **Human Response:** IT technician replaces tablet CMOS battery and enables network time synchronization.
- **Data State:** Record committed with corrected logical sequence and flag `CLOCK_DRIFT_CORRECTED`.
- **Audit Event:** `EVENT_CLOCK_DRIFT_COMPENSATED`.
- **Recovery:** Clinical timeline preserved in proper biological sequence.

---

### Failure 25: Machine Translation Semantic Distortion
- **Failure:** Automated translation converts vernacular Odia phrase *"Mo munda ghurauchi"* into *"My head is rotating"* instead of *"Dizziness / Lightheadedness"*.
- **Safety Risk:** Confusion of clinical picture; mistaken for psychiatric delusion rather than vertigo/syncope.
- **Detection:** Medical entity extractor detects low confidence mapping to psychiatric delusions ($C < 0.40$).
- **System Response:** Displays raw Odia text alongside English translation in clinical intake card.
- **Human Response:** Bilingual doctor reads original Odia phrase, recognizes classic idiom for vestibular vertigo, confirms vertigo.
- **Data State:** Translation record updated with clinical normalization; mapping corrected.
- **Audit Event:** `EVENT_TRANSLATION_NORMALIZED`.
- **Recovery:** Diagnostic clarity achieved; appropriate vestibular suppressant prescribed.

---

## 3. Resilience Summary

By systematically anticipating and architecting deterministic responses to all 25 failure modes, CLINOVA AI guarantees that **no single hardware fault, model hallucination, human typo, or network partition can silently compromise clinical patient safety**.
