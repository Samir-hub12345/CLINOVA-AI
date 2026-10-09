# CLINOVA AI — Multilingual Vernacular Architecture & Colloquial Preservation

> **Document ID:** `RES-209`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Linguistics, Vernacular Informatics & NLP Systems Group  

---

## 1. Linguistic Landscape in Target Deployment Regions

In rural and peri-urban Odisha and Northern India, patient symptom descriptions span multiple linguistic registers:
1. **Odia (Pure Vernacular):** e.g., *"ମୋ ଛାତି ରେ ଗପ ଗପ ଲାଗୁଛି ଆଉ ଝାଳ ବୋହୁଛି"* (*chhati re gapa gapa laguchi aau jhala bohuchi*).
2. **Hindi (Pure Vernacular):** e.g., *"सीने में बहुत जलन और घबराहट हो रही है"* (*seene mein bahut jalan aur ghabrahat ho rahi hai*).
3. **Mixed Code-Switching (Odia-English / Hinglish):** e.g., *"Morning ru chest pain start hela, sweating bi achhi"* or *"Khaane ke baad vomiting sensation aa rahi hai"*.
4. **Colloquial Metaphors:** Cultural idioms expressing somatic distress (e.g. Odia *"chhati re gapa gapa"* indicating suffocating retrosternal constriction; Hindi *"kaleja kaanpna"* denoting severe palpitations).

---

## 2. The Original Text Preservation Law

$$\mathbf{TRANSLATION\ MUST\ NEVER\ DESTROY\ THE\ ORIGINAL\ PATIENT\ STATEMENT}$$

A clinical translation that converts *"chhati re gapa gapa laguchi"* solely into *"Chest discomfort"* irreversibly destroys critical clinical nuance (the suffocating, heavy constriction characteristic of acute coronary ischemia).

**The Golden Linguistic Invariant:**
Every vernacular transformation MUST preserve the **original patient statement verbatim**, side-by-side with the translated clinical concept, and extract regional colloquial terms into an explicit preservation dictionary.

---

## 3. The Canonical Multilingual Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTILINGUAL PROCESSING PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ RAW PATIENT SPEECH / NARRATIVE ]                                         │
│  "chhati re gapa gapa laguchi aau bapa nku bi heart attack thila"          │
│          │                                                                  │
│          ▼                                                                  │
│  [ 1. SOURCE PRESERVATION & LANGUAGE IDENTIFICATION ]                       │
│  • Original text stored immutably in source_text                            │
│  • Detected language tagged: 'od' (Odia) / 'hi' (Hindi) / 'mixed'           │
│          │                                                                  │
│          ▼                                                                  │
│  [ 2. COLLOQUIAL IDIOM ISOLATION ]                                          │
│  • Identifies regional somatic idiom: "gapa gapa"                           │
│  • Maps literal translation: "suffocating, heavy constriction"              │
│          │                                                                  │
│          ▼                                                                  │
│  [ 3. CLINICAL CONCEPT NORMALIZATION ]                                      │
│  • Maps concept to SNOMED-CT: "Chest tightness (finding)" [29857009]        │
│          │                                                                  │
│          ▼                                                                  │
│  [ 4. STRUCTURED TRANSLATION PAYLOAD ]                                      │
│  • Emits TranslationResult with original text, translation, & idiom dict    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Translation Result Schema Representation

```json
{
  "source_text": "chhati re gapa gapa laguchi aau bapa nku bi heart attack thila",
  "source_language": "od",
  "target_language": "en",
  "translated_text": "Patient describes severe chest heaviness/tightness and notes father had a heart attack.",
  "preserved_colloquialisms": {
    "gapa gapa": "colloquial Odia idiom denoting suffocating, heavy retrosternal constriction",
    "bapa nku bi": "father also had"
  }
}
```

This ensures that attending physicians who speak the local dialect can always cross-reference the original vernacular phrase directly on their workbench.
