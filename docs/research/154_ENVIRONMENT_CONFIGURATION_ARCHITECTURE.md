# CLINOVA AI — Environment Configuration & Deployment Profiles Architecture

> **Document ID:** `RES-154`  
> **Status:** READY FOR HUMAN REVIEW  
> **Phase:** Phase 8 — Technical Architecture & System Design  
> **Version:** 8.0.0  
> **Date:** October 2026  
> **Authors:** Systems Architecture, Clinical Operations & Configuration Management Group  

---

## 1. The Core Architectural Law: One Codebase, Configured Environments

A catastrophic failure pattern in healthcare software is maintaining separate source code repositories or git branches for different clinical facilities (e.g., a "Hospital version," a "Clinic version," and a "Camp version"). Branch bifurcation creates maintenance debt, untested code divergences, and security vulnerabilities.

**The Golden Law of CLINOVA AI:**
$$\mathbf{ONE\ CODEBASE} \quad \times \quad \mathbf{IMMUTABLE\ CONFIGURATION\ PROFILES}$$

A single unified codebase runs across all six operational healthcare environments. Every difference in facility capability, triage workflow, staff role hierarchy, and queue routing is driven entirely by **strongly typed environment configuration profiles**.

---

## 2. The Six Approved Operational Environment Profiles

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SIX OPERATIONAL ENVIRONMENT PROFILES                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. `ENV_GOV_HOSPITAL`     ──► Government District / Sub-Divisional Hospital│
│  2. `ENV_PHC`              ──► Rural Primary Health Centre / Health Post    │
│  3. `ENV_PUBLIC_CAMP`      ──► Outreach Health Camp / Disaster Relief Site  │
│  4. `ENV_COMPANY_CLINIC`   ──► Corporate Office Occupational Health Centre  │
│  5. `ENV_INDUSTRIAL_HEALTH`──► High-Hazard Factory / Mining Health Unit     │
│  6. `ENV_CAMPUS_HEALTH`    ──► University Student / Residential Clinic      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Environment Profile Configuration Schema

Environment profiles are defined as Pydantic models validated during backend server startup:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class EnvironmentProfile(BaseModel):
    environment_id: str = Field(..., description="Canonical environment token")
    display_name: str = Field(..., description="Human-readable facility type name")
    default_facility_tier: str = Field(..., description="IPHS facility tier classification")
    
    # Workflow Feature Flags
    enable_emergency_casualty_code: bool = True
    enable_multilingual_voice_intake: bool = True
    enable_offline_autonomous_mode: bool = False
    enable_specialist_routing: bool = False
    enable_occupational_hazard_screening: bool = False
    enable_industrial_toxin_panel: bool = False
    enable_student_id_lookup: bool = False
    
    # Queue Configuration
    max_queue_depth_alert: int = Field(50, description="ED queue congestion threshold")
    default_wait_time_alpha: float = Field(5.0, description="Queue wait-time acceleration factor")
    
    # Verification & Approval Rules
    require_dual_review_for_thrombolysis: bool = True
    allow_rural_single_doctor_override: bool = False
    
    # Hardware & Network Defaults
    media_storage_backend: str = Field("LOCAL_FS", description="LOCAL_FS or SUPABASE_STORAGE")
    sync_replication_mode: str = Field("BIDIRECTIONAL", description="OFFLINE_ONLY, BIDIRECTIONAL, or CLOUD_NATIVE")
```

---

## 4. Environment-Specific Profile Matrix

| Profile Feature | `ENV_GOV_HOSPITAL` | `ENV_PHC` | `ENV_PUBLIC_CAMP` | `ENV_COMPANY_CLINIC` | `ENV_INDUSTRIAL_HEALTH` | `ENV_CAMPUS_HEALTH` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Facility Tier** | `LEVEL_4_DH` | `LEVEL_1_PHC` | `TEMPORARY_CAMP` | `OCCUPATIONAL_L1` | `OCCUPATIONAL_L2` | `CAMPUS_CLINIC` |
| **Storage Mode** | On-Premise / Hybrid | Local Mini-PC FS | Local Mini-PC FS | Cloud / Hybrid | On-Premise LAN | Cloud / On-Premise |
| **Sync Mode** | `BIDIRECTIONAL` | `BIDIRECTIONAL` | `OFFLINE_ONLY` | `CLOUD_NATIVE` | `BIDIRECTIONAL` | `CLOUD_NATIVE` |
| **Offline Autonomous** | Optional Fallback | **Mandatory** | **Mandatory** | No | Optional Fallback | No |
| **Specialist Routing** | **Yes** (Cardio, Ortho) | No (Referral only) | No | No | No (Industrial MO) | No |
| **Hazard Screening** | No | No | No | Ergonomics | **Yes** (Silica, Gas) | No |
| **Single-MD Override**| Blocked (Full staff)| **Enabled** (Night) | **Enabled** (Camp MO) | Blocked | Blocked | Blocked |
| **Queue Depth Cap** | 150 patients | 40 patients | 200 patients | 20 patients | 30 patients | 40 patients |

---

## 5. Deployment Injection & Session Immutability Invariant

1. **Boot-Time Injection:** The active environment profile is injected via the system environment variable `CLINOVA_ENVIRONMENT` (e.g. `CLINOVA_ENVIRONMENT=ENV_PHC`) during container startup or process launch.
2. **Configuration Freezing:** Upon startup, the settings are parsed into an immutable singleton `app.core.config.settings`.
3. **Session Immutability Invariant:**
   $$\mathbf{Inv\ ENV\text{-}1}: \quad \forall \text{ active session } s, \quad s.\text{environment} = \text{DeploymentEnvironment} = \text{Constant}$$
   Under no circumstances can an end-user, nurse, or doctor alter the active environment configuration profile during an active clinical session. Switching an environment profile requires an administrative server restart with configuration change logging.
