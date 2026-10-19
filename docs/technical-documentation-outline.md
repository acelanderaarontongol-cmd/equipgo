# Technical Documentation Draft (export to PDF, 8-15 pages)

Fill every `TODO` with your own words and screenshots. Each member should be able to explain every section.

1. **Title page**: group name, members, roles.
2. **Project description and modules**: EquipGo; frontend, inventory-api, borrow-api, worker, db, proxy.
3. **Architecture**: diagram (`architecture.png`); request flow Browser > proxy > service > db; ports, network `equipgo-net`, volume `db-data`. TODO: screenshot of `docker compose ps`.
4. **Technology stack table**: copy from `project-proposal.md`.
5. **Dockerfiles**: pinned slim/alpine bases, dependencies copied first for layer cache, multi-stage `test` and `production` targets, non-root users, `.dockerignore`, HEALTHCHECK. TODO: your own explanation of one Dockerfile line by line.
6. **Docker Compose**: services, `depends_on: service_healthy`, db healthcheck, named volume, user-defined network, only proxy publishes a port, env vars from `.env`, `${TAG}` image tags.
7. **Jenkins setup**: image with Docker CLI, `jenkins_home` volume, plugins, credential `equipgo-env`, trigger. TODO: screenshots.
8. **Pipeline**: what each stage does and what happens on failure. TODO: Stage View screenshot (green and failed).
9. **Testing strategy**: unit tests per backend module run inside Docker; failure at Test blocks Deploy.
10. **Rollback and persistence proof**: TODO: screenshots of `TAG=<n> docker compose up -d --no-build` and data after redeploy.
11. **Problems encountered and fixes**: TODO (write the real ones; see Section 15 of the guideline for common ones).
12. **Individual contributions and references**: TODO from the git log.
