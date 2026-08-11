# Epicenter API

Backend for the Epicenter disaster atlas. Disaster records live in **PostgreSQL**
instead of being hardcoded in the frontend, served over a **FastAPI** REST API,
with **JWT auth**, **analytics endpoints**, an **ETL importer**, a **scheduled
background job**, and an **optional Claude-powered summarizer**.

This has been built and tested end-to-end (Postgres → ETL → API → auth → CRUD
→ analytics) — see "What's actually been tested" below for exactly what was run.

## Architecture

```
epicenter-backend/
  app/
    main.py            FastAPI app, CORS, lifespan (DB init + scheduler)
    config.py           Settings, loaded from environment / .env
    database.py          SQLAlchemy engine/session
    models.py            Category, Disaster, User tables
    schemas.py            Pydantic request/response models
    security.py            Password hashing (bcrypt) + JWT
    dependencies.py         get_current_user / require_admin
    routers/
      auth.py                 /auth/register, /auth/login, /auth/me
      disasters.py             /api/disasters CRUD + filtering + search
      analytics.py              /api/analytics/* aggregate stats
      llm.py                     /api/disasters/{id}/summarize (optional)
    services/
      llm_summary.py               Claude API call for summarization
  etl/
    import_disasters.py    Idempotent upsert of categories + disasters
    parse_casualties.py     Best-effort death-toll range extraction
    usgs_feed.py              Optional live USGS earthquake feed puller
    scheduler.py                APScheduler background job runner
    cats_raw.json, disasters_raw.json   Seed data (117 curated disasters)
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
```

## Quick start (Docker)

```bash
cp .env.example .env        # fill in JWT_SECRET, optionally ANTHROPIC_API_KEY
docker compose up --build
```

This starts Postgres, runs the ETL seed job once, and boots the API on
`http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

## Quick start (local, no Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Point at a running Postgres instance
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/epicenter"
export JWT_SECRET="something-long-and-random"

# Load the seed data
python -m etl.import_disasters

# Run the API (also starts the scheduler)
uvicorn app.main:app --reload
```

## REST endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Liveness check |
| POST | `/auth/register` | — | Create a user (first user becomes admin) |
| POST | `/auth/login` | — | Returns a JWT (`OAuth2PasswordRequestForm`: `username`=email) |
| GET | `/auth/me` | ✅ | Current user |
| GET | `/api/categories` | — | All 20 disaster categories |
| GET | `/api/disasters` | — | List/filter/search: `?category=`, `?year_min=`, `?year_max=`, `?q=`, `?limit=`, `?offset=`, `?sort=` |
| GET | `/api/disasters/{id}` | — | Single record |
| POST | `/api/disasters` | ✅ | Create |
| PATCH | `/api/disasters/{id}` | ✅ | Partial update |
| DELETE | `/api/disasters/{id}` | ✅ | Delete |
| GET | `/api/analytics/summary` | — | Totals, by-category, by-decade, top-10 deadliest, all in one call |
| GET | `/api/analytics/by-category` | — | Count per category |
| GET | `/api/analytics/by-decade` | — | Count per decade bucket |
| GET | `/api/analytics/deadliest` | — | Top N by estimated death toll (`?limit=`) |
| POST | `/api/disasters/{id}/summarize` | ✅ | Calls Claude to (re)generate a summary; 501 if `ANTHROPIC_API_KEY` isn't set |

Any list/detail GET works unauthenticated (read-only public API); writes
require a bearer token from `/auth/login`.

## ETL & scheduled updates

`etl/import_disasters.py` is idempotent — it upserts by `id`, so re-running it
(manually or via the scheduler) picks up edits to the seed file without
duplicating records.

```bash
python -m etl.import_disasters                # curated seed data only
python -m etl.import_disasters --usgs          # also pulls live USGS earthquakes
python -m etl.import_disasters --file other.json
```

The API process starts a background `APScheduler` job (`etl/scheduler.py`)
that re-runs the ETL (curated + USGS) every `ETL_SCHEDULE_HOURS` (default 24).
For a heavier production setup, run `python -m etl.scheduler` as its own
worker/cron job instead of in-process.

**Note on the USGS feed:** `etl/usgs_feed.py` pulls
`earthquake.usgs.gov/.../significant_month.geojson` and maps it into the same
record shape as the curated data. This wasn't reachable from this sandbox's
restricted network, so it's implemented and unit-testable but **not
live-verified from here** — it fails soft (logs and returns `[]`) if the feed
is unreachable, so a blocked network won't break the rest of the ETL run.

## Optional LLM summarization

Set `ANTHROPIC_API_KEY` (and optionally `ANTHROPIC_MODEL`) and call
`POST /api/disasters/{id}/summarize` to have Claude generate a fresh
2-3 sentence summary from the record's structured fields, stored in
`llm_summary`. Without a key configured, the endpoint returns `501` instead
of failing — verified in this sandbox.

## Casualty-range parsing

Death tolls in the source data are free text ("~230,000", "55,000-60,000+",
"1-4 million"). `etl/parse_casualties.py` extracts a best-effort
`(min, max)` integer range **only from stats whose label mentions deaths/
lives lost** (not magnitude, VEI, or other numeric stats — an earlier version
of this script mistakenly parsed "9.5 Mw" as a casualty count and caused a
Postgres integer overflow; both bugs are fixed and re-tested). Records with no
parseable number (e.g. "Low (remote region)") get `NULL`, which analytics
queries correctly exclude rather than treating as zero.

## What's actually been tested

Everything below was run against a live PostgreSQL 16 + FastAPI stack in the
build sandbox, not just written and assumed correct:

- ETL import of all 117 disasters + 20 categories, idempotent re-run
- Casualty parser against real records (fixed two real bugs: magnitude
  numbers being misread as deaths; a `passlib`/`bcrypt` version
  incompatibility that broke every password hash)
- `GET /api/categories`, filtered/search `GET /api/disasters`
- `POST /auth/register` → `POST /auth/login` → `GET /auth/me`
- Full disaster CRUD lifecycle (create → patch → delete → 404 confirms gone),
  with 401s confirmed for unauthenticated writes
- `analytics/by-category`, `analytics/deadliest`, `analytics/summary`
- `analytics/by-decade` — caught and fixed a real bug where SQLAlchemy
  silently promoted `(year / 10) * 10` to real-number division, which
  mathematically cancels out and returns the original year; fixed with
  integer-safe subtraction/modulo and re-verified
- `POST /api/disasters/{id}/summarize` correctly 501s with no API key set

**Not tested here** (documented instead): the live USGS feed pull (network
restricted in this sandbox), and the LLM summarizer actually calling the
Claude API (no key available in this environment) — both are implemented and
fail gracefully if unreachable/unconfigured, but you should smoke-test them
in your own environment before relying on them.

## Known limitations / next steps

- Table creation uses `Base.metadata.create_all()` for simplicity. For a real
  deployment, switch to Alembic migrations so schema changes are versioned.
- `CORSMiddleware` is wide open (`allow_origins=["*"]`) — tighten to your
  frontend's actual origin before deploying.
- Coordinates (`lat`/`lon`) are real; `map_x`/`map_y` are precomputed
  equirectangular projections onto the stylized 1000×500 frontend map — if
  you add records via the API, compute those as
  `x = (lon+180)/360*1000`, `y = (90-lat)/180*500`.
