"""
Performance tracking and ETA calculation for route imports.

Stores historical tile download performance to provide accurate time estimates.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def get_performance_file_path() -> Path:
    """Get the path to the performance history JSON file."""
    # Use user's home directory for cross-platform compatibility
    home = Path.home()
    blosm_dir = home / ".blosm"
    blosm_dir.mkdir(exist_ok=True)
    return blosm_dir / "performance_history.json"


def load_performance_history() -> Dict:
    """Load performance history from disk."""
    perf_file = get_performance_file_path()
    if not perf_file.exists():
        return {
            "version": "1.0",
            "imports": [],
            "avg_tile_ms": 0.0,
            "total_imports": 0
        }

    try:
        with open(perf_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"[BLOSM] Performance history load error: {e}")
        return {
            "version": "1.0",
            "imports": [],
            "avg_tile_ms": 0.0,
            "total_imports": 0
        }


def save_performance_data(tile_count: int, avg_tile_ms: float, total_elapsed_s: float) -> None:
    """
    Save performance data from a completed import.

    Args:
        tile_count: Number of tiles downloaded
        avg_tile_ms: Average time per tile in milliseconds
        total_elapsed_s: Total elapsed time in seconds
    """
    if tile_count <= 0 or avg_tile_ms <= 0:
        return

    history = load_performance_history()

    # Add new import record
    import_record = {
        "tile_count": tile_count,
        "avg_tile_ms": avg_tile_ms,
        "total_elapsed_s": total_elapsed_s,
        "timestamp": None  # Could add datetime if needed
    }

    history["imports"].append(import_record)
    history["total_imports"] = len(history["imports"])

    # Keep only last 50 imports
    if len(history["imports"]) > 50:
        history["imports"] = history["imports"][-50:]

    # Calculate rolling average
    if history["imports"]:
        total_ms = sum(imp["avg_tile_ms"] for imp in history["imports"])
        history["avg_tile_ms"] = total_ms / len(history["imports"])
    else:
        history["avg_tile_ms"] = 0.0

    # Save to disk
    perf_file = get_performance_file_path()
    try:
        with open(perf_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        print(f"[BLOSM] Performance data saved: {tile_count} tiles, avg {avg_tile_ms:.0f} ms/tile")
    except IOError as e:
        print(f"[BLOSM] Performance history save error: {e}")


def calculate_eta(tile_count: int) -> Optional[float]:
    """
    Calculate estimated time for import based on historical performance.

    Args:
        tile_count: Number of tiles to download

    Returns:
        Estimated time in seconds, or None if no history available
    """
    if tile_count <= 0:
        return None

    history = load_performance_history()
    avg_ms = history.get("avg_tile_ms", 0.0)

    if avg_ms <= 0:
        # No history, use conservative estimate: 1000ms per tile
        avg_ms = 1000.0
        print("[BLOSM] No performance history, using default estimate")

    # Calculate ETA in seconds
    eta_seconds = (tile_count * avg_ms) / 1000.0
    return eta_seconds


def format_eta(seconds: Optional[float]) -> str:
    """
    Format ETA in human-readable format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted string like "2m 30s" or "45s" or "~1m"
    """
    if seconds is None or seconds <= 0:
        return "Unknown"

    if seconds < 60:
        return f"~{int(seconds)}s"

    minutes = int(seconds / 60)
    remaining_seconds = int(seconds % 60)

    if remaining_seconds == 0:
        return f"~{minutes}m"
    else:
        return f"~{minutes}m {remaining_seconds}s"
