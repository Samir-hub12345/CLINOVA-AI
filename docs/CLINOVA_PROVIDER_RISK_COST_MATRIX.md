# CLINOVA AI — Provider Risk & Cost Matrix
**Phase 0 Architecture Discovery**  
**Repository Commit:** `238f1eb917829642ca7525735d25f5882206247e` | **Branch:** `master`  
**Operating Rules:** 4, 8, 13 (API Approval Gate, Provider Policy Audit & Research Requirement)

---

## 1. Provider Profile: Google Gemini API

- **Provider:** Google LLC / Google Cloud Platform
- **Service Name:** Google Gemini API (via `google-genai` Python SDK)
- **Evaluated Model:** `gemini-2.5-flash`
- **Release Date:** June 17, 2025
- **Official Status:** Generally Available (GA)
- **Target Context Window:** 1,048,576 input tokens / 65,536 output tokens

---

## 2. Official Pricing Structure (Grounded in Official Docs)

Google Gemini enforces pricing based on input/output tokens, modality, and consumption model:

### Standard Inference (Per 1 Million Tokens in USD)

| Tier | Input (Text / Image / Video) | Input (Audio Waveform) | Output (Text + Thinking Tokens) | Context Caching | Grounding (Search / Maps) | Data Used for Google Training? |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Free Tier** | **$0.00** | **$0.00** | **$0.00** | Not Available | Free up to 500 RPD | **YES (Google product improvement)** |
| **Paid Tier** | **$0.30** | **$1.00** | **$2.50** | $0.03/1M in + $1/1M/hr | 1,500 RPD free, then $35/1k | **NO (Strict customer privacy)** |

### Batch & Flex Inference (50% Cost Reduction for Async Workloads)

| Inference Mode | Input (Text / Image) | Input (Audio) | Output (Text) | Availability |
|:---|:---:|:---:|:---:|:---:|
| **Batch API** | $0.15 / 1M | $0.50 / 1M | $1.25 / 1M | Paid Tier Only |
| **Flex Inference** | $0.15 / 1M | $0.50 / 1M | $1.25 / 1M | Paid Tier Only |
| **Priority Inference** | $0.54 / 1M | $1.80 / 1M | $4.50 / 1M | Paid Tier Only |

---

## 3. Rate Limits & Quotas

Gemini API quotas are enforced per project and evaluated across RPM, TPM, and RPD:

| Metric | Free Tier Default | Paid Tier 1 ($250 cap) | Paid Tier 2 ($2,000 cap) | Paid Tier 3 ($20k+ cap) |
|:---|:---:|:---:|:---:|:---:|
| **Requests Per Minute (RPM)** | 15 RPM | 1,000 RPM | 2,000 RPM | 4,000+ RPM |
| **Tokens Per Minute (TPM)** | 1,000,000 TPM | 4,000,000 TPM | 8,000,000 TPM | 16,000,000+ TPM |
| **Requests Per Day (RPD)** | 1,500 RPD | Unlimited (spend-capped) | Unlimited | Unlimited |
| **Spend Limit (Rolling 10-Min)** | N/A (Free) | **$10 per 10 mins** | **$50 per 10 mins** | **$200 per 10 mins** |

*Note: If an application exceeds $10 in rolling 10-minute spend on Tier 1, API returns `429 RESOURCE_EXHAUSTED`.*

---

## 4. Projected Operating Cost Modeling

Assumptions based on Clinova production telemetry:
- **Triage Request:** ~600 input tokens + ~400 output tokens = 1,000 tokens total.
- **SOAP Note Draft:** ~1,200 input tokens + ~600 output tokens = 1,800 tokens total.
- **Speech Audio Clip (30 sec):** ~8,000 audio tokens input + ~50 text tokens output.

### Scenario A: Rural Primary Health Centre (PHC) — 200 Patients / Day
- 200 Triage Requests: 120k in, 80k out = $0.036 + $0.20 = **$0.24**
- 100 SOAP Notes: 120k in, 60k out = $0.036 + $0.15 = **$0.19**
- 50 Audio Transcriptions: 400k audio in, 2.5k out = $0.40 + $0.01 = **$0.41**
- **Daily Operating Cost:** **$0.84 / day** (~$25.20 / month)

### Scenario B: District Hospital Outpatient Department (OPD) — 1,500 Patients / Day
- 1,500 Triage Requests: 900k in, 600k out = $0.27 + $1.50 = **$1.77**
- 800 SOAP Notes: 960k in, 480k out = $0.29 + $1.20 = **$1.49**
- 300 Audio Transcriptions: 2.4M audio in, 15k out = $2.40 + $0.04 = **$2.44**
- **Daily Operating Cost:** **$5.70 / day** (~$171.00 / month)

### Scenario C: Regional Public Health Network — 10,000 Patients / Day
- 10,000 Triage Requests: 6M in, 4M out = $1.80 + $10.00 = **$11.80**
- 6,000 SOAP Notes: 7.2M in, 3.6M out = $2.16 + $9.00 = **$11.16**
- 2,000 Audio Transcriptions: 16M audio in, 100k out = $16.00 + $0.25 = **$16.25**
- **Daily Operating Cost:** **$39.21 / day** (~$1,176.30 / month)
- **Annual Cloud Cost:** **~$14,311.65 / year**

*Comparison:* A single local inference server equipped with an NVIDIA RTX 4090 (24GB VRAM) costs ~$2,200 (one-time capex) and can serve ~10,000 local SLM inferences/day at near-zero recurring token cost.

---

## 5. Risk Assessment Matrix

| Risk Domain | Risk Factor | Current Vulnerability in Codebase | Severity | Mitigation / Recommended Solution |
|:---|:---|:---|:---:|:---|
| **Privacy & Legal** | **Free Tier Data Training** | If an operator uses a standard free AI Studio key, Google's terms explicitly state inputs are **used to train and improve Google products**. | **CRITICAL** | Never use Free Tier keys for patient data. Migrate to local SLM or enforce paid zero-retention enterprise tier. |
| **Privacy & Legal** | **Direct PII Transmission** | `gemini_service.py:120` sends raw un-anonymized `patient_name` to Google in SOAP synthesis requests. | **CRITICAL** | Replace cloud SOAP generation with Clinova local structured clinical note generator or sanitize inputs. |
| **Privacy & Legal** | **Biometric Audio Leak** | `speech_service.py` sends raw patient voice audio bytes directly to external Google cloud endpoints. | **HIGH** | Replace cloud audio ingestion with on-premise AI4Bharat IndicWhisper or Faster-Whisper. |
| **Security** | **API Key Management** | Keys stored in local `.env`. If misconfigured or committed to Git, cloud spend could be hijacked. | **MEDIUM** | Verified: `.env` is gitignored and not in history. Enforce strict server-side secrets loading via environment variables. |
| **Reliability** | **Cloud Outages & Air-Gap Failure** | Rural clinics frequently suffer internet loss; external API calls fail or timeout. | **HIGH** | Maintain and strengthen Clinova's 100% offline deterministic fallback heuristics. |
| **Reliability** | **Runtime Code Bug** | `gemini_service.py:456` references missing `settings.GEMINI_MODEL`, causing voice chat to crash at runtime. | **HIGH** | Fix settings model configuration or remove external voice chat call in favor of local turn-taking. |
| **Vendor Lock-in** | **Proprietary API Dependency** | Code is tied to Google's proprietary SDK syntax (`google.genai.Client`). | **MEDIUM** | Encapsulate all inference behind an abstract Clinova model provider interface (`O1` layer). |
