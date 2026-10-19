# Project Proposal (Appendix A)

| Item | Details |
|---|---|
| Group name | _fill in_ |
| Project title | EquipGo: Campus Lab Equipment Borrowing |
| Short description | EquipGo lets students browse laboratory equipment, borrow and return items, and see notifications. Three application modules plus a worker run in Docker behind an Nginx reverse proxy with a PostgreSQL database on a named volume. Jenkins automatically tests, builds, and deploys every push. |
| Repository URL | _fill in_ |
| Project Lead / Scrum Master | _name_ |
| DevOps / CI-CD Engineer | _name_ |
| Infrastructure Engineer | _name_ |
| Backend and Database Engineer | _name_ |
| Frontend, QA, and Documentation Lead | _name_ |

| Module / Container | Technology | Purpose | Justification |
|---|---|---|---|
| proxy | Nginx 1.27 | Single entry point, path routing | Lightweight, simple config, widely documented |
| frontend | Static HTML/JS, nginx-unprivileged | User interface, build label | No build tooling needed; runs as non-root |
| inventory-api | Node.js 20 + Express | Equipment CRUD | Small, fast to write; built-in test runner |
| borrow-api | Python 3.12 + Flask + Gunicorn | Borrow/return business logic | Readable; pytest is easy; shows a polyglot stack |
| worker | Python 3.12 | Creates notification records | Demonstrates a background service |
| db | PostgreSQL 16 Alpine | Relational data | Equipment/borrowings are relational; constraints keep stock valid |
| jenkins | Jenkins LTS + Docker CLI | CI/CD | Required by the course; pipeline as code |

| Pipeline Plan | Details |
|---|---|
| Git hosting | GitHub |
| Trigger | Webhook via ngrok (preferred), Poll SCM every 2 min as fallback |
| Planned stages | Checkout, Test, Build Images, Deploy, Smoke Test |
| Tests to be run | inventory-api (node:test), borrow-api and worker (pytest + ruff) |
| Planned bonus features | _e.g. Slack/Discord notification, parameterized rollback job_ |

Attach: `docs/architecture.png`.
