# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Cinema listings app: Python scrapers → PostgreSQL → FastAPI backend → Next.js frontend, with email alerts for subscribed movies. See README.md for full setup.

## Commands

```bash
docker compose up --build -d                                 # start postgres + backend + scheduler
docker compose run --rm backend python -m jobs.scrape_all    # scrape now
ruff check src/backend/src                                   # lint backend

cd src/frontend/cinema && npm run dev                         # frontend (localhost:3000, needs backend on :8000)
```

No test suite exists yet.

## Architecture

- `src/backend/src/api/` — FastAPI routes + Pydantic schemas
- `src/backend/src/db/` — SQLAlchemy models (`db/models/`) and DB access (`db/repo/`)
- `src/backend/src/data_sources/scrapers/` — one module per venue, each exposing `VENUE_NAME` and `scrape() -> list[ListingDC]`
- `src/backend/src/data_sources/sync.py` — upserts scraped listings, dedupes via hashed `listing_id`
- `src/backend/src/data_sources/notify.py` — emails subscribers about new matching listings
- `src/backend/src/jobs/scrape_all.py` — cron entrypoint that ties scrape → sync → notify together
- `src/frontend/cinema/` — Next.js app; `lib/api.ts` is the backend client

New venue = new module in `data_sources/scrapers/`, registered in `SCRAPERS` in `jobs/scrape_all.py`.
