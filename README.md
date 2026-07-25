# Cinema App

A cinema listings app that scrapes showtimes, stores them in PostgreSQL, and serves them via a FastAPI backend with a Next.js frontend. Includes email alerts when subscribed movies are scheduled.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Node.js](https://nodejs.org/) 20+ (for the frontend)
- Python 3.9+ (optional, for local backend development)

## Quick start

### 1. Configure environment

Copy the example env file and adjust if needed:

```bash
cp .env.example .env
```

Default values work for local development:

| Variable | Default |
|----------|---------|
| `POSTGRES_USER` | `user` |
| `POSTGRES_PASSWORD` | `password` |
| `POSTGRES_DB` | `cinema` |
| `DATABASE_URL` | `postgresql://user:password@postgres:5432/cinema` |
| `PUBLIC_API_URL` | `http://localhost:8000` |

Email alerts log to the console unless you set `RESEND_API_KEY` or `SMTP_*` variables (see `.env.example`).

### 2. Build and start backend services

From the repo root:

```bash
docker compose up --build -d
```

This starts three services:

| Service | Port | Description |
|---------|------|-------------|
| **postgres** | 5432 | PostgreSQL database |
| **backend** | 8000 | FastAPI API |
| **scheduler** | — | Cron job (scrapes at 06:00 and 18:00 Dublin time) |

The backend creates database tables automatically on startup.

Verify the API is running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. Run the UI

The UI is a **Next.js app** in `src/frontend/cinema`. It runs **locally on your machine** — it is not part of Docker Compose.

**Start the backend first.** The UI fetches listings from the API on port 8000. If the backend is not running, the page will load but search/listings will fail.

```bash
# from repo root — backend + postgres only is enough for the UI
docker compose up -d postgres backend

# verify the API is up
curl http://localhost:8000/health
```

**Development:**

```bash
cd src/frontend/cinema
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Optionally point the UI at a different API URL by creating `.env.local`:

```bash
cp .env.example .env.local
```

Default is `NEXT_PUBLIC_API_URL=http://localhost:8000`, so this is only needed if your backend runs elsewhere.

If you change frontend code and the dev server was already running, restart it (`Ctrl+C`, then `npm run dev` again).

**Production build:**

```bash
cd src/frontend/cinema
npm run build
npm start
```

Serves on port **3000** by default.

### 4. Populate listings (first run)

The scheduler runs automatically twice daily. To scrape immediately:

```bash
docker compose run --rm backend python -m jobs.scrape_all
```

Rebuild the backend image first if you changed scraper code:

```bash
docker compose build backend
docker compose run --rm backend python -m jobs.scrape_all
```

## Project structure

```
cinema-app/
├── docker-compose.yml          # Postgres, backend, scheduler
├── requirements.txt            # Python deps (used by Dockerfile)
├── pyproject.toml              # Python project config
├── .env.example
├── src/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── crontab             # Scrape schedule
│   │   └── src/
│   │       ├── api/            # FastAPI routes
│   │       ├── db/             # SQLAlchemy models + repo
│   │       ├── data_sources/   # Scrapers, sync, notifications
│   │       ├── jobs/           # scrape_all entrypoint
│   │       └── common/         # Email, config, utilities
│   └── frontend/
│       └── cinema/             # Next.js app
```

## Local backend development (without Docker)

Useful for iterating on Python code with your IDE:

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Start Postgres via Docker, then run the API against it:

```bash
docker compose up -d postgres
export DATABASE_URL=postgresql://user:password@localhost:5432/cinema
export PYTHONPATH=src/backend/src
python -m db.repo.run          # create tables
uvicorn api.main:app --reload --app-dir src/backend/src
```

Run the scraper locally:

```bash
PYTHONPATH=src/backend/src python -m jobs.scrape_all
```

## Useful commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f scheduler

# Restart a service
docker compose restart backend

# Stop everything
docker compose down

# Stop and remove database volume (wipes data)
docker compose down -v

# Lint backend
ruff check src/backend/src

# Build frontend for production
cd src/frontend/cinema && npm run build && npm start
```

## Connecting to the database

Use any PostgreSQL client (e.g. pgAdmin) with:

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `5432` |
| Database | `cinema` |
| Username | `user` |
| Password | `password` |

Use credentials from your `.env` if you changed the defaults.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/listings/` | All cinema listings |
| POST | `/subscriptions/` | Subscribe to movie alerts |
| GET | `/subscriptions/confirm?token=…` | Confirm subscription (email link) |
| GET | `/subscriptions/unsubscribe?token=…` | Unsubscribe (email link) |

## Production notes

- Set `PUBLIC_API_URL` to your deployed backend URL so confirmation/unsubscribe links in emails work.
- Configure `RESEND_API_KEY` or SMTP settings for real email delivery.
- The scheduler container uses `TZ=Europe/Dublin`; scrape times follow Dublin local time.
- Rebuild images after code changes: `docker compose up --build -d`.
