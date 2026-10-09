# CLINOVA AI — Dataset Versioning & Lineage Policy

> **Document ID:** `RES-251`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Data Governance, AI Artifact Management & Lineage Group  

---

## 1. Lineage Policy & Immutability Invariant
Under CLINOVA Data Governance policy:
$$\text{NEVER SILENTLY REPLACE AN EXISTING BENCHMARK DATASET.}$$

Every dataset release must carry immutable cryptographic and metadata versioning. Any alteration to source records, schema definitions, or split partitions mandates incrementing the version tag and recording a new lineage ledger entry.

---

## 2. Mandatory Dataset Metadata Schema
Every published dataset release must record ten canonical metadata attributes:
1. `dataset_id`: Unique identifier (e.g. `CLINOVA-SYNTHETIC-PHASE11`).
2. `version`: Semantic version tag (`v1.0.0-phase11`).
3. `creation_date`: ISO-8601 UTC timestamp (`2026-10-08T14:00:00Z`).
4. `generator_version`: Code version of generator (`v1.0.0-generator`).
5. `schema_version`: Canonical schema version (`v1.0.0-canonical-22`).
6. `split`: Partition identifier (`TRAIN`, `VALIDATION`, `TEST`, `ADVERSARIAL_TEST`, `MULTILINGUAL_TEST`, `SAFETY_TEST`).
7. `record_count`: Number of validated JSONL records in partition.
8. `language_distribution`: Exact count and percentage of `en`, `hi`, `od`, and `mixed` records.
9. `environment_distribution`: Distribution across `OPD`, `EMERGENCY_DEPT`, `WARD`, `OT`, `COMMUNITY_HEALTH`, `TELEMEDICINE`.
10. `safety_case_count`: Number of explicit adversarial and safety boundary cases.

---

## 3. Phase 11 Canonical Dataset Registry

| Dataset Artifact | Split Identifier | Version Tag | Records | Byte Size | SHA-256 Checksum (Prefix) |
|---|---|:---:|:---:|:---:|---|
| `data/synthetic/train.jsonl` | `TRAIN` | `v1.0.0-phase11` | 4 | 10,257 B | `f8b2c4...` |
| `data/synthetic/validation.jsonl` | `VALIDATION` | `v1.0.0-phase11` | 2 | 5,268 B | `e3a9d1...` |
| `data/synthetic/test.jsonl` | `TEST` | `v1.0.0-phase11` | 5 | 12,189 B | `a7c1b5...` |
| `data/synthetic/adversarial_test.jsonl` | `ADVERSARIAL_TEST` | `v1.0.0-phase11` | 4 | 9,700 B | `4d2e8f...` |
| `data/synthetic/multilingual_test.jsonl` | `MULTILINGUAL_TEST` | `v1.0.0-phase11` | 3 | 8,280 B | `91b6c7...` |
| `data/synthetic/safety_test.jsonl` | `SAFETY_TEST` | `v1.0.0-phase11` | 2 | 4,684 B | `3c8f12...` |
