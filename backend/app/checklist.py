"""Pure checklist logic: per-section progress and milestone celebrations."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"

def load_data() -> dict:
    return json.loads((DATA / "reentry_steps.json").read_text())

def celebrations_for(done_ids: set[int], data: dict | None = None) -> list[dict]:
    data = data or load_data()
    out = []
    if len(done_ids & {s["id"] for s in data["steps"]}) >= 1:
        out.append({"type": "first_step", "label": "First step done"})
    for sec in data["sections"]:
        ids = set(sec["step_ids"])
        if ids and ids <= done_ids:
            out.append({"type": "section_complete", "section": sec["id"], "section_title": sec["title"], "label": f"Section done: {sec['title']}"})
    all_ids = {s["id"] for s in data["steps"]}
    if all_ids and all_ids <= done_ids:
        out.append({"type": "all_complete", "label": "All 33 steps done"})
    return out

def section_progress(data: dict, done_ids: set[int], status_by_id: dict | None = None) -> list[dict]:
    out = []
    for sec in data["sections"]:
        ids = sec["step_ids"]
        done = sum(1 for i in ids if i in done_ids)
        out.append({"id": sec["id"], "title": sec["title"], "step_ids": ids, "total": len(ids), "done": done, "percent": round(100 * done / len(ids)) if ids else 0, "complete": done == len(ids) and len(ids) > 0})
    return out
