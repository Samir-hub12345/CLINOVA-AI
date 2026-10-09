# CLINOVA AI — Configuration Threat Model & STRIDE Security Analysis

> **Document ID:** `RES-185`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Application Security, Penetration Testing & Threat Modeling Group  

---

## 1. Threat Modeling Scope & Methodology

Configuration vulnerabilities represent the single largest vector of healthcare data breaches and system outages globally. In distributed clinical systems combining rural edge nodes with cloud hubs, configuration mistakes can compromise patient confidentiality, corrupt triage rankings, or expose database administrative privileges.

This analysis evaluates thirteen configuration failure vectors using the **STRIDE methodology** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).

---

## 2. Exhaustive STRIDE Threat Analysis Matrix

| Threat Vector | STRIDE Category | Attack Scenario | Clinical & Technical Impact | Architectural Mitigation | Verification Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Service-Role Key Leaked to Frontend** | Elevation of Privilege | Developer puts `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY` in frontend `.env`. | Attacker inspects JS bundle and extracts admin token, bypassing all Row Level Security. | Next.js AST linter blocks build; Zod schema rejects key; CI regex check. | Automated bundle scan fails build if key found. |
| **2. `.env` Committed to Git** | Information Disclosure | Engineer commits production credentials in git repo. | Public or compromised repository exposes live database passwords. | `.gitignore` covers `.env*` except `.env.example`; pre-commit git-secrets hook. | CI secret-scanner (`trufflehog`) runs on PRs. |
| **3. Production URL Used Locally** | Tampering / Info Leak | Developer configures local laptop to point to live hospital PostgreSQL. | Developer tests corrupt real patient episodes or leak real PHI. | Pre-flight URL validator rejects production domains when `APP_ENV=dev`. | Boot fails if `DATABASE_URL` contains `prod` or `.gov.in`. |
| **4. Test App Pointed to Production** | Tampering / DoS | Automated CI runner runs destructive test suite against production database. | Test drops tables or overwrites live clinical records. | Test runner requires `DATABASE_URL` to be `:memory:` or `*_test`. | Boot halts if test suite detects live database. |
| **5. Malicious Environment ID** | Elevation of Privilege | Attacker injects malformed or unapproved environment string. | System executes with unintended facility permissions. | Strict enum validation (`ClinovaFacilityProfile`) rejects unapproved tokens. | Enum validation fails fast on unknown tokens. |
| **6. CORS Wildcard (`*`) in Production** | Information Disclosure | Sysadmin sets `CORS_ORIGINS=["*"]` to resolve browser cross-domain issues. | Malicious website executes authenticated requests using victim clinician's session. | Startup validator strictly forbids `*` in `district_hospital` and `cloud_preview`. | Startup fails fast if `*` is present in production CORS. |
| **7. Debug Enabled in Production** | Information Disclosure | `DEBUG=True` left active in live hospital deployment. | Interactive stack traces reveal SQL queries, directory paths, and memory state. | Startup validator terminates process if `DEBUG=True` when `APP_ENV != dev`. | Boot fails fast if `DEBUG=True` in production. |
| **8. Synthetic Mode Disabled Accidentally** | Information Disclosure | Evaluator disables synthetic data on uncertified cloud preview instance. | Real patient data ingested without DPDP Act consent or hospital certification. | `CLINOVA_DATA_MODE=live` requires affirmative multi-key production confirmation. | Boot halts if `live` mode is enabled in cloud preview. |
| **9. Public Storage Bucket Misconfigured** | Information Disclosure | Cloud storage bucket created with public read access enabled. | Sensitive patient prescription photos accessible via public web search. | Bucket marked private; media served strictly via signed 15-minute URLs. | Automated Terraform / CLI check verifies private bucket. |
| **10. Default Password Retained** | Spoofing / Elevation | Default development database password used in live hospital server. | Attacker connects to PostgreSQL port using well-known credentials. | Startup validator checks entropy of `SECRET_KEY` and rejects default strings. | Boot fails if secret matches known dev default. |
| **11. Secrets Logged to Files/Console** | Information Disclosure | Exception logger dumps full environment settings dictionary to stdout. | Credentials written to unencrypted log files or central monitoring. | Pydantic `SecretStr` masks all credentials (`**********`); log filter masks tokens. | Unit test asserts `str(settings)` exposes no secrets. |
| **12. Secrets Included in Error Responses** | Information Disclosure | Uncaught exception handler returns database connection string in HTTP 500. | Client receives internal database password in JSON response. | Global FastAPI exception handler strips internal details in non-dev modes. | Exception test asserts response contains only opaque UUID. |
| **13. Stale Credentials on Edge Node** | Elevation of Privilege | Decommissioned staff member's token remains valid on disconnected edge server. | Unauthorized actor logs into rural clinic during network blackout. | Node enforces local password rotation manifests and short-lived JWTs. | Local token validity ceiling capped at 8 hours. |

---

## 3. Defense-in-Depth Implementation Guidelines

1. **Static AST Analysis:** Automated build pipelines parse all frontend source code and reject any occurrence of private key identifiers.
2. **Runtime Memory Masking:** All cryptographic credentials utilize Pydantic's `SecretStr` type, ensuring that printing or serializing the settings model produces `SecretStr('**********')`.
3. **Fail-Closed Configuration Guards:** In any scenario where a security setting cannot be definitively verified, the system defaults to the most secure, air-gapped, and restricted posture.
