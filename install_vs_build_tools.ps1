# install_vs_build_tools.ps1
# Downloads and launches Visual Studio Build Tools installer to install C++ build tools (VC++), and installs CMake.
# Run PowerShell as Administrator to perform silent install.

$vsUrl = 'https://aka.ms/vs/17/release/vs_BuildTools.exe'
$vsInstaller = "$env:TEMP\vs_BuildTools.exe"

Write-Host "Downloading Visual Studio Build Tools installer to $vsInstaller"
Invoke-WebRequest -Uri $vsUrl -OutFile $vsInstaller -UseBasicParsing

Write-Host "Starting Visual Studio Build Tools installer (silent). This may take a long time..."
Start-Process -FilePath $vsInstaller -ArgumentList '--add', 'Microsoft.VisualStudio.Workload.VCTools', '--add', 'Microsoft.VisualStudio.Component.VC.14.29.x86.x64', '--includeRecommended', '--quiet', '--wait', '--norestart' -Wait -NoNewWindow

# Install CMake (Windows) if not present
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    Write-Host "CMake not found. Installing CMake via choco if available, otherwise provide manual instructions."
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install cmake --installargs 'ADD_CMAKE_TO_PATH=System' -y
    } else {
        Write-Host "Chocolatey not found. Download the CMake installer and run it manually from https://cmake.org/download/"
        Write-Host "Or install CMake from the Visual Studio Installer (Individual components -> CMake tools for Windows)."
    }
}

Write-Host "Visual Studio Build Tools + CMake step finished. Reboot may be required for PATH updates."
