# CLINOVA AI - Automated PostgreSQL Backup Script
# Generates a timestamped, SHA-256 checksummed database dump.

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
$DefaultBackupDir = Join-Path $ProjectRoot "backups"

param (
    [string]$DbName = "clinova",
    [string]$DbUser = "postgres",
    [string]$DbHost = "127.0.0.1",
    [string]$DbPort = "5432",
    [string]$BackupDir = $DefaultBackupDir
)

$ErrorActionPreference = "Stop"

Write-Host "=== CLINOVA AI Database Backup Initiated ===" -ForegroundColor Cyan
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFolder = [System.IO.Path]::GetFullPath($BackupDir)

if (-not (Test-Path -Path $BackupFolder)) {
    New-Item -ItemType Directory -Path $BackupFolder -Force | Out-Null
    Write-Host "Created backup directory: $BackupFolder" -ForegroundColor Green
}

$BackupFile = Join-Path -Path $BackupFolder -ChildPath "${DbName}_backup_${Timestamp}.sql"
$ChecksumFile = Join-Path -Path $BackupFolder -ChildPath "${DbName}_backup_${Timestamp}.sha256"

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

# Look for pg_dump executable in PATH or standard PostgreSQL directories
$PgDumpPath = ""
$PgDumpCmd = Get-Command "pg_dump" -ErrorAction SilentlyContinue
if ($PgDumpCmd) {
    $PgDumpPath = $PgDumpCmd.Source
} else {
    $commonPgPaths = @(
        "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        "C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"
    )
    foreach ($candidate in $commonPgPaths) {
        if (Test-Path $candidate) {
            $PgDumpPath = $candidate
            break
        }
    }
}

if ($PgDumpPath -and (Test-Path $PgDumpPath)) {
    Write-Host "Executing pg_dump via $PgDumpPath..." -ForegroundColor Yellow
    $env:PGPASSWORD = $dbPassword
    & "$PgDumpPath" -h $DbHost -p $DbPort -U $DbUser -d $DbName -F p -f "$BackupFile"
} else {
    Write-Host "Using Python SQL dump fallback..." -ForegroundColor Yellow
    $PythonScript = @"
import asyncio, asyncpg, json, os

async def dump():
    user = os.environ.get("DB_USER", "postgres")
    pwd = os.environ.get("DB_PWD", "postgres")
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "clinova")
    backup_file = os.environ.get("BACKUP_FILE", "backup.sql")

    conn = await asyncpg.connect(f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}")
    tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(f"-- CLINOVA AI Native Backup\n")
        f.write(f"-- Source: {dbname} on {host}:{port}\n\n")
        for r in tables:
            t = r['table_name']
            cols = await conn.fetch(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position")
            col_names = [c['column_name'] for c in cols]
            rows = await conn.fetch(f'SELECT * FROM "{t}"')
            f.write(f"-- Table: {t} ({len(rows)} rows)\n")
            for row in rows:
                vals = []
                for c in col_names:
                    v = row[c]
                    if v is None:
                        vals.append("NULL")
                    elif isinstance(v, (int, float)):
                        vals.append(str(v))
                    elif isinstance(v, bool):
                        vals.append("TRUE" if v else "FALSE")
                    elif isinstance(v, (dict, list)):
                        safe = json.dumps(v).replace("'", "''")
                        vals.append(f"'{safe}'")
                    else:
                        safe = str(v).replace("'", "''")
                        vals.append(f"'{safe}'")
                col_list = ', '.join([f'"{c}"' for c in col_names])
                val_list = ', '.join(vals)
                f.write(f'INSERT INTO "{t}" ({col_list}) VALUES ({val_list});\n')
            f.write("\n")
    await conn.close()
    print(f"Dump complete: {len(tables)} tables processed")

asyncio.run(dump())
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
    $env:DB_NAME = $DbName
    $env:BACKUP_FILE = $BackupFile

    & $py -c "$PythonScript"

    Remove-Item env:DB_USER -ErrorAction SilentlyContinue
    Remove-Item env:DB_PWD -ErrorAction SilentlyContinue
    Remove-Item env:DB_HOST -ErrorAction SilentlyContinue
    Remove-Item env:DB_PORT -ErrorAction SilentlyContinue
    Remove-Item env:DB_NAME -ErrorAction SilentlyContinue
    Remove-Item env:BACKUP_FILE -ErrorAction SilentlyContinue
}

if (Test-Path $BackupFile) {
    $Hash = (Get-FileHash -Path $BackupFile -Algorithm SHA256).Hash
    "$Hash *$([System.IO.Path]::GetFileName($BackupFile))" | Out-File -FilePath $ChecksumFile -Encoding utf8
    $Size = (Get-Item $BackupFile).Length / 1KB

    Write-Host "Backup created successfully!" -ForegroundColor Green
    Write-Host "File: $BackupFile ($([math]::Round($Size, 2)) KB)"
    Write-Host "SHA-256: $Hash"
} else {
    Write-Error "Backup file creation failed!"
}
