import os
import uuid
import base64
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

_key = os.getenv("OPENAI_API_KEY", "")
print(f"[startup] OPENAI_API_KEY present: {bool(_key)}, length: {len(_key)}")

from build_graph import workflow
from schemas import EssayState
from utils import resolve_annotations, render_annotated_essay, get_criterion_color
from donation import build_upi_url, generate_qr_bytes

# ---------------------------------------------------------------------------
# In-memory task store
# ---------------------------------------------------------------------------
tasks: dict[str, dict] = {}


async def _cleanup_expired_tasks():
    while True:
        await asyncio.sleep(300)
        now = asyncio.get_event_loop().time()
        expired = [k for k, v in tasks.items() if now - v["created_at"] > 1800]
        for k in expired:
            del tasks[k]


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_cleanup_expired_tasks())
    yield
    task.cancel()


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "")
templates.env.globals["adsense_client_id"] = ADSENSE_CLIENT_ID


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/ads.txt")
async def ads_txt():
    return FileResponse("static/ads.txt", media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/evaluate")
async def evaluate(request: Request, topic: str = Form(...), essay: str = Form(...)):
    if not topic.strip() or not essay.strip():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Please provide both topic and essay.",
            "topic": topic,
            "essay": essay,
        })

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "topic": topic,
        "essay": essay,
        "result": None,
        "created_at": asyncio.get_event_loop().time(),
    }

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _run_evaluation, task_id)

    return RedirectResponse(f"/loading/{task_id}", status_code=303)


def _run_evaluation(task_id: str):
    task = tasks[task_id]
    try:
        initial_state: EssayState = {
            "topic": task["topic"],
            "essay": task["essay"],
            "overall": "",
        }
        result = workflow.invoke(initial_state)
        task["result"] = result
        task["status"] = "done"
    except Exception as e:
        task["status"] = "error"
        task["error_msg"] = str(e)


@app.get("/loading/{task_id}", response_class=HTMLResponse)
async def loading(request: Request, task_id: str):
    if task_id not in tasks:
        return RedirectResponse("/")
    if tasks[task_id]["status"] == "done":
        return RedirectResponse(f"/results/{task_id}")
    return templates.TemplateResponse("loading.html", {
        "request": request,
        "task_id": task_id,
    })


@app.get("/api/status/{task_id}")
async def task_status(task_id: str):
    if task_id not in tasks:
        return JSONResponse({"status": "not_found"}, status_code=404)
    task = tasks[task_id]
    resp: dict = {"status": task["status"]}
    if task["status"] == "done":
        resp["redirect"] = f"/results/{task_id}"
    elif task["status"] == "error":
        resp["error"] = task.get("error_msg", "Unknown error")
    return JSONResponse(resp)


@app.get("/results/{task_id}", response_class=HTMLResponse)
async def results(request: Request, task_id: str, criterion: str | None = None):
    if task_id not in tasks or tasks[task_id]["status"] != "done":
        return RedirectResponse("/")

    task = tasks[task_id]
    result = task["result"]
    essay_text = task["essay"]

    # Build raw annotations from all criteria
    raw_annotations = []
    for crit_key, evaluation in result.get("evaluations", {}).items():
        annotations = getattr(evaluation, "annotations", None) or []
        for ann in annotations:
            raw_annotations.append({
                "quote": ann.quote,
                "paragraph_number": ann.paragraph_number,
                "type": crit_key,
                "severity": ann.severity,
                "message": ann.issue,
                "impact": ann.impact,
                "suggestions": [ann.suggestion],
            })

    # Filter by criterion if requested
    if criterion and criterion in result.get("evaluations", {}):
        filtered = [a for a in raw_annotations if a["type"] == criterion]
        resolved = resolve_annotations(essay_text, filtered, allow_overlaps=True)
        filter_label = criterion
    else:
        resolved = resolve_annotations(essay_text, raw_annotations, allow_overlaps=False)
        filter_label = None

    annotated_html = render_annotated_essay(essay_text, resolved)

    # Prepare criterion card data
    criteria_data = []
    for key, evaluation in result.get("evaluations", {}).items():
        criteria_data.append({
            "key": key,
            "name": key.replace("_", " ").title(),
            "rating": getattr(evaluation, "rating", ""),
            "feedback": getattr(evaluation, "feedback", ""),
            "color": get_criterion_color(key),
        })

    return templates.TemplateResponse("results.html", {
        "request": request,
        "task_id": task_id,
        "topic": task["topic"],
        "score": result.get("score", 0),
        "overall": result.get("overall", ""),
        "strengths": result.get("strengths", []),
        "weaknesses": result.get("weaknesses", []),
        "annotated_html": annotated_html,
        "criteria_data": criteria_data,
        "resolved_count": len(resolved),
        "total_annotations": len(raw_annotations),
        "filter_label": filter_label,
    })


@app.get("/api/qr/{amount}")
async def qr_code(amount: int):
    upi_url = build_upi_url(amount if amount > 0 else None)
    qr_bytes = generate_qr_bytes(upi_url)
    b64 = base64.b64encode(qr_bytes).decode()
    return JSONResponse({
        "qr_data_url": f"data:image/png;base64,{b64}",
        "upi_url": upi_url,
    })
