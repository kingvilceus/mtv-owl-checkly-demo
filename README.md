# mtv-owl-fs-assessment

Full-stack assessment project: a minimal app over `funds.csv` — Postgres, a
Python (FastAPI) API, and a React frontend.

This branch (`migrate-column-2`) is **Part 2 — migrate the column**. It adds
`commitment_cents` (bigint) + `currency` (char(3)) next to the raw `commitment`
text and serves the parsed values. The raw column is kept so Step 1 instances keep
working through a rolling deploy; dropping it is Step 3.

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
| `make test`                | migrate, then run the parser unit tests             |
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

`/funds` returns `commitment_cents` (minor units, **always × 100**, JPY included)
and `currency` (ISO code, or `null`). It no longer returns the raw `commitment`
string.

## Schema

```text
funds(
  fund_id text pk, fund_name text, manager text, strategy text,
  vintage_year int, commitment text NULL,
  commitment_cents bigint NULL, currency char(3) NULL,
  reported_at date
)
```

- `0001` — baseline table with raw `commitment` text.
- `0002` — `parse_commitment(text)` (one PL/pgSQL parser), the `commitment_cents` /
  `currency` columns, a `BEFORE INSERT OR UPDATE` trigger that keeps them synced
  (so `make seed`'s `COPY` fills them), and a one-time backfill of existing rows.

### Rolling-deploy safety

`0002` is purely additive — nothing renamed or dropped — so Step 1 code still
reading `commitment` serves correct traffic against this schema while Step 2 code
reads the new columns. Replay:

```sh
git switch standup-app-1 && make seed && make serve PORT=8000   # old code
git switch migrate-column-2 && make migrate && make serve PORT=8001   # same DB
curl localhost:8000/funds   # still works — commitment column untouched
```

## Out of scope for Part 2

Dropping the raw `commitment` column + trigger and moving parsing into `seed.py`
(**Step 3**); `NOT NULL` on the new columns (25 rows are legitimately null); auth;
CI; FX/rounding beyond × 100.
