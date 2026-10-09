"""CLINOVA AI — Deterministic Mock Runtime Adapter for Isolated Validation.

Phase 10: Local AI Runtime Foundation & Safe Inference Architecture.
Hermetic test double allowing comprehensive test harness execution without external daemons.
Supports pre-configured responses and explicit error/anomaly injection.
"""

import json
from typing import Dict, Any, Optional
from app.ai_runtime.adapters.base import RuntimeAdapter
from app.ai_runtime.models import (
    RuntimeConfig,
    RuntimeState,
    ModelDescriptor,
    EconomicTier,
)


class MockDeterministicAdapter(RuntimeAdapter):
    """Zero-dependency deterministic mock runtime for isolated testing."""

    def __init__(self, config: Optional[RuntimeConfig] = None):
        if config is None:
            config = RuntimeConfig(
                endpoint_url="mock://in-process",
                model_descriptor=ModelDescriptor(
                    model_id="qwen3-4b-instruct-mock",
                    version="1.0.0-mock",
                    quantization="Q4_K_M",
                    parameter_count_billions=4.0,
                    license="Apache-2.0",
                    context_window_tokens=8192,
                    memory_budget_mb=3200,
                    economic_tier=EconomicTier.FREE_LOCAL,
                )
            )
        super().__init__(config)
        self.injected_response: Optional[str] = None
        self.inject_malformed_json: bool = False
        self.inject_timeout: bool = False
        self.inject_oom: bool = False
        self.inject_unavailable: bool = False
        self.health_state: RuntimeState = RuntimeState.MODEL_READY

    def set_injected_response(self, response_text: str):
        """Sets an explicit text response to be returned by next call."""
        self.injected_response = response_text

    def set_injected_error(
        self,
        malformed_json: bool = False,
        timeout: bool = False,
        oom: bool = False,
        unavailable: bool = False,
    ):
        """Configures simulated runtime failure modes."""
        self.inject_malformed_json = malformed_json
        self.inject_timeout = timeout
        self.inject_oom = oom
        self.inject_unavailable = unavailable
        if unavailable:
            self.health_state = RuntimeState.MODEL_UNAVAILABLE
        else:
            self.health_state = RuntimeState.MODEL_READY

    async def check_health(self) -> RuntimeState:
        if self.inject_unavailable:
            return RuntimeState.MODEL_UNAVAILABLE
        return self.health_state

    async def get_model_info(self) -> ModelDescriptor:
        return self.config.model_descriptor

    async def invoke_raw(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        enforce_json: bool = True,
    ) -> str:
        """Produces mocked completion or simulates failure conditions."""
        if self.inject_unavailable:
            raise RuntimeError("MODEL_UNAVAILABLE: Mock inference engine is offline.")
        if self.inject_timeout:
            raise TimeoutError("TIMEOUT: Mock inference exceeded request timeout limit.")
        if self.inject_oom:
            raise MemoryError("OUT_OF_MEMORY: Host memory exhausted during tensor allocation.")
        if self.inject_malformed_json:
            return '{"status": "INCOMPLETE_JSON", "unclosed_brace": [1, 2, '

        if self.injected_response is not None:
            resp = self.injected_response
            self.injected_response = None  # Consume single-use injection
            return resp

        # Extract evidence ID dynamically from user_prompt if present
        import re
        ev_id = "ev-test-001"
        match = re.search(r'id="([^"]+)"', user_prompt)
        if match:
            ev_id = match.group(1)

        # Default standard valid response depending on task in user_prompt / system_prompt
        if "EXTRACTION" in system_prompt or "symptoms" in user_prompt:
            return json.dumps({
                "symptoms": [
                    {
                        "name": "Chest Pain",
                        "duration": "2 hours",
                        "severity": "SEVERE",
                        "body_site": "Substernal",
                        "source_evidence_id": ev_id,
                    }
                ],
                "vital_mentions": [
                    {
                        "parameter": "HR",
                        "value": 110.0,
                        "unit": "bpm",
                        "source_evidence_id": ev_id,
                    }
                ],
                "reported_allergies": ["Penicillin"],
                "reported_medications": ["Aspirin 75mg"],
                "identified_gaps": ["Cardiac enzyme history missing"],
            })

        if "TIMELINE" in system_prompt or "timeline_events" in user_prompt:
            return json.dumps({
                "timeline_events": [
                    {
                        "event_title": "Symptom Onset",
                        "relative_time": "2 hours prior to presentation",
                        "description": "Patient developed sudden onset retrosternal chest pain and diaphoresis.",
                        "source_evidence_ids": [ev_id],
                        "epistemic_status": "INFERRED",
                    },
                    {
                        "event_title": "Triage Presentation",
                        "relative_time": "Presentation",
                        "description": "Arrived at triage with elevated heart rate (HR 110 bpm).",
                        "source_evidence_ids": [ev_id],
                        "epistemic_status": "VERIFIED",
                    }
                ],
                "chronological_progression": "Sudden onset chest pain progressing over 2 hours without spontaneous relief.",
                "unresolved_items": ["Exact time of last meal", "Prior cardiac intervention dates"],
                "conflict_notes": [],
            })

        if "MISSING_INFO" in system_prompt or "MISSING_INFORMATION" in system_prompt:
            return json.dumps({
                "identified_gaps": [
                    {
                        "parameter_name": "Electrocardiogram (ECG)",
                        "clinical_rationale": "Essential to evaluate ST-segment elevation or acute ischemia in acute chest pain.",
                        "priority": "CRITICAL",
                        "target_domain": "LABS",
                        "recommended_action": "Perform 12-lead ECG immediately upon clinician review.",
                        "evidence_reference": ev_id,
                    },
                    {
                        "parameter_name": "Cardiac Troponin",
                        "clinical_rationale": "Required for confirming or ruling out myocardial injury.",
                        "priority": "IMPORTANT",
                        "target_domain": "LABS",
                        "recommended_action": "Order point-of-care or laboratory cardiac troponin.",
                        "evidence_reference": ev_id,
                    }
                ],
                "completeness_score": 0.75,
                "high_priority_gap_count": 1,
                "epistemic_uncertainty_note": "Critical diagnostic baseline ECG is currently unrecorded.",
            })

        if "CASE_SUMMARY" in system_prompt:
            return json.dumps({
                "chief_complaint": "Acute onset substernal chest discomfort",
                "brief_chronology": "Patient presented with 2 hours of crushing retrosternal pain radiating to left jaw.",
                "pertinent_positives": ["Diaphoresis", "Tachycardia (HR 110)"],
                "pertinent_negatives": ["No fever", "No vomiting"],
                "uncertainty_statement": "Prior ECG baseline and family cardiac history are unrecorded.",
                "epistemic_distinctions": {
                    "KNOWN": ["Chest pain duration 2h", "Heart rate 110 bpm"],
                    "UNKNOWN": ["Baseline ECG", "Troponin status"],
                    "CONFLICTING": [],
                    "UNRELIABLE": [],
                    "VERIFIED": ["Triage vitals recorded by nurse"],
                    "INFERRED": ["Suspected acute coronary syndrome based on symptoms"],
                },
                "source_evidence_ids": [ev_id],
            })

        if "SUMMARY" in system_prompt:
            return json.dumps({
                "chief_complaint": "Acute onset substernal chest discomfort",
                "brief_chronology": "Patient presented with 2 hours of crushing retrosternal pain radiating to left jaw.",
                "pertinent_positives": ["Diaphoresis", "Tachycardia (HR 110)"],
                "pertinent_negatives": ["No fever", "No vomiting"],
                "uncertainty_statement": "Prior ECG baseline and family cardiac history are unrecorded.",
                "epistemic_distinctions": {
                    "KNOWN": ["Chest pain duration 2h", "Heart rate 110 bpm"],
                    "UNKNOWN": ["Baseline ECG", "Troponin status"],
                    "CONFLICTING": [],
                    "UNRELIABLE": [],
                    "VERIFIED": ["Triage vitals recorded by nurse"],
                    "INFERRED": ["Suspected acute coronary syndrome based on symptoms"],
                },
                "source_evidence_ids": [ev_id],
            })

        if "QUESTION" in system_prompt or "FOLLOWUP" in system_prompt or "candidate_questions" in user_prompt:
            return json.dumps({
                "candidate_questions": [
                    {
                        "question_text": "Does the chest pain radiate to your left arm or jaw?",
                        "language": "en",
                        "information_gap": "Radiation of chest pain",
                        "rationale": "Clarifies typical anginal features vs musculoskeletal cause",
                        "priority": 1,
                        "target_evidence_id": ev_id,
                    }
                ],
                "total_gaps_identified": 1,
            })

        if "TRANSLATION" in system_prompt or "target_language" in user_prompt:
            return json.dumps({
                "source_text": "chhati re gapa gapa laguchi",
                "source_language": "od",
                "target_language": "en",
                "translated_text": "Patient reports severe chest heaviness / tightness.",
                "preserved_colloquialisms": {
                    "gapa gapa": "colloquial Odia idiom denoting suffocating, heavy chest constriction"
                },
            })

        if "NORMALIZATION" in system_prompt or "colloquial_term" in user_prompt:
            return json.dumps({
                "entities": [
                    {
                        "colloquial_term": "chhati re gapa gapa",
                        "standard_concept": "Chest tightness",
                        "coding_system": "SNOMED-CT",
                        "concept_code": "29857009",
                        "mapping_confidence": 0.92,
                    }
                ]
            })

        if "DRAFT_NOTE" in system_prompt or "TRIAGE_DRAFT" in system_prompt or "subjective_draft" in user_prompt:
            return json.dumps({
                "subjective_draft": "Patient reports retrosternal chest pain of 2 hours duration.",
                "objective_observations_draft": "Heart rate 110 bpm, tachycardic, diaphoretic.",
                "vital_summary_draft": "HR 110 bpm, tachycardic at presentation.",
                "deterministic_risk_summary": "P2_VERY_URGENT risk tier based on tachycardia and chest pain red flag.",
                "clinical_concerns": ["Acute Coronary Syndrome", "Aortic Dissection rule-out"],
                "suggested_next_steps": ["Immediate 12-lead ECG", "IV access", "Clinician review"],
                "uncertainty_and_gaps": "Baseline cardiac history and serial troponins unrecorded.",
                "advisory_considerations_draft": "Consider acute coronary evaluation and serial troponin.",
                "disclaimer": "DRAFT ASSISTANT NOTE ONLY. NOT A FINAL CLINICAL RECORD. REQUIRES RMP REVIEW AND SIGN-OFF.",
            })

        if "ADVISORY" in system_prompt or "differential_considerations" in user_prompt:
            return json.dumps({
                "candidate_signals": ["Cardiac", "Ischemic"],
                "differential_considerations": [
                    {
                        "condition_name": "Acute Coronary Syndrome",
                        "supporting_evidence_ids": [ev_id],
                        "opposing_evidence_ids": [],
                        "epistemic_note": "Candidate consideration based on retrosternal discomfort and tachycardia.",
                    }
                ],
                "suggested_diagnostic_pathways": ["12-lead ECG", "Serum Troponin"],
                "safety_reminders": ["Maintain continuous monitoring while awaiting physician."],
                "is_autonomous_diagnosis": False,
            })

        # Generic valid fallback JSON
        return json.dumps({"status": "SUCCESS", "message": "Default mock response"})
