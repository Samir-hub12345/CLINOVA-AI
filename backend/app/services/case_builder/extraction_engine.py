"""Structured extraction engine for Clinova AI.

Extracts discrete canonical clinical facts with strict anti-hallucination ground checks,
negation detection, certainty tagging, attribution tracking, and temporal structuring.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from app.models.case_evidence import CaseEvidence, EvidenceSourceType
from app.models.canonical_case import FactPolarity, FactCertainty, TemporalStatus


class CandidateFact:
    """Internal representation of a candidate fact before persistence."""
    def __init__(
        self,
        category: str,
        concept: str,
        value: str,
        source_evidence_id: Optional[str] = None,
        source_span: Optional[str] = None,
        polarity: str = FactPolarity.AFFIRMED.value,
        certainty: str = FactCertainty.REPORTED.value,
        attribution: str = "PATIENT_REPORTED",
        temporal_status: str = TemporalStatus.CURRENT.value,
        duration: Optional[str] = None,
        onset_approximate: Optional[str] = None,
        unit: Optional[str] = None,
        normalized_value: Optional[str] = None,
    ):
        self.category = category
        self.concept = concept
        self.value = value
        self.source_evidence_id = source_evidence_id
        self.source_span = source_span
        self.polarity = polarity
        self.certainty = certainty
        self.attribution = attribution
        self.temporal_status = temporal_status
        self.duration = duration
        self.onset_approximate = onset_approximate
        self.unit = unit
        self.normalized_value = normalized_value


class StructuredExtractionEngine:
    """Extracts grounded clinical facts from multimodal evidence records."""

    # Negation trigger patterns
    NEGATION_PATTERNS = [
        r"\b(no|not|denies|denied|denying|without|absent|rules\s+out|ruled\s+out|negative\s+for|none|no\s+history\s+of)\b",
        r"\b(না|नाହିଁ|ନୁହେଁ|ନାଇଁ)\b",  # Odia/Bengali negation cues
        r"\b(नहीं|ना)\b",  # Hindi negation cues
    ]

    # Uncertainty trigger patterns
    UNCERTAINTY_PATTERNS = [
        r"\b(possible|suspected|maybe|approximate|unsure|questionable|borderline|equivocal|probable|likely|uncertain)\b",
        r"\b(ହୁଏତ|ସମ୍ଭାବ୍ୟ)\b",  # Odia uncertainty
        r"\b(शायद|संभवतः)\b",  # Hindi uncertainty
    ]

    # Temporal patterns
    DURATION_PATTERNS = [
        r"\bfor\s+(\d+\s*(?:days?|weeks?|months?|years?|hours?|mins?|minutes?))\b",
        r"\b(\d+\s*(?:days?|weeks?|months?|years?))\s*dhari\b",  # Indic translit
        r"\b(\d+)\s*(?:दिन|ଦିନ)\b",  # Hindi/Odia days
    ]

    ONSET_PATTERNS = [
        r"\bsince\s+([a-zA-Z0-9\s]+?)(?:,|\.|$|and)",
        r"\b(\d+\s*(?:days?|weeks?|months?|years?))\s+ago\b",
        r"\bstarted\s+([a-zA-Z0-9\s]+?)(?:,|\.|$)",
    ]

    # Clinical concept dictionary for deterministic extraction
    SYMPTOMS_MAP = {
        "chest pain": ["chest pain", "angina", "chest tightness", "substernal pain", "chest pressure", "ଛାତିରେ ଯନ୍ତ୍ରଣା", "छाती में दर्द"],
        "shortness of breath": ["shortness of breath", "dyspnea", "breathlessness", "difficulty breathing", "sob", "ନିଶ୍ୱାସ ନେବାରେ କଷ୍ଟ", "सांस लेने में तकलीफ", "सांस फूलना"],
        "fever": ["fever", "pyrexia", "high temp", "chills", "febrile", "ଜ୍ୱର", "बुखार"],
        "headache": ["headache", "head pain", "migraine", "cephalea", "ମୁଣ୍ଡ ବିନ୍ଧା", "सिर दर्द"],
        "cough": ["cough", "dry cough", "productive cough", "coughing", "ଖାସ", "खांसी"],
        "fatigue": ["fatigue", "generalized weakness", "body ache", "malaise", "tiredness", "ଦୁର୍ବଳତା", "कमजोरी"],
        "nausea": ["nausea", "feeling sick", "ବାନ୍ତି ଭାବ", "जी मिचलाना"],
        "vomiting": ["vomiting", "emesis", "ବାନ୍ତି", "उल्टी"],
        "dizziness": ["dizziness", "giddiness", "lightheadedness", "vertigo", "ମୁଣ୍ଡ ବୁଲେଇବା", "चक्कर"],
        "diaphoresis": ["diaphoresis", "profuse sweating", "sweating", "cold sweat", "ଝାଳ", "पसीना"],
        "palpitations": ["palpitations", "racing heart", "rapid heartbeat", "ଧଡ଼ଧଡ଼"],
        "abdominal pain": ["abdominal pain", "stomach ache", "belly pain", "ପେଟ ବ୍ୟଥା", "पेट दर्द"],
    }

    CONDITIONS_MAP = {
        "Essential Hypertension": ["hypertension", "high blood pressure", "high bp", "htn", "उच्च रक्तचाप"],
        "Type 2 Diabetes Mellitus": ["diabetes", "type 2 diabetes", "t2dm", "high sugar", "sugar disease", "madhumeha", "मधुमेह"],
        "Asthma": ["asthma", "bronchial asthma", "दमा"],
        "Coronary Artery Disease": ["coronary artery disease", "cad", "heart disease", "ischemic heart disease"],
        "Hyperlipidemia": ["hyperlipidemia", "high cholesterol", "dyslipidemia"],
        "Chronic Kidney Disease": ["chronic kidney disease", "ckd", "renal failure"],
    }

    MEDICATIONS_MAP = {
        "Metformin": ["metformin", "glycomet"],
        "Lisinopril": ["lisinopril", "zestril"],
        "Atorvastatin": ["atorvastatin", "lipitor", "atorva"],
        "Amlodipine": ["amlodipine", "norvasc", "amlong"],
        "Paracetamol": ["paracetamol", "acetaminophen", "crocin", "dolo"],
        "Aspirin": ["aspirin", "ecosprin"],
        "Albuterol": ["albuterol", "salbutamol", "asthalin"],
    }

    ALLERGIES_MAP = {
        "Penicillin": ["penicillin", "amoxicillin allergy", "penicillin allergy"],
        "Sulfa drugs": ["sulfa drugs", "sulfa", "sulfonamides"],
        "Aspirin": ["aspirin allergy"],
        "Latex": ["latex allergy", "latex"],
    }

    def __init__(self):
        pass

    def _determine_attribution(self, source_type: Any) -> str:
        src_str = str(getattr(source_type, "value", source_type)).lower()
        if "clinician" in src_str or "staff" in src_str:
            return "CLINICIAN_ENTERED"
        elif "device" in src_str or "monitor" in src_str:
            return "DEVICE_MEASURED"
        elif "document" in src_str or "ocr" in src_str or "lab" in src_str:
            return "DOCUMENT_EXTRACTED"
        return "PATIENT_REPORTED"

    def _check_negation(self, text: str, span_start: int, span_end: int) -> bool:
        """Checks if the concept span is preceded or directly followed by a negation marker in the clause."""
        # Check window of ~50 chars before the span
        window_start = max(0, span_start - 50)
        prefix = text[window_start:span_start].lower()
        
        # Split on sentence/clause boundaries and coordinating conjunctions to prevent cross-clause negation leakage
        clauses = re.split(r"[.;?!,]|\b(?:but|and|yet|however)\b", prefix)
        clause = clauses[-1] if clauses else prefix

        for pattern in self.NEGATION_PATTERNS:
            if re.search(pattern, clause, re.IGNORECASE):
                return True

        # Check immediate suffix (only direct terms like 'absent', 'negative', 'none', not verbs like 'denies')
        suffix = text[span_end:min(len(text), span_end + 25)].lower()
        suffix_clause = re.split(r"[.;?!,]|\b(?:but|and|yet|however)\b", suffix)[0]
        for pattern in [r"\b(absent|negative|none|nil|zero)\b"]:
            if re.search(pattern, suffix_clause, re.IGNORECASE):
                return True

        return False

    def _check_uncertainty(self, text: str, span_start: int, span_end: int) -> bool:
        """Checks if the concept is accompanied by uncertainty markers."""
        window_start = max(0, span_start - 50)
        prefix = text[window_start:span_start].lower()
        clauses = re.split(r"[.;?!]", prefix)
        clause = clauses[-1] if clauses else prefix

        for pattern in self.UNCERTAINTY_PATTERNS:
            if re.search(pattern, clause, re.IGNORECASE):
                return True
        return False

    def _extract_duration(self, text: str, span_start: int, span_end: int) -> Tuple[Optional[str], Optional[str], str]:
        """Extracts duration, onset, and temporal status."""
        window_start = max(0, span_start - 60)
        window_end = min(len(text), span_end + 80)
        context = text[window_start:window_end]

        duration = None
        onset = None
        temporal_status = TemporalStatus.CURRENT.value

        for pattern in self.DURATION_PATTERNS:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                duration = match.group(1).strip()
                break

        for pattern in self.ONSET_PATTERNS:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                onset = match.group(1).strip()
                break

        # Check for historical signals
        if re.search(r"\b(\d+\s*years?\s*ago|history of|diagnosed in \d{4}|past|childhood)\b", context, re.IGNORECASE):
            temporal_status = TemporalStatus.HISTORICAL.value
        elif re.search(r"\b(resolved|stopped|no longer|past episode)\b", context, re.IGNORECASE):
            temporal_status = TemporalStatus.RESOLVED.value
        elif re.search(r"\b(recurrent|intermittent|episodes)\b", context, re.IGNORECASE):
            temporal_status = TemporalStatus.RECURRING.value
        elif duration or onset or re.search(r"\b(current|today|ongoing|now)\b", context, re.IGNORECASE):
            temporal_status = TemporalStatus.CURRENT.value

        return duration, onset, temporal_status

    def extract_from_evidence(self, evidence: CaseEvidence) -> Tuple[List[CandidateFact], int]:
        """Extracts grounded facts from a single evidence record.
        
        Returns:
            Tuple[List[CandidateFact], int]: (extracted_facts, rejected_count)
        """
        facts: List[CandidateFact] = []
        rejected_count = 0

        # Primary text to extract from: normalized_value preferred, fallback to raw_value
        text = (evidence.normalized_value or evidence.raw_value or "").strip()
        if not text:
            return facts, rejected_count

        attribution = self._determine_attribution(evidence.source_type)

        # 1. Family History Extraction (Strict Isolation!)
        # Any statement mentioning family members must NOT be assigned to patient conditions.
        fam_matches = list(re.finditer(
            r"\b(father|mother|brother|sister|parents|paternal|maternal|family\s+history)\b.*?(?:had|has|diagnosed with|history of)\s+([a-zA-Z\s]+?)(?:[.;,]|$)",
            text,
            re.IGNORECASE,
        ))
        for m in fam_matches:
            member = m.group(1).capitalize()
            condition_str = m.group(2).strip()
            span = m.group(0)
            
            # Ground check: span must exist in text
            if span in text:
                facts.append(
                    CandidateFact(
                        category="family_history",
                        concept=f"Family History ({member})",
                        value=f"{member} diagnosed with {condition_str}",
                        source_evidence_id=evidence.id,
                        source_span=span,
                        polarity=FactPolarity.AFFIRMED.value,
                        certainty=FactCertainty.REPORTED.value,
                        attribution=attribution,
                        temporal_status=TemporalStatus.HISTORICAL.value,
                    )
                )

        # 2. Vitals Extraction (Blood pressure, Heart rate, SpO2, Temperature, RR)
        vital_patterns = [
            ("Blood Pressure", r"\b(?:BP|blood\s+pressure)[:\s]*(\d{2,3}/\d{2,3})\s*(mmHg)?\b", "mmHg"),
            ("Heart Rate", r"\b(?:HR|heart\s+rate|pulse)[:\s]*(\d{2,3})\s*(bpm|beats/min)?\b", "bpm"),
            ("Respiratory Rate", r"\b(?:RR|respiratory\s+rate)[:\s]*(\d{1,2})\s*(breaths/min|/min)?\b", "breaths/min"),
            ("Oxygen Saturation", r"\b(?:SpO2|oxygen\s+saturation|saturation)[:\s]*(\d{2,3})\s*(%)?\b", "%"),
            ("Body Temperature", r"\b(?:Temp|temperature)(?:\s+(?:measured|reading|triage\s+reading|is|of|level))?[:\s]*(\d{2,3}(?:\.\d)?)\s*(F|C|°F|°C)?\b", "C"),
        ]

        for vital_concept, pattern, default_unit in vital_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val = match.group(1)
                unit = match.group(2) or default_unit
                span = match.group(0)
                
                # Ground check
                if span in text:
                    facts.append(
                        CandidateFact(
                            category="vital",
                            concept=vital_concept,
                            value=f"{val} {unit}".strip(),
                            unit=unit,
                            source_evidence_id=evidence.id,
                            source_span=span,
                            polarity=FactPolarity.AFFIRMED.value,
                            certainty=FactCertainty.CONFIRMED.value if attribution != "PATIENT_REPORTED" else FactCertainty.REPORTED.value,
                            attribution="DEVICE_MEASURED" if attribution == "DEVICE_MEASURED" else attribution,
                            temporal_status=TemporalStatus.CURRENT.value,
                        )
                    )

        # 3. Lab Values Extraction
        lab_patterns = [
            ("HbA1c", r"\b(?:HbA1c|glycated\s+hemoglobin)[:\s]*(\d{1,2}(?:\.\d)?)\s*(%)?\b", "%"),
            ("Hemoglobin", r"\b(?:Hb|hemoglobin)[:\s]*(\d{1,2}(?:\.\d)?)\s*(g/dL|g/dl)?\b", "g/dL"),
            ("Platelet Count", r"\b(?:platelets|platelet\s+count)[:\s]*(\d{1,3}(?:,\d{3})*|\d+)\s*(/?mcL|/?cumm)?\b", "/mcL"),
            ("Serum Creatinine", r"\b(?:creatinine|serum\s+creatinine)[:\s]*(\d{1,2}(?:\.\d)?)\s*(mg/dL|mg/dl)?\b", "mg/dL"),
            ("Random Blood Sugar", r"\b(?:RBS|random\s+blood\s+sugar)[:\s]*(\d{2,3})\s*(mg/dL|mg/dl)?\b", "mg/dL"),
            ("Fasting Blood Sugar", r"\b(?:FBS|fasting\s+blood\s+sugar)[:\s]*(\d{2,3})\s*(mg/dL|mg/dl)?\b", "mg/dL"),
            ("Total Leukocyte Count", r"\b(?:WBC|total\s+leukocyte\s+count)[:\s]*(\d{3,5})\s*(/cumm|/?mcL)?\b", "/mcL"),
        ]

        for lab_concept, pattern, default_unit in lab_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val = match.group(1)
                unit = match.group(2) or default_unit
                span = match.group(0)
                if span in text:
                    facts.append(
                        CandidateFact(
                            category="lab_value",
                            concept=lab_concept,
                            value=f"{val} {unit}".strip(),
                            unit=unit,
                            source_evidence_id=evidence.id,
                            source_span=span,
                            polarity=FactPolarity.AFFIRMED.value,
                            certainty=FactCertainty.CONFIRMED.value,
                            attribution="DOCUMENT_EXTRACTED",
                            temporal_status=TemporalStatus.CURRENT.value,
                        )
                    )

        # 4. Symptoms Extraction
        for canonical_symptom, synonyms in self.SYMPTOMS_MAP.items():
            for syn in synonyms:
                if any(ord(c) > 127 for c in syn):
                    idx = text.lower().find(syn.lower())
                    match_span = (idx, idx + len(syn)) if idx != -1 else None
                else:
                    m = re.search(rf"\b{re.escape(syn)}\b", text, re.IGNORECASE)
                    match_span = m.span() if m else None

                if match_span:
                    span_start, span_end = match_span
                    span = text[span_start:span_end]

                    # Ground check
                    if span not in text:
                        rejected_count += 1
                        continue

                    # Check negation
                    is_negated = self._check_negation(text, span_start, span_end)
                    polarity = FactPolarity.NEGATED.value if is_negated else FactPolarity.AFFIRMED.value

                    # Check uncertainty
                    is_uncertain = self._check_uncertainty(text, span_start, span_end)
                    certainty = FactCertainty.UNCERTAIN.value if is_uncertain else FactCertainty.REPORTED.value

                    # Extract temporal cues
                    duration, onset, temporal_status = self._extract_duration(text, span_start, span_end)

                    facts.append(
                        CandidateFact(
                            category="symptom",
                            concept=canonical_symptom.title(),
                            value=span,
                            source_evidence_id=evidence.id,
                            source_span=span,
                            polarity=polarity,
                            certainty=certainty,
                            attribution=attribution,
                            temporal_status=temporal_status,
                            duration=duration,
                            onset_approximate=onset,
                        )
                    )
                    break  # One match per symptom concept in this evidence item

        # 5. Documented Conditions Extraction (Excluding family history clauses)
        for canonical_cond, synonyms in self.CONDITIONS_MAP.items():
            for syn in synonyms:
                if any(ord(c) > 127 for c in syn):
                    idx = text.lower().find(syn.lower())
                    match_span = (idx, idx + len(syn)) if idx != -1 else None
                else:
                    m = re.search(rf"\b{re.escape(syn)}\b", text, re.IGNORECASE)
                    match_span = m.span() if m else None

                if match_span:
                    span_start, span_end = match_span
                    span = text[span_start:span_end]

                    # Ensure this mention is NOT in a family history clause
                    pre_window = text[max(0, span_start - 40):span_start].lower()
                    if re.search(r"\b(father|mother|brother|sister|family)\b", pre_window):
                        continue

                    # Ground check
                    if span not in text:
                        rejected_count += 1
                        continue

                    is_negated = self._check_negation(text, span_start, span_end)
                    polarity = FactPolarity.NEGATED.value if is_negated else FactPolarity.AFFIRMED.value
                    
                    duration, onset, temporal_status = self._extract_duration(text, span_start, span_end)
                    if temporal_status == TemporalStatus.CURRENT.value and not duration:
                        temporal_status = TemporalStatus.HISTORICAL.value  # Past conditions defaults to historical

                    facts.append(
                        CandidateFact(
                            category="documented_condition",
                            concept=canonical_cond,
                            value=span,
                            source_evidence_id=evidence.id,
                            source_span=span,
                            polarity=polarity,
                            certainty=FactCertainty.CONFIRMED.value if attribution != "PATIENT_REPORTED" else FactCertainty.REPORTED.value,
                            attribution=attribution,
                            temporal_status=temporal_status,
                            duration=duration,
                            onset_approximate=onset,
                        )
                    )
                    break

        # 6. Medications Extraction
        for canonical_med, synonyms in self.MEDICATIONS_MAP.items():
            for syn in synonyms:
                pattern = rf"\b{re.escape(syn)}(?:\s+\d+(?:mg|mcg))?\b"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    span = match.group(0)
                    if span in text:
                        facts.append(
                            CandidateFact(
                                category="medication",
                                concept=canonical_med,
                                value=span,
                                source_evidence_id=evidence.id,
                                source_span=span,
                                polarity=FactPolarity.AFFIRMED.value,
                                certainty=FactCertainty.REPORTED.value,
                                attribution=attribution,
                                temporal_status=TemporalStatus.CURRENT.value,
                            )
                        )
                    break

        # 7. Allergies Extraction
        for canonical_allergy, synonyms in self.ALLERGIES_MAP.items():
            for syn in synonyms:
                pattern = rf"\b{re.escape(syn)}\b"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    span = match.group(0)
                    if span in text:
                        facts.append(
                            CandidateFact(
                                category="allergy",
                                concept=canonical_allergy,
                                value=span,
                                source_evidence_id=evidence.id,
                                source_span=span,
                                polarity=FactPolarity.AFFIRMED.value,
                                certainty=FactCertainty.CONFIRMED.value,
                                attribution=attribution,
                                temporal_status=TemporalStatus.HISTORICAL.value,
                            )
                        )
                    break

        return facts, rejected_count
