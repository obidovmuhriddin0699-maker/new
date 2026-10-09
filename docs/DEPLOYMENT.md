# Production deployment (PHASE 12)

Goal: the panel runs at `https://<your domain>` on a Linux VPS. It has an automatic
certificate, daily backups, alerts when something breaks, and one-command updates and
rollbacks.

```
 Internet ──► :80/:443  Caddy (TLS, HTTP→HTTPS, HSTS, real client IP)
                          │ edge network (172.30.0.0/24)
                          ▼
                     frontend :3000 (Next.js panel + BFF)  ── not published
                          │
            backend · worker · beat · telegram-bot · backup
                          │ data network (internal: no internet)
                     postgres · redis
```

Only Caddy publishes ports. Everything else is reachable only inside Docker networks, and
`scripts/prod-smoke.sh` checks this.

---

## 1. Server

| | Minimum | Recommended |
|---|---|---|
| Without local AI (Ollama elsewhere, or AI not used) | 2 vCPU, 4 GB RAM, 40 GB SSD | 2 vCPU, 4 GB |
| With Ollama on the same server (`qwen2.5:3b`) | 4 vCPU, 8 GB RAM, 60 GB SSD | 4–8 vCPU, 16 GB |

These are estimates:

* The app stack's memory limits add up to about 2.5 GB.
* `qwen2.5:3b` needs about 2–3 GB of RAM while it answers; larger models need more.
* On a CPU-only VPS, generation takes tens of seconds. That is fine because AI jobs run
  in the background.
* Media uploads and backups grow over time. The ops monitor warns below 10 % free disk.

Use Ubuntu Server 24.04 LTS (22.04 also works) with a public IPv4 address.

## 2. Domain (DNS)

At your DNS provider, create an **A record** `panel.example.com → <server IPv4>`. If the
server has IPv6, also add an **AAAA** record. Wait until it resolves:

```powershell
Resolve-DnsName panel.example.com        # Windows PowerShell
```
```bash
dig +short panel.example.com             # Linux / macOS
```

Caddy gets the Let's Encrypt certificate on first start. This only works once DNS
points at the server and ports 80 and 443 are open.

## 3. Prepare the server

### 3.1 SSH from Windows 11 (PowerShell)

The OpenSSH client is built into Windows 11.

```powershell
ssh-keygen -t ed25519 -C "muxriddin-vps"            # press Enter for the default path; set a passphrase
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@<server-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
ssh root@<server-ip>
```

### 3.2 Deploy user, firewall and updates (on the server)

```bash
adduser deploy && usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh && cp ~/.ssh/authorized_keys /home/deploy/.ssh/ && chown -R deploy:deploy /home/deploy/.ssh

# Firewall: SSH + web only
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 443/udp && ufw enable

# Automatic security updates
apt update && apt install -y unattended-upgrades && dpkg-reconfigure -plow unattended-upgrades
```

**Harden SSH.** First check that `ssh deploy@<server-ip>` works with your key. Then set
these in `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
PermitRootLogin no
```

Then run `systemctl restart ssh`.

> **Docker and ufw.** Ports that Docker publishes bypass ufw rules. That is why only Caddy
> publishes ports here (80 and 443, which must be open anyway). PostgreSQL, Redis, the
> backend and the panel publish nothing. Do not add `ports:` to them.

### 3.3 Docker

Follow the official guide, https://docs.docker.com/engine/install/ubuntu/ (apt repository).
Then:

```bash
usermod -aG docker deploy          # log out and back in as deploy
docker version && docker compose version
```

## 4. Configuration

As the `deploy` user:

```bash
sudo mkdir -p /opt/muxriddin && sudo chown deploy:deploy /opt/muxriddin
git clone https://github.com/<you>/<repo>.git /opt/muxriddin && cd /opt/muxriddin
cp .env.production.example .env.production && chmod 600 .env.production
nano .env.production
```

Replace every `change-me` value; the generation commands are at the top of the file. The
values that matter for this phase:

| Variable | Value |
|---|---|
| `DOMAIN` | `panel.example.com` |
| `CADDY_TLS` | Your e-mail address for Let's Encrypt. Use `internal` only for testing (self-signed) |
| `CORS_ORIGINS`, `PANEL_PUBLIC_URL`, `MEDIA_PUBLIC_BASE_URL` | `https://panel.example.com` |
| `ALLOWED_HOSTS` | `panel.example.com,backend,localhost,127.0.0.1` |
| `META_REDIRECT_URI` | `https://panel.example.com/instagram/callback` |
| `BACKUP_UID` / `BACKUP_GID` | Output of `id -u` / `id -g` for the deploy user (usually 1000) |
| `LEGAL_OPERATOR_NAME`, `LEGAL_CONTACT_EMAIL` | Shown on `/privacy` and `/terms` |
| `TELEGRAM_*` | Optional; also used for the ops alerts (§8) |

> **Keep a copy of `.env.production` off the server**, for example in a password manager.
> Without `TOKEN_ENCRYPTION_KEYS`, a restored backup cannot decrypt the Instagram tokens,
> and you would have to reconnect Instagram.

**AI on the server:** use the containerised Ollama:

```bash
# in .env.production: OLLAMA_BASE_URL=http://ollama:11434
docker compose -f docker-compose.prod.yml --env-file .env.production --profile ollama up -d ollama
docker compose -f docker-compose.prod.yml --env-file .env.production exec ollama ollama pull qwen2.5:3b
```

## 5. First deploy

```bash
./scripts/deploy.sh
```

What it does:

1. **Preflight:**
   - the env file exists, has no `change-me` values and has its required keys;
   - `docker compose config` is valid;
   - the backup directory belongs to `BACKUP_UID`.
2. **Build:** builds the images and tags them with the git commit
   (`muxriddin-backend:<sha>`).
3. **Backup:** if the stack is already running, it takes a backup first, so a bad
   migration can be undone.
4. **Release:** tags the build as `:prod` and runs `up -d`:
   - the migrate service applies migrations and the least-privilege DB role;
   - every app service starts;
   - Caddy obtains the certificate.
5. **Record:** writes the release to `.deploy/releases`.
6. **Verify:** waits for health, then runs `scripts/prod-smoke.sh` (up to 44 checks). It exits
   non-zero if any check fails.

Create the first owner. The command prompts for the password, so it does not land in
shell history:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production run --rm backend \
  python -m app.cli create-admin --email you@example.com
```

Open `https://panel.example.com`, log in, and run the full smoke test with the session
checks:

```bash
SMOKE_EMAIL=you@example.com SMOKE_PASSWORD='...' ./scripts/prod-smoke.sh
```

## 6. Meta app: Live mode checklist

Real publishing stays off (`META_DRY_RUN=true`) until you switch it on. In the Meta app
dashboard (Instagram API with Instagram Login), check:

1. Under **Business login settings**, set these URLs exactly:
   - OAuth redirect URI: `https://panel.example.com/instagram/callback`
   - Deauthorize callback: `https://panel.example.com/api/meta/deauthorize`
   - Data deletion request: `https://panel.example.com/api/meta/data-deletion`
2. Under **App settings → Basic**, set:
   - Privacy Policy URL: `https://panel.example.com/privacy`
   - Terms of Service URL: `https://panel.example.com/terms`
   - App icon and category.
   These pages are public, have no login, and Meta's crawler can read them.
3. Under **App roles**, add your Instagram account as a tester and accept the invite in
   Instagram.
4. In `.env.production`, set `META_APP_ID` and `META_APP_SECRET` (the **Instagram** app
   ID and secret). Then rerun `./scripts/deploy.sh` with `SKIP_BUILD=1`.
5. In the panel, go to **Instagram → Instagram’ni ulash** and check that the permissions
   are granted.
6. Publish one post with `META_DRY_RUN=false`, then turn on the schedule.
7. Your own account only needs Standard Access. Connecting other people's accounts needs
   **Business verification** and **App Review** (Advanced Access) first; see
   README §12–13.

> The `/privacy` and `/terms` texts are a **template**: they describe what this software
> actually does. Have them reviewed for your jurisdiction (for example, Uzbekistan's
> personal data law) before you go Live.

## 7. Backups and restore

**Automatic.** The `backup` service runs every day at `BACKUP_TIME` (UTC) and writes to
`BACKUP_DIR`:

* `db-<stamp>.dump`: `pg_dump -Fc` of the whole database;
* `media-<stamp>.tar.gz`: uploaded media;
* `backup-<stamp>.sha256`: checksums.

Files are owner-only (0600). Backups older than `BACKUP_RETENTION_DAYS` are deleted.
Each run is recorded in the database, and the ops monitor alerts when a backup fails or
is more than 26 hours old. Setting `BACKUP_HEARTBEAT_URL` (for example a free
healthchecks.io check) also alerts you when the server itself is down.

To back up right now:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec backup sh /backup.sh once
```

**Copy backups off the server.** A backup that lives only on the VPS is lost together
with the VPS. From Windows PowerShell:

```powershell
scp -r deploy@panel.example.com:/opt/muxriddin/backups "$env:USERPROFILE\Documents\muxriddin-backups"
```

Run it weekly with Task Scheduler, or use `rclone` on the server to sync to object
storage. Keep `.env.production` in a separate safe place.

**Restore:**

```bash
./scripts/restore.sh backups/db-<stamp>.dump backups/media-<stamp>.tar.gz
```

The script:

1. Verifies the checksums.
2. Asks you to type `restore`.
3. Backs up the current state first, so a restore can itself be undone.
4. Stops the app.
5. Restores the database in one transaction.
6. Restores the media.
7. Re-applies migrations and the app-role grants.
8. Starts everything again.

Then run `./scripts/prod-smoke.sh`. Tested in PHASE 12: data deleted after a backup came
back, the audit trigger and app-role restrictions stayed intact, and the smoke test
passed.

Restoring onto a **new server**:

1. Follow §3–4 with the **same** `.env.production`.
2. Run `./scripts/deploy.sh`.
3. Copy the backup files into `backups/`.
4. Run `./scripts/restore.sh`.

## 8. Monitoring and alerts

| What | How |
|---|---|
| Panel is up | Point an external uptime monitor (UptimeRobot, Better Stack, healthchecks.io…) at `https://panel.example.com/api/backend/health`. It returns 200 with database and Redis `ok`, and 503 when they are not |
| Server or backups stopped | `BACKUP_HEARTBEAT_URL` (§7) |
| Problems inside the app | **Ops monitor** (Celery beat, every 5 min) → Telegram + overview banner |

The ops monitor reports:

| Problem | Severity |
|---|---|
| Redis down | 🔴 |
| Instagram needs reconnecting (token missing, expired, or a permission removed) | 🔴 |
| Token expires within 5 days and was not refreshed | 🟡 |
| Publishing failed in the last 24 h | 🟡 |
| A publish has been stuck for more than 30 min | 🔴 |
| A scheduled post is more than 15 min overdue (worker or beat not running; ignored in dry run) | 🔴 |
| Backup missing, failed, or older than 26 h | 🔴 / 🟡 |
| The latest insights sync failed | 🟡 |
| Media disk below 10 % (🟡) or 5 % (🔴) free | 🟡 / 🔴 |

How the alerts behave:

* **When:** an alert is sent only when the set of problems changes. While a problem stays
  open, a reminder goes out once every 24 h. When everything recovers, a "✅ Tizim holati
  tiklandi" message is sent.
* **Where:** Telegram, to linked owners and admins (needs `--profile telegram`), plus a
  banner on the panel's overview page. Owners and admins can also call
  `GET /api/v1/system/ops-status`.
* **Record:** every alert is also an `OPS_ALERT` entry in the audit log.

**Logs:** run `docker compose -f docker-compose.prod.yml --env-file .env.production logs -f backend worker caddy`.

* Format: JSON, rotated at 10 MB × 5 per service.
* Redaction: Caddy's access log hides the OAuth `code`/`state` and the
  `Cookie`/`Authorization` headers, and the app masks tokens.

## 9. Updates and rollback

```bash
cd /opt/muxriddin && git pull && ./scripts/deploy.sh      # backup → migrate → start → smoke
```

If the smoke test fails, or something looks wrong:

```bash
./scripts/rollback.sh            # previous release's images
./scripts/rollback.sh <sha>      # a specific release from .deploy/releases
```

Rollback switches **images only**. If the release you are leaving ran a database
migration, also restore the backup that `deploy.sh` took right before it (§7).

Running `rollback.sh` again switches back to the newer release. Pass a tag to choose
exactly.

**Maintenance:**

* **Base images and OS fixes:** bump the image digests (docs/DOCKER.md §5).
* **Reboots:** unattended-upgrades installs security fixes. Reboot when
  `/var/run/reboot-required` exists. All services have `restart: unless-stopped`.

## 10. Troubleshooting

| Symptom | Fix |
|---|---|
| Browser shows a certificate error, or Caddy logs `challenge failed` | DNS doesn't point to the server yet, or port 80 or 443 is closed (check `ufw status` and the provider's firewall). Check with `docker compose ... logs caddy` |
| `too many certificates` (Let's Encrypt rate limit) | Test with `CADDY_TLS=internal`, then switch to your e-mail. Don't delete the `caddy_data` volume: it holds the certificate |
| 400 `Invalid host header` | Add `DOMAIN` to `ALLOWED_HOSTS` |
| Audit log shows `172.30.0.1` for every login | Only for requests made from the server itself (Docker's userland proxy). Real visitors are recorded with their own IP. Check with `SMOKE_HOST=<server public IP> ./scripts/prod-smoke.sh` |
| `deploy.sh`: "owned by uid 0, but BACKUP_UID=1000" | Set `BACKUP_UID`/`BACKUP_GID` to `id -u`/`id -g`, or run `sudo chown deploy:deploy backups` |
| "Hali birorta zaxira nusxa olinmagan" alert right after installing | Expected until the first nightly run. Run a backup now (§7) |
| Telegram alerts don't arrive | Telegram needs `--profile telegram`, `TELEGRAM_ENABLED=true`, and an account linked under Panel → Telegram |
| Smoke test `FAIL panel /login 200` | `docker compose ... ps`: is the frontend healthy? Then check `logs frontend caddy` |
