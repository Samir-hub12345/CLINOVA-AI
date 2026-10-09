# CLINOVA AI — Local-First Privacy & Zero-Egress AI Architecture

> **Document ID:** `RES-210`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 10 — Local AI Runtime Foundation & Safe Inference Architecture  
> **Version:** 10.0.0  
> **Date:** October 2026  
> **Authors:** Information Security, Data Privacy & Regulatory Compliance Group  

---

## 1. Statutory Compliance: The DPDP Act 2023 Mandate

Under Sections 4, 6, and 8 of the **Digital Personal Data Protection (DPDP) Act, 2023**, healthcare data fiduciaries must implement robust technical safeguards preventing unauthorized processing and cross-border transfer of sensitive personal data.

Transmitting raw clinical transcripts, audio recordings, or patient vitals to commercial foreign cloud APIs (e.g., OpenAI, Google Cloud US endpoints) without explicit multi-party consent and cross-border data transfer agreements violates Indian statutory frameworks.

---

## 2. Zero-Egress Network Perimeter

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ZERO-EGRESS AI NETWORK BOUNDARY                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ ON-PREMISE LOCAL CLINIC NETWORK ]                                        │
│                                                                             │
│  ┌───────────────────────┐             HTTP Loopback (127.0.0.1)            │
│  │ FASTAPI BACKEND       │ ──────────────────────────────────────────────┐  │
│  │ (Domain Core)         │                                               │  │
│  └───────────────────────┘                                               │  │
│              ▲                                                           ▼  │
│              │                                              ┌────────────┴┐ │
│  Local Wi-Fi │ (LAN Only)                                   │ OLLAMA /    │ │
│  WPA3 / TLS  │                                              │ LLAMA.CPP   │ │
│              ▼                                              │ (Local CPU) │ │
│  ┌───────────────────────┐                                  └─────────────┘ │
│  │ FRONTLINE TABLETS     │                                                  │
│  │ (Nurse / Doctor UI)   │                                                  │
│  └───────────────────────┘                                                  │
│                                                                             │
│  ═════════════════════════════════════════════════════════════════════════  │
│  FIREWALL BOUNDARY: BLOCK ALL OUTBOUND WAN ACCESS TO EXTERNAL AI SERVICES   │
│  🚫 No OpenAI (api.openai.com)                                              │
│  🚫 No Google Gemini (generativelanguage.googleapis.com)                    │
│  🚫 No Anthropic (api.anthropic.com)                                        │
│  ═════════════════════════════════════════════════════════════════════════  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Privacy Boundary Enforcement across Data Lifecycle

| Lifecycle Stage | Architectural Privacy Rule | Enforcement Mechanism |
|:---|:---|:---|
| **Inference Transport** | Restricted to localhost socket `127.0.0.1`. | Backend firewall rejects non-loopback connections. |
| **Operational Logging** | Zero PHI in log streams. | Regex redactors mask names, phone numbers, Aadhaar in console logs. |
| **Inference Caching** | Cached purely in volatile RAM; keyed to hash. | Volatile dictionary cleared on restart; TTL eviction after 1 hour. |
| **Prompt Storage** | Case prompts assembled dynamically in-memory. | Raw assembled prompt text is never written to disk. |
| **Output Persistence** | Only validated structured results saved. | Stored in encrypted SQLite / PostgreSQL `ai_inferences` table. |
| **Data Purge / Deletion** | DPDP Act Right to Erasure compliance. | Soft-delete cascaded across evidence and inference records. |

---

## 4. Local Deletion & Data Minimisation Guarantees

1. **Volatile Memory Scrubbing:** Context strings passed to `invoke_raw()` exist in Python process memory only during execution and are released for garbage collection immediately upon completion.
2. **Zero Secondary Telemetry:** Local inference daemons are booted with disabled usage telemetry (`OLLAMA_NOPRUNE=1`, `OLLAMA_ORIGINS=""`).
3. **Hardware Decommissioning:** Hard drives from edge Mini-PCs undergo cryptographic erasure in compliance with NIST SP 800-88 Rev. 1 before hardware transfer.
