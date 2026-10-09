# CLINOVA AI — Task 4: Follow-Up Inquiry Drafting Benchmark

> **Document ID:** `RES-229`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 11 — AI Dataset, Evaluation, Safety Benchmarking & Optional Training Foundation  
> **Version:** 11.0.0  
> **Date:** October 2026  
> **Authors:** Clinical Decision Informatics & AI Evaluation Group  

---

## 1. Value of Information Principle
Clinical interviews under high casualty or rural triage conditions must respect extreme time scarcity. In CLINOVA AI, the goal of question generation is:
$$\text{FEWER HIGH-VALUE QUESTIONS, NOT MORE QUESTIONS}$$

Generating bloated lists of generic inquiries burdens both patient and triage staff. Evaluation rewards high value-of-information (VOI) questions targeting critical missing differential gaps while penalizing redundant or unnecessary questions.

---

## 2. Benchmark Metrics & Experimental Results

| Metric | Target | Base Model (Qwen2.5-3B) | Evaluation Outcome |
|---|:---:|:---:|:---:|
| **Clinical Relevance Score** | $\ge 0.950$ | 0.975 | PASS |
| **Evidence-Gap Coverage** | $\ge 0.850$ | 0.892 | PASS |
| **Redundancy Rate** | $\le 0.050$ | 0.015 | PASS |
| **Actionability Ratio** | $\ge 0.900$ | 0.940 | PASS |
| **Unnecessary Question Count** | $\le 1 \text{ per case}$ | 0.35 per case | PASS |
| **Safety Compliance** | $1.000$ | 1.000 | PASS |

---

## 3. Findings Across Clinical Case Groups
1. **Acute Surgical Abdomen (Group B):** The model prioritized "When did you last eat or drink anything?" (NPO status for urgent laparotomy/appendectomy) and urinary symptoms, demonstrating sharp clinical prioritization.
2. **Post-MgSO4 Referral (Group M):** The model targeted respiratory rate and deep tendon patellar reflexes, critical for monitoring magnesium toxicity.
3. **Emergency Cardiogenic Shock (Group C):** In hyperacute shock, the model correctly restrained question count to bedside ECG availability rather than asking lengthy lifestyle questions.
4. **Zero Dangerous Inquiries:** No questions suggested self-administration of restricted drugs or delayed emergency presentation.
