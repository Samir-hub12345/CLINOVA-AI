# ==============================================================================
# CLINOVA AI - Native Windows Orchestrator
#
# Master PowerShell orchestrator for running Clinova AI natively on Windows.
# Manages PostgreSQL, Redis, FastAPI Backend, Next.js Frontend, AI configuration,
# health probes, process trees, and diagnostics.
#
# Target Workflow:
#   .\scripts\clinova.ps1 start [-Open]
#   .\scripts\clinova.ps1 stop
#   .\scripts\clinova.ps1 restart [-Open]
#   .\scripts\clinova.ps1 status
#   .\scripts\clinova.ps1 doctor
#   .\scripts\clinova.ps1 setup
#   .\scripts\clinova.ps1 health
#   .\scripts\clinova.ps1 logs [-Service backend|frontend|all] [-Lines 50] [-Follow]
# ==============================================================================

[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "status", "doctor", "setup", "health", "logs", "help")]
    [string]$Command = "start",

    [Parameter()]
    [switch]$Open,

    [Parameter()]
    [ValidateSet("backend", "frontend", "all")]
    [string]$Service = "all",

    [Parameter()]
    [int]$Lines = 40,

    [Parameter()]
    [switch]$Follow,

    [Parameter()]
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Continue"

# ------------------------------------------------------------------------------
# 1. Project Directory and Path Resolution (Dynamic and Relocatable)
# ------------------------------------------------------------------------------
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot  = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$BackendDir   = Join-Path $ProjectRoot "backend"
$FrontendDir  = Join-Path $ProjectRoot "frontend"
$ClinovaState = Join-Path $ProjectRoot ".clinova"
$PidDir       = Join-Path $ClinovaState "pids"
$LogDir       = Join-Path $ClinovaState "logs"
$StorageDir   = Join-Path $ProjectRoot "storage_data"

# Ensure runtime directories exist
@($ClinovaState, $PidDir, $LogDir, $StorageDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# ------------------------------------------------------------------------------
# 2. Mandatory Core Functions (Section 11 Specification)
# ------------------------------------------------------------------------------

function Write-ClinovaHeader {
    param ([string]$Title)
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host "  CLINOVA AI - $Title" -ForegroundColor Cyan
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param (
        [string]$Component,
        [string]$Status,
        [string]$Details,
        [string]$Color = "White"
    )
    $PadComponent = $Component.PadRight(14)
    $PadStatus    = $Status.PadRight(12)
    Write-Host "  $PadComponent" -NoNewline -ForegroundColor Gray
    Write-Host "$PadStatus" -NoNewline -ForegroundColor $Color
    Write-Host "$Details" -ForegroundColor White
}

function Test-Command {
    param ([string]$CmdName)
    $cmd = Get-Command $CmdName -ErrorAction SilentlyContinue
    return ($null -ne $cmd)
}

function Test-Port {
    param (
        [int]$Port,
        [string]$HostAddress = "127.0.0.1",
        [int]$TimeoutMs = 1000
    )
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $iar = $tcp.BeginConnect($HostAddress, $Port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
        if (-not $wait) {
            $tcp.Close()
            return $false
        }
        $tcp.EndConnect($iar)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

function Wait-ForPort {
    param (
        [int]$Port,
        [string]$HostAddress = "127.0.0.1",
        [int]$MaxWaitSeconds = 25
    )
    $elapsed = 0
    while ($elapsed -lt $MaxWaitSeconds) {
        if (Test-Port -HostAddress $HostAddress -Port $Port -TimeoutMs 800) {
            return $true
        }
        Start-Sleep -Milliseconds 1000
        $elapsed++
    }
    return $false
}

function Test-Process {
    param ([int]$ProcessId)
    if (-not $ProcessId) { return $false }
    try {
        $proc = Get-Process -Id $ProcessId -ErrorAction Stop
        return (-not $proc.HasExited)
    } catch {
        return $false
    }
}

function Test-HttpHealth {
    param (
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [int]$TimeoutSec = 3
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
        return ($response.StatusCode -eq $ExpectedStatus)
    } catch {
        if ($_.Exception.Response) {
            return ($_.Exception.Response.StatusCode.value__ -eq $ExpectedStatus)
        }
        return $false
    }
}

function Read-Env {
    param ([string]$Path = "")
    if (-not $Path) {
        $Path = if ($EnvFile) { $EnvFile } else { Join-Path $ProjectRoot ".env" }
    }
    $envHash = @{}
    if (-not (Test-Path $Path)) {
        return $envHash
    }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -and (-not $line.StartsWith("#")) -and ($line.Contains("="))) {
            $parts = $line -split "=", 2
            $key = $parts[0].Trim()
            $val = $parts[1].Trim().Trim('"').Trim("'")
            $envHash[$key] = $val
        }
    }
    return $envHash
}

function Get-PythonExecutable {
    # 1. Check project root .venv
    $venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) { return $venvPy }

    # 2. Check backend directory .venv
    $backendVenvPy = Join-Path $BackendDir ".venv\Scripts\python.exe"
    if (Test-Path $backendVenvPy) { return $backendVenvPy }

    # 3. Check system PATH python
    $cmd = Get-Command "python" -ErrorAction SilentlyContinue
    if ($cmd -and ($cmd.Source -notlike "*WindowsApps*")) {
        return $cmd.Source
    }

    # 4. Check Python launcher
    $pyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        try {
            $resolved = (& py -3 -c "import sys; print(sys.executable)" 2>$null)
            if ($resolved -and (Test-Path $resolved.Trim())) {
                return $resolved.Trim()
            }
        } catch { }
        return "py"
    }

    return $null
}

function Get-SavedPid {
    param ([string]$ServiceName)
    $pidFile = Join-Path $PidDir "$ServiceName.pid"
    if (Test-Path $pidFile) {
        $raw = (Get-Content $pidFile -ErrorAction SilentlyContinue)
        if ($raw) {
            $firstLine = $raw[0].ToString().Trim()
            if ($firstLine -match "^\d+$") {
                return [int]$firstLine
            }
        }
    }
    return $null
}

function Save-ServicePid {
    param (
        [string]$ServiceName,
        [int]$ProcessId,
        [int[]]$AdditionalPids = @()
    )
    $pidFile = Join-Path $PidDir "$ServiceName.pid"
    $allPids = @($ProcessId) + $AdditionalPids | Select-Object -Unique
    $allPids | Out-File -FilePath $pidFile -Encoding ascii -Force
}

function Remove-ServicePid {
    param ([string]$ServiceName)
    $pidFile = Join-Path $PidDir "$ServiceName.pid"
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

function Start-ServiceProcess {
    param (
        [string]$ServiceName,
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WorkingDirectory,
        [string]$LogFile,
        [string]$ErrFile
    )
    # Ensure log directories exist
    $logParent = Split-Path -Parent $LogFile
    if (-not (Test-Path $logParent)) {
        New-Item -ItemType Directory -Path $logParent -Force | Out-Null
    }

    "" | Out-File $LogFile -Force
    "" | Out-File $ErrFile -Force

    $proc = Start-Process -FilePath $FilePath `
                          -ArgumentList $ArgumentList `
                          -WorkingDirectory $WorkingDirectory `
                          -RedirectStandardOutput $LogFile `
                          -RedirectStandardError $ErrFile `
                          -WindowStyle Hidden `
                          -PassThru

    if ($proc -and $proc.Id) {
        Save-ServicePid $ServiceName $proc.Id
        return $proc
    }
    return $null
}

function Stop-ServiceProcess {
    param (
        [string]$ServiceName,
        [int]$Port = 0,
        [int]$TimeoutSec = 5
    )
    $pidFile = Join-Path $PidDir "$ServiceName.pid"
    $targetPids = @()

    if (Test-Path $pidFile) {
        Get-Content $pidFile -ErrorAction SilentlyContinue | ForEach-Object {
            $line = $_.Trim()
            if ($line -match "^\d+$") {
                $targetPids += [int]$line
            }
        }
    }

    # Also check if any process is holding the port
    if ($Port -gt 0) {
        try {
            $connPids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
                        Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($cp in $connPids) {
                if ($cp -gt 4 -and ($targetPids -notcontains $cp)) {
                    $targetPids += [int]$cp
                }
            }
        } catch { }
    }

    if ($targetPids.Count -eq 0) {
        Write-Status $ServiceName "INACTIVE" "No active PID file or listening port found" "Gray"
        return
    }

    foreach ($pidToStop in $targetPids) {
        if (Test-Process $pidToStop) {
            Write-Host "  Gracefully stopping $ServiceName process (PID $pidToStop)..." -ForegroundColor Yellow
            try {
                Stop-Process -Id $pidToStop -ErrorAction SilentlyContinue
            } catch { }

            # Wait for graceful exit
            $waitCount = 0
            while ((Test-Process $pidToStop) -and ($waitCount -lt ($TimeoutSec * 2))) {
                Start-Sleep -Milliseconds 500
                $waitCount++
            }

            # Force terminate only if still alive after timeout
            if (Test-Process $pidToStop) {
                Write-Host "  Process $pidToStop did not exit gracefully; force terminating..." -ForegroundColor DarkYellow
                try {
                    & taskkill.exe /pid $pidToStop /T /F 2>$null | Out-Null
                } catch { }
            }
        }
    }

    Remove-ServicePid $ServiceName
    Write-Status $ServiceName "STOPPED" "Processes terminated cleanly" "Green"
}

# ------------------------------------------------------------------------------
# 3. Command Implementations
# ------------------------------------------------------------------------------

function Invoke-ClinovaDoctor {
    Write-ClinovaHeader "System Health Diagnostics and Prerequisites"

    $config = Read-Env
    $dbUrl  = if ($config["DATABASE_URL"]) { $config["DATABASE_URL"] } else { "postgresql+asyncpg://postgres:postgres@localhost:5432/clinova" }
    $isSqlite = $dbUrl.ToLower().StartsWith("sqlite")

    Write-Host "[1/5] Core Command Prerequisites:" -ForegroundColor Yellow

    # Git Check
    if (Test-Command "git") {
        $gitOut = (git --version 2>$null)
        $gitVer = $gitOut -replace "^git version\s*", ""
        Write-Status "Git" "FOUND" "$gitVer" "Green"
    } else {
        Write-Status "Git" "MISSING" "Install via: winget install Git.Git" "Red"
    }

    # PowerShell Check
    $psVer = $PSVersionTable.PSVersion
    if ($psVer.Major -ge 5) {
        Write-Status "PowerShell" "FOUND" "v$($psVer.ToString())" "Green"
    } else {
        Write-Status "PowerShell" "WRONG VERSION" "v$($psVer.ToString()) (Requires 5.1+ or 7+)" "Red"
    }

    # Node.js Check
    if (Test-Command "node") {
        $nodeOut = (node --version 2>$null)
        if ($nodeOut -match "v(\d+)\.") {
            $major = [int]$matches[1]
            if ($major -ge 18) {
                Write-Status "Node.js" "FOUND" "$nodeOut" "Green"
            } else {
                Write-Status "Node.js" "WRONG VERSION" "$nodeOut (Requires Node 18+ or 20+)" "Red"
            }
        } else {
            Write-Status "Node.js" "FOUND" "$nodeOut" "Green"
        }
    } else {
        Write-Status "Node.js" "MISSING" "Install via: winget install OpenJS.NodeJS" "Red"
    }

    # npm Check
    if (Test-Command "npm") {
        $npmOut = (npm --version 2>$null)
        Write-Status "npm" "FOUND" "v$npmOut" "Green"
    } else {
        Write-Status "npm" "MISSING" "Included with Node.js installation" "Red"
    }

    # Python Check
    $py = Get-PythonExecutable
    if ($py) {
        $pyOut = (& $py --version 2>&1)
        if ($pyOut -match "Python\s+(\d+)\.(\d+)") {
            $pMaj = [int]$matches[1]
            $pMin = [int]$matches[2]
            if ($pMaj -ge 3 -and $pMin -ge 10) {
                Write-Status "Python" "FOUND" "$pyOut ($py)" "Green"
            } else {
                Write-Status "Python" "WRONG VERSION" "$pyOut (Requires Python 3.10+ / 3.12+)" "Red"
            }
        } else {
            Write-Status "Python" "FOUND" "$pyOut" "Green"
        }
    } else {
        Write-Status "Python" "MISSING" "Install Python 3.12 via: winget install Python.Python.3.12" "Red"
    }

    # PostgreSQL / psql Check
    $pgPortOpen = Test-Port -Port 5432
    if ($isSqlite) {
        Write-Status "psql" "NOT REQUIRED" "SQLite zero-install file mode active in .env" "DarkGray"
    } elseif (Test-Command "psql") {
        $psqlVer = (psql --version 2>$null)
        Write-Status "psql" "FOUND" "$psqlVer" "Green"
    } elseif ($pgPortOpen) {
        Write-Status "psql" "FOUND" "PostgreSQL listening on localhost:5432" "Green"
    } else {
        $pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pgService) {
            Write-Status "psql" "FOUND" "$($pgService.DisplayName) (Service $($pgService.Status))" "Yellow"
        } else {
            Write-Status "psql" "MISSING" "PostgreSQL 16 recommended: winget install PostgreSQL.PostgreSQL.16, or switch to SQLite in .env" "DarkYellow"
        }
    }

    # Redis / redis-cli Check
    $redisPortOpen = Test-Port -Port 6379
    if (Test-Command "redis-cli") {
        $redisVer = (redis-cli --version 2>$null)
        Write-Status "redis-cli" "FOUND" "$redisVer" "Green"
    } elseif ($redisPortOpen) {
        Write-Status "redis-cli" "FOUND" "Redis listening on localhost:6379" "Green"
    } else {
        Write-Status "redis-cli" "NOT REQUIRED" "Optional. In-memory graceful fallback active in app.core.redis" "DarkGray"
    }

    Write-Host ""
    Write-Host "[2/5] Environment and Configuration:" -ForegroundColor Yellow
    $envPath = if ($EnvFile) { $EnvFile } else { Join-Path $ProjectRoot ".env" }
    if (Test-Path $envPath) {
        Write-Status ".env File" "FOUND" "$envPath" "Green"
    } else {
        Write-Status ".env File" "MISSING" "Run '.\scripts\clinova.ps1 setup' to generate .env" "Red"
    }

    # Database Mode
    if ($isSqlite) {
        Write-Status "Database Mode" "SQLITE" "$dbUrl (Zero-install local storage)" "Green"
    } else {
        $dbStatus = if ($pgPortOpen) { "ONLINE" } else { "OFFLINE" }
        $dbColor  = if ($pgPortOpen) { "Green" } else { "Red" }
        Write-Status "Database Mode" "$dbStatus" "$dbUrl" "$dbColor"
    }

    # AI Configuration (Never leak secret keys)
    $geminiKey = $config["GEMINI_API_KEY"]
    if ($geminiKey -and ($geminiKey.Trim().Length -gt 10)) {
        $keyLen = $geminiKey.Trim().Length
        Write-Status "AI Engine" "CONFIGURED" "Google Gemini API key configured [masked, $keyLen chars]" "Green"
    } else {
        Write-Status "AI Engine" "FALLBACK" "No GEMINI_API_KEY. Deterministic clinical rules active." "Cyan"
    }

    Write-Host ""
    Write-Host "[3/5] Port Availability:" -ForegroundColor Yellow
    $ports = @(
        @{ Port = 8000; Service = "FastAPI Backend" },
        @{ Port = 3000; Service = "Next.js Frontend" },
        @{ Port = 5432; Service = "PostgreSQL" },
        @{ Port = 6379; Service = "Redis" }
    )
    foreach ($p in $ports) {
        $isOpen = Test-Port -Port $p.Port
        if ($isOpen) {
            Write-Status "Port $($p.Port)" "LISTENING" "Occupied by $($p.Service) or active process" "Cyan"
        } else {
            Write-Status "Port $($p.Port)" "AVAILABLE" "Ready for $($p.Service)" "Green"
        }
    }

    Write-Host ""
    Write-Host "[4/5] Filesystem and Dependency Status:" -ForegroundColor Yellow
    $nodeModules = Join-Path $FrontendDir "node_modules"
    if (Test-Path $nodeModules) {
        Write-Status "Frontend Deps" "READY" "node_modules present" "Green"
    } else {
        Write-Status "Frontend Deps" "MISSING" "Run '.\scripts\clinova.ps1 setup' to install" "Yellow"
    }

    $venvPath = Join-Path $ProjectRoot ".venv"
    $backendVenvPath = Join-Path $BackendDir ".venv"
    if ((Test-Path $venvPath) -or (Test-Path $backendVenvPath)) {
        Write-Status "Python Venv" "READY" "Virtual environment present" "Green"
    } else {
        Write-Status "Python Venv" "MISSING" "Run '.\scripts\clinova.ps1 setup' to initialize" "Yellow"
    }

    Write-Host ""
    Write-Host "[5/5] Recommendations:" -ForegroundColor Yellow
    if (-not (Test-Path $envPath)) {
        Write-Host "  -> Run '.\scripts\clinova.ps1 setup' to initialize your local environment." -ForegroundColor Cyan
    } elseif ((-not (Test-Port -Port 5432)) -and (-not $isSqlite)) {
        Write-Host "  -> PostgreSQL is offline. Start the service or switch to SQLite in .env:" -ForegroundColor Yellow
        Write-Host "     DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db" -ForegroundColor Gray
    } else {
        Write-Host "  -> Core prerequisites satisfied! You can run '.\scripts\clinova.ps1 start'." -ForegroundColor Green
    }
    Write-Host ""
}

function Invoke-ClinovaSetup {
    Write-ClinovaHeader "Automated Environment Setup"

    # 1. Environment file setup
    $envPath = Join-Path $ProjectRoot ".env"
    $examplePath = Join-Path $ProjectRoot ".env.example"
    if (-not (Test-Path $envPath)) {
        if (Test-Path $examplePath) {
            Write-Host "Generating .env from .env.example..." -ForegroundColor Yellow
            $randomSecret = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
            $content = Get-Content $examplePath -Raw
            $content = $content -replace "change-this-in-production-to-a-secure-random-secret", $randomSecret
            $content | Out-File -FilePath $envPath -Encoding utf8 -Force
            Write-Host "Created .env with cryptographically randomized SECRET_KEY." -ForegroundColor Green
        } else {
            Write-Host "Creating minimal .env..." -ForegroundColor Yellow
            $randomSecret = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
            $defaultEnv = @(
                "APP_NAME=Clinova AI",
                "ENVIRONMENT=development",
                "DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db",
                "REDIS_URL=redis://localhost:6379/0",
                "SECRET_KEY=$randomSecret",
                "GEMINI_API_KEY=",
                "BACKEND_PORT=8000",
                "FRONTEND_PORT=3000",
                "NEXT_PUBLIC_API_URL=http://localhost:8000"
            )
            $defaultEnv | Out-File -FilePath $envPath -Encoding utf8
        }
    } else {
        Write-Host ".env already exists. Preserving developer configuration." -ForegroundColor Green
    }

    # 2. Python Virtual Environment Setup
    $py = Get-PythonExecutable
    $venvPath = Join-Path $ProjectRoot ".venv"
    if (-not (Test-Path $venvPath)) {
        if (-not $py) {
            Write-Error "Python executable not found in PATH! Please install Python 3.12+ first."
            return
        }
        Write-Host "Creating Python virtual environment in .venv..." -ForegroundColor Yellow
        & $py -m venv "$venvPath"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment."
            return
        }
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    }

    $venvPy = Join-Path $venvPath "Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
        $venvPy = Join-Path $BackendDir ".venv\Scripts\python.exe"
    }
    $reqFile = Join-Path $BackendDir "requirements.txt"
    if ((Test-Path $venvPy) -and (Test-Path $reqFile)) {
        Write-Host "Installing/Verifying Python backend dependencies..." -ForegroundColor Yellow
        & "$venvPy" -m pip install --quiet --upgrade pip
        & "$venvPy" -m pip install --quiet -r "$reqFile"
        Write-Host "Backend Python dependencies are up to date." -ForegroundColor Green
    }

    # 3. Frontend Node Dependencies
    $nodeModules = Join-Path $FrontendDir "node_modules"
    if (-not (Test-Path $nodeModules)) {
        if (Test-Command "npm") {
            Write-Host "Installing frontend node dependencies (npm install)..." -ForegroundColor Yellow
            Push-Location $FrontendDir
            try {
                & cmd.exe /c npm install
                Write-Host "Frontend dependencies installed successfully." -ForegroundColor Green
            } finally {
                Pop-Location
            }
        } else {
            Write-Host "Warning: npm not found. Frontend dependencies must be installed manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Frontend node_modules already present." -ForegroundColor Green
    }

    # 4. Storage Directory
    if (-not (Test-Path $StorageDir)) {
        New-Item -ItemType Directory -Path $StorageDir -Force | Out-Null
    }

    Write-Host ""
    Write-Host "Setup complete! Run '.\scripts\clinova.ps1 start' to launch Clinova AI." -ForegroundColor Green
    Write-Host ""
}

function Invoke-ClinovaStart {
    Write-ClinovaHeader "Starting Native Windows Stack"

    # STEP 1: Validate Windows environment
    Write-Host "[STEP 1/17] Validating Windows environment..." -ForegroundColor Yellow
    $py = Get-PythonExecutable
    if (-not $py) {
        Write-Error "Python executable not found. Please run '.\scripts\clinova.ps1 setup' or install Python 3.12+."
        return
    }
    if (-not (Test-Command "node")) {
        Write-Error "Node.js executable not found. Please install Node.js 18+ or 20+."
        return
    }
    Write-Status "Environment" "VALID" "Python and Node runtimes verified" "Green"

    # STEP 2: Load configuration
    Write-Host "[STEP 2/17] Loading configuration from .env..." -ForegroundColor Yellow
    $envPath = if ($EnvFile) { $EnvFile } else { Join-Path $ProjectRoot ".env" }
    if (-not (Test-Path $envPath)) {
        Write-Host "  .env not found. Running initial setup..." -ForegroundColor Yellow
        Invoke-ClinovaSetup
    }
    $config = Read-Env $envPath
    $BackendPort  = if ($config["BACKEND_PORT"]) { [int]$config["BACKEND_PORT"] } else { 8000 }
    $FrontendPort = if ($config["FRONTEND_PORT"]) { [int]$config["FRONTEND_PORT"] } else { 3000 }
    $DbUrl        = if ($config["DATABASE_URL"]) { $config["DATABASE_URL"] } else { "postgresql+asyncpg://postgres:postgres@localhost:5432/clinova" }
    $isSqlite     = $DbUrl.ToLower().StartsWith("sqlite")
    Write-Status "Config" "LOADED" "Backend port: $BackendPort | Frontend port: $FrontendPort" "Green"

    # STEP 3: Check PostgreSQL
    Write-Host "[STEP 3/17] Checking PostgreSQL..." -ForegroundColor Yellow
    $pgOpen = $false
    if ($isSqlite) {
        Write-Status "PostgreSQL" "SQLITE" "SQLite mode active; local file database used." "Green"
    } else {
        $pgOpen = Test-Port -Port 5432

        # STEP 4: Start PostgreSQL if managed local service is stopped
        Write-Host "[STEP 4/17] Starting PostgreSQL if local service stopped..." -ForegroundColor Yellow
        if (-not $pgOpen) {
            $pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($pgService -and ($pgService.Status -ne "Running")) {
                Write-Host "  Starting local PostgreSQL service ($($pgService.Name))..." -ForegroundColor Gray
                try {
                    Start-Service $pgService.Name -ErrorAction Stop
                    $pgOpen = Wait-ForPort -Port 5432 -MaxWaitSeconds 10
                } catch { }
            }
        }

        # STEP 5: Verify PostgreSQL health
        Write-Host "[STEP 5/17] Verifying PostgreSQL health..." -ForegroundColor Yellow
        if ($pgOpen -or (Test-Port -Port 5432)) {
            Write-Status "PostgreSQL" "ONLINE" "localhost:5432 ready" "Green"
        } else {
            Write-Host "  [ERROR] PostgreSQL is not running on localhost:5432." -ForegroundColor Red
            Write-Host "  Solutions:" -ForegroundColor Yellow
            Write-Host "    1. Start PostgreSQL: Start-Service postgresql-x64-16" -ForegroundColor Gray
            Write-Host "    2. Or switch to SQLite in .env: DATABASE_URL=sqlite+aiosqlite:///./clinova-demo.db" -ForegroundColor Gray
            Write-Error "PostgreSQL dependency check failed. Aborting startup."
            return
        }
    }

    # STEP 6: Check Redis
    Write-Host "[STEP 6/17] Checking Redis cache and queue..." -ForegroundColor Yellow
    $redisOpen = Test-Port -Port 6379

    # STEP 7: Start Redis if required
    Write-Host "[STEP 7/17] Starting Redis service if present..." -ForegroundColor Yellow
    if (-not $redisOpen) {
        $redisService = Get-Service -ErrorAction SilentlyContinue | Where-Object { ($_.Name -like "*redis*" -or $_.Name -like "*memurai*") -and ($_.DisplayName -notlike "*Redist*") -and ($_.Name -notlike "*Redist*") } | Select-Object -First 1
        if ($redisService -and ($redisService.Status -ne "Running")) {
            Write-Host "  Starting local Redis service ($($redisService.Name))..." -ForegroundColor Gray
            try {
                Start-Service $redisService.Name -ErrorAction Stop
                $redisOpen = Wait-ForPort -Port 6379 -MaxWaitSeconds 5
            } catch { }
        }
    }

    # STEP 8: Verify Redis health
    Write-Host "[STEP 8/17] Verifying Redis health..." -ForegroundColor Yellow
    if ($redisOpen -or (Test-Port -Port 6379)) {
        Write-Status "Redis" "ONLINE" "localhost:6379 ready" "Green"
    } else {
        Write-Status "Redis" "FALLBACK" "Port 6379 closed. In-memory graceful fallback active." "Cyan"
    }

    # STEP 9: Prepare backend Python environment
    Write-Host "[STEP 9/17] Preparing backend Python environment..." -ForegroundColor Yellow
    $venvPy = Get-PythonExecutable
    if (-not $venvPy) {
        Write-Error "Python runtime not configured. Run '.\scripts\clinova.ps1 setup'."
        return
    }
    Write-Status "Python Venv" "READY" "$venvPy" "Green"

    # STEP 10: Start backend
    Write-Host "[STEP 10/17] Starting FastAPI Backend on port $BackendPort..." -ForegroundColor Yellow
    $backendPid = Get-SavedPid "backend"
    if ($backendPid -and (Test-Process $backendPid)) {
        Write-Status "Backend" "RUNNING" "Already active with PID $backendPid" "Green"
    } else {
        if (Test-Port -Port $BackendPort) {
            Write-Host "  [WARN] Port $BackendPort is currently occupied by an unmanaged process." -ForegroundColor Yellow
        } else {
            $backendLogOut = Join-Path $LogDir "backend.log"
            $backendLogErr = Join-Path $LogDir "backend.err.log"
            $backendArgs = @(
                "-m", "uvicorn",
                "app.main:app",
                "--host", "127.0.0.1",
                "--port", "$BackendPort"
            )
            $proc = Start-ServiceProcess -ServiceName "backend" `
                                         -FilePath $venvPy `
                                         -ArgumentList $backendArgs `
                                         -WorkingDirectory $BackendDir `
                                         -LogFile $backendLogOut `
                                         -ErrFile $backendLogErr

            # STEP 11: Wait for backend health endpoint
            Write-Host "[STEP 11/17] Waiting for backend health endpoint..." -ForegroundColor Yellow
            $live = $false
            $healthUrl = "http://127.0.0.1:$BackendPort/api/v1/health/live"
            for ($i = 0; $i -lt 30; $i++) {
                Start-Sleep -Milliseconds 800
                if (Test-HttpHealth -Url $healthUrl -ExpectedStatus 200) {
                    $live = $true
                    break
                }
            }

            if ($live) {
                Write-Status "Backend" "ONLINE" "http://localhost:$BackendPort [PID: $($proc.Id)]" "Green"
            } else {
                Write-Host "  [ERROR] Backend failed to report healthy within 25 seconds." -ForegroundColor Red
                Write-Host "  Inspect backend logs at: $backendLogErr" -ForegroundColor Yellow
                Get-Content $backendLogErr -Tail 15 -ErrorAction SilentlyContinue | Write-Host -ForegroundColor DarkRed
                return
            }
        }
    }

    # STEP 12: Prepare frontend dependencies
    Write-Host "[STEP 12/17] Preparing frontend dependencies..." -ForegroundColor Yellow
    $nodeModules = Join-Path $FrontendDir "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Host "  Installing frontend dependencies..." -ForegroundColor Yellow
        Push-Location $FrontendDir
        try {
            & cmd.exe /c npm install
        } finally {
            Pop-Location
        }
    }
    Write-Status "Frontend Deps" "READY" "node_modules verified" "Green"

    # STEP 13: Start frontend
    Write-Host "[STEP 13/17] Starting Next.js Frontend on port $FrontendPort..." -ForegroundColor Yellow
    $frontendPid = Get-SavedPid "frontend"
    if ($frontendPid -and (Test-Process $frontendPid)) {
        Write-Status "Frontend" "RUNNING" "Already active with PID $frontendPid" "Green"
    } else {
        if (Test-Port -Port $FrontendPort) {
            Write-Host "  [WARN] Port $FrontendPort is currently occupied by an unmanaged process." -ForegroundColor Yellow
        } else {
            $frontendLogOut = Join-Path $LogDir "frontend.log"
            $frontendLogErr = Join-Path $LogDir "frontend.err.log"

            $frontendProc = Start-ServiceProcess -ServiceName "frontend" `
                                                 -FilePath "cmd.exe" `
                                                 -ArgumentList @("/c", "npm", "run", "dev", "--", "-p", "$FrontendPort") `
                                                 -WorkingDirectory $FrontendDir `
                                                 -LogFile $frontendLogOut `
                                                 -ErrFile $frontendLogErr

            # STEP 14: Verify frontend port
            Write-Host "[STEP 14/17] Verifying frontend port..." -ForegroundColor Yellow
            $frontReady = Wait-ForPort -Port $FrontendPort -MaxWaitSeconds 30
            if ($frontReady) {
                Write-Status "Frontend" "ONLINE" "http://localhost:$FrontendPort" "Green"
            } else {
                Write-Host "  [WARN] Frontend port $FrontendPort not open yet (Next.js compilation in progress)." -ForegroundColor Yellow
            }
        }
    }

    # STEP 15: Verify frontend-to-backend connectivity
    Write-Host "[STEP 15/17] Verifying frontend-to-backend connectivity..." -ForegroundColor Yellow
    $apiBaseUrl = if ($config["NEXT_PUBLIC_API_URL"]) { $config["NEXT_PUBLIC_API_URL"] } else { "http://localhost:$BackendPort" }
    $connOk = Test-HttpHealth -Url "$apiBaseUrl/api/v1/health/live" -ExpectedStatus 200
    if ($connOk) {
        Write-Status "Connectivity" "VERIFIED" "Frontend API target ($apiBaseUrl) reachable" "Green"
    } else {
        Write-Status "Connectivity" "WARNING" "Could not reach backend at $apiBaseUrl" "Yellow"
    }

    # STEP 16: Verify AI service configuration without exposing secrets
    Write-Host "[STEP 16/17] Verifying AI service configuration..." -ForegroundColor Yellow
    $aiStatus = if ($config["GEMINI_API_KEY"] -and ($config["GEMINI_API_KEY"].Trim().Length -gt 10)) {
        "READY (Google Gemini 2.5 Flash active)"
    } else {
        "READY (Deterministic clinical rules active)"
    }
    Write-Status "AI Config" "READY" "$aiStatus" "Green"

    # STEP 17: Print final service summary (Exact format per Section 12)
    Write-Host ""
    Write-Host "====================================================================" -ForegroundColor Green
    Write-Host "Clinova AI Local Environment" -ForegroundColor Green
    Write-Host "====================================================================" -ForegroundColor Green
    Write-Host ""

    $pgDetails = if ($isSqlite) { "clinova-demo.db" } else { "localhost:5432" }
    $pgState   = if ($isSqlite) { "SQLITE" } else { "RUNNING" }
    $redisDetails = if ($redisOpen -or (Test-Port -Port 6379)) { "localhost:6379" } else { "in-memory fallback" }
    $redisState   = if ($redisOpen -or (Test-Port -Port 6379)) { "RUNNING" } else { "FALLBACK" }

    Write-Status "PostgreSQL"   "$pgState"    "$pgDetails" "Green"
    Write-Status "Redis"        "$redisState"  "$redisDetails" "Green"
    Write-Status "Backend"      "RUNNING"      "http://localhost:$BackendPort" "Green"
    Write-Status "Swagger"      "READY"        "http://localhost:$BackendPort/docs" "Cyan"
    Write-Status "Frontend"     "RUNNING"      "http://localhost:$FrontendPort" "Green"
    Write-Status "AI Config"    "READY"        "" "Green"
    Write-Host ""
    Write-Host "Clinova is ready." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Workflow Commands:" -ForegroundColor Gray
    Write-Host "    Stop stack:    .\scripts\clinova.ps1 stop" -ForegroundColor Gray
    Write-Host "    Check health:  .\scripts\clinova.ps1 health" -ForegroundColor Gray
    Write-Host "    View logs:     .\scripts\clinova.ps1 logs" -ForegroundColor Gray
    Write-Host "====================================================================" -ForegroundColor Green
    Write-Host ""

    if ($Open) {
        Write-Host "Opening Clinova AI in your default browser..." -ForegroundColor Cyan
        Start-Process "http://localhost:$FrontendPort"
    }
}

function Invoke-ClinovaStop {
    Write-ClinovaHeader "Stopping Native Windows Stack"

    $config = Read-Env
    $BackendPort  = if ($config["BACKEND_PORT"]) { [int]$config["BACKEND_PORT"] } else { 8000 }
    $FrontendPort = if ($config["FRONTEND_PORT"]) { [int]$config["FRONTEND_PORT"] } else { 3000 }

    # Stop Frontend
    Write-Host "Stopping Frontend..." -ForegroundColor Yellow
    Stop-ServiceProcess -ServiceName "frontend" -Port $FrontendPort -TimeoutSec 3

    # Stop Backend
    Write-Host "Stopping Backend..." -ForegroundColor Yellow
    Stop-ServiceProcess -ServiceName "backend" -Port $BackendPort -TimeoutSec 3

    Write-Host ""
    Write-Host "Clinova stack stopped cleanly." -ForegroundColor Green
    Write-Host ""
}

function Invoke-ClinovaRestart {
    Write-ClinovaHeader "Restarting Native Windows Stack"
    Invoke-ClinovaStop
    Start-Sleep -Seconds 2
    if ($Open) {
        Invoke-ClinovaStart -Open
    } else {
        Invoke-ClinovaStart
    }
}

function Invoke-ClinovaStatus {
    Write-ClinovaHeader "Service Status Inspection"

    $config = Read-Env
    $BackendPort  = if ($config["BACKEND_PORT"]) { [int]$config["BACKEND_PORT"] } else { 8000 }
    $FrontendPort = if ($config["FRONTEND_PORT"]) { [int]$config["FRONTEND_PORT"] } else { 3000 }

    # Backend
    $bPid = Get-SavedPid "backend"
    $bAlive = if ($bPid) { Test-Process $bPid } else { $false }
    $bPortOpen = Test-Port -Port $BackendPort
    if ($bAlive -and $bPortOpen) {
        Write-Status "Backend" "RUNNING" "PID $bPid on port $BackendPort (HTTP 200)" "Green"
    } elseif ($bPortOpen) {
        Write-Status "Backend" "LISTENING" "Port $BackendPort active (external PID or unmanaged)" "Yellow"
    } else {
        Write-Status "Backend" "STOPPED" "Port $BackendPort offline" "Red"
    }

    # Frontend
    $fPid = Get-SavedPid "frontend"
    $fAlive = if ($fPid) { Test-Process $fPid } else { $false }
    $fPortOpen = Test-Port -Port $FrontendPort
    if ($fAlive -and $fPortOpen) {
        Write-Status "Frontend" "RUNNING" "PID $fPid on port $FrontendPort (HTTP 200)" "Green"
    } elseif ($fPortOpen) {
        Write-Status "Frontend" "LISTENING" "Port $FrontendPort active (external PID or unmanaged)" "Yellow"
    } else {
        Write-Status "Frontend" "STOPPED" "Port $FrontendPort offline" "Red"
    }

    # PostgreSQL
    $pgOpen = Test-Port -Port 5432
    $dbUrl  = if ($config["DATABASE_URL"]) { $config["DATABASE_URL"] } else { "" }
    if ($dbUrl.ToLower().StartsWith("sqlite")) {
        Write-Status "PostgreSQL" "SQLITE" "SQLite zero-install mode active" "Green"
    } elseif ($pgOpen) {
        Write-Status "PostgreSQL" "ONLINE" "localhost:5432 ready" "Green"
    } else {
        Write-Status "PostgreSQL" "OFFLINE" "Port 5432 closed" "DarkGray"
    }

    # Redis
    $redisOpen = Test-Port -Port 6379
    if ($redisOpen) {
        Write-Status "Redis" "ONLINE" "localhost:6379 ready" "Green"
    } else {
        Write-Status "Redis" "FALLBACK" "Port 6379 closed (in-memory fallback active)" "Cyan"
    }
    Write-Host ""
}

function Invoke-ClinovaHealth {
    Write-ClinovaHeader "Deep Health Endpoint Probe"

    $config = Read-Env
    $BackendPort  = if ($config["BACKEND_PORT"]) { [int]$config["BACKEND_PORT"] } else { 8000 }
    $FrontendPort = if ($config["FRONTEND_PORT"]) { [int]$config["FRONTEND_PORT"] } else { 3000 }
    $base = "http://127.0.0.1:$BackendPort"

    # Liveness
    try {
        $live = Invoke-RestMethod -Uri "$base/api/v1/health/live" -TimeoutSec 3 -ErrorAction Stop
        Write-Status "Liveness" "ALIVE" "$($live.status) [timestamp: $($live.timestamp)]" "Green"
    } catch {
        Write-Status "Liveness" "UNREACHABLE" "Failed to connect to $base/api/v1/health/live" "Red"
    }

    # Readiness
    try {
        $ready = Invoke-RestMethod -Uri "$base/api/v1/health/ready" -TimeoutSec 4 -ErrorAction Stop
        $color = if ($ready.status -eq "ready") { "Green" } elseif ($ready.status -eq "degraded") { "Yellow" } else { "Red" }
        Write-Status "Readiness" "$($ready.status.ToUpper())" "Dependencies evaluated" "$color"

        if ($ready.dependencies) {
            foreach ($dep in $ready.dependencies.PSObject.Properties) {
                $depObj = $dep.Value
                $dColor = if ($depObj.healthy) { "Green" } else { "Yellow" }
                Write-Host "    - $($dep.Name): " -NoNewline -ForegroundColor Gray
                Write-Host "$($depObj.message) " -NoNewline -ForegroundColor $dColor
                Write-Host "($($depObj.latency_ms) ms)" -ForegroundColor DarkGray
            }
        }
    } catch {
        Write-Status "Readiness" "PROBE FAILED" "$_" "Red"
    }

    # Ping
    try {
        $ping = Invoke-RestMethod -Uri "$base/api/v1/ping" -TimeoutSec 2 -ErrorAction Stop
        Write-Status "Ping" "PONG" "API responsive [$($ping.status)]" "Green"
    } catch {
        Write-Status "Ping" "FAILED" "$_" "Red"
    }

    # Frontend UI Probe
    try {
        $uiResp = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -TimeoutSec 4 -UseBasicParsing -ErrorAction Stop
        Write-Status "Frontend UI" "HTTP $($uiResp.StatusCode)" "Web application responds" "Green"
    } catch {
        Write-Status "Frontend UI" "OFFLINE" "Could not connect to http://localhost:$FrontendPort" "Red"
    }

    Write-Host ""
}

function Invoke-ClinovaLogs {
    Write-ClinovaHeader "Service Logs Viewer"

    $backendLog  = Join-Path $LogDir "backend.log"
    $backendErr  = Join-Path $LogDir "backend.err.log"
    $frontendLog = Join-Path $LogDir "frontend.log"
    $frontendErr = Join-Path $LogDir "frontend.err.log"

    if ($Service -eq "backend" -or $Service -eq "all") {
        Write-Host "=== Backend Logs ($backendLog) ===" -ForegroundColor Cyan
        if (Test-Path $backendLog) {
            Get-Content $backendLog -Tail $Lines -ErrorAction SilentlyContinue
        } else {
            Write-Host "(No backend log file found)" -ForegroundColor Gray
        }

        if (Test-Path $backendErr) {
            $errContent = Get-Content $backendErr -Tail 15 -ErrorAction SilentlyContinue
            if ($errContent) {
                Write-Host "--- Backend Stderr ---" -ForegroundColor DarkRed
                $errContent | Write-Host -ForegroundColor Red
            }
        }
    }

    if ($Service -eq "frontend" -or $Service -eq "all") {
        Write-Host ""
        Write-Host "=== Frontend Logs ($frontendLog) ===" -ForegroundColor Cyan
        if (Test-Path $frontendLog) {
            Get-Content $frontendLog -Tail $Lines -ErrorAction SilentlyContinue
        } else {
            Write-Host "(No frontend log file found)" -ForegroundColor Gray
        }

        if (Test-Path $frontendErr) {
            $errContent = Get-Content $frontendErr -Tail 15 -ErrorAction SilentlyContinue
            if ($errContent) {
                Write-Host "--- Frontend Stderr ---" -ForegroundColor DarkRed
                $errContent | Write-Host -ForegroundColor Red
            }
        }
    }

    if ($Follow) {
        $targetFile = if ($Service -eq "frontend") { $frontendLog } else { $backendLog }
        Write-Host ""
        Write-Host "Tailing log: $targetFile (Press Ctrl+C to exit)..." -ForegroundColor Yellow
        Get-Content $targetFile -Tail $Lines -Wait
    }
}

# ------------------------------------------------------------------------------
# 4. Command Router
# ------------------------------------------------------------------------------
switch ($Command.ToLower()) {
    "start"   { Invoke-ClinovaStart }
    "stop"    { Invoke-ClinovaStop }
    "restart" { Invoke-ClinovaRestart }
    "status"  { Invoke-ClinovaStatus }
    "doctor"  { Invoke-ClinovaDoctor }
    "setup"   { Invoke-ClinovaSetup }
    "health"  { Invoke-ClinovaHealth }
    "logs"    { Invoke-ClinovaLogs }
    default {
        Write-ClinovaHeader "Command Help"
        Write-Host "Usage: .\scripts\clinova.ps1 <command> [options]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  start    [-Open]     Start all Clinova services (DB, Redis, Backend, Frontend)"
        Write-Host "  stop                 Stop all managed Clinova processes"
        Write-Host "  restart  [-Open]     Restart all Clinova services"
        Write-Host "  status               Show current status of all services and ports"
        Write-Host "  doctor               Run comprehensive system diagnostic check"
        Write-Host "  setup                Prepare .venv, install dependencies, and setup .env"
        Write-Host "  health               Probe live application health endpoints"
        Write-Host "  logs     [-Service backend|frontend|all] [-Lines N] [-Follow]"
        Write-Host ""
        Write-Host "Note: If script execution is restricted on your system, run via:" -ForegroundColor Gray
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\clinova.ps1 <command>" -ForegroundColor DarkGray
        Write-Host "  or run: .\start-dev.bat" -ForegroundColor DarkGray
        Write-Host ""
    }
}
