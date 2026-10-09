# CLINOVA AI — Network Ingress, CORS & Transport Layer Security Specification

> **Document ID:** `RES-179`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 9 — Environment, Secrets & Configuration Foundation  
> **Version:** 9.0.0  
> **Date:** October 2026  
> **Authors:** Network Security, Infrastructure Engineering & Web Safety Group  

---

## 1. Network Boundary Overview & Zero-Trust Ingress

Medical information systems are prime targets for cross-origin attacks, session hijacking, and network eavesdropping. In a hospital or rural clinic setting, clinicians frequently connect personal devices or access external websites while authenticated to internal medical software.

CLINOVA AI enforces strict **Per-Environment Origin Whitelisting** and **Mandatory Transport Layer Security (TLS)**.

---

## 2. Inviolable Rule: Prohibition of CORS Wildcards (`*`)

**The CORS Security Law:**
$$\mathbf{Authenticated\ Production\ CORS} \cap \{ \text{"*"} \} = \emptyset$$

Under no circumstances may `allow_origins=["*"]` be configured in any production, edge, or cloud preview deployment.

### Why Wildcards Are Catastrophic in Clinical Workstations:
1. **Cross-Origin Credential Theft:** If a doctor opens an untrusted web page in a background browser tab while logged into CLINOVA AI, a malicious script on that page could execute authenticated AJAX requests to `http://192.168.1.10:8000/api/v1/cases` and extract confidential patient medical records if CORS is un-restricted.
2. **Session Hijacking:** Wildcard origins prevent browsers from safely isolating session cookies and authorization headers.

---

## 3. Environment-Specific CORS Matrix

| Environment (`APP_ENV`) | Allowed Origins (`CORS_ORIGINS`) | TLS / HTTPS Requirement | Local LAN / Host Behavior |
| :--- | :--- | :--- | :--- |
| **`DEV`** | `["http://localhost:3000", "http://127.0.0.1:3000"]` | HTTP Permitted (Localhost) | Loopback only (`127.0.0.1`) |
| **`LOCAL_DEMO`** | `["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.1.*"]` | HTTP Permitted | Localhost + optional private Wi-Fi hotspot subnet |
| **`PHC_EDGE`** | `["http://192.168.1.*", "https://192.168.1.*"]` | Recommended Self-Signed TLS; HTTP allowed on isolated LAN | Restricted strictly to the local clinic router subnet (`192.168.1.0/24`) |
| **`DISTRICT_HOSPITAL`** | Explicit hospital FQDNs: `["https://clinova.hospital.internal", "https://triage.hospital.internal"]` | **MANDATORY HTTPS (TLS 1.3)** | Enterprise hospital intranet; public Internet ingress blocked |
| **`CLOUD_PREVIEW`** | Specific cloud domain: `["https://preview.clinova.health"]` | **MANDATORY HTTPS (TLS 1.3)** | Global CDN ingress; HSTS preloaded |
| **`TEST`** | `["http://127.0.0.1:3333"]` | HTTP Permitted | Isolated local test harness port |

---

## 4. CORS Implementation & Startup Validation in FastAPI

The backend configuration parser strictly validates `CORS_ORIGINS` during application startup:

```python
# CORS Configuration Parser & Security Guardrail
@field_validator("CORS_ORIGINS", mode="after")
@classmethod
def validate_cors_safety(cls, v: list[str], info: ValidationInfo) -> list[str]:
    app_env = info.data.get("APP_ENV", AppEnv.DEV)
    
    # Check 1: Wildcard check in production/preview
    if app_env in [AppEnv.DISTRICT_HOSPITAL, AppEnv.CLOUD_PREVIEW, AppEnv.PHC_EDGE]:
        if "*" in v or any(origin.strip() == "*" for origin in v):
            raise ValueError(
                f"FATAL SECURITY VIOLATION: Wildcard CORS ('*') is strictly prohibited in {app_env}!"
            )
            
    # Check 2: HTTP check in cloud preview
    if app_env == AppEnv.CLOUD_PREVIEW:
        for origin in v:
            if origin.startswith("http://"):
                raise ValueError(
                    f"FATAL SECURITY VIOLATION: Plain HTTP origin '{origin}' is forbidden in cloud_preview!"
                )
                
    return v
```

---

## 5. Transport Layer Security (TLS) Standards

1. **Cloud & District Hospital:**
   - Enforce TLS 1.3 with forward secrecy ciphers (`TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`).
   - Strict HTTP Strict Transport Security (HSTS) with `max-age=31536000; includeSubDomains`.
2. **Rural PHC Edge LAN:**
   - Isolated physical Wi-Fi routers with WPA3/WPA2-Enterprise encryption.
   - Frontline tablets connect to the Local Clinic Server via private mDNS or static IP (`https://192.168.1.10:8000`), using pre-installed district root certificates.
