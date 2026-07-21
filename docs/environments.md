# Running the application: production vs. local dev

There are two ways to run this app. Pick based on what you're doing:

- **Full stack (docker-compose)** — closest to production, everything containerized. Every backend/frontend code change requires an image rebuild. Use this to test the whole thing end-to-end (nginx, gunicorn, Prometheus/Grafana wiring) before a deploy.
- **Local dev (hot reload)** — only the database (and optionally Prometheus/Grafana) run in Docker; the backend runs as `uvicorn --reload` and the frontend as the Vite dev server, both natively on the host. Use this for day-to-day development — no rebuild/restart needed between edits.

Both modes read secrets/config from env files at the repo root — see [Env files](#env-files) below for which one to use where.

## Full stack (docker-compose)

```bash
make run-all
# same as: docker-compose --env-file .env-docker up --build
```

Starts, on the `appnet`/`monitoring` docker networks:
- `db` — TimescaleDB (Postgres 15), published on `5432`
- `backend` — built from the root `Dockerfile`, runs `gunicorn -k uvicorn.workers.UvicornWorker backend:app`, published on `8001`
- `frontend` — built from `frontend/Dockerfile` (Vite build → static assets served by nginx), published on `80`
- `prometheus` — `9090`
- `grafana` — `3000` (default admin/admin, see README for password reset)

Because `backend` and `frontend` are baked images (`COPY` in the Dockerfile, no source volume mounts), any code change requires `docker-compose up --build` again. That rebuild is what local dev mode avoids.

There's also `make run`, which builds and runs **only** the backend container standalone, joining a pre-existing `storage_appnet` network (i.e. assumes the `Storage/` compose stack is already running separately). This is a legacy single-container path, not the normal way to run the full app locally.

## Local dev (hot reload)

**1. Start the database** (and optionally Prometheus/Grafana) via docker-compose, without touching backend/frontend:

```bash
docker-compose --env-file .env-docker up -d db
# or, if you also want dashboards/metrics locally:
docker-compose --env-file .env-docker up -d db prometheus grafana
```

**2. Run the backend with auto-reload**, natively (not in Docker):

```bash
LOG_PATH=. uvicorn backend:app --reload --port 8001 --env-file .env
```

This uses `.env`, not `.env-docker` — `.env` has `DB_HOST=localhost` (talking to the `db` container's port published on the host) and also carries `DATABASE_URL` (needed by Alembic's async engine) plus the Instagram vars that `.env-docker` omits. Port `8001` matters: the frontend's API client is hardcoded to `http://127.0.0.1:8001` (see below), so don't move the backend to a different port without also changing that.

Note the in-process `APScheduler` job (channel poll every 15 minutes, see `backend.py`) still runs under `--reload`; each auto-reload restarts it.

**3. Run the frontend dev server**, from `frontend/`:

```bash
npm install   # first time only
npm run dev
```

Vite serves on `http://localhost:5173` with HMR. `.env`'s `CORS_ALLOW_ORIGINS` already includes `http://localhost:5173`, so no CORS changes are needed. The frontend talks to the backend at the hardcoded `http://127.0.0.1:8001` (`frontend/src/main.tsx`) — `frontend/public/config.json`'s `apiBaseUrl` is not currently wired into the app, so editing it has no effect (tracked as a known gap; see `docs/plans.txt` "hardcoded hosts").

**4. Migrations**, when the schema changes, run against `.env` (native, not `.env-docker` — the latter has no `DATABASE_URL`):

```bash
alembic upgrade head
alembic revision --autogenerate -m "message"
```

## Env files

| File | `DB_HOST` | Used by |
|---|---|---|
| `.env` | `localhost` | Native `uvicorn --reload` runs, Alembic (needs its `DATABASE_URL`) |
| `.env-docker` | `db` | `docker-compose` full-stack backend container |

Both are git-ignored; ask a teammate or check your secrets manager for real values.