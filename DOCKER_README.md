# Running the Face Attendance System with Docker (Recommended)

This file explains how to build and run the backend (with dlib compiled in a Linux container) and MySQL using Docker Compose.

Why use Docker?
- Linux build environment reliably compiles `dlib` and other native deps.
- Keeps your local Windows dev environment clean.
- Production-like containerized run with `gunicorn`.

Files added to project:
- `backend/Dockerfile` — builds backend image (installs system deps and compiles dlib).
- `docker-compose.yml` — services: `db` (MySQL) and `backend` (built from Dockerfile).
- `start_docker.ps1` — helper script that checks Docker, runs `docker-compose up --build -d`, and waits for `http://localhost:5000/api/health`.
- `RUN_DOCKER.bat` — Windows wrapper to run `start_docker.ps1`.
- `install_docker.ps1` — helper to download Docker Desktop installer and start it (manual GUI install still required).
 - `entrypoint.sh` (in `backend/`) — runs DB migrations then starts Gunicorn inside the backend container.
 - `docker-compose.prod.yml` — production compose file (db, backend, nginx). Use this to run a production-style stack.
 - `.env.production.example` — example production environment variables.

Quick start (after Docker Desktop installed)

1. Open PowerShell in project root.
2. Run:

```powershell
.\RUN_DOCKER.bat   # uses docker-compose.yml (dev) which builds backend image

# For production compose (nginx + built frontend), run:
docker-compose -f docker-compose.prod.yml up --build -d
```

This runs `docker-compose up --build -d` and waits for the backend health check.

Manual compose commands

```powershell
# Build and start in background
docker-compose up --build -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Common issues & fixes
- "docker: command not found" → install Docker Desktop: https://www.docker.com/get-started
- dlib build errors in container → check `docker-compose logs backend` and share logs; Linux builds usually succeed if apt packages present
- DB connection errors → ensure `DB_HOST` in `.env` or `docker-compose.yml` matches the service name `db`

If you want, I can walk you through the first run and troubleshoot any errors you see in the container logs.
