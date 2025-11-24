# install_docker.ps1
# Downloads Docker Desktop installer and launches it for manual install.
# NOTE: The installer requires user interaction (GUI) and admin privileges.

$installerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$downloadPath = Join-Path $env:TEMP "DockerDesktopInstaller.exe"

Write-Host "This script will download Docker Desktop installer to:`n$downloadPath`nYou must run the installer manually and follow the GUI prompts."

# Check admin elevation
function Test-Admin {
    $cur = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($cur)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "This script requires Administrator privileges. Please run PowerShell as Administrator and re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Downloading Docker Desktop installer..."
try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $downloadPath -UseBasicParsing -TimeoutSec 600
    Write-Host "Downloaded to $downloadPath"
    Write-Host "Launching installer (you will need to follow GUI prompts)."
    Start-Process -FilePath $downloadPath -Wait
    Write-Host "Installer finished. Restart recommended."
} catch {
    Write-Host "Download or launch failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "If Docker Desktop runs the first time, enable WSL2 backend for best performance and reboot if prompted."