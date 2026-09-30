"""Workspace deep-links for the architecture view (skill databricks-arch-diagram · deep-links.md).

IDs live in config/app.json (``${VAR:default}`` resolved from env); URLs are composed here from the
workspace host, so the client never needs to know it. Missing id or host → empty url → inert tile.
"""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter

from ..config import get_workspace_client

router = APIRouter()
CONFIG = Path(__file__).resolve().parents[2] / "config" / "app.json"


@lru_cache(maxsize=1)
def _config() -> dict:
    text = re.sub(r"\$\{(\w+)(?::([^}]*))?\}", lambda m: os.environ.get(m.group(1)) or (m.group(2) or ""), CONFIG.read_text())
    return json.loads(text)


def _host() -> str:
    try:
        host = get_workspace_client().config.host or ""
    except Exception:
        host = os.environ.get("DATABRICKS_HOST", "")
    host = host.rstrip("/")
    return host if not host or host.startswith("http") else f"https://{host}"


@router.get("/api/resources")
def resources():
    c, host = _config(), _host()
    d, nb = c["data"], c["notebooks"]
    model = c["mlModelName"].replace(".", "/")

    def link(path: str, *ids: str) -> str:
        return f"{host}{path}" if host and all(ids) else ""

    items = {
        "job": (c["jobId"], link(f"/jobs/{c['jobId']}", c["jobId"])),
        "pipeline": (c["pipelineId"], link(f"/pipelines/{c['pipelineId']}", c["pipelineId"])),
        "genie": (c["genieSpaceId"], link(f"/genie/rooms/{c['genieSpaceId']}", c["genieSpaceId"])),
        "lakebase": (c["lakebaseProjectId"], link(f"/lakebase/projects/{c['lakebaseProjectId']}", c["lakebaseProjectId"])),
        "app": (c["appName"], link(f"/apps/{c['appName']}", c["appName"])),
        "catalog": (d["gold"], link(f"/explore/data/{d['catalog']}/{d['gold']}", d["gold"])),
        "model": (c["mlModelName"], link(f"/explore/data/models/{model}", c["mlModelName"])),
        "volume": (d["volume"], link(f"/explore/data/volumes/{d['catalog']}/{d['bronze']}/{d['volume']}", d["volume"])),
        **{f"nb_{k}": (v, link(f"/editor/notebooks/{v}", v)) for k, v in nb.items()},
    }
    return {k: {"id": i, "url": u} for k, (i, u) in items.items()}
