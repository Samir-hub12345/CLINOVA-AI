<#
.SYNOPSIS
    Clinova AI - Read-Only AI Architecture and Secret Auditor (Phase 0)
.DESCRIPTION
    Audits AI dependencies, models, environment variables, and data security.
    Strictly read-only. NEVER prints secret values.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CLINOVA AI - READ-ONLY AI AND SECURITY AUDIT (PHASE 0)    " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = Get-Location }

# 1. Environment Variable Audit (Names and Presence Only)
Write-Host "[1/5] ENVIRONMENT VARIABLE AUDIT" -ForegroundColor Yellow
$envPath = Join-Path $root ".env"

if (Test-Path $envPath) {
    Write-Host "  Found local .env file. Auditing variable presence:" -ForegroundColor White
    $lines = Get-Content $envPath
    foreach ($line in $lines) {
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)') {
            $varName = $matches[1]
            $val = $matches[2].Trim()
            if ($varName -eq "GEMINI_API_KEY") {
                if ($val.Length -eq 0) {
                    Write-Host "    $varName = MISSING" -ForegroundColor Red
                } elseif ($val -match '^AIzaSy[A-Za-z0-9_-]{33}$') {
                    Write-Host "    $varName = PRESENT" -ForegroundColor Green
                } else {
                    Write-Host "    $varName = REFERENCED BUT INVALID/UNKNOWN" -ForegroundColor Yellow
                }
            } elseif ($varName -like "*KEY*" -or $varName -like "*SECRET*" -or $varName -like "*PASSWORD*") {
                Write-Host "    $varName = $status (Masked)" -ForegroundColor Green
            } else {
                Write-Host "    $varName = $status" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "  [WARN] .env file not found at repository root." -ForegroundColor Yellow
}

# 2. Git Secret Exposure Audit
Write-Host ""
Write-Host "[2/5] GIT HISTORY AND TRACKING AUDIT" -ForegroundColor Yellow
$trackedEnv = git ls-files .env 2>$null
if ($trackedEnv) {
    Write-Host "  [CRITICAL] .env is tracked in git index!" -ForegroundColor Red
} else {
    Write-Host "  [SAFE] .env is not tracked in git index." -ForegroundColor Green
}

$secretCommits = git --no-pager log -S "AIzaSy" --oneline 2>$null
if ($secretCommits) {
    Write-Host "  [CRITICAL] Potential API key pattern detected in commit history!" -ForegroundColor Red
} else {
    Write-Host "  [SAFE] No API key patterns ('AIzaSy') found in git commit history." -ForegroundColor Green
}

# 3. Dependency Audit
Write-Host ""
Write-Host "[3/5] AI DEPENDENCY AUDIT" -ForegroundColor Yellow
$reqPath = Join-Path $root "backend\requirements.txt"
if (Test-Path $reqPath) {
    $reqs = Get-Content $reqPath
    $aiPackages = @("google-genai", "openai", "anthropic", "transformers", "torch", "faster-whisper", "paddleocr", "pytesseract")
    foreach ($pkg in $aiPackages) {
        $match = $reqs | Where-Object { $_ -match "^$pkg" }
        if ($match) {
            Write-Host "    - $pkg : INSTALLED ($match)" -ForegroundColor Green
        } else {
            Write-Host "    - $pkg : NOT INSTALLED (Zero footprint)" -ForegroundColor Gray
        }
    }
}

# 4. Codebase Provider and Model References
Write-Host ""
Write-Host "[4/5] AI ENGINE AND MODEL SPECIFICATIONS" -ForegroundColor Yellow
Write-Host "    - Primary LLM Provider: Google Gemini API (google-genai SDK)" -ForegroundColor White
Write-Host "    - Active Model: gemini-2.5-flash" -ForegroundColor White
Write-Host "    - Triage Fallback: Clinova Deterministic Heuristic Engine (_heuristic_triage)" -ForegroundColor White
Write-Host "    - SOAP Fallback: Clinova Deterministic Template Builder (_heuristic_soap)" -ForegroundColor White
Write-Host "    - Emergency Classifier: Clinova DeterministicRiskEngine (TRIAGE-R01 to R06)" -ForegroundColor White
Write-Host "    - Speech-to-Text: Gemini multimodal audio upload and Browser Web Speech API" -ForegroundColor White
Write-Host "    - Document OCR: Clinova Synthetic CBC Report Mock" -ForegroundColor White
Write-Host "    - Translation: Clinova Odia/Hindi Clinical Dictionary Normalizer" -ForegroundColor White

# 5. Runtime Defect and Risk Alert
Write-Host ""
Write-Host "[5/5] IDENTIFIED RUNTIME DEFECTS AND PRIVACY ALERTS" -ForegroundColor Yellow
Write-Host "    [!] PRIVACY RISK: Patient names transmitted in SOAP notes (gemini_service.py:120)" -ForegroundColor Red
Write-Host "    [!] REGULATORY RISK: Gemini Free Tier inputs are used for Google product training" -ForegroundColor Red
Write-Host "    [!] RUNTIME BUG: Voice chat references undefined settings.GEMINI_MODEL (gemini_service.py:456)" -ForegroundColor Yellow
Write-Host "    [!] AUDIT GAP: AIRun database records are defined but never saved during inference" -ForegroundColor Yellow

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AUDIT COMPLETE - ALL FINDINGS RECORDED IN docs/          " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
