Production checklist for Face Attendance

1. Secrets & Environment
   - Copy `.env.production.example` to `.env` (or set env vars in your deployment system).
   - Ensure `SECRET_KEY`, `JWT_SECRET_KEY`, and DB credentials are secure.

2. Build Frontend
   - On your machine: `cd frontend && npm ci && npm run build`
   - This creates `frontend/dist` which will be served by nginx in `docker-compose.prod.yml`.

3. Start Production Stack (Docker)
   - `docker-compose -f docker-compose.prod.yml up --build -d`
   - Wait until `http://<host>/api/health` returns healthy.

4. Database Migrations
   - The backend container runs `flask db upgrade` in `entrypoint.sh` if migrations are present. Make sure `migrations/` is included.
   - Alternatively run migrations manually:
     `docker-compose exec backend flask db upgrade`

5. SSL
   - Obtain TLS certs for your domain and mount them into nginx, or use a load balancer with TLS termination.
   - For Let's Encrypt, consider using a companion container (certbot / nginx-proxy) or run certbot on host.

6. Logging & Monitoring
   - Configure persistent logs (bind-mount `logs/` into backend container) or ship logs to centralized service.
   - Add health checks, alerting, and metrics (Prometheus/Grafana) as needed.

7. Backups
   - Schedule regular DB backups of MySQL volume `db_data` to external storage.

8. Scaling
   - For production scale, run backend behind a proper process manager / uWSGI/gunicorn and use multiple replicas behind a load balancer.

9. CI/CD
   - Build and test images in CI, push to registry, and deploy via docker-compose or container orchestrator.

10. Security
   - Rotate secrets, run vulnerability scans, keep dependencies updated.

