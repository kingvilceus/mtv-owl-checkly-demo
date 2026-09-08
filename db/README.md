# `db/` — schema & migrations

Postgres schema, evolved through numbered SQL migrations applied by
[yoyo-migrations](https://ollycope.com/software/yoyo/latest/).

## Layout

```
db/migrations/
  NNNN.<name>.sql            # forward migration
  NNNN.<name>.rollback.sql   # matching rollback (yoyo pairs them by name)
```

yoyo applies files in filename order and records what it has run in
`_yoyo_migration` (plus `_yoyo_log`, `_yoyo_version`, `yoyo_lock`). Config is in
[`../yoyo.ini`](../yoyo.ini); the database URL is passed per command.

## Migrations

| #      | Adds                                                                                               |
| ------ | -------------------------------------------------------------------------------------------------- |
| `0001` | `funds` table (raw `commitment` as `text`), `funds_strategy_idx`                                   |
| `0002` | `parse_commitment(text)`, `commitment_cents` + `currency`, a sync trigger, and a one-time backfill |

### `parse_commitment(raw text) -> (commitment_cents bigint, currency char(3))`

The single source of truth for turning a raw commitment string
(`"$15,000,000 USD"`, `"USD 10,000,000"`, `"~$1,000,000 USD"`, …) into
`(amount × 100, ISO code)`. Non-numeric / blank → `(NULL, NULL)`. Used by the
`funds_sync_commitment` trigger (so `make seed`'s `COPY` fills the columns) and by
the `0002` backfill.

## Commands

```sh
make migrate        # yoyo apply — bring the DB up to the current checkout
make seed           # drop/recreate DB, migrate, load data/funds.csv
make psql           # psql shell

# roll a migration back (from the api container):
docker compose run --rm api yoyo rollback --batch --revision 0002 \
  --database "$DATABASE_URL"
```

## Adding a migration

1. `db/migrations/0003.<name>.sql` + `0003.<name>.rollback.sql`.
2. Keep each file idempotent-friendly where practical (`IF EXISTS`, etc.).
3. `make migrate` locally, then `make seed` to check a from-scratch build.
4. PL/pgSQL bodies: wrap in `-- noqa: disable=all` / `-- noqa: enable=all` if
   sqlfluff trips on the `$$` quoting.

## Note

yoyo logs `relation "yoyo_lock" already exists` and a `yoyo_tmp_…` drop failure on
most runs — that is yoyo's own create-and-catch bookkeeping, not an error.
