# install_cmake.ps1
# Automates installing CMake on Windows.
# Tries (in order): winget, chocolatey, direct MSI download + msiexec silent install.
# Requires Administrator privileges for system-wide PATH install.

$cmakeVersion = '3.27.8'
$arch = 'windows-x86_64'
$msiName = "cmake-$cmakeVersion-$arch.msi"
$msiUrl = "https://github.com/Kitware/CMake/releases/download/v$cmakeVersion/$msiName"
$msiPath = Join-Path $env:TEMP $msiName

function Install-With-Winget {
    Write-Host "Trying winget to install CMake..."
    try {
        winget install --id Kitware.CMake -e --silent
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Install-With-Choco {
    Write-Host "Trying Chocolatey to install CMake..."
    try {
        choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Install-With-MSI {
    Write-Host "Downloading CMake MSI from $msiUrl to $msiPath"
    try {
        Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Error "Failed to download CMake MSI. Please download manually from https://cmake.org/download/"
        return $false
    }
    Write-Host "Installing CMake MSI silently (adds CMake to system PATH)."
    $msiArgs = "/i `"$msiPath`" /qn ADD_CMAKE_TO_PATH=System"
    $proc = Start-Process -FilePath msiexec.exe -ArgumentList $msiArgs -Wait -Passthru -NoNewWindow
    if ($proc.ExitCode -eq 0) {
        Write-Host "CMake MSI installed successfully."
        return $true
    } else {
        Write-Error "msiexec returned exit code $($proc.ExitCode)."
        return $false
    }
}

# Main
if (Get-Command cmake -ErrorAction SilentlyContinue) {
    Write-Host "CMake is already installed at: $(Get-Command cmake). Skipping installation."
    exit 0
}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    if (Install-With-Winget) { Write-Host "Installed CMake with winget."; exit 0 }
}

if (Get-Command choco -ErrorAction SilentlyContinue) {
    if (Install-With-Choco) { Write-Host "Installed CMake with Chocolatey."; exit 0 }
}

# Fallback to MSI
if (Install-With-MSI) { Write-Host "Installed CMake via MSI."; exit 0 }

Write-Error "CMake installation failed. Please install manually from https://cmake.org/download/ and ensure it's added to PATH."