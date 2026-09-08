# mtv-owl-fs-assessment

Full-stack assessment project: a minimal app over `funds.csv` — Postgres, a
Python (FastAPI) API, and a React frontend.

This branch (`standup-app-1`) is **Part 1 — stand up the app**. The `commitment`
column is loaded as raw text and is not parsed; that comes in a later step.

## Stack

| Piece             | What                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------- |
| `db`              | Postgres 16 (Docker)                                                                      |
| `api/`            | FastAPI + psycopg, read-only endpoints over `funds`                                       |
| `web/`            | Vite + React + TypeScript, one table view                                                 |
| `db/migrations/`  | SQL migrations applied with [yoyo-migrations](https://ollycope.com/software/yoyo/latest/) |
| `scripts/seed.py` | drop/recreate DB → migrate → load the CSV                                                 |

Everything runs in Docker Compose (project name `owl-fs`).

## Requirements

- Docker with the Compose plugin (`docker compose`)
- [`uv`](https://docs.astral.sh/uv/) — only for the lint hooks (`make hooks` / `make lint`)

## Quick start

```sh
cp .env.example .env        # optional; defaults work out of the box
make seed                   # recreate DB, run migrations, load funds.csv
make serve PORT=8000        # API on http://localhost:8000
make web                    # React app on http://localhost:5173
```

Check it:

```sh
curl localhost:8000/health
curl 'localhost:8000/funds?strategy=Infrastructure&limit=5'
curl localhost:8000/funds/F-1001
```

## Make targets

| Target                     | Purpose                                             |
| -------------------------- | --------------------------------------------------- |
| `make seed`                | drop & recreate the database, migrate, load the CSV |
| `make migrate`             | apply every migration up to the current checkout    |
| `make serve PORT=xxxx`     | run the API on that port                            |
| `make web`                 | run the React dev server                            |
| `make up` / `make down`    | start / tear down the whole stack                   |
| `make psql`                | psql shell on the app database                      |
| `make hooks` / `make lint` | install / run the pre-commit hooks                  |

`DATABASE_URL` (env or `make DATABASE_URL=… <target>`) overrides the target
database, so two checkouts can be pointed at one Postgres to compare behavior.

## API

| Method | Path               | Notes                                              |
| ------ | ------------------ | -------------------------------------------------- |
| GET    | `/health`          | DB connectivity check                              |
| GET    | `/funds`           | `?strategy=`, `?limit=` (omit for all), `?offset=` |
| GET    | `/funds/{fund_id}` | 404 if unknown                                     |
| GET    | `/strategies`      | distinct strategy values (for the filter)          |

`commitment` is returned as the exact stored string (or `null` when blank).

## Schema (migration `0001`)

```text
funds(
  fund_id text pk, fund_name text, manager text, strategy text,
  vintage_year int, commitment text NULL, reported_at date
)
```

## Out of scope for Part 1

`commitment` parsing/normalization (Part 2), auth, CI, production web serving,
and tests beyond the seed/health smoke check.
