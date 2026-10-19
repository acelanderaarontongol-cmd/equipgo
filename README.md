# EquipGo: Campus Lab Equipment Borrowing

A small multi-module app, fully containerized with Docker and deployed automatically by Jenkins
on every `git push`. Built for the System Architecture and Integration final project.

## Team
| Member | Role |
|---|---|
| _Name 1_ | Project Lead / Scrum Master |
| _Name 2_ | DevOps / CI-CD Engineer |
| _Name 3_ | Infrastructure Engineer |
| _Name 4_ | Backend and Database Engineer |
| _Name 5_ | Frontend, QA, and Documentation Lead |

## Architecture
```
Browser --> proxy (Nginx :8080)
              |-- /                 --> frontend      (Nginx, static)
              |-- /api/inventory/   --> inventory-api (Node.js/Express) --\
              '-- /api/borrow/      --> borrow-api    (Python/Flask)    ---+--> db (PostgreSQL 16, volume db-data)
                                        worker        (Python, polls db) -/
Network: equipgo-net     Only the proxy publishes a port (8080).

Developer --git push--> GitHub --webhook (ngrok) / Poll SCM--> Jenkins
Jenkins: Checkout > Test > Build Images (tag = build #) > Deploy > Smoke Test
```
See `docs/architecture.png` (export it from `docs/architecture.mmd`).

| Container | Tech | Role |
|---|---|---|
| proxy | Nginx 1.27 | Single public entry point |
| frontend | Static HTML/JS on nginx-unprivileged | UI; shows build number in the footer |
| inventory-api | Node.js 20, Express | Equipment CRUD (`/health`, `/equipment`) |
| borrow-api | Python 3.12, Flask, Gunicorn | Borrow/return logic, notifications list |
| worker | Python 3.12 | Writes a notification record for every new borrow/return |
| db | PostgreSQL 16 Alpine | Data in named volume `db-data`, not published |

## Prerequisites
Git, Docker (Compose v2), 8 GB RAM recommended.

## Run the application locally
```bash
cp .env.example .env        # then edit the password
docker compose up -d --build
# open http://localhost:8080
```
Data survives `docker compose down` + `docker compose up -d` (do NOT add `-v`).

## Start Jenkins (separate compose file)
```bash
cd infra/jenkins
docker compose up -d --build
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
Open http://localhost:8081, install suggested plugins + **Docker Pipeline**, create the admin user.
Then:
1. Manage Jenkins > Credentials: add a **Secret file** with ID `equipgo-env` (your real `.env`).
   Add a Git access token too if the repo is private.
2. New Item > Pipeline > *Pipeline script from SCM* > repo URL, branch `main`, Script Path `Jenkinsfile`.
3. Verify: `docker exec jenkins docker ps`.

## Trigger configuration
- **Webhook (preferred):** job option "GitHub hook trigger for GITScm polling"; GitHub > Settings >
  Webhooks > `https://<ngrok-url>/github-webhook/`, `application/json`, push events. Run `ngrok http 8081`.
- **Fallback:** the Jenkinsfile already contains `pollSCM('H/2 * * * *')`.

## Rollback
```bash
TAG=<previous build number> docker compose -p equipgo up -d --no-build
```

## Tests
Each backend module has a `test` stage in its Dockerfile, run by Jenkins with
`docker build --target test ./<module>`:
inventory-api (node:test), borrow-api (pytest + ruff), worker (pytest + ruff).

## Security note
Jenkins mounts `/var/run/docker.sock` and runs as root. Acceptable in a lab only; safer options are
dedicated build agents, rootless Docker, Docker-in-Docker with TLS, or Kaniko.
