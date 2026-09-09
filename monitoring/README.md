# `monitoring/` — Checkly API monitoring (POC)

Synthetic monitoring for the funds API as code:
[Checkly](https://www.checklyhq.com/) API checks in TypeScript, run on demand
(`make monitor`) or on a schedule (`make monitor-deploy`).

The API isn't deployed publicly, so Checkly reaches it through a **Private
Location** — a `checkly/agent` container ([docker-compose.monitoring.yml](../docker-compose.monitoring.yml))
on the compose network that executes the checks against `http://api:8000`.

## Layout

| File                      | Role                                                       |
| ------------------------- | ---------------------------------------------------------- |
| `checkly.config.ts`       | project config; picks private vs public locations from env |
| `__checks__/api.check.ts` | one `CheckGroup` + 6 `ApiCheck`s                           |
| `package.json`            | `checkly` CLI + `typescript` + `dotenv`                    |

## Checks

| Check               | Request                          | Assertions                              |
| ------------------- | -------------------------------- | --------------------------------------- |
| `GET /health`       | `/health`                        | 200, `$.status == "ok"`, < 2s           |
| `GET /funds`        | `/funds?limit=5`                 | 200, `$.total > 0`, `$.funds` not empty |
| `GET /funds` filter | `/funds?strategy=Infrastructure` | 200, first row's `strategy` matches     |
| `GET /funds/F-1001` | `/funds/F-1001`                  | 200, `$.fund_id == "F-1001"`            |
| `GET /funds/<bad>`  | `/funds/does-not-exist`          | 404                                     |
| `GET /strategies`   | `/strategies`                    | 200, `$.strategies` not empty           |

Assertions stay on fields that survive every migration step (`fund_id`, `total`,
`strategy`, status codes), so the checks don't break when the `commitment`
columns change.

## One-time setup

1. Sign up at [checklyhq.com](https://www.checklyhq.com/) (free trial).
2. **Private Location:** dashboard → Private Locations → _New_. Name it
   `owl-fs-local`; copy the agent key (`pl_...`, shown once).
3. **Account credentials:** dashboard → User Settings → API Keys (`CHECKLY_API_KEY`)
   and Account Settings → General (`CHECKLY_ACCOUNT_ID`). Or run `npx checkly login`.
4. Fill the repo's root `.env` (keys documented in [`.env.example`](.env.example)):

   ```sh
   CHECKLY_AGENT_API_KEY=pl_...
   CHECKLY_API_KEY=...
   CHECKLY_ACCOUNT_ID=...
   CHECKLY_PRIVATE_LOCATION=owl-fs-local
   MONITOR_TARGET_URL=http://api:8000
   ```

## Run it

```sh
make up             # API on the compose network
make monitor-agent  # start the agent — dashboard shows "1 agent connected"
make monitor        # npx checkly test — runs all 6 checks on the private location
make monitor-deploy # schedule them every 5 min
```

Add an email/Slack **alert channel** in the dashboard (or as an `AlertChannel`
construct here) so failures actually notify someone.

## Without a private location (deployed API)

Set `MONITOR_TARGET_URL` to the public URL and leave `CHECKLY_PRIVATE_LOCATION`
unset — the checks then run from Checkly's global public locations
(`us-east-1`, `eu-west-1`). No agent needed.

## CI

[`.github/workflows/checkly.yml`](../.github/workflows/checkly.yml) typechecks the
checks on every relevant PR, and (once `CHECKLY_API_KEY` + `CHECKLY_ACCOUNT_ID`
are set as repo secrets) runs `checkly test --record` on PRs and `checkly deploy`
on merge to `main`.

## Notes

- Checkly CLI pinned to 4.x; `npx checkly runtimes` lists runtime IDs.
- `npx checkly test` needs account credentials even to list checks — the local
  typecheck (`npm run typecheck`) is the offline gate.
- `make monitor` passes `--private-location` and loads `../.env`; a bare
  `npx checkly test` runs from a Checkly public location that can't reach
  `http://api:8000`.
- `checkly deploy` schedules real monitors in your account — `npx checkly destroy`
  removes them.
