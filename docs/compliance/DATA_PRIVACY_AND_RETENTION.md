# CLINOVA AI — Data Privacy, Anonymization & Retention Policy

## 1. Privacy-by-Design Architecture
CLINOVA AI protects patient privacy through automated de-identification at the ingestion boundary:

1. **Direct Identifier Stripping:**
   - Patient names, phone numbers, email addresses, and national IDs (Aadhaar, ABHA) are redacted via deterministic regex patterns and NLP named-entity recognition.
2. **Synthetic Identifier Assignment:**
   - Every case receives an ephemeral synthetic identifier (`CLV-xxxx` or `CG-xxxx`) unlinked from identifiable government registers in the prototype environment.
3. **Audio Biometrics Protection:**
   - Voice recordings are processed in-memory for speech-to-text conversion and discarded immediately after transcription verification.

---

## 2. Minimal Data Retention Schedule

```
┌──────────────────────────────┬────────────────────────────┬─────────────────────────────┐
│ Artifact Type                │ Retention Period           │ Disposal Method             │
├──────────────────────────────┼────────────────────────────┼─────────────────────────────┤
│ Raw Audio Recordings         │ Ephemeral (In-Memory / 1 hr│ Secure overwrite & wipe     │
│ Uploaded Lab Scans / PDFs    │ 24 Hours                   │ Secure unlinking & delete   │
│ Synthesized Triage Sessions  │ 24 Hours (Demo / Prototype)│ Database cascade drop       │
│ Audit Trail (De-identified)  │ 90 Days                    │ Encrypted log archive       │
└──────────────────────────────┴────────────────────────────┴─────────────────────────────┘
```

---

## 3. Prototype Synthetic Data Guarantee
For educational, benchmarking, and demonstration purposes, the system operates exclusively on synthetic patient scenarios, simulated lab reports, and open public health statistics.
