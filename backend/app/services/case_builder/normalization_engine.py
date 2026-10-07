"""Clinical concept and unit normalization engine for Clinova AI."""

import re
from typing import List, Optional
from app.services.case_builder.extraction_engine import CandidateFact


class ClinicalNormalizationEngine:
    """Normalizes clinical concepts, units, and values into standard clinical representations."""

    CONCEPT_SYNONYM_DICTIONARY = {
        # Symptoms
        "fever": "Pyrexia",
        "pyrexia": "Pyrexia",
        "high temperature": "Pyrexia",
        "shortness of breath": "Dyspnea",
        "dyspnea": "Dyspnea",
        "breathlessness": "Dyspnea",
        "difficulty breathing": "Dyspnea",
        "sob": "Dyspnea",
        "chest pain": "Chest Pain",
        "angina": "Chest Pain",
        "substernal pain": "Chest Pain",
        "headache": "Headache",
        "cephalalgia": "Headache",
        "cough": "Cough",
        "fatigue": "Generalized Weakness",
        "generalized weakness": "Generalized Weakness",
        "body ache": "Generalized Weakness",
        "diaphoresis": "Diaphoresis",
        "sweating": "Diaphoresis",
        "profuse sweating": "Diaphoresis",
        "nausea": "Nausea",
        "vomiting": "Vomiting",
        "dizziness": "Dizziness",
        "giddiness": "Dizziness",
        "palpitations": "Palpitations",
        "abdominal pain": "Abdominal Pain",

        # Conditions
        "hypertension": "Essential Hypertension",
        "high blood pressure": "Essential Hypertension",
        "high bp": "Essential Hypertension",
        "htn": "Essential Hypertension",
        "diabetes": "Type 2 Diabetes Mellitus",
        "type 2 diabetes": "Type 2 Diabetes Mellitus",
        "t2dm": "Type 2 Diabetes Mellitus",
        "sugar disease": "Type 2 Diabetes Mellitus",
        "madhumeha": "Type 2 Diabetes Mellitus",
        "asthma": "Bronchial Asthma",
        "bronchial asthma": "Bronchial Asthma",
        "cad": "Coronary Artery Disease",
        "coronary artery disease": "Coronary Artery Disease",
        "ckd": "Chronic Kidney Disease",
        "chronic kidney disease": "Chronic Kidney Disease",
        "hyperlipidemia": "Hyperlipidemia",
        "high cholesterol": "Hyperlipidemia",
    }

    def __init__(self):
        pass

    def normalize_fact(self, fact: CandidateFact) -> CandidateFact:
        """Normalizes concept name, value, and units for a candidate fact."""
        # 1. Normalize concept name
        clean_concept = fact.concept.lower().strip()
        if clean_concept in self.CONCEPT_SYNONYM_DICTIONARY:
            fact.concept = self.CONCEPT_SYNONYM_DICTIONARY[clean_concept]

        # 2. Category-specific normalization
        if fact.category == "vital":
            self._normalize_vital(fact)
        elif fact.category == "lab_value":
            self._normalize_lab(fact)
        elif fact.category == "symptom":
            self._normalize_symptom(fact)
        elif fact.category == "medication":
            self._normalize_medication(fact)
        elif fact.category == "documented_condition":
            if not fact.normalized_value:
                fact.normalized_value = fact.concept

        return fact

    def _normalize_vital(self, fact: CandidateFact):
        val = fact.value.strip()

        if fact.concept == "Blood Pressure":
            m = re.search(r"(\d{2,3}/\d{2,3})", val)
            if m:
                fact.normalized_value = f"{m.group(1)} mmHg"
                fact.unit = "mmHg"
        elif fact.concept == "Heart Rate":
            m = re.search(r"(\d{2,3})", val)
            if m:
                fact.normalized_value = f"{m.group(1)} bpm"
                fact.unit = "bpm"
        elif fact.concept == "Respiratory Rate":
            m = re.search(r"(\d{1,2})", val)
            if m:
                fact.normalized_value = f"{m.group(1)} breaths/min"
                fact.unit = "breaths/min"
        elif fact.concept == "Oxygen Saturation":
            m = re.search(r"(\d{2,3})", val)
            if m:
                fact.normalized_value = f"{m.group(1)}%"
                fact.unit = "%"
        elif fact.concept == "Body Temperature":
            m = re.search(r"(\d{2,3}(?:\.\d)?)", val)
            if m:
                temp_val = float(m.group(1))
                if temp_val > 50:  # Fahrenheit
                    celsius = round((temp_val - 32) * 5.0 / 9.0, 1)
                    fact.normalized_value = f"{temp_val}°F ({celsius}°C)"
                    fact.unit = "°F"
                else:  # Celsius
                    fahr = round((temp_val * 9.0 / 5.0) + 32, 1)
                    fact.normalized_value = f"{temp_val}°C ({fahr}°F)"
                    fact.unit = "°C"

    def _normalize_lab(self, fact: CandidateFact):
        val = fact.value.strip()
        m = re.search(r"(\d+(?:\.\d+)?)", val)
        if m:
            num = m.group(1)
            unit = fact.unit or ""
            fact.normalized_value = f"{num} {unit}".strip()

    def _normalize_symptom(self, fact: CandidateFact):
        parts = [fact.concept]
        if fact.duration:
            parts.append(f"duration: {fact.duration}")
        if fact.onset_approximate:
            parts.append(f"onset: {fact.onset_approximate}")
        fact.normalized_value = ", ".join(parts)

    def _normalize_medication(self, fact: CandidateFact):
        fact.normalized_value = fact.value.strip().title()

    def normalize_all(self, facts: List[CandidateFact]) -> List[CandidateFact]:
        return [self.normalize_fact(f) for f in facts]
