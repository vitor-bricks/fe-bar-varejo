"""LojaBR · Centro de Abastecimento — FastAPI entrypoint (REST under /api, React build under /)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from server.routes import agent, genie, lakebase_status, network, overview, queue

app = FastAPI(title="LojaBR · Centro de Abastecimento", version="2.0.0")
for r in (overview, network, queue, agent, lakebase_status, genie):
    app.include_router(r.router)


@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "lojabr-abastecimento"}


DIST = Path(__file__).parent.resolve() / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        f = (DIST / full_path).resolve()
        if full_path and f.is_file() and DIST in f.parents:
            return FileResponse(f)
        return FileResponse(DIST / "index.html")
