"""Configuration & dual-mode auth (local CLI profile vs Databricks Apps service principal).

Same pattern as the LojaBR War Room app.
"""
from __future__ import annotations

import os
from functools import lru_cache

IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))

GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f1b906cf2d15b4b1c72c3b25ddb2f0")
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "38762a7d9e9e5b33")
LAKEBASE_HOST = os.environ.get("LAKEBASE_HOST", "ep-royal-silence-d24b1cks.database.us-east-1.cloud.databricks.com")
LAKEBASE_DB = os.environ.get("LAKEBASE_DB", "retail")
LAKEBASE_PORT = int(os.environ.get("LAKEBASE_PORT", "5432"))
LAKEBASE_ENDPOINT = os.environ.get("LAKEBASE_ENDPOINT", "projects/fe-bar-varejo/branches/production/endpoints/primary")
LOCAL_PROFILE = os.environ.get("DATABRICKS_PROFILE", "fevm-stable")


@lru_cache(maxsize=1)
def get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient() if IS_DATABRICKS_APP else WorkspaceClient(profile=LOCAL_PROFILE)


def get_current_user_email(request=None) -> str:
    """The Apps gateway forwards the signed-in user's identity; used as the author of approvals."""
    if request is not None:
        for header in ("x-forwarded-email", "x-forwarded-preferred-username", "x-forwarded-user"):
            v = request.headers.get(header)
            if v:
                return v
    try:
        me = get_workspace_client().current_user.me()
        return me.user_name or me.display_name or "unknown"
    except Exception:
        return os.environ.get("USER", "unknown")
