# run_all.ps1 - build & start db+backend, run migrations, and remind to start frontend
Set-Location -Path "C:\projects\face"

Write-Host "1) Bringing up database and backend with docker compose..."
# Try docker compose, fall back to docker-compose
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "Running: docker compose up -d --build"
    docker compose up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "docker compose returned non-zero exit code. Trying docker-compose..."
        docker-compose up -d --build
    }
} else {
    Write-Error "docker CLI not found. Start Docker Desktop and re-open PowerShell.";
    exit 1
}

Write-Host "Waiting 20 seconds for MySQL to initialise..."
Start-Sleep -Seconds 20

Write-Host "2) Running backend setup to create tables (one-off)..."
# Use try/catch to show helpful output
try {
    docker compose run --rm backend python run.py
} catch {
    Write-Warning "Failed to run python run.py inside backend container. Trying alembic upgrade head..."
    try {
        docker compose run --rm backend alembic upgrade head
    } catch {
        Write-Error "Both run.py and alembic upgrade failed. Check backend logs: docker compose logs backend --tail 200"
        exit 1
    }
}

Write-Host "All done. Tail backend logs to watch startup:"
Write-Host "  docker compose logs -f backend"
Write-Host "Start the frontend in a NEW terminal:";
Write-Host "  cd C:\projects\face\frontend";
Write-Host "  npm ci";
Write-Host "  npm run dev";
Write-Host "Frontend will be available at http://localhost:5173 (open in browser)";

Write-Host "To stop everything: docker compose down";
Write-Host "To remove volumes (delete DB data): docker compose down -v";
