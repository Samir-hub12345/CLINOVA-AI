# Clinova AI — Native Windows Development & Runtime Guide

**Version:** 1.0  
**Target Environment:** Microsoft Windows 10/11 / Windows Server  
**Primary Tooling:** VS Code, PowerShell 5.1+, Node.js 20+, Python 3.12+  
**Primary Startup Command:** `.\scripts\clinova.ps1 start`  

---

## 1. Overview

Clinova AI runs natively on Microsoft Windows without requiring Docker Desktop, Linux containers, or WSL virtualization for local development.

The native stack orchestrates:
- **FastAPI Backend:** High-performance asynchronous Python runtime with SQLAlchemy 2.0 and Pydantic v2.
- **Next.js Frontend:** React 18 / Next.js 15 clinical workstation UI with Tailwind CSS and Lucide icons.
- **Database:** Native Windows PostgreSQL 16 (or zero-install async SQLite mode for instant local testing).
- **Cache & Queues:** Native Windows Redis / Memurai with automatic graceful in-memory fallback.
- **AI Engine:** Google Gemini 2.5 Flash API with deterministic clinical heuristics fallback.
- **Orchestration:** Unified PowerShell script (`scripts/clinova.ps1`) managing dependencies, processes, health checks, and logs.

---

## 2. Core Prerequisites

Before running Clinova AI, ensure the following software is installed on Windows:

| Prerequisite | Minimum Version | Recommended Installation Command |
| :--- | :--- | :--- |
| **Git** | 2.40+ | `winget install Git.Git` |
| **PowerShell** | 5.1 or 7+ | Included with Windows (or `winget install Microsoft.PowerShell`) |
| **Node.js & npm** | Node 20+ / npm 10+ | `winget install OpenJS.NodeJS` |
| **Python** | 3.12+ | `winget install Python.Python.3.12` |
| **PostgreSQL** | 16 (or SQLite fallback) | `winget install PostgreSQL.PostgreSQL.16` |
| **Redis** | Optional (Memurai) | `winget install Memurai.MemuraiDeveloper` |

To diagnose your system's prerequisites at any time:
```powershell
.\scripts\clinova.ps1 doctor
```

---

## 3. Quick Start Workflow

### First-Time Setup
Run the automated setup to create the Python virtual environment, install requirements, set up npm packages, and generate `.env`:
```powershell
.\scripts\clinova.ps1 setup
```

### Daily Startup (One Command)
Start the entire Clinova AI stack:
```powershell
.\scripts\clinova.ps1 start
```

To start the stack and automatically open the application in your default browser:
```powershell
.\scripts\clinova.ps1 start -Open
```

### Checking Stack Status
Inspect running processes, PID tracking, ports, and responsiveness:
```powershell
.\scripts\clinova.ps1 status
```

### Deep Health Probe
Inspect live health and latency metrics across database, cache, and API:
```powershell
.\scripts\clinova.ps1 health
```

### Inspecting Logs
View runtime output from backend and frontend services:
```powershell
# Tail both backend and frontend logs
.\scripts\clinova.ps1 logs

# Tail backend only
.\scripts\clinova.ps1 logs -Service backend -Lines 60

# Live follow
.\scripts\clinova.ps1 logs -Service backend -Follow
```

### Stopping Services
Gracefully stop only Clinova-managed processes without affecting other applications:
```powershell
.\scripts\clinova.ps1 stop
```

### Restarting Services
Stop and cleanly relaunch the stack:
```powershell
.\scripts\clinova.ps1 restart
```

---

## 4. Database Setup & Modes

Clinova AI supports two native database modes:

### Mode A: Native PostgreSQL (Recommended for Development & Production Parity)
1. Install PostgreSQL 16 via Windows installer or Winget:
   ```powershell
   winget install PostgreSQL.PostgreSQL.16
   ```
2. Verify service is running:
   ```powershell
   Start-Service postgresql-x64-16
   ```
3. Set your connection string in `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/clinova
   ```
4. Clinova automatically runs additive migrations (`Base.metadata.create_all` and `upgrade_ownership`) and seeds initial clinical demo data on startup.

### Mode B: Zero-Install Local SQLite (Instant Demo Mode)
If PostgreSQL is not installed, Clinova supports an asynchronous SQLite database using `aiosqlite`:
1. In `.env`, set:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db
   ```
2. Run `.\scripts\clinova.ps1 start`. No external database service required!

---

## 5. Redis Setup & Graceful Fallback

Clinova AI uses Redis for caching, session management, and rate limiting:
- **If Redis is installed & running:** Clinova automatically connects to `redis://localhost:6379/0`.
- **If Redis is not installed:** Clinova's `app.core.redis` automatically activates a graceful local fallback. The application remains fully functional, reporting `degraded` on readiness probes without crashing or blocking development.

To install a native Windows Redis-compatible engine (Memurai):
```powershell
winget install Memurai.MemuraiDeveloper
Start-Service memurai
```

---

## 6. AI Configuration & Security

Clinova AI integrates with Google Gemini for advanced clinical reasoning, SOAP note generation, and conversational intake:

1. Configure your key in `.env` (server-side only):
   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```
2. **Security Guarantee:**
   - `GEMINI_API_KEY` is loaded exclusively by the FastAPI backend (`backend/app/core/config.py`).
   - The key is **never** exposed to the frontend or bundled into client JavaScript.
   - Diagnostic commands (`doctor`, `health`, `status`) always mask the key length and never print secret values.
   - If no API key is provided, Clinova seamlessly falls back to deterministic clinical heuristic rules.

---

## 7. Troubleshooting & Common Errors

### Error: Port 8000 or 3000 already in use
Run `.\scripts\clinova.ps1 doctor` to inspect port usage. If an unmanaged process is holding the port:
```powershell
Get-NetTCPConnection -LocalPort 8000, 3000 | Select-Object LocalAddress, LocalPort, State, OwningProcess
```
Terminate stale instances if needed:
```powershell
Stop-Process -Id <OwningProcessId> -Force
```

### Error: PowerShell Script Execution Blocked
If Windows restricts script execution for the current session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Error: PostgreSQL Connection Refused
- Ensure the Windows service is running: `Start-Service postgresql-x64-16`
- Or switch to SQLite mode in `.env`: `DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db`

---

## 8. Safe Environment Reset & Cleanup

To perform a clean reset of runtime state and logs:
```powershell
# 1. Stop active services
.\scripts\clinova.ps1 stop

# 2. Clean temporary state and logs
Remove-Item -Path ".clinova\logs\*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".clinova\pids\*" -Force -ErrorAction SilentlyContinue

# 3. Clean temporary demo database (if in SQLite mode)
Remove-Item -Path "clinova-demo.db" -Force -ErrorAction SilentlyContinue
```

To remove all installed dependencies:
```powershell
# Remove Python virtual environment
Remove-Item -Recurse -Force ".venv"

# Remove Frontend node modules
Remove-Item -Recurse -Force "frontend\node_modules"
```
Then re-run `.\scripts\clinova.ps1 setup` for a pristine installation.
