from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from src.agents.skills import process_single
from src.agents.worker import enqueue_batch

app = FastAPI(title="CV Agentic SaaS MVP")

# Static mount for saved outputs
DEFAULT_STORAGE = os.environ.get("STORAGE_DIR") or str(Path("data/outputs").resolve())
os.makedirs(DEFAULT_STORAGE, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=DEFAULT_STORAGE), name="outputs")


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
    # Map filesystem path to served URL if present
    out_path = result.get("output_url")
    if out_path and os.path.exists(out_path):
        result["output_url"] = f"/outputs/{os.path.basename(out_path)}"
    return result


@app.post("/batch")
async def batch(background_tasks: BackgroundTasks, files: list[UploadFile]):
    payload = [await f.read() for f in files]
    job_id = enqueue_batch(payload)  # async job (MVP placeholder)
    return {"job_id": job_id, "status": "queued"}


@app.get("/", response_class=HTMLResponse)
async def index():
    tpl = Path("templates/index.html")
    if tpl.exists():
        return HTMLResponse(tpl.read_text(encoding="utf-8"))
    # Fallback inline HTML
    return HTMLResponse("""
<!doctype html>
<html>
<head><meta charset=\"utf-8\"><title>CV Agentic SaaS MVP</title></head>
<body>
  <h1>CV Agentic SaaS MVP</h1>
  <input type="file" id="fileInput" accept="image/*" />
  <button id="sendBtn">Process</button>
  <pre id="out"></pre>
  <div id="imgBox"></div>
  <script>
    const btn = document.getElementById('sendBtn');
    btn.onclick = async () => {
      const f = document.getElementById('fileInput').files[0];
      if (!f) { alert('Choose an image'); return; }
      const fd = new FormData();
      fd.append('file', f, f.name);
      const r = await fetch('/process', { method: 'POST', body: fd });
      const j = await r.json();
      document.getElementById('out').textContent = JSON.stringify(j, null, 2);
      const imgBox = document.getElementById('imgBox');
      imgBox.innerHTML = '';
      if (j.output_url) {
        const img = document.createElement('img');
        img.src = j.output_url;
        img.style.maxWidth = '400px';
        imgBox.appendChild(img);
      }
    };
  </script>
  </body></html>
    """)
