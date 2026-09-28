"""Lakebase (Postgres) helper — cached OAuth credential + per-call connection, with the latency
of every read recorded so the app can show p50/p95/p99 of its real serving traffic.

Credential model (same as the War Room app): mint a ~1h token from
`/api/2.0/postgres/credentials`, cache it for 50 min, re-mint on auth failure.
In Apps the Postgres role is the service principal's client id; locally, the user's email.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from collections import deque
from contextlib import contextmanager
from typing import Any, Optional

import psycopg2
import psycopg2.extras

from .config import LAKEBASE_DB, LAKEBASE_ENDPOINT, LAKEBASE_HOST, LAKEBASE_PORT, get_current_user_email, get_workspace_client

log = logging.getLogger(__name__)
_TOKEN_TTL_S = 50 * 60
_lock = threading.Lock()
_cached: Optional[tuple[float, str]] = None
LATENCIES_MS: deque[float] = deque(maxlen=2000)   # rolling window of real read latencies


def _token(force: bool = False) -> str:
    global _cached
    with _lock:
        if not force and _cached and time.monotonic() - _cached[0] < _TOKEN_TTL_S:
            return _cached[1]
        w = get_workspace_client()
        try:
            tok = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": LAKEBASE_ENDPOINT})["token"]
        except Exception as exc:   # principal without credential-mint rights: its workspace OAuth token also authenticates
            log.warning("postgres/credentials failed (%s); falling back to workspace OAuth token", exc)
            tok = w.config.authenticate()["Authorization"].split(" ", 1)[1]
        _cached = (time.monotonic(), tok)
        return tok


def _user() -> str:
    return os.environ.get("DATABRICKS_CLIENT_ID") or get_current_user_email()


_POOL: list = []            # idle connections (small LIFO pool, thread-safe via _pool_lock)
_pool_lock = threading.Lock()
_POOL_MAX = 8


def _new_conn():
    kw = dict(host=LAKEBASE_HOST, port=LAKEBASE_PORT, dbname=LAKEBASE_DB, user=_user(), sslmode="require",
              connect_timeout=10, keepalives=1, keepalives_idle=30)
    try:
        conn = psycopg2.connect(password=_token(), **kw)
    except psycopg2.OperationalError as exc:
        log.warning("Lakebase connect failed, retrying with a fresh token: %s", exc)
        conn = psycopg2.connect(password=_token(force=True), **kw)
    conn.autocommit = True     # one round trip per statement; writes commit immediately
    return conn


@contextmanager
def connect():
    """Borrow a pooled connection (TLS + auth handshake paid once, not per query)."""
    with _pool_lock:
        conn = _POOL.pop() if _POOL else None
    if conn is None or conn.closed:
        conn = _new_conn()
    ok = True
    try:
        yield conn
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        ok = False
        raise
    finally:
        if ok and not conn.closed:
            with _pool_lock:
                if len(_POOL) < _POOL_MAX:
                    _POOL.append(conn); conn = None
        if conn is not None:
            conn.close()


def _run(fn):
    """Run fn(conn); if the pooled connection went stale (idle timeout), retry once on a fresh one."""
    try:
        with connect() as conn:
            return fn(conn)
    except (psycopg2.OperationalError, psycopg2.InterfaceError) as exc:
        log.info("stale Lakebase connection, retrying: %s", exc)
        with connect() as conn:
            return fn(conn)


def query(sql: str, params: Any = None) -> list[dict]:
    def fn(conn):
        t0 = time.perf_counter()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(r) for r in cur.fetchall()]
        LATENCIES_MS.append((time.perf_counter() - t0) * 1000)
        return rows
    return _run(fn)


def execute(sql: str, params: Any = None) -> None:
    def fn(conn):
        with conn.cursor() as cur:
            cur.execute(sql, params)
    _run(fn)


def latency_stats() -> dict:
    xs = sorted(LATENCIES_MS)
    if not xs:
        return {"calls": 0}
    pct = lambda p: round(xs[min(len(xs) - 1, int(p * len(xs)))], 1)
    return {"calls": len(xs), "p50": pct(0.50), "p95": pct(0.95), "p99": pct(0.99),
            "min": round(xs[0], 1), "max": round(xs[-1], 1), "mean": round(sum(xs) / len(xs), 1)}
