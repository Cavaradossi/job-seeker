"""Audit logging: append every application event to the tracker + a daily debrief.

Tracker schema: see doc/tracker_schema.md
    date,company,role,location,variant_used,jd_source,status,applied_via,response_date,notes

Privacy: the tracker (outputs/job_application_tracker.csv) and history/ are
gitignored — they hold real company names and dates and never get published.
"""
from __future__ import annotations

import csv
import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "outputs" / "job_application_tracker.csv"
HISTORY = ROOT / "history"

COLUMNS = [
    "date", "company", "role", "location", "variant_used", "jd_source",
    "status", "applied_via", "response_date", "notes",
]


def _today() -> str:
    return datetime.date.today().isoformat()


def _ensure_tracker() -> None:
    TRACKER.parent.mkdir(parents=True, exist_ok=True)
    if not TRACKER.exists():
        TRACKER.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")


def append_row(row: dict) -> Path:
    _ensure_tracker()
    r = {k: row.get(k, "") for k in COLUMNS}
    with TRACKER.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([r[k] for k in COLUMNS])
    return TRACKER


def log_event(jd, variant: Optional[str], pdf, status: str, applied_via: str,
              notes: str = "") -> Path:
    """Record one application event. `status` ∈ dry_run | degraded | submitted | user_cancelled | failed."""
    row = {
        "date": _today(),
        "company": getattr(jd, "company", "") or "",
        "role": getattr(jd, "title", "") or "",
        "location": getattr(jd, "location", "") or "",
        "variant_used": variant or "",
        "jd_source": getattr(jd, "url", "") or "",
        "status": status,
        "applied_via": applied_via,
        "response_date": "",
        "notes": notes,
    }
    path = append_row(row)

    HISTORY.mkdir(parents=True, exist_ok=True)
    debrief = HISTORY / f"apply_{_today()}.log"
    with debrief.open("a", encoding="utf-8") as f:
        f.write(
            f"[{_today()}] {status} | {row['company']} | {row['role']} | "
            f"variant={variant} | pdf={pdf} | via={applied_via} | {notes}\n"
        )
    return path
