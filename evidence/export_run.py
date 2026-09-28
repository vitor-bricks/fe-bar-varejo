#!/usr/bin/env python3
"""Export an executed Databricks notebook run (job task run) to Markdown WITH cell outputs.

The FE Bar evaluator reads text only, so this turns a real job run into a readable record:
each cell's source followed by the output it produced in that run.

Usage: python3 evidence/export_run.py <task_run_id> <out.md> [--profile fevm-stable]
"""
import base64, json, re, subprocess, sys, urllib.parse

run_id, out_path = sys.argv[1], sys.argv[2]
profile = sys.argv[sys.argv.index("--profile") + 1] if "--profile" in sys.argv else "fevm-stable"

exp = json.loads(subprocess.run(["databricks", "jobs", "export-run", run_id, "--views-to-export", "CODE",
                                 "-p", profile, "-o", "json"], capture_output=True, text=True).stdout)
html = exp["views"][0]["content"]
m = re.search(r"__DATABRICKS_NOTEBOOK_MODEL = '([^']+)'", html)
model = json.loads(urllib.parse.unquote(base64.b64decode(m.group(1)).decode("utf-8")))


def text_of(result):
    """Flatten a command result into plain text (stdout, tables, errors)."""
    if not result:
        return ""
    t, data = result.get("type"), result.get("data")
    if t == "listResults" and isinstance(data, list):
        return "\n".join(filter(None, (text_of(x) for x in data)))
    if t == "table" and isinstance(data, list):
        cols = [c.get("name", "") for c in result.get("schema", [])]
        lines = [" | ".join(cols)] + [" | ".join("" if v is None else str(v) for v in row) for row in data[:25]]
        return "\n".join(lines)
    if t == "error" or result.get("cause"):
        return "ERROR: " + re.sub(r"\x1b\[[0-9;]*m", "", str(result.get("summary") or result.get("cause") or ""))[:2000]
    if isinstance(data, str):
        if t == "html" or data.lstrip().startswith("<"):
            return re.sub(r"\s+\n", "\n", re.sub(r"<[^>]+>", " ", data)).strip()
        return re.sub(r"\x1b\[[0-9;]*m", "", data)
    return ""


lines = [f"# Executed notebook — {model.get('name')}", "",
         f"Job task run `{run_id}` · exported with cell outputs (`databricks jobs export-run`).", ""]
for cmd in sorted(model.get("commands", []), key=lambda c: c.get("position", 0)):
    src = cmd.get("command", "").strip()
    if src.startswith("%md"):
        lines += [re.sub(r"^%md\s?", "", src, flags=re.M), ""]
        continue
    lines += ["```python", src, "```"]
    out = text_of(cmd.get("results")).strip()
    if out:
        lines += ["", "**Output**", "", "```text", out[:6000], "```"]
    lines.append("")
open(out_path, "w").write("\n".join(lines))
print(f"wrote {out_path} ({len(model.get('commands', []))} cells)")
