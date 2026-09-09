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
| `GET /funds/<bad>`  | `/funds/does-not-exist`          | `shouldFail`, status is exactly 404     |
| `GET /strategies`   | `/strategies`                    | 200, `$.strategies` not empty           |

Assertions stay on fields that survive every migration step (`fund_id`, `total`,
`strategy`, status codes), so the checks don't break when the `commitment`
columns change. The 404 check sets `shouldFail: true` because Checkly fails an API
check on any `>= 400` response before assertions run.

## One-time setup

1. Sign up at [checklyhq.com](https://www.checklyhq.com/) (free trial).
2. **Private Location:** dashboard → Private Locations → _New_. Name it
   `owl-fs-local`; copy the agent key (`pl_...`, shown once).
3. **Account credentials** for the CLI: a **user** API key (`cu_...`, from User
   Settings → API keys — _not_ the `pl_` location key) and the account id (it's in
   the dashboard URL: `app.checklyhq.com/accounts/<CHECKLY_ACCOUNT_ID>/...`). Or
   just run `cd monitoring && npx checkly login` and skip these two.
4. Fill the repo's root `.env` (keys documented in [`.env.example`](.env.example)):

   ```sh
   CHECKLY_AGENT_API_KEY=pl_...          # the Private Location key
   CHECKLY_API_KEY=cu_...                # user API key (or use `checkly login`)
   CHECKLY_ACCOUNT_ID=xxxxxxxx-xxxx-...  # or use `checkly login`
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

## What to expect

`make monitor` runs the checks on the agent and prints:

```text
Running 6 checks in private location owl-fs-local.

__checks__/api.check.ts
  ✔ GET /funds
  ✔ GET /funds?strategy=Infrastructure
  ✔ GET /funds/<unknown> -> 404
  ✔ GET /funds/F-1001
  ✔ GET /health
  ✔ GET /strategies

6 passed, 6 total
```

Exit code is non-zero if any check fails, so it works as a gate. After
`make monitor-deploy` the six checks show up under **Home** in the dashboard and
re-run every 5 minutes; `--record` runs (and CI runs) also appear under **Test
sessions** with full request/response traces.

Prove alerting end to end:

```sh
make monitor-deploy
docker compose stop api      # break it
# ~5 min later: the checks go red on the dashboard (and alert, if a channel is set)
docker compose start api     # recover
cd monitoring && npx checkly destroy   # remove the scheduled monitors
```

## Without a private location (deployed API)

Set `MONITOR_TARGET_URL` to the public URL and leave `CHECKLY_PRIVATE_LOCATION`
unset — the checks then run from Checkly's global public locations
(`us-east-1`, `eu-west-1`). No agent needed.

## CI

[`.github/workflows/checkly.yml`](../.github/workflows/checkly.yml) typechecks the
checks on every relevant PR, and (once `CHECKLY_API_KEY` + `CHECKLY_ACCOUNT_ID`
are set as repo secrets) runs `checkly test --record` on PRs and `checkly deploy`
on merge to `main`.

## Troubleshooting

| Symptom                                              | Fix                                                                                                                                                          |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Running N checks in eu-central-1` (a public region) | `CHECKLY_PRIVATE_LOCATION` isn't set in `.env` — `make monitor` needs it to pass `--private-location`.                                                       |
| All checks fail with connection errors               | the agent isn't up or isn't connected — `make monitor-agent`, then check the dashboard's Private Locations page and `docker compose ... logs checkly-agent`. |
| `Authentication failed`                              | `CHECKLY_API_KEY` is the `pl_` key, not a `cu_` user key — fix it or run `checkly login`.                                                                    |
| 404 check fails though the status is 404             | it needs `shouldFail: true` (already set); a bare assertion isn't enough.                                                                                    |
| `make up` errors on `CHECKLY_AGENT_API_KEY`          | you ran the monitoring overlay without the key — the base `make up` never needs it.                                                                          |

## Notes

- Checkly CLI pinned to 4.x; `npx checkly runtimes` lists runtime IDs.
- `npx checkly test` needs account credentials even to list checks — the local
  typecheck (`npm run typecheck`) is the offline gate.
- `make monitor` passes `--private-location` and loads `../.env`; a bare
  `npx checkly test` runs from a Checkly public location that can't reach
  `http://api:8000`.
- `checkly deploy` schedules real monitors in your account — `npx checkly destroy`
  removes them.
