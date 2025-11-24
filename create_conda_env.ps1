# create_conda_env.ps1
# Usage: run this in an elevated PowerShell or normal PowerShell if conda is available.
# It creates a conda environment from `environment.yml` and activates it.

$envFile = Join-Path $PSScriptRoot 'environment.yml'
if (-not (Test-Path $envFile)) {
    Write-Error "environment.yml not found in $PSScriptRoot"
    exit 1
}

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "conda not found on PATH. Install Anaconda or Miniconda first: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
}

Write-Host "Creating conda environment from $envFile (may take several minutes)"
conda env create -f $envFile

Write-Host "To activate the environment run:`n    conda activate face-attendance"
Write-Host "Then verify dlib import:`n    python -c "import dlib; print(dlib.__version__)""
