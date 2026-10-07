# CLINOVA AI — PHASE 4: VERIFY REST API SPECIFICATION

All Phase 4 endpoints are exposed under `/api/v1/cases/` and require valid JWT Bearer authentication.

---

## 1. Endpoints Overview

| Method | Path | Role Authorization | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/cases/{case_id}/verify` | Patient (owner), Nurse, Staff, Doctor, Admin | Executes verification engine pipeline on current case snapshot. |
| `GET` | `/api/v1/cases/{case_id}/verification` | Patient (owner), Nurse, Staff, Doctor, Admin | Retrieves latest verification run, findings, conflicts, and stale status. |
| `GET` | `/api/v1/cases/{case_id}/verification/runs` | Patient (owner), Nurse, Staff, Doctor, Admin | Lists all historical verification runs for the case. |
| `GET` | `/api/v1/cases/{case_id}/verification/runs/{run_id}` | Patient (owner), Nurse, Staff, Doctor, Admin | Retrieves a specific verification run by ID. |
| `GET` | `/api/v1/cases/{case_id}/verification/findings` | Patient (owner), Nurse, Staff, Doctor, Admin | Lists findings with optional severity, status, or category filters. |
| `POST` | `/api/v1/cases/{case_id}/verification/findings/{finding_id}/resolve` | Nurse, Staff, Doctor, Admin | Resolves an open finding with clinician rationale. |
| `GET` | `/api/v1/cases/{case_id}/review-readiness` | Patient (owner), Nurse, Staff, Doctor, Admin | Returns an explainable review readiness index and summary. |

---

## 2. Endpoint Details

### 2.1 Trigger Verification Run
- **Route:** `POST /api/v1/cases/{case_id}/verify`
- **Request Body (Optional):**
```json
{
  "force_reverify": false,
  "include_ai_checks": true
}
```
- **Response (200 OK):**
```json
{
  "id": "c1f7a0b2-4d5e-4c7a-9a8f-123456789abc",
  "case_id": "a2b3c4d5-...",
  "case_version": 1,
  "status": "completed",
  "engine_version": "4.0.0",
  "ruleset_version": "4.0.0",
  "review_readiness_status": "review_ready",
  "review_readiness_score": 0.85,
  "review_readiness_reasons": [
    "Case information is complete, internally consistent, and fully grounded to source evidence.",
    "Patient identity verified.",
    "Presenting complaint and symptom graph documented.",
    "2 multimodal evidence records linked with SHA-256 provenance."
  ],
  "findings_count": 1,
  "blocking_findings_count": 0,
  "high_findings_count": 0,
  "unresolved_findings_count": 1,
  "structural_integrity_status": "VALID",
  "completeness_status": "COMPLETE",
  "consistency_status": "CONSISTENT",
  "temporal_status": "COHERENT",
  "provenance_status": "COMPLETE",
  "uncertainty_status": "CLEAR",
  "is_current": true,
  "is_stale": false,
  "latency_ms": 42,
  "started_at": "2026-10-06T22:30:00Z",
  "completed_at": "2026-10-06T22:30:00Z",
  "findings": [
    {
      "id": "f1a2b3c4-...",
      "finding_type": "EVIDENCE_QUALITY",
      "category": "MEASUREMENTS",
      "field_name": "Blood Pressure",
      "severity": "LOW",
      "status": "UNRESOLVED",
      "is_blocking": false,
      "title": "Patient-Reported Vital Sign: Blood Pressure",
      "description": "Vital sign 'Blood Pressure' (120/80 mmHg) is patient-reported rather than clinically measured.",
      "explanation": "Patient self-reported vitals must be distinguished from objective medical device measurements taken at triage.",
      "rule_id": "evidence_status_awareness_rule",
      "rule_version": "4.0.0"
    }
  ],
  "conflicts": []
}
```

### 2.2 Resolve Verification Finding
- **Route:** `POST /api/v1/cases/{case_id}/verification/findings/{finding_id}/resolve`
- **Authorization:** Nurse, Staff, Doctor, Admin (Patients receive `403 Forbidden`).
- **Request Body:**
```json
{
  "resolution_state": "RESOLVED_BY_HUMAN_VERIFICATION",
  "resolution_notes": "Reading confirmed via manual sphygmomanometer check at triage."
}
```
- **Response (200 OK):**
```json
{
  "id": "f1a2b3c4-...",
  "status": "RESOLVED_BY_HUMAN_VERIFICATION",
  "resolution_notes": "Reading confirmed via manual sphygmomanometer check at triage.",
  "resolved_by_user_id": "u-doc-123",
  "resolved_at": "2026-10-06T22:35:00Z"
}
```

### 2.3 Review Readiness Summary
- **Route:** `GET /api/v1/cases/{case_id}/review-readiness`
- **Response (200 OK):**
```json
{
  "case_id": "a2b3c4d5-...",
  "case_version": 2,
  "verified_case_version": 1,
  "review_readiness_status": "review_ready",
  "review_readiness_score": 0.85,
  "review_readiness_reasons": [
    "Patient identity verified.",
    "Presenting complaint and symptom graph documented."
  ],
  "is_stale": true,
  "blocking_count": 0,
  "unresolved_count": 1,
  "completeness_status": "COMPLETE",
  "consistency_status": "CONSISTENT",
  "temporal_status": "COHERENT",
  "provenance_status": "COMPLETE",
  "uncertainty_status": "CLEAR",
  "last_verified_at": "2026-10-06T22:30:00Z"
}
```

---

## 3. Error Handling

- `401 Unauthorized`: Missing or expired JWT access token.
- `403 Forbidden`: Cross-patient IDOR access attempt (Patient B attempting to access Patient A's verification), or Patient attempting to resolve a clinician finding.
- `404 Not Found`: Case or finding ID does not exist.
- `422 Unprocessable Entity`: Invalid request payload.
- `500 Internal Server Error`: Verification engine failure (recorded in `verification_runs` with `status: failed` and safe degradation).
