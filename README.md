# CV Agentic SaaS MVP

[![CI](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/ci.yml)
[![Docker Publish](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/docker-publish.yml)
[![Release](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/release.yml/badge.svg)](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/release.yml)
[![Railway Deploy](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/railway-deploy.yml/badge.svg)](https://github.com/Anandharajan/cv-agentic-saas-mvp/actions/workflows/railway-deploy.yml)

Minimal agentic computer vision SaaS: background segmentation, image QA, and basic tagging with a FastAPI service.

## Quickstart

- Install: `pip install -r requirements.txt`
- Run API: `uvicorn src.infer:app --host 0.0.0.0 --port 8080`
- Example client: `python examples/demo_client.py`

See `CVAAS.md` for the playbook and roadmap.

## GitHub Deployment (GHCR)

- On push to `main`, GitHub Actions builds and pushes a Docker image to `ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`.
- On tag `vX.Y.Z`, the Release workflow also publishes a tagged image and uploads artifacts.

### Steps

- Ensure GitHub Actions has permission to publish packages: Repo Settings -> Actions -> General -> Workflow permissions -> enable Read and Write. Also set Packages visibility as needed.
- Push to `main`: the `Docker Publish` workflow will produce `:latest` and `:sha` tags.
- Tag a release: `git tag v0.1.0 && git push origin v0.1.0`.

### Run from GHCR

- `docker pull ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`
- `docker run -p 8080:8080 ghcr.io/<OWNER>/cv-agentic-saas-mvp:latest`

## One-Click Cloud (optional)

- Connect this repo to Render or Railway as a Docker service; use `Dockerfile` and port `8080`.

## Vercel Deploy

### Recommended approaches

- GitHub Integration (preferred): connect this repo in Vercel. Vercel builds and deploys on push. Configure the project to use the `Dockerfile` if your Vercel plan supports Docker-based deployments; otherwise use a Python Serverless Function wrapper (see below).
- Deploy Hook (added): workflow `.github/workflows/vercel-deploy.yml` calls a Vercel Deploy Hook on pushes/tags when `VERCEL_DEPLOY_HOOK_URL` secret is set.

### Setup (GitHub Integration)

- Create a Vercel account and install the Vercel GitHub App.
- Import this repository and select branch `main`.
- If Docker builds are supported on your plan: use the provided `Dockerfile` and set the port to `8080`.
- If not, use a Serverless Function wrapper:
  - Create `api/process.py` in a separate branch to call into `src.agents.skills.process_single` and handle uploads.
  - Move `templates/index.html` to `public/index.html` for static hosting.

### Setup (Deploy Hook)

- In Vercel -> Project -> Settings -> Git -> Deploy Hooks -> create a hook for branch `main` and copy the URL.
- In GitHub -> Repo -> Settings -> Secrets and variables -> Actions -> New repository secret:
  - `VERCEL_DEPLOY_HOOK_URL` = the copied Deploy Hook URL
- On push or tag, the Vercel Deploy workflow triggers the hook to redeploy.

### Open the app

- After Vercel finishes building, open the assigned URL. The UI is at `/` and `POST /process` accepts image uploads.

## Railway Deploy (optional)

### What it does

- Workflow `.github/workflows/railway-deploy.yml` deploys to Railway on pushes to `main` using the Railway CLI.

### Setup

- Create a Railway account and a new project.
- Locally: `npm i -g @railway/cli`, then in this repo run `railway init` (or `railway link`) to connect the project; commit the generated `.railway/` directory.
- In GitHub -> Repo -> Settings -> Secrets and variables -> Actions -> New repository secret:
  - `RAILWAY_TOKEN` = your Railway deploy token (`railway login` then `railway tokens create`).

### Deploy

- Push to `main` -> Actions -> Railway Deploy runs and rolls out the app.
- The workflow will skip if either `RAILWAY_TOKEN` is missing or `.railway/` is not present.

