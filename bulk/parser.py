from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

COORD_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)")
SHOT_RE = re.compile(r"\b(CC\d+)\b", re.IGNORECASE)
LEGACY_RE = re.compile(r"^\s*\[(?P<task>[^\]]+)\]\[(?P<addr>[^\]]+)\](?:\[(?P<date>[^\]]+)\])?\s*$")


@dataclass(frozen=True)
class BulkRoute:
    shot_code: str
    start_address: str
    end_address: str
    start_coords: str
    end_coords: str
    due_date: str
    sheet_status: str


def parse_manifest_text(text: str) -> List[BulkRoute]:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if _looks_like_legacy(lines):
        return list(_iter_legacy_jobs(lines))

    rows = _read_csv_rows(text)
    if not rows:
        return []

    if _looks_like_tracker(rows):
        return list(_iter_tracker_jobs(rows))

    if _looks_like_manifest_5col(rows):
        return list(_iter_manifest_5col_jobs(rows))

    # Fallback: attempt 5-column parse when there is enough data.
    if any(len(r) >= 5 for r in rows):
        return list(_iter_manifest_5col_jobs(rows))

    return []


def parse_manifest_path(path: Path) -> List[BulkRoute]:
    text = path.read_text(encoding="utf-8-sig")
    return parse_manifest_text(text)


def _read_csv_rows(text: str) -> List[List[str]]:
    if text is None:
        return []
    reader = csv.reader(io.StringIO(text))
    rows = []
    for row in reader:
        if not row:
            continue
        if any((cell or "").strip() for cell in row):
            rows.append([cell or "" for cell in row])
    return rows


def _looks_like_legacy(lines: Sequence[str]) -> bool:
    if not lines:
        return False
    matches = sum(1 for line in lines if LEGACY_RE.match(line))
    return matches >= max(1, int(len(lines) * 0.6))


def _looks_like_tracker(rows: Sequence[Sequence[str]]) -> bool:
    for row in rows[:10]:
        if _find_shot_cell(row):
            return True
        joined = " ".join((c or "") for c in row).lower()
        if "map gfx" in joined:
            return True
    return False


def _looks_like_manifest_5col(rows: Sequence[Sequence[str]]) -> bool:
    if not rows:
        return False
    header = _normalize_header(rows[0])
    if header:
        if "shot code" in header or "start address" in header:
            return True
        if "code" in header and "end address" in header:
            return True
    # If the first row looks like CC code + 5 columns, treat as 5-col.
    if len(rows[0]) >= 5 and SHOT_RE.search(rows[0][0] or ""):
        return True
    return False


def _normalize_header(row: Sequence[str]) -> List[str]:
    return [((cell or "").strip().lower()) for cell in row]


def _clean_address(addr: str) -> str:
    return (addr or "").strip().strip('"').strip()


def _parse_location_field(field: str) -> Tuple[str, str]:
    """Return (address_text, coords_str_or_empty)."""
    if not field:
        return "", ""
    match = COORD_RE.search(field)
    if not match:
        return _clean_address(field), ""

    lat = float(match.group(1))
    lon = float(match.group(2))

    # Heuristic fix: Toronto latitude sign sometimes appears negative in tracker.
    if lat < 0.0 and 40.0 <= abs(lat) <= 50.0 and -100.0 <= lon <= -60.0:
        lat = -lat

    addr = _clean_address(field[: match.start()].strip(" -:"))
    return addr, f"{lat:.6f}, {lon:.6f}"


def _find_shot_cell(row: Sequence[str]) -> Optional[str]:
    for cell in row:
        if "MAP GFX" not in (cell or ""):
            continue
        match = SHOT_RE.search(cell)
        if match:
            return match.group(1).upper()
    return None


def _iter_tracker_jobs(rows: Sequence[Sequence[str]]) -> Iterable[BulkRoute]:
    for row in rows:
        if not row:
            continue
        shot = _find_shot_cell(row)
        if not shot:
            continue

        due_date = (row[3] if len(row) > 3 else "").strip()
        sheet_status = (row[4] if len(row) > 4 else "").strip()
        start_field = row[5] if len(row) > 5 else ""
        end_field = row[6] if len(row) > 6 else ""

        start_addr, start_coords = _parse_location_field(start_field)
        end_addr, end_coords = _parse_location_field(end_field)

        yield BulkRoute(
            shot_code=shot,
            due_date=due_date,
            sheet_status=sheet_status,
            start_address=start_addr,
            start_coords=start_coords,
            end_address=end_addr,
            end_coords=end_coords,
        )


def _iter_manifest_5col_jobs(rows: Sequence[Sequence[str]]) -> Iterable[BulkRoute]:
    header = _normalize_header(rows[0]) if rows else []
    has_header = bool(header) and any("address" in h or "shot" in h or "code" in h for h in header)

    if has_header:
        indices = _map_manifest_header(header)
        data_rows = rows[1:]
    else:
        indices = {
            "shot": 0,
            "start_address": 1,
            "start_coords": 2,
            "end_address": 3,
            "end_coords": 4,
        }
        data_rows = rows

    for row in data_rows:
        if not row:
            continue
        if indices["shot"] >= len(row):
            continue
        shot = _clean_address(row[indices["shot"]])
        if not shot:
            continue
        start_addr = _clean_address(_safe_cell(row, indices["start_address"]))
        start_coords = _clean_address(_safe_cell(row, indices["start_coords"]))
        end_addr = _clean_address(_safe_cell(row, indices["end_address"]))
        end_coords = _clean_address(_safe_cell(row, indices["end_coords"]))

        yield BulkRoute(
            shot_code=shot,
            due_date="",
            sheet_status="",
            start_address=start_addr,
            start_coords=start_coords,
            end_address=end_addr,
            end_coords=end_coords,
        )


def _map_manifest_header(header: Sequence[str]) -> dict:
    def find_index(keys: Sequence[str]) -> int:
        for key in keys:
            for idx, cell in enumerate(header):
                if key in cell:
                    return idx
        return -1

    shot_idx = find_index(["shot code", "shot", "code", "task", "taskid"])
    start_addr_idx = find_index(["start address", "start", "pu location", "pickup", "pick up"])
    start_coords_idx = find_index(["start coords", "start coord", "start coordinate", "start lat", "start lon"])
    end_addr_idx = find_index(["end address", "end", "drop off", "dropoff", "drop off location", "dropoff location"])
    end_coords_idx = find_index(["end coords", "end coord", "end coordinate", "end lat", "end lon"])

    return {
        "shot": shot_idx if shot_idx >= 0 else 0,
        "start_address": start_addr_idx if start_addr_idx >= 0 else 1,
        "start_coords": start_coords_idx if start_coords_idx >= 0 else 2,
        "end_address": end_addr_idx if end_addr_idx >= 0 else 3,
        "end_coords": end_coords_idx if end_coords_idx >= 0 else 4,
    }


def _safe_cell(row: Sequence[str], idx: int) -> str:
    if idx < 0 or idx >= len(row):
        return ""
    return row[idx] or ""


def _iter_legacy_jobs(lines: Sequence[str]) -> Iterable[BulkRoute]:
    for line in lines:
        match = LEGACY_RE.match(line)
        if not match:
            continue
        shot = (match.group("task") or "").strip()
        addr_block = (match.group("addr") or "").strip()
        due_date = (match.group("date") or "").strip()

        start_addr, end_addr = _split_legacy_address(addr_block)
        yield BulkRoute(
            shot_code=shot,
            due_date=due_date,
            sheet_status="",
            start_address=start_addr,
            start_coords="",
            end_address=end_addr,
            end_coords="",
        )


def _split_legacy_address(block: str) -> Tuple[str, str]:
    parts = re.split(r"\s*[-\u2013\u2014]\s*", block, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return block.strip(), ""
