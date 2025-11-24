# start_docker.ps1
# Checks Docker availability, builds images, starts services, and waits for health endpoint.

param(
    [int]$HealthPort = 5000,
    [int]$WaitSeconds = 120
)

function Test-Docker {
    try {
        if (Get-Command docker -ErrorAction SilentlyContinue) { return $true }
        return $false
    } catch {
        return $false
    }
}

Write-Host "Checking Docker availability..."
if (-not (Test-Docker)) {
    Write-Host "Docker CLI not found. Please install Docker Desktop for Windows and enable WSL2 or use Windows containers."
    Write-Host "Download: https://www.docker.com/get-started"
    exit 1
}

Write-Host "Docker available. Building and starting containers (this may take several minutes)..."
Push-Location $PSScriptRoot
try {
    docker-compose up --build -d --remove-orphans
} catch {
    Write-Host "docker-compose up failed:" $_
    Pop-Location
    exit 1
}

Write-Host "Waiting for backend health endpoint http://localhost:$HealthPort/api/health to become available..."
$deadline = (Get-Date).AddSeconds($WaitSeconds)
while ((Get-Date) -lt $deadline) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$HealthPort/api/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Host "Backend is healthy."
            Pop-Location
            exit 0
        }
    } catch {
        Write-Host -NoNewline "."
    }
    Start-Sleep -Seconds 2
}

Write-Host "\nTimed out waiting for backend health endpoint. Check container logs with: docker-compose logs backend"
Pop-Location
exit 2
