# `web/` — React frontend

Single-page fund table. Vite + React 18 + TypeScript. Deliberately minimal — the
brief says the frontend content is up to us.

## Layout

| File               | Role                                                          |
| ------------------ | ------------------------------------------------------------- |
| `src/main.tsx`     | React entry point                                             |
| `src/App.tsx`      | the whole UI: strategy filter, page-size control, funds table |
| `src/api.ts`       | `fetchFunds` / `fetchStrategies` + `formatCommitment` helper  |
| `src/index.css`    | styles (palette adapted from the react-reduction admin theme) |
| `vite.config.ts`   | dev server on `:5173`                                         |
| `eslint.config.js` | flat ESLint config (TS + react-hooks + react-refresh)         |
| `scripts/lint.sh`  | ESLint entry used by the repo pre-commit hook                 |
| `Dockerfile`       | `node:22-alpine` running the Vite dev server                  |

## Run

```sh
make web                      # via compose -> http://localhost:5173
# or directly:
npm --prefix web install
npm --prefix web run dev
```

Needs the API running (`make serve` or `make up`).

## Config

`VITE_API_URL` — API base URL, baked in at dev-server start
(default `http://localhost:8000`).

## What it calls

`GET /funds` (with `strategy` / `limit` / `offset`) and `GET /strategies`.
`commitment_cents` + `currency` are rendered with `Intl.NumberFormat` (dividing
cents by 100); `—` when null.

## Checks

```sh
npm --prefix web run build    # tsc + vite build
npm --prefix web run lint     # eslint (also runs in pre-commit)
```
