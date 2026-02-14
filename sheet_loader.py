"""Load scholarship applications from Google Sheets (CSV export) or local CSV."""

import csv
import io
import urllib.request
from pathlib import Path

from config import SHEET_CSV_URL, COLUMNS, LOCAL_CSV_PATH

HEADER_MAP = {
    "University": "university",
    "Program": "program",
    "Scholarship": "scholarship",
    "Deadline": "deadline",
    "Application date": "application_date",
    "Application Status": "application_status",
    "Point of Entry": "point_of_entry",
    "Country": "country",
    "Link": "link",
}


def _normalize_row(raw_headers: list[str], row: list[str]) -> dict:
    out = {col: "" for col in COLUMNS}
    for i, raw in enumerate(raw_headers):
        h = raw.strip()
        key = HEADER_MAP.get(h)
        if key:
            out[key] = (row[i] if i < len(row) else "").strip()
    return out


def _fetch_csv(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "ScholarshipTracker/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        text = r.read().decode("utf-8", errors="replace")
    if not text.strip():
        return []
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    raw_headers = [h.strip().lstrip("\ufeff") for h in rows[0]]
    return [
        _normalize_row(raw_headers, row)
        for row in rows[1:]
        if any(cell.strip() for cell in row)
    ]


def load_from_sheet() -> list[dict]:
    return _fetch_csv(SHEET_CSV_URL)


def load_from_local(path: str | Path | None = None) -> list[dict]:
    path = path or Path(LOCAL_CSV_PATH)
    path = Path(path)
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    raw_headers = [h.strip().lstrip("\ufeff") for h in rows[0]]
    return [
        _normalize_row(raw_headers, row)
        for row in rows[1:]
        if any(cell.strip() for cell in row)
    ]


def load_scholarships(use_local_fallback: bool = True) -> list[dict]:
    try:
        data = load_from_sheet()
        if data:
            return data
    except Exception:
        pass
    if use_local_fallback:
        data = load_from_local()
        if data:
            return data
    return []
