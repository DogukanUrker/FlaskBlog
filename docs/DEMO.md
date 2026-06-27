# Live Demo — Self-Hosting Reference

> The public demo at **[flaskblog.dogukanurker.com](https://flaskblog.dogukanurker.com)**
> runs on my personal home server, not a PaaS. This file is the _map_ of that
> deployment: the architecture, the non-default choices, and the gotchas that
> bit me along the way — so future-me (or anyone curious) can see how a real
> self-hosted demo is wired end to end.
>
> Nothing here is required to run FlaskBlog yourself — the [README](README.md)
> covers local + Docker. This is purely how the _live demo_ is hosted.

---

## What it is

A public, internet-reachable instance of FlaskBlog, served from a headless
home server, fronted by Cloudflare, auto-deployed on every push to `main`, and
reset to a clean seeded state every night. The whole point: people can do live
end-to-end testing (register, post, comment, even the admin panel) without
cloning the repo — and whatever they break is throwaway.

The deployment is **hub-local**: the prod image, compose file, environment, and
tunnel config live only on the server. They are deliberately **not committed**
to this repo, so they never collide with the dev `Dockerfile` and never leak
secrets. This doc describes them; it doesn't ship them.

---

## Traffic flow

```
Visitor browser
   │  https://flaskblog.dogukanurker.com
   ▼
Cloudflare edge (TLS terminates here, free cert, DDoS/WAF in front)
   │  QUIC tunnel (outbound from the server — no port-forward, no public IP)
   ▼
cloudflared  (systemd service on the home server)
   │  http://localhost:1283
   ▼
gunicorn  (1 worker / 4 threads, non-root)
   │
   ▼
Flask app  →  SQLite  (instance/flaskblog.db, bind-mounted from host)
```

Because the tunnel is **outbound-only**, the server never exposes a port to the
internet. The ISP gives a dynamic IP and blocks inbound anyway — irrelevant
here, Cloudflare reaches the box through the tunnel the box itself dialed out.

---

## The production image

A second Dockerfile (`Dockerfile.prod`, hub-local, untracked) — separate from the
dev `Dockerfile` so the two never interfere.

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-alpine

RUN addgroup -g 1000 flaskblog && \
    adduser -u 1000 -G flaskblog -D flaskblog

WORKDIR /app
RUN chown flaskblog:flaskblog /app
USER flaskblog

COPY --chown=flaskblog:flaskblog app/pyproject.toml app/uv.lock ./
RUN uv sync --frozen --no-dev --no-cache && \
    uv pip install --no-cache gunicorn

COPY --chown=flaskblog:flaskblog app/ .

RUN mkdir -p instance log

ENV PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=1283 \
    DEBUG_MODE=False

EXPOSE 1283

CMD [".venv/bin/gunicorn", \
     "--workers", "1", "--threads", "4", \
     "--bind", "0.0.0.0:1283", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "app:app"]
```

Decisions that matter:

- **gunicorn, not `app.run()`** — the dev server (`uv run app.py`) is single-threaded
  and explicitly not for production. gunicorn is `uv pip install`-ed into the synced
  venv at build time, so `pyproject.toml` stays untouched.
- **Exec-form CMD straight to the venv binary** — clean PID 1, proper `SIGTERM` /
  graceful shutdown (no `uv run` wrapper swallowing signals).
- **`python3.13-alpine`** — the dependency set is pure-Python (even password hashing
  uses `sha512_crypt`, no native ext), so musl builds clean and the image stays small.
  3.13 over 3.14 to avoid bleeding-edge wheel gaps.
- **Non-root, uid 1000** — matches the host user, so the bind-mounted DB is writable
  without ownership churn.
- **`init_db(app)` runs at import** (module level, not under `if __name__`), so gunicorn
  importing `app:app` creates the tables and seeds the default admin on worker boot —
  no separate entrypoint script needed.

A `Dockerfile.prod.dockerignore` keeps the committed seed DB and caches out of the
build context (the build context ends up ~0.5 MB instead of dragging in the 11 MB DB).

---

## Data persistence — the hard-won lesson

The single most important decision, because it's the one that can silently wipe
real user data:

**The SQLite DB lives in a host bind mount _outside_ the repo and outside Docker's
volume management** — `~/infra/flaskblog-data/instance/flaskblog.db`.

Why not a named volume? Because the ops auto-deploy tears a service down with
`docker compose down --rmi all --volumes` before rebuilding. `--volumes` deletes
named and anonymous volumes — so a named-volume DB would be **destroyed on every
single deploy**. A bind mount points at a plain host directory Docker doesn't
manage, so it survives `down --volumes`, survives rebuilds, and survives `git pull`.

This was verified the blunt way: ran the exact `down --rmi all --volumes` the deploy
uses, then confirmed the DB file was still sitting on disk, untouched.

```yaml
# docker-compose.yml (hub-local, untracked)
services:
  flaskblog:
    build:
      context: .
      dockerfile: Dockerfile.prod
    image: flaskblog:prod
    container_name: flaskblog
    restart: unless-stopped
    ports:
      - "1283:1283"
    environment:
      APP_SECRET_KEY: "${FLASKBLOG_SECRET_KEY:?set in .env}"
      DEFAULT_ADMIN_PASSWORD: "${FLASKBLOG_ADMIN_PASSWORD:?set in .env}"
      DEBUG_MODE: "False"
      LOG_TO_FILE: "True"
    volumes:
      - ~/infra/flaskblog-data/instance:/app/instance
      - ~/infra/flaskblog-data/log:/app/log
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:1283/"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Two more gotchas baked in above:

- **`APP_SECRET_KEY` must be stable.** The app defaults it to a random value per
  process start — fine for dev, fatal for an auto-rebuilding prod: every redeploy
  would rotate the key and log every user out. It's pinned via `.env` (gitignored,
  never committed).
- **Healthcheck hits `127.0.0.1`, not `localhost`.** With IPv6 enabled, `localhost`
  resolves to `::1` first, but gunicorn binds IPv4 `0.0.0.0` — so `localhost` gave
  `connection refused` and the container reported `unhealthy` while serving fine.
  Forcing IPv4 fixed it.

Secrets (`.env`, the tunnel credentials JSON) are never committed and never printed.

---

## Auto-deploy

Every push to `main` reaches the live demo within ~2 minutes, no manual step.

A small poller (`repos_autopull.sh`) walks every service registered in the ops
`services.mk`, fast-forward-pulls each `~/repos/*` git repo, and — only if `HEAD`
moved — tears the service down and rebuilds it (`--pull --no-cache`, then `up -d`).
FlaskBlog is registered there, so it's picked up automatically.

The poller runs as a **systemd timer** (`repos-autopull.timer`, every 2 min,
`OnBootSec=1min`) — reboot-safe, unlike the stray `while true` loop it replaced.
The log is rotated by logrotate (`copytruncate`, so the poller never has to stop).

Because the bind-mounted DB survives the `down --volumes` in that rebuild, an
auto-deploy never touches user data.

---

## Nightly reset

The demo is reset to a clean, populated state every night at **04:00**
(`flaskblog_demo_reset.sh`, cron):

1. `docker compose stop` (so SQLite isn't swapped under a live file descriptor)
2. remove the live DB + any `-wal` / `-shm` / `-journal` sidecars
3. copy the **committed seed** `app/instance/flaskblog.db` into place
4. `docker compose start`

~3 seconds of downtime no one notices. The seed is the same DB the repo ships so
that a fresh local clone starts with demo content — so the live demo and a local
clone show the exact same starting data, and any visitor damage is thrown away
overnight.

This is also why the demo's `admin / admin` login is left as-is: it's intentional,
so visitors can test the admin panel too, and the nightly wipe makes it safe.

---

## Cloudflare Tunnel

A named tunnel (`flaskblog`) routes `flaskblog.dogukanurker.com` to
`http://localhost:1283`. The domain's DNS is on Cloudflare, so `cloudflared tunnel
route dns` created the CNAME automatically — no manual record, and the existing
apex/`www`/mail records were untouched (only a new subdomain was added).

`cloudflared` runs as a **systemd service** reading `/etc/cloudflared/config.yml`
(moved there from `~/.cloudflared` so root's service install finds it; credentials
JSON `chmod 600`). Reboot-safe; if the terminal or SSH session that first started
it dies, the service keeps the tunnel up.

```yaml
# /etc/cloudflared/config.yml
tunnel: <tunnel-uuid>
credentials-file: /etc/cloudflared/<tunnel-uuid>.json
ingress:
  - hostname: flaskblog.dogukanurker.com
    service: http://localhost:1283
  - service: http_status:404
```

---

## Resource footprint

Measured on the actual box (Ryzen 5 5600, shared with an LLM stack), so the demo
had to earn its RAM:

| State                  | RAM          | Notes                                  |
| ---------------------- | ------------ | -------------------------------------- |
| Idle                   | ~12–20 MB    | drops back to ~12 MB after load clears |
| Under 30-parallel load | ~200 MB peak | transient spike, frees immediately     |
| Image size             | 235 MB       | alpine + uv + pure-Python deps         |
| Seed DB                | ~11 MB       | 17 posts / 103 users                   |

Latency: a single real request renders in **~63 ms** locally; **~378 ms** through
the public URL (the extra ~300 ms is the Cloudflare round-trip to the Frankfurt
edge, not the app). A single worker handles the synthetic load with zero errors;
real visitors hit one request at a time and never see the spike.

One worker was the deliberate pick over more: this box showed 2 workers as a dead
zone (GIL + SQLite contention, no real gain), 3 workers faster but with a ~400 MB
peak — not worth it for a demo where a real visitor's experience is identical
either way. Pragmatic beats maximal.

---

## Known caveats

- The app has open advisories (privilege escalation, stored XSS) that are being
  fixed gradually. On a public demo they're mitigated, not solved, by the nightly
  wipe + throwaway data model — anything an attacker does is gone by morning.
- SQLite + single writer is fine for demo traffic; it is not a high-write,
  multi-instance production setup, and isn't meant to be.

---

## Reproduce the shape of it

If you want a similar self-hosted demo for your own Flask app, the moving parts are:
a prod Dockerfile with gunicorn, a **bind-mounted** (not named-volume) SQLite path
so rebuilds don't wipe data, a stable `SECRET_KEY` from a gitignored `.env`, a
systemd timer for pull-and-rebuild auto-deploy, a nightly seed-restore cron, and a
Cloudflare named tunnel as a systemd service. No public IP, no port-forward, no
cloud bill.
