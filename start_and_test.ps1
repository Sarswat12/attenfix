<#
start_and_test.ps1
Automates: docker compose up, waits for DB, runs backend setup, opens frontend, runs register+login tests
Run from PowerShell: .\start_and_test.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Repository path: $repo"
Set-Location $repo

function Invoke-FaceCommand($cmd) {
    # Use an approved verb ('Invoke') to satisfy PSScriptAnalyzer PSUseApprovedVerbs
    Write-Host "=> $cmd"
    cmd.exe /c $cmd
}

Write-Host "1) Bringing up containers (build + up)..."
# Try docker compose, fallback is handled by CLI
& docker compose up -d --build

Write-Host "2) Waiting for MySQL to be ready..."
# Increase attempts for slower environments and be more robust with ping methods
$maxAttempts = 240
$attempt = 0
function Test-MySqlReady {
    param()
    # Try direct mysqladmin first
    try {
        $res = docker compose exec -T db mysqladmin ping -uroot -pexample 2>&1
        if ($res -match "mysqld is alive") { return $true }
    } catch {}

    # Fallback: run via shell inside container (some images require sh -c)
    try {
        $res2 = docker compose exec -T db sh -c "mysqladmin ping -uroot -pexample" 2>&1
        if ($res2 -match "mysqld is alive") { return $true }
    } catch {}

    return $false
}

while ($true) {
    Write-Host "MySQL readiness attempt: $attempt/$maxAttempts"
    try {
        if (Test-MySqlReady) {
            Write-Host "MySQL is alive"
            break
        } else {
            Write-Host "MySQL not ready yet. Showing short status:"
            docker compose ps --services --filter "status=running"
        }
    } catch {
        Write-Verbose "MySQL ping attempt failed, will retry: $($_.Exception.Message)"
    }
    $attempt++
    if ($attempt -ge $maxAttempts) {
        Write-Error "MySQL did not become ready after waiting. Check docker compose logs for db."
        docker compose logs --tail 300 db
        exit 1
    }
    Start-Sleep -Seconds 5
}

Write-Host "3) Running backend setup (creates tables / migrations)..."
try {
    docker compose run --rm backend python run.py
} catch {
    Write-Warning "backend setup failed; continuing to tests. Check logs."
}

Write-Host "4) Starting frontend in a new terminal window..."
$frontendFolder = Join-Path $repo 'frontend'
# Build a command that the new PowerShell will run
$frontendCmd = "Set-Location -LiteralPath '$frontendFolder'; npm ci; npm run dev"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","$frontendCmd"

Start-Sleep -Seconds 4

Write-Host "5) Running authentication smoke tests (register -> login) against http://localhost:5000"
$testEmail = "autotest+$(Get-Random -Minimum 1000 -Maximum 9999)@example.com"
$testPass = "TestPass!123"
$regBody = @{ first_name='Auto'; last_name='Tester'; email=$testEmail; password=$testPass; role='employee' } | ConvertTo-Json

try {
    $regResp = Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/api/auth/register' -Headers @{ 'Content-Type' = 'application/json' } -Body $regBody -TimeoutSec 30
    Write-Host "Register response:`n" ($regResp | ConvertTo-Json -Depth 3)
} catch {
    Write-Warning "Register failed: $($_.Exception.Message)"
    Write-Warning "Backend logs (last 200 lines):" 
    docker compose logs --tail 200 backend
    exit 1
}

try {
    $loginBody = @{ email=$testEmail; password=$testPass } | ConvertTo-Json
    $loginResp = Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/api/auth/login' -Headers @{ 'Content-Type' = 'application/json' } -Body $loginBody -TimeoutSec 30
    Write-Host "Login response:`n" ($loginResp | ConvertTo-Json -Depth 3)
    $token = $loginResp.token
} catch {
    Write-Warning "Login failed: $($_.Exception.Message)"
    docker compose logs --tail 200 backend
    exit 1
}

Write-Host "6) Verifying user present in DB and auth_tokens"
try {
    docker compose exec -T db sh -c "mysql -uroot -pexample face_attendance_db -e \"SELECT id,email,name,role,status,created_at FROM users WHERE email='$testEmail'\""
    docker compose exec -T db sh -c "mysql -uroot -pexample face_attendance_db -e \"SELECT id,user_id,is_revoked,issued_at,expires_at FROM auth_tokens WHERE user_id IS NOT NULL ORDER BY issued_at DESC LIMIT 5\""
} catch {
    Write-Warning "Could not query DB: $($_.Exception.Message)"
}

Write-Host "7) Testing token-protected route (/api/auth/verify-token)"
try {
    $headers = @{ 'Authorization' = "Bearer $token" }
    $verify = Invoke-RestMethod -Method Get -Uri 'http://localhost:5000/api/auth/verify-token' -Headers $headers -TimeoutSec 15
    Write-Host "Verify-token response:`n" ($verify | ConvertTo-Json -Depth 3)
} catch {
    Write-Warning "Verify-token failed: $($_.Exception.Message)"
    docker compose logs --tail 200 backend
}

Write-Host "Automation complete. Frontend started in separate window. Check outputs above for results."