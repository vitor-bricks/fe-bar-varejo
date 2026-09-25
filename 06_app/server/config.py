"""Dual-mode auth: works both in Databricks Apps (service principal) and locally (CLI profile)."""
import os
from databricks.sdk import WorkspaceClient

IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))
_client = None


def get_workspace_client() -> WorkspaceClient:
    global _client
    if _client is None:
        if IS_DATABRICKS_APP:
            _client = WorkspaceClient()
        else:
            _client = WorkspaceClient(profile=os.environ.get("DATABRICKS_PROFILE", "fevm-stable"))
    return _client


def get_oauth_token() -> str:
    """OAuth bearer token for the current principal (used as Lakebase password and API auth)."""
    w = get_workspace_client()
    headers = w.config.authenticate()
    if isinstance(headers, dict) and "Authorization" in headers:
        return headers["Authorization"].split(" ", 1)[1]
    return getattr(w.config, "token", "") or ""


def get_workspace_host() -> str:
    if IS_DATABRICKS_APP:
        host = os.environ.get("DATABRICKS_HOST", "")
        if host and not host.startswith("http"):
            host = f"https://{host}"
        return host
    return get_workspace_client().config.host
