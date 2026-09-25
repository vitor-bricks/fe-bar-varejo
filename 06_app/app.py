"""FE Bar Varejo — Retail Intelligence Control Tower (FastAPI backend)."""
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import data, genie

app = FastAPI(title="LojaBR Varejo — Control Tower")

STATIC = os.path.join(os.path.dirname(__file__), "static")


@app.get("/api/health")
def api_health():
    return data.health()


@app.get("/api/kpis")
def api_kpis():
    return data.kpis()


@app.get("/api/trend")
def api_trend():
    return data.trend()


@app.get("/api/worklist")
def api_worklist(store: str = "", limit: int = 50):
    return data.worklist(store or None, limit)


@app.get("/api/stores")
def api_stores():
    return data.stores()


@app.get("/api/regions")
def api_regions():
    return data.regions()


@app.get("/api/rationale")
def api_rationale():
    return data.rationale()


class Ask(BaseModel):
    question: str


@app.post("/api/genie")
def api_genie(body: Ask):
    try:
        return genie.ask(body.question)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---- static SPA ----
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


@app.get("/{path:path}")
def spa(path: str):
    f = os.path.join(STATIC, path)
    if os.path.isfile(f):
        return FileResponse(f)
    return FileResponse(os.path.join(STATIC, "index.html"))
