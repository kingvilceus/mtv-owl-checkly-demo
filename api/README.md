# `api/` — FastAPI service

Read-only HTTP API over the `funds` table. FastAPI + SQLAlchemy 2.0, talking to
Postgres via psycopg 3.

## Layout

| File               | Role                                                                |
| ------------------ | ------------------------------------------------------------------- |
| `app/main.py`      | FastAPI app + route handlers                                        |
| `app/db.py`        | SQLAlchemy `Engine` + `sessionmaker` + the `get_session` dependency |
| `app/models.py`    | declarative `Fund` model                                            |
| `app/schemas.py`   | Pydantic response models (`FundOut`, `FundsPage`)                   |
| `requirements.txt` | pinned runtime deps                                                 |
| `Dockerfile`       | `python:3.12-slim`; source is bind-mounted in dev                   |

## Endpoints

| Method | Path               | Notes                                            |
| ------ | ------------------ | ------------------------------------------------ |
| GET    | `/health`          | runs `SELECT 1`                                  |
| GET    | `/funds`           | `?strategy=`, `?limit=` (omit = all), `?offset=` |
| GET    | `/funds/{fund_id}` | 404 if unknown                                   |
| GET    | `/strategies`      | distinct `strategy` values                       |

`/funds` returns `commitment_cents` (bigint minor units, ×100) + `currency`
(ISO code or `null`). Swagger UI at `/docs`.

## Config

`DATABASE_URL` is the only input (default `postgresql://owl:owl@db:5432/owl`).
`db.py` rewrites the scheme to `postgresql+psycopg://` for SQLAlchemy.

## Run

```sh
make serve PORT=8000                     # in the compose stack
# or, against a local Postgres (make up provides one on :5432):
DATABASE_URL=postgresql://owl:owl@localhost:5432/owl \
  uvicorn app.main:app --app-dir api --reload
```

## Notes

- The `Fund` model deliberately never mapped the raw `commitment` column, so no
  query selected it — which is what let migration `0003` drop it without a code
  change here.
- Parser tests live in [`../tests/`](../tests/) and run with `make test`.
