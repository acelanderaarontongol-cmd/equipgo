# Demo Video Script (recorded instead of a live presentation)

Target length: about 10 minutes. All five members must appear or speak. Do not cut the footage where
the pipeline fires on its own; that proves the trigger is real. Record a second clean take as backup.

**Before recording:** stack and Jenkins already running, images pulled, ngrok tunnel + webhook active,
one equipment item already borrowed so persistence can be shown. Screen layout: browser, Jenkins, terminal.

| # | Speaker (suggested) | Show / Say |
|---|---|---|
| 0 | Everyone, 30 s | Introduce the group, app, and roles. |
| 1 | Infrastructure Eng. | Architecture slide, then `docker compose ps`: 6 containers, only the proxy publishes a port. Open http://localhost:8080 and point out the footer build number (e.g. Build 14). Explain *why* each tech was chosen. |
| 2 | Frontend Lead | Change the page heading or version text, `git commit`, `git push`. |
| 3 | DevOps Eng. | Do NOT click Build Now. Show Jenkins starting by itself; walk through the Stage View: Checkout, Test, Build, Deploy, Smoke Test. Explain the Jenkinsfile and credentials. |
| 4 | Frontend Lead | Refresh browser: new heading, new build number (15). The earlier borrowing is still listed. |
| 5 | Backend Eng. | Push a commit that breaks a test (e.g. change `compute_due_date` or an assertion). Show the build failing at **Test**; refresh the app: still Build 15. Revert, push, show it pass (Build 17). |
| 6 | Backend Eng. | Persistence: `docker compose down` then `docker compose up -d --no-build`; records and notifications still there. Explain the named volume. |
| 7 | Project Lead | Rollback: `TAG=15 docker compose -p equipgo up -d --no-build`; footer shows Build 15. Explain image tagging. |
| 8 | Project Lead | Security note on the Docker socket, lessons learned, closing. |

**Tips:** rehearse twice on the recording machine; use a large terminal font; narrate the *why*;
keep the Stage View screenshot for the technical documentation.
