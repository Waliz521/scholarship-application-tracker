"""Load scholarship applications from Google Sheets (CSV export) or local CSV."""

import csv
import io
import urllib.request
from pathlib import Path

from config import SHEET_CSV_URL, COLUMNS, LOCAL_CSV_PATH

# Exact and normalized (lowercase) header -> our column key
HEADER_MAP = {
    "University": "university",
    "Program": "program",
    "Scholarship": "scholarship",
    "Deadline": "deadline",
    "Application date": "application_date",
    "Application Date": "application_date",
    "Application Status": "application_status",
    "Point of Entry": "point_of_entry",
    "Country": "country",
    "Link": "link",
}
HEADER_MAP_LOWER = {k.lower().strip(): v for k, v in HEADER_MAP.items()}

# Fallback: column index -> key (sheet order A-I)
COLUMN_INDEX_MAP = {i: col for i, col in enumerate(COLUMNS)}


def _header_to_key(h: str) -> str | None:
    h = h.strip()
    if not h:
        return None
    if h in HEADER_MAP:
        return HEADER_MAP[h]
    return HEADER_MAP_LOWER.get(h.lower())


def _normalize_row(raw_headers: list[str], row: list[str], use_index_fallback: bool = False) -> dict:
    out = {col: "" for col in COLUMNS}
    if use_index_fallback and len(raw_headers) >= len(COLUMNS):
        for i, col in enumerate(COLUMNS):
            if i < len(row):
                out[col] = (row[i] or "").strip()
        return out
    for i, raw in enumerate(raw_headers):
        key = _header_to_key(raw)
        if key:
            out[key] = (row[i] if i < len(row) else "").strip()
    return out


def _row_has_data(row_dict: dict) -> bool:
    return any((v or "").strip() for v in row_dict.values())


def _fetch_csv(url: str) -> list[dict]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ScholarshipTracker/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        text = r.read().decode("utf-8", errors="replace")
    if not text or not text.strip():
        return []
    # If response looks like HTML (e.g. login page), don't parse as CSV
    stripped = text.strip().lower()
    if stripped.startswith("<!") or "<html" in stripped[:200]:
        return []
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    raw_headers = [h.strip().lstrip("\ufeff") for h in rows[0]]
    # Prefer header mapping; fallback to position if first header looks like "university"
    first_header = (raw_headers[0] or "").lower()
    use_index = "university" in first_header and len(raw_headers) >= len(COLUMNS)
    result = []
    for row in rows[1:]:
        if not any((c or "").strip() for c in row):
            continue
        row_dict = _normalize_row(raw_headers, row, use_index_fallback=use_index)
        if _row_has_data(row_dict):
            result.append(row_dict)
    return result


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
    first_header = (raw_headers[0] or "").lower()
    use_index = "university" in first_header and len(raw_headers) >= len(COLUMNS)
    result = []
    for row in rows[1:]:
        if not any((c or "").strip() for c in row):
            continue
        row_dict = _normalize_row(raw_headers, row, use_index_fallback=use_index)
        if _row_has_data(row_dict):
            result.append(row_dict)
    return result


def load_scholarships(use_local_fallback: bool = True) -> list[dict]:
    try:
        data = load_from_sheet()
        if data:
            return data
    except Exception:
        pass
    if use_local_fallback:
        try:
            data = load_from_local()
            if data:
                return data
        except Exception:
            pass
    return []
