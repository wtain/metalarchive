# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Telegram channel analytics tool. It scrapes a Telegram channel (posts, views, reactions, comments, subscribers) via Telethon, stores time-series snapshots in Postgres/TimescaleDB, runs AI post-tagging/title extraction, and exposes a FastAPI backend + React dashboard for viewing metrics and daily digests.

The **active application** is: `backend.py` (FastAPI entrypoint) + `api/` + `storage_client/` + `synchronizer/` + `telegram/` + `aitools/` + `database_saver/` + `frontend/`. Root-level scripts like `TelegramBot.py`, `MetalArchivesApi.py`, `StatisticsBot.py`, `DiscographyExample.py`, `WalkGraphExample.py`, `download_metal_archive.py`, `migration_example.py`, `instagram_check.py`, `channel_stats.py` are older exploratory/one-off scripts (last touched Sep 2025) predating the FastAPI app and are not part of the running system — don't build on them without checking with the user first.

## Commands

Backend (run from repo root):
```bash
# local run without docker (loads .env, writes logs to current dir)
LOG_PATH=. uvicorn backend:app --reload --port 8002 --env-file .env

# via Makefile (docker build + run, joins existing storage_appnet)
make run

# full stack: db + backend + frontend + prometheus + grafana
make run-all   # docker-compose --env-file .env-docker up --build

# regenerate requirements.txt after installing new deps
make freeze
```

Frontend (run from `frontend/`):
```bash
npm install
npm run dev       # vite dev server
npm run build
npm run preview
```

Database / migrations (alembic reads `DATABASE_URL` from `.env`):
```bash
alembic upgrade head
alembic revision --autogenerate -m "message"
```

Storage container (Postgres/TimescaleDB, from `Storage/`):
```bash
docker-compose up -d      # starts the db container
make dump                 # ./dump_database.sh
make restore DUMP_FILE_NAME=<file>
```

Manually trigger a Telegram scrape / batch update once the backend is running:
```bash
curl -X POST http://127.0.0.1:8001/api/updater/update
curl -X POST http://127.0.0.1:8001/api/updater/update_tags
curl -X POST http://127.0.0.1:8001/api/updater/update_titles
curl http://127.0.0.1:8001/metrics   # Prometheus metrics
```

There is no test suite in this repo yet (see `docs/plans.txt` "Technical debt" — tests are a known gap). There is no linter configured for either backend or frontend.

## Architecture

**Data flow (one "batch run"):**
1. `POST /api/updater/update` (`api/updater.py`) kicks off `synchronizer/poller.py::poll_from_telegram`, or the FastAPI `lifespan` background scheduler (`APScheduler`, every 15 min in `backend.py`) does it automatically.
2. `telegram/TelegramSession.py` decrypts the Telethon session file (Fernet, key from `ENCRYPTION_KEY`) from `/var/lib/telegram/stats_session.session.enc` into a temp file, used for the duration of the poll, then deletes it.
3. `telegram/telegram_client.py::TelegramTelethonClient` wraps Telethon to list channel messages, participants, and comment counts/threads (via raw `GetRepliesRequest`).
4. `storage_client/DatabaseSession.py` opens a `BatchRun` row (one per poll) and hands out `PostsStatsDatabaseSaver` / `SubscribersDatabaseSaver` (`database_saver/`) which buffer rows and flush them to Postgres on `__exit__`.
5. On new posts, `database_saver/posts.py` also runs AI extraction inline: `aitools/tags.py` (KeyBERT + multilingual sentence-transformer) and `aitools/title.py` (`cointegrated/rut5-base-multitask` seq2seq model, Russian headline generation) — these load ML models lazily on first use and are slow on cold start.

**Storage layer (`storage_client/`):**
- `models.py` — SQLAlchemy ORM models: `BatchRun` (one per scrape), `Post`/`PostHeader`/`PostTags` (content + AI-derived title/tags), `PostMetric` (per-batch views/reactions/comments time series, FK to both `Post` and `BatchRun`), `Subscriber` (per-batch subscriber snapshot, FK to `BatchRun`).
- `db_sync.py` / `db_async.py` — two separate engines/sessionmakers, from `SYNC_DATABASE_URL` and `DATABASE_URL` respectively. Most of the app (FastAPI routes, `database_saver`) uses the **sync** engine; async is set up for alembic migrations. Don't assume they point at the same driver string.
- `db/session.py` — the FastAPI `Depends(get_db)` dependency, built on the sync `SessionLocal`.
- Metrics are stored as **per-batch snapshots**, not deltas — "diffs" (daily/weekly/monthly digest, new/removed subscribers) are computed on read by joining a post/subscriber against two different `BatchRun` ids (see `daily_digest.py` and `api/reports.py`). `BatchRun.id` ordering is treated as chronological.

**API (`api/`)**, all mounted under `/api/<name>` in `backend.py`:
- `updater.py` — triggers scrape (`/update`) and re-runs AI tagging/titling over all stored post text (`/update_tags`, `/update_titles`).
- `posts.py` — single-post text/tags/header/metrics lookups.
- `reports.py` — `/digest` (diff between two batch runs, period-based) and `/top` (top posts by views in the latest batch).
- `tags.py` — manual add/delete of a post tag.
- `subscribers.py` — subscriber count over time, bucketed by period.

Routes generally take a raw `Session` and hand-build SQLAlchemy queries (aliased joins, `func.coalesce` for diffing) rather than going through a repository layer — expect to write SQL-shaped queries directly in route handlers, and expect DB rows/DTOs to be loosely typed (`api/posts.py::convert_data_to_json` reflects column names off the query itself).

**Frontend (`frontend/`)**: Vite + React + TypeScript + Tailwind + shadcn/ui + recharts, React Router. `SMMetricsClient` (`src/client/SMMetricsClient.tsx`) is the single hand-written API client wrapping axios calls to the backend routes above — add new backend endpoints there and to `src/dto/BackendDataTypes.ts` when wiring up new UI data. Pages live in `src/pages/` (Reactions, Top Posts, Subscribers, Post List/Details); `public/config.json` supplies runtime config (e.g. backend base URL) separate from build-time env.

**Config / secrets**: All config comes from env vars via `python-dotenv` (`environment/secrets.py` for Telegram/encryption secrets; `.env` for local runs, `.env-docker` for docker-compose). `CHANNEL_NAME` is currently a single hardcoded channel — multi-channel/multi-tenant support is not implemented (see `docs/plans.txt`). The Telegram session file must be encrypted at rest; `encryption_script.py` is the helper for producing `secrets/stats_session.session.enc` from a plaintext session.

**Observability**: `logging_config.py` defines the shared logging config (used by both uvicorn/gunicorn and `logging.config.dictConfig` in `backend.py`); most modules log to the `uvicorn.info` logger for that reason. `metrics/middleware.py` is a Starlette middleware exporting Prometheus counters/histograms (`http_requests_total`, `http_response_time`) scraped by the `prometheus` docker-compose service and visualized in `grafana`.

**Migrations**: Alembic (`alembic/`) targets `storage_client.models.Base.metadata` and reads `DATABASE_URL` (async engine, `alembic/env.py`) — note this differs from the sync engine most of the app uses. Only one baseline migration exists so far (`617d84857b66_baseline.py`); schema is otherwise young and still shifting (see `docs/plans.txt` "Data management").

## Known rough edges (see `docs/plans.txt` for the full running list)

- No tests, no linter, in either backend or frontend.
- Two DB engines/URLs (`DATABASE_URL` vs `SYNC_DATABASE_URL`) must be kept in sync manually when changing connection settings.
- Concurrency: the 15-min scheduled update and a manually-triggered `/api/updater/update` can race; there's no lock around batch runs.
- DTOs are not unified between backend (loosely-typed dict/tuple conversions) and frontend (`BackendDataTypes.ts`) — check both sides when changing a response shape.