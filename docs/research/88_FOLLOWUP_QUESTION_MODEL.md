# CLINOVA AI — Follow-Up Questions & Interactive Completion Data Model

> **Document ID:** `RES-88`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 6 — Master Case / Data Model Specification  
> **Version:** 6.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Systems Architecture & Health Informatics Research Group  

---

## 1. Architectural Foundations: Targeted Next-Best-Information (NBI)

When the Missing Information Audit (`STATE_MISSING_AUDIT`) identifies critical clinical gaps, asking 20 generic questions causes severe cognitive fatigue and session abandonment. In illiterate or stressed rural patients, endless forms cause high drop-off rates.

CLINOVA AI enforces **Targeted Next-Best-Information (NBI) Questioning**:
1. **Hard Upper Bound:** Maximum 1 to 3 high-yield questions presented per patient session.
2. **Multi-Target Respondents:** Questions are targeted specifically to `PATIENT`, `CAREGIVER`, `NURSE`, or `DOCTOR`.
3. **Multimodal Response Formats:** Supports `BOOLEAN`, `CHOICE`, `NUMBER`, `TEXT`, and vernacular `VOICE`.
4. **Architectural Continuity:** Reconciles with the codebase's existing completion architecture (Alembic migration `0009_phase5_intelligent_completion_architecture.py`).

---

## 2. Relational Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FOLLOW-UP QUESTIONING SCHEMA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  cases (case_id PK)                                                         │
│    │                                                                        │
│    ├── completion_sessions (session_id PK, case_id FK)                      │
│    │     └── [Turn Counter, Max Turns (3), Stopping Reason, Readiness Score]│
│    │                                                                        │
│    └── followup_questions (question_id PK, session_id FK, case_id FK)       │
│          ├── [Target Respondent, Modality, Question Text, Language]         │
│          └── followup_answers (answer_id PK, question_id FK)                │
│                └── [Extracted Value, Audio Pointer, Verification State]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Relational DDL Specification (PostgreSQL / Supabase)

### 3.1 `completion_sessions` Table

```sql
CREATE TABLE completion_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    session_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'
        CHECK (session_status IN ('ACTIVE', 'COMPLETED', 'TIMED_OUT', 'ABANDONED', 'ESCALATED_EMERGENCY')),
    current_turn INTEGER NOT NULL DEFAULT 1,
    max_turns INTEGER NOT NULL DEFAULT 3,
    questions_presented_count INTEGER NOT NULL DEFAULT 0,
    questions_answered_count INTEGER NOT NULL DEFAULT 0,
    initial_gap_count INTEGER NOT NULL,
    remaining_gap_count INTEGER NOT NULL,
    initial_readiness_score NUMERIC(4,3) NOT NULL,
    current_readiness_score NUMERIC(4,3) NOT NULL,
    stopping_reason VARCHAR(64), -- 'ALL_CRITICAL_GAPS_RESOLVED', 'MAX_TURNS_REACHED', 'TIMEOUT_SKIP'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX ix_comp_sessions_case ON completion_sessions(case_id);
```

### 3.2 `followup_questions` Table

```sql
CREATE TABLE followup_questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    session_id UUID NOT NULL REFERENCES completion_sessions(id) ON DELETE CASCADE,
    missing_item_id UUID REFERENCES missing_information_items(missing_item_id) ON DELETE SET NULL,
    turn_number INTEGER NOT NULL CHECK (turn_number >= 1 AND turn_number <= 3),
    target_respondent VARCHAR(32) NOT NULL DEFAULT 'PATIENT'
        CHECK (target_respondent IN ('PATIENT', 'CAREGIVER', 'NURSE', 'DOCTOR')),
    question_text TEXT NOT NULL,
    language_code VARCHAR(16) NOT NULL DEFAULT 'or', -- Odia, Hindi, English
    response_type VARCHAR(32) NOT NULL 
        CHECK (response_type IN ('BOOLEAN', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'NUMERIC', 'TEXT', 'VOICE')),
    options_json JSONB, -- For CHOICE: [{"code": "YES", "label": "Yes / ହଁ"}, ...]
    priority_score NUMERIC(4,3) NOT NULL DEFAULT 1.000,
    clinical_rationale TEXT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'PRESENTED'
        CHECK (status IN ('PRESENTED', 'ANSWERED', 'SKIPPED', 'TIMED_OUT')),
    presented_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    answered_at TIMESTAMPTZ
);

CREATE INDEX ix_fu_questions_case ON followup_questions(case_id);
CREATE INDEX ix_fu_questions_session ON followup_questions(session_id);
```

### 3.3 `followup_answers` Table

```sql
CREATE TABLE followup_answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL UNIQUE REFERENCES followup_questions(question_id) ON DELETE CASCADE,
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    response_type VARCHAR(32) NOT NULL,
    response_value_raw TEXT NOT NULL,
    response_value_normalized JSONB NOT NULL,
    response_audio_id UUID REFERENCES audio_recordings(id) ON DELETE SET NULL,
    answered_by_actor_id UUID NOT NULL REFERENCES users(id),
    answered_by_actor_role VARCHAR(32) NOT NULL,
    source_type VARCHAR(32) NOT NULL DEFAULT 'PATIENT_REPORTED'
        CHECK (source_type IN ('PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'STAFF_ENTERED', 'CLINICIAN_VERIFIED')),
    latency_seconds NUMERIC(5,2),
    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_fu_answers_case ON followup_answers(case_id);
```

---

## 4. SQLite Dialect Implementation (Local Edge Mini-PC)

```sql
CREATE TABLE completion_sessions (
    id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    session_status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (session_status IN ('ACTIVE', 'COMPLETED', 'TIMED_OUT', 'ABANDONED', 'ESCALATED_EMERGENCY')),
    current_turn INTEGER NOT NULL DEFAULT 1,
    max_turns INTEGER NOT NULL DEFAULT 3,
    questions_presented_count INTEGER NOT NULL DEFAULT 0,
    questions_answered_count INTEGER NOT NULL DEFAULT 0,
    initial_gap_count INTEGER NOT NULL,
    remaining_gap_count INTEGER NOT NULL,
    initial_readiness_score REAL NOT NULL,
    current_readiness_score REAL NOT NULL,
    stopping_reason TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE followup_questions (
    question_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    session_id TEXT NOT NULL REFERENCES completion_sessions(id) ON DELETE CASCADE,
    missing_item_id TEXT REFERENCES missing_information_items(missing_item_id) ON DELETE SET NULL,
    turn_number INTEGER NOT NULL CHECK (turn_number >= 1 AND turn_number <= 3),
    target_respondent TEXT NOT NULL DEFAULT 'PATIENT' CHECK (target_respondent IN ('PATIENT', 'CAREGIVER', 'NURSE', 'DOCTOR')),
    question_text TEXT NOT NULL,
    language_code TEXT NOT NULL DEFAULT 'or',
    response_type TEXT NOT NULL CHECK (response_type IN ('BOOLEAN', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'NUMERIC', 'TEXT', 'VOICE')),
    options_json TEXT, -- JSON text
    priority_score REAL NOT NULL DEFAULT 1.0,
    clinical_rationale TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PRESENTED' CHECK (status IN ('PRESENTED', 'ANSWERED', 'SKIPPED', 'TIMED_OUT')),
    presented_at TEXT NOT NULL,
    answered_at TEXT
);

CREATE TABLE followup_answers (
    answer_id TEXT PRIMARY KEY NOT NULL,
    question_id TEXT NOT NULL UNIQUE REFERENCES followup_questions(question_id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    response_type TEXT NOT NULL,
    response_value_raw TEXT NOT NULL,
    response_value_normalized TEXT NOT NULL, -- JSON text
    response_audio_id TEXT REFERENCES audio_recordings(id) ON DELETE SET NULL,
    answered_by_actor_id TEXT NOT NULL REFERENCES users(id),
    answered_by_actor_role TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'PATIENT_REPORTED' CHECK (source_type IN ('PATIENT_REPORTED', 'VOICE_TRANSCRIBED', 'STAFF_ENTERED', 'CLINICIAN_VERIFIED')),
    latency_seconds REAL,
    answered_at TEXT NOT NULL
);
```

---

## 5. Invariants Governing Follow-Up Questioning

$$\begin{aligned}
\mathbf{Inv\ Q\text{-}1} &: \quad \forall s \in \text{CompletionSessions}, \quad s.\text{questions\_presented\_count} \le s.\text{max\_turns} \le 3 \\
\mathbf{Inv\ Q\text{-}2} &: \quad q.\text{status} = \text{'ANSWERED'} \iff \exists a \in \text{FollowupAnswers} \text{ s.t. } a.\text{question\_id} = q.\text{question\_id} \\
\mathbf{Inv\ Q\text{-}3} &: \quad \text{If patient response triggers a Red Flag (e.g. crushing chest pain = TRUE), instant emergency jump executes.}
\end{aligned}$$
