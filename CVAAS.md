# Codex CLI Playbook — Agentic SaaS MVP (CV-as-a-Service)

> **Goal:** Use **Codex CLI** to spin up a production-grade, *agentic* MVP that solves a clear customer pain point, targets a defined ICP, and ships to GitHub with CI/CD, Dockerized inference, and release artifacts. This playbook is step-by-step and “ready to paste” into your terminal.

> **Base template:** This plan extends the repo skeleton and CI patterns in your attached file (training, ONNX/TensorRT export, FastAPI service, CI). 

---

## 1) Problem, ICP, and MVP Scope

### 1.1 Pain Point (pick one tightly scoped)

**Automated product image QA + tagging for SMB e-commerce**
Merchants waste hours cleaning backgrounds, tagging attributes, and checking image quality. Errors hurt conversion and SEO.

### 1.2 Ideal Customer Profile (ICP) — checklist

* [ ] Region: India/SEA SMB e-commerce sellers (Shopify/WooCommerce), 10–1000 SKUs/month
* [ ] Roles: Store owners/ops leads without in-house ML
* [ ] Must-have signals: frequent image uploads, manual tagging backlog, marketplace rejections for poor imagery
* [ ] Willing to pay: ₹5k–₹50k/month for >50% time savings and fewer listing rejections
* [ ] Data availability: access to product images via S3/Drive/Shopify APIs
* [ ] Success metric: ≥50% reduction in manual edits; ≤1% false background-keep; attribute tagging precision@5 ≥0.9

### 1.3 MVP “One Big Thing”

**Ship a single API & minimal dashboard that:**

1. **Segments** product foreground for clean background (white/transparent),
2. **Detects** quality issues (blurry, low-res, clutter),
3. **Tags** basic attributes (category, color, material), and
4. Returns a **ready-to-list** image + JSON metadata.

**Out of scope (for now):** custom fine-tuning UI, multi-tenant billing, advanced workflows.

---

## 2) System Architecture (high level)

* **Agentic layer (Planner/Workers):** Plans tasks per image batch, calls skills (segment, tag, QA), routes failures, and triggers export/optimization/deploy.
* **Model layer:** Detector/Segmenter/Classifier (PyTorch), export to ONNX, optional TensorRT.
* **API:** FastAPI `POST /process` (single) and `POST /batch` (async).
* **Queue/Workers:** Simple `rq` (Redis) or Celery; start with in-process workers for MVP CI smoke.
* **Storage:** Local `data/` for MVP; swap to S3/GCS later.
* **CI/CD:** GitHub Actions (lint/test/build Docker/release).
* **Observability:** minimal request logs, latency, throughput, error codes; simple Prometheus endpoint or logs-first.

---

## 3) Repo Layout (augmented)

We reuse and extend the structure from the attached file. New agentic modules are marked **NEW**.

```
.
├── src/
│   ├── agents/                     # **NEW** agentic orchestration
│   │   ├── planner.py              # LLM-free, rules-first planner for MVP
│   │   ├── skills.py               # call segment/detect/classify; compose results
│   │   └── worker.py               # background job runner (in-proc or rq)
│   ├── models/
│   │   ├── detector.py
│   │   ├── segmenter.py
│   │   └── classifier.py
│   ├── data/loader.py
│   ├── utils/{logger.py,metrics.py}
│   ├── train.py
│   ├── eval.py
│   └── infer.py                    # FastAPI service (extended with /process)
├── tools/
│   ├── export_onnx.py
│   └── optimize_tensorrt.py
├── scripts/
│   ├── download_datasets.py
│   ├── run_experiment.sh
│   └── benchmark_inference.py
├── examples/{demo_client.py,edge_run.py}
├── docs/{architecture.md,deployment.md,benchmarks.md}
├── configs/                        # **NEW** tiny YAMLs for tasks & thresholds
│   ├── mvp.yaml
│   └── thresholds.yaml
├── .github/workflows/{ci.yml,release.yml}
├── Dockerfile
├── requirements.txt
├── Makefile                        # **NEW** dev ergonomics
├── .env.example                    # **NEW** runtime envs
└── README.md
```

---

## 4) Step-by-Step: Create & Push the Repo with Codex CLI

> Replace placeholders before running.

```bash
# ---------- Variables ----------
GITHUB_USER="<GITHUB_ORG_OR_USER>"
REPO_NAME="cv-agentic-saas-mvp"
EMAIL="<YOUR_EMAIL>"

# ---------- Create & clone ----------
codex repo create $GITHUB_USER/$REPO_NAME --public \
  --description "Agentic CV SaaS MVP: segmentation, QA, tagging + API, Docker, CI"

git clone https://github.com/$GITHUB_USER/$REPO_NAME.git
cd $REPO_NAME
git config user.email "$EMAIL"
git config user.name "$GITHUB_USER"

# ---------- Scaffolding ----------
mkdir -p src/{agents,models,data,utils} tools examples scripts docs configs .github/workflows results
touch README.md LICENSE .gitignore requirements.txt environment.yml Dockerfile Makefile .env.example \
  src/{train.py,eval.py,infer.py} \
  src/models/{__init__.py,backbones.py,detector.py,segmenter.py,classifier.py} \
  src/data/loader.py src/utils/{logger.py,metrics.py} \
  src/agents/{planner.py,skills.py,worker.py} \
  tools/{export_onnx.py,optimize_tensorrt.py} \
  scripts/{download_datasets.py,benchmark_inference.py,run_experiment.sh} \
  examples/{demo_client.py,edge_run.py} \
  docs/{architecture.md,deployment.md,benchmarks.md} \
  .github/workflows/{ci.yml,release.yml} \
  configs/{mvp.yaml,thresholds.yaml}

# ---------- First commit ----------
git add .
git commit -m "chore(init): agentic CV SaaS MVP skeleton"
git push -u origin main
```

---

## 5) File Contents — Copy/Paste Minimums

> These give Codex enough structure to implement & iterate. They extend the templates from your attached file (training loop, FastAPI service, ONNX export, CI). 

### 5.1 `.gitignore`

```
__pycache__/
*.pyc
.env
data/
runs/
models/
results/
*.log
.vscode/
.DS_Store
```

### 5.2 `requirements.txt`

```
torch>=1.12
torchvision
onnx
onnxruntime
fastapi
uvicorn
pydantic
opencv-python
albumentations
numpy
Pillow
tqdm
pyyaml
rq            # simple queue (optional; can remove if in-proc)
redis         # if you enable rq worker
```

### 5.3 `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "src.infer:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 5.4 `Makefile`

```makefile
.PHONY: dev run test docker build push
dev:            ## install deps
	pip install -r requirements.txt
run:            ## run API
	uvicorn src.infer:app --host 0.0.0.0 --port 8080
test:           ## smoke tests
	python scripts/download_datasets.py --dest data/
	python src/train.py --task classify --small
docker:         ## build image
	docker build -t $(REPO_NAME):local .
```

### 5.5 `src/infer.py` (extend to MVP endpoints)

```python
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
from io import BytesIO
from PIL import Image

from src.agents.skills import process_single
from src.agents.worker import enqueue_batch

app = FastAPI(title="CV Agentic SaaS MVP")

class ProcessResult(BaseModel):
    status: str
    width: int
    height: int
    tags: dict
    qa: dict
    output_url: str | None

@app.post("/process", response_model=ProcessResult)
async def process(file: UploadFile = File(...)):
    content = await file.read()
    img = Image.open(BytesIO(content)).convert("RGB")
    result = process_single(img)  # segment -> qa -> tag
    return result

@app.post("/batch")
async def batch(background_tasks: BackgroundTasks, files: list[UploadFile]):
    payload = [await f.read() for f in files]
    job_id = enqueue_batch(payload)   # async job
    return {"job_id": job_id, "status": "queued"}
```

### 5.6 `src/agents/skills.py` (agentic “skills”)

```python
from PIL import Image
from pydantic import BaseModel

class Result(BaseModel):
    status: str = "ok"
    width: int = 0
    height: int = 0
    tags: dict = {}
    qa: dict = {}
    output_url: str | None = None

def segment_foreground(img: Image.Image) -> Image.Image:
    # TODO: call segmenter; MVP returns original
    return img

def quality_check(img: Image.Image) -> dict:
    # TODO: simple heuristics (size, sharpness proxy)
    w, h = img.size
    return {"min_size_ok": w*h >= 512*512, "sharpness": "tbd"}

def tag_attributes(img: Image.Image) -> dict:
    # TODO: classifier or color histogram
    return {"category": "unknown", "dominant_color": "tbd"}

def save_output(img: Image.Image) -> str | None:
    # TODO: write to local disk or S3; return URL/path
    return None

def process_single(img: Image.Image) -> Result:
    seg = segment_foreground(img)
    qa = quality_check(seg)
    tags = tag_attributes(seg)
    out_url = save_output(seg)
    r = Result(width=img.size[0], height=img.size[1], tags=tags, qa=qa, output_url=out_url)
    return r.dict()
```

### 5.7 `src/agents/planner.py` (rules-first planner)

```python
def plan(tasks: list[str]) -> list[str]:
    # Deterministic plan: segment -> qa -> tag -> export (optional)
    ordered = []
    if "segment" in tasks: ordered.append("segment")
    if "qa" in tasks:       ordered.append("qa")
    if "tag" in tasks:      ordered.append("tag")
    return ordered
```

### 5.8 `src/agents/worker.py` (in-process, with optional RQ)

```python
import os, uuid
from typing import List
try:
    import rq, redis
    RQ = True
except Exception:
    RQ = False

def enqueue_batch(payloads: List[bytes]) -> str:
    job_id = str(uuid.uuid4())
    # MVP: no real queue processing; extend to rq later
    # if RQ: enqueue to Redis queue
    return job_id
```

### 5.9 `configs/mvp.yaml`

```yaml
mvp:
  steps: ["segment", "qa", "tag"]
  export: false
```

### 5.10 `configs/thresholds.yaml`

```yaml
qa:
  min_pixels: 262144   # 512*512
  blur_threshold: 50   # TODO: Laplacian var heuristic
```

> **Note:** Keep training/export/CI files from your base template; fill in real model code as you iterate. 

---

## 6) CI/CD & Quality Gates

### 6.1 `.github/workflows/ci.yml` (augment smoke)

* Install deps → prepare tiny data → run smoke train (`--small`) → start API → hit `/process` with a sample.

### 6.2 `.github/workflows/release.yml`

* On tag: build Docker, push image, attach release artifacts (ONNX files, example client).

### 6.3 DevEx & Standards

* **Conventional Commits**, **Semantic Versioning**
* **Formatting/Linting:** `ruff`, `black` (optional)
* **Tests:** add a couple of unit tests for `skills.py`

---

## 7) Security, Privacy, and Ops (MVP level)

* **Secrets:** use GitHub Actions secrets for any keys (none needed for local MVP).
* **Input validation:** accept images only; limit size; sanitize metadata.
* **Privacy:** don’t store originals by default; only derived outputs if asked.
* **Observability:** simple request logs with latency, outcome; later add `/metrics`.

---

## 8) API Contract (for customers)

```
POST /process (multipart/form-data)
  file: image/*
Response 200:
{
  "status": "ok",
  "width": 1024,
  "height": 1024,
  "tags": {"category":"shoe","dominant_color":"black"},
  "qa": {"min_size_ok": true, "sharpness": "tbd"},
  "output_url": "s3://.../image.png"
}

POST /batch (multipart/form-data)
  files: image[]  (up to 50 for MVP)
Response 202: {"job_id":"<uuid>","status":"queued"}
```

---

## 9) PMF Loop & Launch Checklist

### 9.1 Success Metrics

* Time saved per 100 images (target: >50%)
* % auto-accepted by marketplaces (target: >95%)
* Precision@5 for tags (≥0.9)
* p95 latency `/process` < 1.5s on CPU container

### 9.2 Feedback Loop

* Add “reason codes” in QA (why an image failed)
* Telemetry: count failure modes (blurry, low-res)
* Weekly customer call; prioritize one blocker/week

### 9.3 Launch Steps

1. Ship public GitHub repo (MIT/Apache-2.0)
2. Publish Docker image (GHCR or Docker Hub)
3. Post a short Loom + README quickstart
4. Offer 7-day pilot to 3–5 SMB stores

---

## 10) Running Locally

```bash
# 1) Install
pip install -r requirements.txt

# 2) Prepare tiny data
python scripts/download_datasets.py --dest data/

# 3) Smoke train (CI-size)
python src/train.py --task classify --small

# 4) Run API
uvicorn src.infer:app --host 0.0.0.0 --port 8080

# 5) Call API (example)
python examples/demo_client.py
```

---

## 11) Export & Optimization (optional in MVP)

```bash
# Export ONNX (placeholder creates file; replace with real export later)
python tools/export_onnx.py --ckpt runs/classify/best.pt --out models/mvp.onnx

# (Optional) TensorRT optimize for GPU targets
python tools/optimize_tensorrt.py --onnx models/mvp.onnx --out models/mvp-trt.plan
```

> Mirrors the export/optimization flow from your base template. 

---

## 12) What Codex Should Implement Next (in order)

1. **Fill `segment_foreground`** with a lightweight UNet/DeepLabV3 and background matting.
2. **Implement `quality_check`** (min size, Laplacian variance for blur).
3. **Implement `tag_attributes`** with a tiny classifier + color histogram.
4. **Unit tests** for skills; add mAP/mIoU/top-k metrics.
5. **Replace placeholders** in `export_onnx.py`; add parity checks.
6. **CI**: request/response smoke; artifact upload (sample outputs).
7. **Docs**: `docs/architecture.md` diagrams & `docs/deployment.md` steps.

---

## 13) Licensing, Pricing, and Next Iterations

* **License:** MIT/Apache-2.0 for code; models under respective licenses.
* **Pricing (pilot):** Free 7 days → ₹5k/mo includes 10k images; overage ₹0.25/image.
* **Near-term roadmap:** Shopify/WooCommerce app, S3 ingest, basic dashboard, retries/review queue.

---

### Attribution

* Repo scaffolding, CI smoke tests, Dockerized inference, and export steps build directly upon the structure described in your attached instructions. 

---

**You’re set.** Run the commands in §4 to create the repo with Codex CLI, paste in the file contents from §5, and iterate per §12 to reach a usable, agentic MVP that targets a tight ICP and a single painful job-to-be-done.
