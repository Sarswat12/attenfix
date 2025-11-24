# attempt_dlib_install_with_vs_env.ps1
# Tries to locate CMake and Visual Studio VC environment, sets PATH for the session,
# and runs pip install for dlib using the project's venv python.

$venvPython = 'C:\projects\face\venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error "Venv python not found at $venvPython"
    exit 1
}

Write-Host "Searching for cmake.exe..."
$cmakeCmd = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmakeCmd) {
    Write-Host "Found cmake on PATH: $($cmakeCmd.Path)"
    $cmakeDir = Split-Path $cmakeCmd.Path
} else {
    # search common Program Files location (non-recursive for speed)
    $candidates = @(
        'C:\Program Files\CMake\bin',
        'C:\Program Files (x86)\CMake\bin'
    )
    $cmakeDir = $null
    foreach ($cand in $candidates) {
        if (Test-Path (Join-Path $cand 'cmake.exe')) { $cmakeDir = $cand; break }
    }
    if (-not $cmakeDir) {
        Write-Host "CMake not found in standard locations. Searching Program Files (may take time)..."
        try {
            $found = Get-ChildItem 'C:\Program Files' -Recurse -Filter 'cmake.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) { $cmakeDir = $found.DirectoryName }
        } catch {
            Write-Host "Search failed or access denied when searching C:\Program Files"
        }
    }
}

if ($cmakeDir) {
    Write-Host "Using CMake directory: $cmakeDir"
    $env:Path = "$cmakeDir;$env:Path"
} else {
    Write-Warning "CMake not found. dlib build will likely fail without CMake."
}

Write-Host "Searching for Visual Studio vcvarsall.bat..."
$vcvars = $null
try {
    $vcvars = Get-ChildItem 'C:\Program Files\Microsoft Visual Studio' -Recurse -Filter 'vcvarsall.bat' -ErrorAction SilentlyContinue | Select-Object -First 1
} catch {
    Write-Host "Search for vcvarsall.bat failed or access denied."
}

if ($vcvars) {
    $vcvarsPath = $vcvars.FullName
    Write-Host "Found vcvarsall at: $vcvarsPath"
    Write-Host "Calling vcvarsall and running pip install dlib in the same cmd session..."
        $callCmd = "call `"$vcvarsPath`" amd64 && `"$venvPython`" -m pip install --upgrade pip setuptools wheel && `"$venvPython`" -m pip install dlib"
        Write-Host "Executing in cmd.exe: $callCmd"
        $arguments = @('/c', $callCmd)
        $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList $arguments -NoNewWindow -Wait -PassThru
        exit $proc.ExitCode
} else {
    Write-Warning "vcvarsall.bat not found. Attempting pip install without MSVC environment."
    & $venvPython -m pip install --upgrade pip setuptools wheel
    & $venvPython -m pip install dlib
    exit $LASTEXITCODE
}
