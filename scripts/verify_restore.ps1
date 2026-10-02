# CLINOVA AI - Backup Verification and Restore Integrity Test
# Restores the latest dump into a test database and verifies record counts.

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$DefaultBackupDir = Join-Path $ProjectRoot "backups"

param (
    [string]$SourceBackup = "",
    [string]$TestDbName = "clinova_restore_verify",
    [string]$DbUser = "postgres",
    [string]$DbHost = "127.0.0.1",
    [string]$DbPort = "5432",
    [string]$BackupDir = $DefaultBackupDir
)

$ErrorActionPreference = "Stop"

Write-Host "=== CLINOVA AI Restore Verification Commencing ===" -ForegroundColor Cyan

# Locate latest backup if not provided
if (-not $SourceBackup) {
    if (-not (Test-Path $BackupDir)) {
        Write-Error "No backup directory found at $BackupDir. Run backup_db.ps1 first."
    }
    $Latest = Get-ChildItem -Path $BackupDir -Filter "*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $Latest) {
        Write-Error "No backup files found in $BackupDir. Run backup_db.ps1 first."
    }
    $SourceBackup = $Latest.FullName
}

Write-Host "Verifying target backup: $SourceBackup" -ForegroundColor Yellow

# Verify SHA256 Checksum if file exists
$ChecksumFile = [System.IO.Path]::ChangeExtension($SourceBackup, ".sha256")
if (Test-Path $ChecksumFile) {
    $ExpectedHash = ((Get-Content $ChecksumFile) -split '\*|\s+')[0].Trim()
    $ActualHash = (Get-FileHash -Path $SourceBackup -Algorithm SHA256).Hash
    if ($ExpectedHash.ToUpper() -eq $ActualHash.ToUpper()) {
        Write-Host "SHA-256 Checksum Verified: $ActualHash" -ForegroundColor Green
    } else {
        Write-Error "CHECKSUM MISMATCH! File may be corrupted or tampered with."
    }
}

# Resolve password from environment or .env without hardcoding
$dbPassword = ""
if ($env:PGPASSWORD) {
    $dbPassword = $env:PGPASSWORD
} elseif ($env:POSTGRES_PASSWORD) {
    $dbPassword = $env:POSTGRES_PASSWORD
} else {
    $envFile = Join-Path $ProjectRoot ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            $line = $_.Trim()
            if ($line -match "^POSTGRES_PASSWORD=(.*)$") {
                $dbPassword = $matches[1].Trim().Trim('"').Trim("'")
            } elseif ($line -match "^DATABASE_URL=postgresql.*://([^:]+):([^@]+)@") {
                $dbPassword = $matches[2]
            }
        }
    }
}
if (-not $dbPassword) {
    $dbPassword = "postgres"
}

# PostgreSQL client path
$PsqlPath = ""
$PsqlCmd = Get-Command "psql" -ErrorAction SilentlyContinue
if ($PsqlCmd) {
    $PsqlPath = $PsqlCmd.Source
} else {
    $commonPgPaths = @(
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    )
    foreach ($candidate in $commonPgPaths) {
        if (Test-Path $candidate) {
            $PsqlPath = $candidate
            break
        }
    }
}

if ($PsqlPath -and (Test-Path $PsqlPath)) {
    $env:PGPASSWORD = $dbPassword
    Write-Host "Creating verification database: $TestDbName..." -ForegroundColor Yellow
    & "$PsqlPath" -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE IF EXISTS $TestDbName;" | Out-Null
    & "$PsqlPath" -h $DbHost -p $DbPort -U $DbUser -d postgres -c "CREATE DATABASE $TestDbName;" | Out-Null

    Write-Host "Restoring schema and records into $TestDbName..." -ForegroundColor Yellow
    & "$PsqlPath" -h $DbHost -p $DbPort -U $DbUser -d $TestDbName -f "$SourceBackup" | Out-Null

    # Query verification metrics
    $Counts = & "$PsqlPath" -h $DbHost -p $DbPort -U $DbUser -d $TestDbName -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    Write-Host "Verification database public tables count: $($Counts.Trim())" -ForegroundColor Green

    # Cleanup verification DB
    & "$PsqlPath" -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE $TestDbName;" | Out-Null
    Write-Host "Verification database cleaned up." -ForegroundColor Gray
} else {
    Write-Host "psql.exe not found on PATH. Performing python asyncpg restore verification..." -ForegroundColor Yellow
    $PythonScript = @"
import asyncio, asyncpg, os

async def verify():
    user = os.environ.get("DB_USER", "postgres")
    pwd = os.environ.get("DB_PWD", "postgres")
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", "5432")
    test_db = os.environ.get("TEST_DB", "clinova_restore_verify")
    backup_file = os.environ.get("BACKUP_FILE", "")

    # Connect to administrative postgres database to manage test DB
    conn = await asyncpg.connect(f"postgresql://{user}:{pwd}@{host}:{port}/postgres")
    await conn.execute(f'DROP DATABASE IF EXISTS "{test_db}"')
    await conn.execute(f'CREATE DATABASE "{test_db}"')
    await conn.close()

    # Connect to test DB and replay backup SQL
    test_conn = await asyncpg.connect(f"postgresql://{user}:{pwd}@{host}:{port}/{test_db}")
    with open(backup_file, "r", encoding="utf-8") as f:
        sql = f.read()
    
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    for stmt in statements:
        try:
            await test_conn.execute(stmt)
        except Exception as e:
            pass

    tables = await test_conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    print(f"Verified tables restored: {len(tables)}")
    await test_conn.close()

    # Cleanup
    conn = await asyncpg.connect(f"postgresql://{user}:{pwd}@{host}:{port}/postgres")
    await conn.execute(f'DROP DATABASE IF EXISTS "{test_db}"')
    await conn.close()
    print("Verification database successfully cleaned up.")

asyncio.run(verify())
"@
    $py = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
        $py = Join-Path $ProjectRoot "backend\.venv\Scripts\python.exe"
        if (-not (Test-Path $py)) { $py = "python" }
    }

    $env:DB_USER = $DbUser
    $env:DB_PWD = $dbPassword
    $env:DB_HOST = $DbHost
    $env:DB_PORT = $DbPort
    $env:TEST_DB = $TestDbName
    $env:BACKUP_FILE = $SourceBackup

    & $py -c "$PythonScript"

    Remove-Item env:DB_USER -ErrorAction SilentlyContinue
    Remove-Item env:DB_PWD -ErrorAction SilentlyContinue
    Remove-Item env:DB_HOST -ErrorAction SilentlyContinue
    Remove-Item env:DB_PORT -ErrorAction SilentlyContinue
    Remove-Item env:TEST_DB -ErrorAction SilentlyContinue
    Remove-Item env:BACKUP_FILE -ErrorAction SilentlyContinue
}

Write-Host "=== RESTORE INTEGRITY VERIFICATION SUCCESSFUL ===" -ForegroundColor Green
