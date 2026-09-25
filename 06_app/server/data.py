"""
Data access for the Control Tower.

Primary source: Lakebase (Postgres) — operational, low-latency serving of the reorder
worklist, KPIs, availability and GenAI rationale. If Lakebase is unavailable, the same
questions are answered from the gold tables via the SQL warehouse (graceful fallback), so
the app always renders.
"""
import os, time
from .config import get_workspace_client, get_oauth_token

PGHOST = os.environ.get("PGHOST")
PGPORT = int(os.environ.get("PGPORT", "5432"))
PGDATABASE = os.environ.get("PGDATABASE", "retail")
PGUSER = os.environ.get("PGUSER")
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "")
GOLD = "serverless_stable_xpbmim_catalog.fe_bar_varejo_gold"

_last_source = "warehouse"


def _pg_query(sql):
    import psycopg2
    conn = psycopg2.connect(host=PGHOST, port=PGPORT, dbname=PGDATABASE, user=PGUSER,
                            password=get_oauth_token(), sslmode="require", connect_timeout=10)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [list(r) for r in cur.fetchall()]
        return cols, rows
    finally:
        conn.close()


def _wh_query(sql):
    w = get_workspace_client()
    resp = w.statement_execution.execute_statement(warehouse_id=WAREHOUSE_ID, statement=sql, wait_timeout="30s")
    sid = resp.statement_id
    for _ in range(20):
        state = resp.status.state.value if resp.status and resp.status.state else "PENDING"
        if state in ("SUCCEEDED", "FAILED", "CANCELED", "CLOSED"):
            break
        time.sleep(1)
        resp = w.statement_execution.get_statement(sid)
    cols = [c.name for c in resp.manifest.schema.columns]
    rows = resp.result.data_array or [] if resp.result else []
    return cols, [list(r) for r in rows]


def query(pg_sql, wh_sql):
    """Try Lakebase per request; on failure fall back to the warehouse for that request only
    (a transient Lakebase blip never permanently downgrades the app). Returns (cols, rows, source)."""
    global _last_source
    if PGHOST:
        try:
            cols, rows = _pg_query(pg_sql)
            _last_source = "lakebase"
            return cols, rows, "lakebase"
        except Exception as e:
            print(f"[data] Lakebase query failed, falling back to warehouse for this request: {e}")
    cols, rows = _wh_query(wh_sql)
    _last_source = "warehouse"
    return cols, rows, "warehouse"


def _dicts(cols, rows):
    return [dict(zip(cols, r)) for r in rows]


# ------------------------------------------------------------------ API methods
def health():
    ok, ms = True, None
    try:
        t0 = time.time()
        query("SELECT 1", "SELECT 1")
        ms = round((time.time() - t0) * 1000, 1)
    except Exception as e:
        ok = False
        print(f"[health] {e}")
    return {"ok": ok, "source": _last_source, "latency_ms": ms}


def kpis():
    cols, rows, src = query(
        "SELECT snapshot_date, stockout_rate, lost_units, lost_revenue, revenue, active_combos FROM kpi_daily ORDER BY snapshot_date",
        f"SELECT snapshot_date, stockout_rate, lost_units, lost_revenue, revenue, active_combos FROM {GOLD}.gold_kpi_daily ORDER BY snapshot_date")
    d = _dicts(cols, rows)
    latest = d[-1] if d else {}
    lost_total = sum(float(x["lost_revenue"] or 0) for x in d)
    rev_total = sum(float(x["revenue"] or 0) for x in d)
    days = len(d) or 1
    at_risk = risk_count()
    return {
        "source": src,
        "latest_date": str(latest.get("snapshot_date", "")),
        "stockout_rate": float(latest.get("stockout_rate", 0) or 0),
        "lost_revenue_today": float(latest.get("lost_revenue", 0) or 0),
        "revenue_today": float(latest.get("revenue", 0) or 0),
        "lost_revenue_period": round(lost_total, 2),
        "revenue_period": round(rev_total, 2),
        "lost_revenue_annualized": round(lost_total * 365 / days, 0),
        "items_at_risk": at_risk,
        "days": days,
    }


def risk_count():
    cols, rows, _ = query(
        "SELECT count(*) FROM current_availability WHERE risk_flag=1",
        f"SELECT count(*) FROM {GOLD}.gold_current_availability WHERE risk_flag=1")
    return int(rows[0][0]) if rows else 0


def trend():
    cols, rows, src = query(
        "SELECT snapshot_date, stockout_rate, lost_revenue, revenue FROM kpi_daily ORDER BY snapshot_date",
        f"SELECT snapshot_date, stockout_rate, lost_revenue, revenue FROM {GOLD}.gold_kpi_daily ORDER BY snapshot_date")
    return [{"date": str(r[0]), "stockout_rate": float(r[1] or 0),
             "lost_revenue": float(r[2] or 0), "revenue": float(r[3] or 0)} for r in rows]


def worklist(store=None, limit=50):
    where = f"WHERE store_id = '{store}'" if store else ""
    cols, rows, src = query(
        f"SELECT store_id, sku, category, region, on_hand_units, reorder_point, avg_units_7d, risk_probability, suggested_order_units, expected_lost_revenue_7d, risk_rank FROM stockout_predictions {where} ORDER BY risk_rank LIMIT {int(limit)}",
        f"SELECT store_id, sku, category, region, on_hand_units, reorder_point, avg_units_7d, risk_probability, suggested_order_units, expected_lost_revenue_7d, risk_rank FROM {GOLD}.gold_stockout_predictions {where} ORDER BY risk_rank LIMIT {int(limit)}")
    return {"source": src, "items": _dicts(cols, rows)}


def stores():
    cols, rows, _ = query(
        "SELECT DISTINCT store_id FROM stockout_predictions ORDER BY store_id",
        f"SELECT DISTINCT store_id FROM {GOLD}.gold_stockout_predictions ORDER BY store_id")
    return [r[0] for r in rows]


def regions():
    cols, rows, src = query(
        "SELECT region, round(sum(expected_lost_revenue_7d),2) exp_lost, count(*) n FROM stockout_predictions GROUP BY region ORDER BY exp_lost DESC",
        f"SELECT region, round(sum(expected_lost_revenue_7d),2) exp_lost, count(*) n FROM {GOLD}.gold_stockout_predictions GROUP BY region ORDER BY exp_lost DESC")
    return [{"region": r[0], "expected_lost_revenue_7d": float(r[1] or 0), "items": int(r[2])} for r in rows]


def rationale():
    cols, rows, src = query(
        "SELECT store_id, sku, category, risk_probability, expected_lost_revenue_7d, suggested_order_units, reorder_rationale FROM reorder_rationale ORDER BY expected_lost_revenue_7d DESC",
        f"SELECT store_id, sku, category, risk_probability, expected_lost_revenue_7d, suggested_order_units, reorder_rationale FROM {GOLD}.gold_reorder_rationale ORDER BY expected_lost_revenue_7d DESC")
    return {"source": src, "items": _dicts(cols, rows)}
