from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Optional
from urllib import parse, request

SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")
GID_RE = re.compile(r"[#&?]gid=([0-9]+)")


def fetch_csv(url: str) -> str:
    sheet_id = _extract_sheet_id(url)
    if not sheet_id:
        raise ValueError("Unable to extract Google Sheet ID from URL")
    gid = _extract_gid(url)
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    if gid:
        export_url = f"{export_url}&gid={gid}"
    tmp_path = _download_to_temp(export_url)
    try:
        return tmp_path.read_text(encoding="utf-8-sig")
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def _extract_sheet_id(url: str) -> Optional[str]:
    if not url:
        return None
    match = SHEET_ID_RE.search(url)
    if match:
        return match.group(1)

    parsed = parse.urlparse(url)
    qs = parse.parse_qs(parsed.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    return None


def _extract_gid(url: str) -> Optional[str]:
    if not url:
        return None
    match = GID_RE.search(url)
    if match:
        return match.group(1)
    parsed = parse.urlparse(url)
    qs = parse.parse_qs(parsed.query)
    if "gid" in qs and qs["gid"]:
        return qs["gid"][0]
    frag_qs = parse.parse_qs(parsed.fragment)
    if "gid" in frag_qs and frag_qs["gid"]:
        return frag_qs["gid"][0]
    return None


def _download_to_temp(url: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp_path = Path(tmp.name)
    request.urlretrieve(url, tmp_path)
    return tmp_path
