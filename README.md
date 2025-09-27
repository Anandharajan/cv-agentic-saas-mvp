# CV Agentic SaaS MVP

Minimal agentic computer vision SaaS: background segmentation, image QA, and basic tagging with a FastAPI service.

Quickstart
- Install: `pip install -r requirements.txt`
- Run API: `uvicorn src.infer:app --host 0.0.0.0 --port 8080`
- Example client: `python examples/demo_client.py`

See CVAAS.md for the playbook and roadmap.

## GitHub Deployment (GHCR)

- On push to `main`, GitHub Actions builds and pushes a Docker image to `ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`.
- On tag `vX.Y.Z`, the Release workflow also publishes a tagged image and uploads artifacts.

Steps
- Ensure GitHub Actions has permission to publish packages: Repo Settings -> Actions -> General -> Workflow permissions -> enable Read and Write. Also Settings -> Packages visibility as needed.
- Push to main: the `Docker Publish` workflow will produce `:latest` and `:sha` tags.
- Tag a release: `git tag v0.1.0 && git push origin v0.1.0`.

Run from GHCR
- `docker pull ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`
- `docker run -p 8080:8080 ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`

One-click cloud deploy (optional)
- Connect this repo to Render or Railway as a Docker service; use `Dockerfile` and port `8080`.
- Or use Fly.io with a `fly.toml` and deploy via GitHub Actions (ask to scaffold).

## Fly.io Deploy via GitHub Actions

What it does
- Workflow `.github/workflows/fly-deploy.yml` deploys the app to Fly.io on pushes to `main` using `fly.toml`.

Setup
- Create a Fly.io account and install `flyctl` locally (optional for initial app creation).
- Generate a Fly API token: `flyctl auth token`.
- In GitHub → Repo → Settings → Secrets and variables → Actions → New repository secret:
  - `FLY_API_TOKEN` = your token
- Optionally rename the app in `fly.toml` if `cv-agentic-saas-mvp` is taken.

Deploy
- Push to `main` → Actions → Fly Deploy runs and rolls out the app.
- After first deploy, find your URL via the job logs or `flyctl status -a <app>`.
