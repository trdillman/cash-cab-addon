"""Route utilities for BLOSM route import."""

from __future__ import annotations

import json
import gzip
import xml.etree.ElementTree as ET
from http.client import IncompleteRead
import math
import re
import time
import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple, Optional
from urllib import error, parse, request

# Import configuration
from .config import DEFAULT_CONFIG

# Module-level constants from config (for backward compatibility)
MIN_NOMINATIM_INTERVAL = DEFAULT_CONFIG.api.nominatim_min_interval_s
EARTH_RADIUS_M = DEFAULT_CONFIG.geography.earth_radius_m
_METERS_PER_DEGREE_LAT = DEFAULT_CONFIG.geography.meters_per_degree_lat
_OVERPASS_TILE_MAX_M = DEFAULT_CONFIG.api.overpass_tile_max_m
_OVERPASS_INTERVAL = DEFAULT_CONFIG.api.nominatim_min_interval_s
_OVERPASS_TIMEOUT = DEFAULT_CONFIG.api.overpass_query_timeout
_MAX_OVERPASS_ATTEMPTS = DEFAULT_CONFIG.api.overpass_max_retries
_last_nominatim_request = 0.0
_last_overpass_request = 0.0

# Global toggle that route operators can override per-call based on addon settings.
SNAP_TO_ROAD_CENTERLINE: bool = True

# Prefer snapping to primary road classes to avoid alleys/service roads near buildings.
_SNAP_HIGHWAY_ALLOWLIST = (
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "living_street",
    "motorway_link",
    "trunk_link",
    "primary_link",
    "secondary_link",
    "tertiary_link",
)


class RouteServiceError(RuntimeError):
    """Raised when external geocoding or routing fails."""


@dataclass(frozen=True)
class GeocodeResult:
    address: str
    lat: float
    lon: float
    display_name: str


@dataclass(frozen=True)
class RouteResult:
    points: Sequence[Tuple[float, float]]
    distance_m: float
    duration_s: float


@dataclass(frozen=True)
class RouteContext:
    start: GeocodeResult
    end: GeocodeResult
    route: RouteResult
    bbox: Tuple[float, float, float, float]
    padded_bbox: Tuple[float, float, float, float]
    width_m: float
    height_m: float
    bbox_area_km2: float
    tile_count: int
    tiles: Sequence[Tuple[float, float, float, float]]


def _throttle_nominatim():
    global _last_nominatim_request
    now = time.monotonic()
    wait = MIN_NOMINATIM_INTERVAL - (now - _last_nominatim_request)
    if wait > 0:
        time.sleep(wait)
    _last_nominatim_request = time.monotonic()


def _throttle_overpass():
    """Basic Overpass rate limiting shared with snapping helper.

    Uses the same interval as Nominatim by default for simplicity.
    """
    global _last_overpass_request
    now = time.monotonic()
    wait = _OVERPASS_INTERVAL - (now - _last_overpass_request)
    if wait > 0:
        time.sleep(wait)
    _last_overpass_request = time.monotonic()


def _request_json(url: str, user_agent: str, timeout: float = 30.0, throttle: bool = False) -> dict:
    if throttle:
        _throttle_nominatim()
    headers = {"User-Agent": user_agent or "BLOSM Route Import"}
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            if status != 200:
                raise RouteServiceError(f"HTTP {status} from {url}")
            payload = resp.read().decode("utf-8")
    except error.URLError as exc:  # includes HTTPError
        raise RouteServiceError(f"Request error for {url}: {exc}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RouteServiceError("Unable to decode response JSON") from exc


def geocode(address: str, user_agent: str) -> GeocodeResult:
    """Geocode a human-readable address via Nominatim, with optional snapping.

    Behaviour:
    - If the user enters a raw \"lat, lon\" string, treat it as coordinates
      directly (no Nominatim call) and optionally snap to the nearest road.
    - Otherwise, call Nominatim to geocode the address, then optionally snap
      the resulting point to the nearest road centerline.

    Raises RouteServiceError with a user-friendly message when no results are
    returned or the response is malformed. The original input string is
    included so the UI can show actionable guidance.
    """
    if not address or not address.strip():
        raise RouteServiceError("Address is empty. Please enter an address.")

    original = address.strip()

    # 1) Support raw \"lat, lon\" input directly (no Nominatim lookup).
    coords = _parse_latlon_input(original)
    if coords is not None:
        lat, lon = coords
        if SNAP_TO_ROAD_CENTERLINE:
            snapped = _snap_to_road_centerline(lat, lon, user_agent=user_agent)
            if snapped is not None:
                lat, lon = snapped
        return GeocodeResult(address=original, lat=lat, lon=lon, display_name=original)

    # 2) Normal path: geocode via Nominatim, then snap result to road centerline.
    query = parse.urlencode({
        "q": original,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
        "countrycodes": DEFAULT_CONFIG.api.nominatim_country_codes
    })
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    data = _request_json(url, user_agent, throttle=True)
    if not data:
        # Explicit, user-facing guidance for bad/unknown addresses
        raise RouteServiceError(
            f"Address not found: \"{original}\". Please check the spelling or try a nearby intersection."
        )
    entry = data[0]
    try:
        lat = float(entry["lat"])
        lon = float(entry["lon"])
    except (KeyError, ValueError) as exc:
        raise RouteServiceError(
            f"Could not read geocoding result for \"{original}\". Please adjust and try again."
        ) from exc

    if SNAP_TO_ROAD_CENTERLINE:
        street_name = None
        try:
            addr_details = entry.get("address") or {}
            if isinstance(addr_details, dict):
                street_name = (
                    addr_details.get("road")
                    or addr_details.get("pedestrian")
                    or addr_details.get("footway")
                    or addr_details.get("street")
                )
        except Exception:
            street_name = None
        snapped = _snap_to_road_centerline(lat, lon, user_agent=user_agent, street_name=street_name)
        if snapped is not None:
            lat, lon = snapped

    return GeocodeResult(address=original, lat=lat, lon=lon, display_name=entry.get("display_name", original))


def decode_polyline(value: str, precision: int = 5) -> List[Tuple[float, float]]:
    if not value:
        return []
    index = 0
    lat = 0
    lon = 0
    coordinates: List[Tuple[float, float]] = []
    factor = 10 ** precision

    length = len(value)
    while index < length:
        result = 0
        shift = 0
        while True:
            if index >= length:
                raise RouteServiceError("Malformed polyline data")
            b = ord(value[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else (result >> 1)
        lat += dlat

        result = 0
        shift = 0
        while True:
            if index >= length:
                raise RouteServiceError("Malformed polyline data")
            b = ord(value[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlon = ~(result >> 1) if result & 1 else (result >> 1)
        lon += dlon

        coordinates.append((lat / factor, lon / factor))

    return coordinates


def fetch_route(start: GeocodeResult, end: GeocodeResult, user_agent: str, waypoints: List[GeocodeResult] = None) -> RouteResult:
    """Fetch driving route from start to end, optionally passing through waypoints"""
    # Build coordinate string: start;waypoint1;waypoint2;...;end
    coord_list = [f"{start.lon},{start.lat}"]
    if waypoints:
        for wp in waypoints:
            coord_list.append(f"{wp.lon},{wp.lat}")
    coord_list.append(f"{end.lon},{end.lat}")
    coords = ";".join(coord_list)

    url = f"{DEFAULT_CONFIG.api.osrm_base_url}/route/v1/driving/{coords}?overview=full&geometries=polyline"
    data = _request_json(url, user_agent, throttle=False)
    if data.get("code") != "Ok" or not data.get("routes"):
        # Provide clear guidance when routing fails between points
        raise RouteServiceError(
            f"Could not find driving directions between \"{start.address}\" and \"{end.address}\". "
            f"Please check address spelling or try adjusting the locations."
        )
    route_data = data["routes"][0]
    geometry = route_data.get("geometry")
    if not geometry:
        raise RouteServiceError(
            "Routing service returned no geometry. Please try again or adjust addresses."
        )
    points = decode_polyline(geometry)
    if not points:
        raise RouteServiceError(
            "Route geometry is empty. Please try again or adjust addresses."
        )
    distance = float(route_data.get("distance", 0.0))
    duration = float(route_data.get("duration", 0.0))
    return RouteResult(points=points, distance_m=distance, duration_s=duration)


def compute_bbox(points: Sequence[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    south = min(lats)
    north = max(lats)
    west = min(lons)
    east = max(lons)
    return south, west, north, east


def pad_bbox(bbox: Tuple[float, float, float, float], padding_m: float) -> Tuple[float, float, float, float]:
    south, west, north, east = bbox
    if padding_m <= 0:
        return south, west, north, east
    mid_lat = (south + north) / 2.0
    lat_pad = padding_m / _METERS_PER_DEGREE_LAT
    lon_scale = math.cos(math.radians(mid_lat))
    if abs(lon_scale) < 1e-6:
        lon_pad = 0.0
    else:
        lon_pad = padding_m / (_METERS_PER_DEGREE_LAT * lon_scale)
    south = max(-90.0, south - lat_pad)
    north = min(90.0, north + lat_pad)
    west = max(-180.0, west - lon_pad)
    east = min(180.0, east + lon_pad)
    return south, west, north, east


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_M * c


def _parse_latlon_input(text: str) -> Optional[Tuple[float, float]]:
    """Parse a simple \"lat, lon\" string into a coordinate pair.

    Returns (lat, lon) if parsing succeeds and values are in a reasonable range,
    otherwise returns None.
    """
    if not text:
        return None
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 2:
        return None
    try:
        lat = float(parts[0])
        lon = float(parts[1])
    except ValueError:
        return None

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    return lat, lon


def _to_local_xy(lat: float, lon: float, lat0: float) -> Tuple[float, float]:
    """Approximate lon/lat (deg) to local metres around reference latitude.

    This is sufficient for short distances like snapping to the nearest road.
    """
    r = EARTH_RADIUS_M
    phi = math.radians(lat)
    lam = math.radians(lon)
    phi0 = math.radians(lat0)
    x = r * lam * math.cos(phi0)
    y = r * phi
    return x, y


def _from_local_xy(x: float, y: float, lat0: float) -> Tuple[float, float]:
    """Inverse of _to_local_xy."""
    r = EARTH_RADIUS_M
    phi0 = math.radians(lat0)
    phi = y / r
    lam = x / (r * math.cos(phi0)) if abs(math.cos(phi0)) > 1e-8 else 0.0
    lat = math.degrees(phi)
    lon = math.degrees(lam)
    return lat, lon


def _project_point_to_segment(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> Tuple[float, float, float]:
    """Return (qx, qy, t) for closest point Q on segment AB to P in 2D."""
    vx = bx - ax
    vy = by - ay
    wx = px - ax
    wy = py - ay

    seg_len2 = vx * vx + vy * vy
    if seg_len2 == 0.0:
        return ax, ay, 0.0

    t = (wx * vx + wy * vy) / seg_len2
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    qx = ax + t * vx
    qy = ay + t * vy
    return qx, qy, t


def _overpass_request_json(body: str, user_agent: str) -> Optional[dict]:
    """Execute a small JSON Overpass query using the configured servers.

    Returns parsed JSON on success, or None on failure.
    """
    servers = DEFAULT_CONFIG.api.overpass_servers
    if not servers:
        return None

    # Ensure we respect a basic interval between Overpass calls.
    _throttle_overpass()

    payload = parse.urlencode({"data": body}).encode("utf-8")
    headers = {"User-Agent": user_agent or DEFAULT_CONFIG.api.nominatim_user_agent}

    last_error: Optional[Exception] = None
    for base in servers:
        url = base.rstrip("/") + "/api/interpreter"
        req = request.Request(url, data=payload, headers=headers)
        try:
            with request.urlopen(req, timeout=_OVERPASS_TIMEOUT) as resp:
                status = getattr(resp, "status", 200)
                if status != 200:
                    continue
                raw = resp.read().decode("utf-8")
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    # Try next server on JSON issues as well
                    last_error = None
                    continue
        except error.URLError as exc:
            last_error = exc
            continue
        except IncompleteRead as exc:
            last_error = exc
            continue

    # If everything failed, return None – snapping will be skipped.
    if last_error is not None:
        print(f"[BLOSM] WARN Overpass snap query failed: {last_error}")
    return None


def _snap_to_road_centerline(
    lat: float,
    lon: float,
    user_agent: str,
    street_name: Optional[str] = None,
    radius_m: float = 150.0,
    max_snap_m: float = 60.0,
) -> Optional[Tuple[float, float]]:
    """Snap a point to the nearest road centerline using Overpass.

    Returns (snapped_lat, snapped_lon) or None if snapping is unavailable.
    """
    allow_re = "|".join(re.escape(v) for v in _SNAP_HIGHWAY_ALLOWLIST)

    def _build_query(require_name_match: bool) -> str:
        name_filter = ""
        if require_name_match and street_name:
            # Case-insensitive partial match; avoids snapping to nearby service/alley roads.
            # Note: Overpass uses regex syntax; escape user-facing names defensively.
            street_re = re.escape(street_name.strip())
            if street_re:
                name_filter = f"[\"name\"~\"{street_re}\",i]"
        return (
            "[out:json][timeout:{timeout}];\n"
            "(\n"
            "  way(around:{radius},{lat},{lon})"
            "[\"highway\"~\"^({allow})$\"]{name_filter};\n"
            ");\n"
            "(._;>;);\n"
            "out body;\n"
        ).format(
            timeout=_OVERPASS_TIMEOUT,
            radius=int(radius_m),
            lat=lat,
            lon=lon,
            allow=allow_re,
            name_filter=name_filter,
        )

    def _build_fallback_query_any_highway() -> str:
        return (
            "[out:json][timeout:{timeout}];\n"
            "(\n"
            "  way(around:{radius},{lat},{lon})[\"highway\"];\n"
            ");\n"
            "(._;>;);\n"
            "out body;\n"
        ).format(timeout=_OVERPASS_TIMEOUT, radius=int(radius_m), lat=lat, lon=lon)

    # Try: name-aware allowlist -> allowlist -> any highway.
    data = None
    if street_name and street_name.strip():
        data = _overpass_request_json(_build_query(require_name_match=True), user_agent=user_agent)
    if not data:
        data = _overpass_request_json(_build_query(require_name_match=False), user_agent=user_agent)
    if not data:
        data = _overpass_request_json(_build_fallback_query_any_highway(), user_agent=user_agent)
    if not data:
        return None

    elements = data.get("elements") or []
    nodes = {
        el["id"]: (float(el["lon"]), float(el["lat"]))  # lon, lat
        for el in elements
        if el.get("type") == "node" and "lon" in el and "lat" in el
    }
    ways = [el for el in elements if el.get("type") == "way" and el.get("nodes")]

    if not nodes or not ways:
        return None

    # Prepare local metric projection anchored at the query latitude.
    px, py = _to_local_xy(lat, lon, lat0=lat)

    best: Optional[Tuple[float, float, float]] = None  # (dist_m, s_lat, s_lon)

    for way in ways:
        node_ids = way.get("nodes", [])
        coords_ll = [nodes.get(nid) for nid in node_ids if nid in nodes]
        if len(coords_ll) < 2:
            continue

        # Work segment-by-segment in local metres
        coords_xy = [_to_local_xy(c[1], c[0], lat0=lat) for c in coords_ll]  # c = (lon, lat)

        for (ax, ay), (bx, by) in zip(coords_xy, coords_xy[1:]):
            qx, qy, _ = _project_point_to_segment(px, py, ax, ay, bx, by)
            dx = qx - px
            dy = qy - py
            dist = math.hypot(dx, dy)
            s_lat, s_lon = _from_local_xy(qx, qy, lat0=lat)

            cand = (dist, s_lat, s_lon)
            if best is None or cand[0] < best[0]:
                best = cand

    if best is None:
        return None

    dist_m, s_lat, s_lon = best
    # Only accept reasonable shifts; otherwise keep original point.
    if dist_m > max_snap_m:
        return None
    return s_lat, s_lon


def bbox_size(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
    south, west, north, east = bbox
    mid_lat = (south + north) / 2.0
    mid_lon = (west + east) / 2.0
    width = haversine_m(mid_lat, west, mid_lat, east)
    height = haversine_m(south, mid_lon, north, mid_lon)
    return width, height


def prepare_route(start_address: str, end_address: str, padding_m: float, user_agent: str, waypoint_addresses: List[str] = None) -> RouteContext:
    """Prepare route context with optional waypoints.

    Wraps geocoding with explicit error messages so the operator can surface
    clear warnings (e.g., which address failed) instead of failing silently.
    """
    # Geocode start/end with targeted messages
    try:
        start = geocode(start_address, user_agent)
    except RouteServiceError as exc:
        raise RouteServiceError(
            f"Start address not found: \"{start_address}\". Please check the spelling."
        ) from exc
    try:
        end = geocode(end_address, user_agent)
    except RouteServiceError as exc:
        raise RouteServiceError(
            f"End address not found: \"{end_address}\". Please check the spelling."
        ) from exc

    # Geocode waypoints if provided
    waypoints = []
    if waypoint_addresses:
        for wp_address in waypoint_addresses:
            if wp_address and wp_address.strip():  # Skip empty addresses
                try:
                    waypoints.append(geocode(wp_address.strip(), user_agent))
                except RouteServiceError as exc:
                    raise RouteServiceError(
                        f"Waypoint address not found: \"{wp_address}\". Please check the spelling."
                    ) from exc

    # Fetch route with waypoints
    route = fetch_route(start, end, user_agent, waypoints=waypoints if waypoints else None)

    bbox = compute_bbox(route.points)
    padded_bbox = pad_bbox(bbox, padding_m)
    width_m, height_m = bbox_size(padded_bbox)
    bbox_area_km2 = (width_m * height_m) / 1_000_000.0
    tiles = _tile_bbox(*padded_bbox)
    tile_count = len(tiles)
    return RouteContext(
        start=start,
        end=end,
        route=route,
        bbox=bbox,
        padded_bbox=padded_bbox,
        width_m=width_m,
        height_m=height_m,
        bbox_area_km2=bbox_area_km2,
        tile_count=tile_count,
        tiles=tuple(tiles),
    )








def _meters_to_lat_delta(meters: float) -> float:
    return meters / _METERS_PER_DEGREE_LAT


def _meters_to_lon_delta(meters: float, latitude: float) -> float:
    scale = math.cos(math.radians(latitude))
    if abs(scale) < 1e-6:
        return 360.0
    return meters / (_METERS_PER_DEGREE_LAT * scale)


def _tile_bbox(south: float, west: float, north: float, east: float) -> List[Tuple[float, float, float, float]]:
    tiles: List[Tuple[float, float, float, float]] = []
    lat_step = _meters_to_lat_delta(_OVERPASS_TILE_MAX_M)
    lat = south
    while lat < north - 1e-9:
        next_lat = min(north, lat + lat_step)
        mid_lat = (lat + next_lat) * 0.5
        lon_step = _meters_to_lon_delta(_OVERPASS_TILE_MAX_M, mid_lat)
        lon = west
        row_added = False
        while lon < east - 1e-9:
            next_lon = min(east, lon + lon_step)
            tiles.append((lat, lon, next_lat, next_lon))
            lon = next_lon
            row_added = True
        if not row_added:
            tiles.append((lat, west, next_lat, east))
        lat = next_lat
    if not tiles:
        tiles.append((south, west, north, east))
    return tiles



class OverpassFetcher:
    """Fetches OSM data for roads/buildings using Overpass with tiling and retries."""

    # Use servers from configuration
    SERVERS = DEFAULT_CONFIG.api.overpass_servers

    def __init__(
        self,
        user_agent: str,
        include_roads: bool,
        include_buildings: bool,
        include_water: bool = False,
        *,
        min_interval_ms: int = 1000,
        timeout_s: float = 30.0,
        max_retries: int = 3,
        logger=None,
        progress=None,
        store_tiles: bool = False,
    ):
        if not include_roads and not include_buildings and not include_water:
            raise RouteServiceError("No layers selected for Overpass fetch")
        self.user_agent = (user_agent or "BLOSM Route Import").strip() or "BLOSM Route Import"
        self.include_roads = include_roads
        self.include_buildings = include_buildings
        self.include_water = include_water
        self._logger = logger
        self._progress = progress
        self._store_tiles = bool(store_tiles)
        self._tile_payloads: List[bytes] = []
        self._tile_bboxes: List[Tuple[float, float, float, float]] = []
        self._server_index = 0
        self._last_request = 0.0
        self._min_interval_s = max(0.0, min_interval_ms / 1000.0)
        self._timeout_s = max(1.0, float(timeout_s))
        self._max_retries = max(0, int(max_retries))
        self._tile_times: List[float] = []
        self._total_start = 0.0
        self._total_elapsed_s = 0.0
        self._cache_ready = False

    @property
    def average_tile_ms(self) -> float:
        return sum(self._tile_times) / len(self._tile_times) if self._tile_times else 0.0

    @property
    def total_elapsed_s(self) -> float:
        return self._total_elapsed_s

    def _sleep_until_ready(self) -> None:
        if self._min_interval_s <= 0:
            return
        now = time.monotonic()
        wait = self._min_interval_s - (now - self._last_request)
        if wait > 0:
            time.sleep(wait)

    def _log(self, message: str) -> None:
        if self._logger:
            self._logger(message)
        else:
            print(f"[BLOSM Route] {message}")

    def _emit_progress(self, message: str) -> None:
        if self._logger:
            try:
                self._logger(message)
            except Exception:
                print(f"[BLOSM Route] {message}")
        print(f"[BLOSM Route] {message}")

    def write_tiles(self, filepath: str, tiles) -> None:
        """Write OSM XML for an explicit list of tiles.

        This helper is used by the main route import as well as the
        Extend City operator so callers can control exactly which tiles
        are fetched (for example, only the tiles that extend the current
        city instead of the full bbox again).
        """
        total_tiles = len(tiles)
        if self._store_tiles:
            self._tile_payloads = []
            self._tile_bboxes = []
        if self._progress:
            try:
                self._progress.begin(total_tiles)
            except Exception:
                pass
        self._log(f"Overpass fetching {len(tiles)} tile(s)")
        root = ET.Element("osm", attrib={"version": "0.6", "generator": "BLOSM Route"})
        if tiles:
            south = min(t[0] for t in tiles)
            west = min(t[1] for t in tiles)
            north = max(t[2] for t in tiles)
            east = max(t[3] for t in tiles)
        else:
            south = west = north = east = 0.0
        ET.SubElement(root, "bounds", attrib={
            "minlat": f"{south:.7f}",
            "minlon": f"{west:.7f}",
            "maxlat": f"{north:.7f}",
            "maxlon": f"{east:.7f}",
        })
        seen = {
            "node": set(),
            "way": set(),
            "relation": set(),
        }
        totals = {"node": 0, "way": 0, "relation": 0}
        self._tile_times = []
        self._total_start = time.perf_counter()
        try:
            for index, tile in enumerate(tiles, 1):
                tile_start = time.perf_counter()
                retries = 0
                while True:
                    try:
                        xml_bytes = self._fetch_tile(tile)
                        break
                    except RouteServiceError as exc:
                        retries += 1
                        if retries > self._max_retries:
                            raise
                        backoff = min(5.0, 2 ** (retries - 1)) + random.uniform(0.0, 0.25)
                        self._log(f"Retry {retries}/{self._max_retries} for tile {index}: {exc} (waiting {backoff:.2f}s)")
                        time.sleep(backoff)
                added = self._merge_xml(root, seen, xml_bytes)
                for key, value in added.items():
                    totals[key] += value
                tile_ms = (time.perf_counter() - tile_start) * 1000.0
                self._tile_times.append(tile_ms)
                elapsed = time.perf_counter() - self._total_start
                avg_ms = self.average_tile_ms or tile_ms
                percent = (index / len(tiles)) * 100.0 if tiles else 0.0
                self._emit_progress(
                    f"Tiles {index}/{len(tiles)} ({percent:.0f}%), last={tile_ms:.0f} ms, avg={avg_ms:.0f} ms, elapsed={elapsed:.1f} s, retries={retries}"
                )
                if self._store_tiles:
                    self._tile_payloads.append(xml_bytes)
                    self._tile_bboxes.append(tile)
                if self._progress:
                    try:
                        self._progress.update(index, total_tiles)
                    except Exception:
                        pass
        finally:
            if self._progress:
                try:
                    self._progress.end()
                except Exception:
                    pass
        self._total_elapsed_s = time.perf_counter() - self._total_start
        ET.ElementTree(root).write(filepath, encoding="utf-8", xml_declaration=True)
        self._log(
            f"Overpass totals: nodes {totals['node']}, ways {totals['way']}, relations {totals['relation']}"
        )
        self._cache_ready = True

    def write(self, filepath: str, south: float, west: float, north: float, east: float) -> None:
        """Backward-compatible entry point that tiles a bbox.

        Existing callers pass a geographic bbox; internally we derive the tile
        list and forward to :meth:`write_tiles` so that other callers (like the
        Extend City operator) can supply their own tile sets.
        """
        tiles = _tile_bbox(south, west, north, east)
        self.write_tiles(filepath, tiles)

    def _fetch_tile(self, tile: Tuple[float, float, float, float]) -> bytes:
        south, west, north, east = tile
        query = self._build_query(south, west, north, east)
        attempts = 0
        total_servers = len(self.SERVERS)
        while True:
            server = self.SERVERS[self._server_index]
            try:
                self._sleep_until_ready()
                data = self._request_overpass(server, query)
                self._log(
                    f"Fetched tile lat {south:.6f}-{north:.6f}, lon {west:.6f}-{east:.6f} from {server}"
                )
                return data
            except RouteServiceError as exc:
                attempts += 1
                self._server_index = (self._server_index + 1) % total_servers
                if attempts > self._max_retries:
                    raise RouteServiceError(f"Overpass request failed after retries: {exc}")
                backoff = min(5.0, 2 ** (attempts - 1)) + random.uniform(0.0, 0.25)
                self._log(f"Switching endpoint (attempt {attempts}/{self._max_retries}) due to: {exc}. Waiting {backoff:.2f}s")
                time.sleep(backoff)

    def _request_overpass(self, server: str, query: str) -> bytes:
        url = f"{server}/api/interpreter"
        self._last_request = time.monotonic()
        req = request.Request(
            url,
            data=query.encode("utf-8"),
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with request.urlopen(req, timeout=self._timeout_s) as resp:
                raw = resp.read()
                headers = resp.headers if resp.headers else {}
                encoding = headers.get("Content-Encoding")
                if encoding == "gzip":
                    raw = gzip.decompress(raw)
                content_length = headers.get("Content-Length")
                if content_length and len(raw) < int(content_length):
                    raise RouteServiceError("Overpass response truncated")
        except error.HTTPError as exc:
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if retry_after:
                try:
                    wait_time = float(retry_after)
                    self._log(f"Retry-After received: waiting {wait_time:.2f}s")
                    time.sleep(min(wait_time, 10.0))
                except ValueError:
                    pass
            raise RouteServiceError(f"Overpass HTTP error {exc.code}") from exc
        except IncompleteRead as exc:
            raise RouteServiceError("Overpass incomplete read") from exc
        except error.URLError as exc:
            raise RouteServiceError(f"Overpass connection error: {exc}") from exc
        finally:
            self._last_request = time.monotonic()
        stripped = raw.strip()
        if not stripped.startswith(b"<?xml") and not stripped.startswith(b"<osm"):
            raise RouteServiceError("Overpass returned unexpected payload")
        if b"</osm>" not in stripped:
            raise RouteServiceError("Overpass response incomplete (missing </osm>)")
        return raw

    def _merge_xml(self, root: ET.Element, seen, xml_bytes: bytes) -> dict:
        try:
            doc = ET.fromstring(xml_bytes)
        except ET.ParseError as exc:
            raise RouteServiceError(f"Unable to parse Overpass XML: {exc}") from exc
        if doc.tag != "osm":
            raise RouteServiceError("Unexpected Overpass root element")
        added = {"node": 0, "way": 0, "relation": 0}
        for child in doc:
            tag = child.tag
            if tag not in seen:
                continue
            element_id = child.get("id")
            if not element_id:
                continue
            key = (tag, element_id)
            if key in seen[tag]:
                continue
            seen[tag].add(key)
            child.tail = None
            root.append(child)
            added[tag] += 1
        return added

    def get_cached_tiles(self):
        if not self._store_tiles or not self._tile_payloads:
            return []
        return list(zip(self._tile_bboxes, self._tile_payloads))

    def _build_query(self, south: float, west: float, north: float, east: float) -> str:
        parts = []
        if self.include_buildings:
            parts.append(f'way["building"]({south},{west},{north},{east});')
            parts.append(f'relation["building"]({south},{west},{north},{east});')
        if self.include_roads:
            parts.append(f'way["highway"]({south},{west},{north},{east});')
        if self.include_water:
            # Smart water import: compact bbox for nearby features, expanded bbox for large water relations

            # Nearby water features in main (compact) bbox - 500m padding area
            parts.append(f'way["natural"="water"]({south},{west},{north},{east});')
            parts.append(f'way["waterway"="river"]({south},{west},{north},{east});')
            parts.append(f'way["waterway"="stream"]({south},{west},{north},{east});')
            parts.append(f'way["waterway"="canal"]({south},{west},{north},{east});')
            parts.append(f'way["waterway"="creek"]({south},{west},{north},{east});')
            parts.append(f'way["waterway"="riverbank"]({south},{west},{north},{east});')
            parts.append(f'way["landuse"="reservoir"]({south},{west},{north},{east});')
            parts.append(f'way["landuse"="water"]({south},{west},{north},{east});')

            # Large water bodies (Great Lakes) with expanded bbox - 1500m expansion for relations only
            # This captures Lake Ontario and similar large lakes without massive bbox expansion
            lat_expansion = 1500.0 / 111320.0  # Convert 1500m to degrees latitude
            lon_expansion = 1500.0 / (111320.0 * 0.965)  # Convert 1500m to degrees longitude (Toronto latitude)

            expanded_south = south - lat_expansion
            expanded_west = west - lon_expansion
            expanded_north = north + lat_expansion
            expanded_east = east + lon_expansion

            # Add large water body relation queries in expanded bbox only
            parts.append(f'relation["natural"="water"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["natural"="coastline"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')

            # Great Lakes specific queries in expanded bbox
            parts.append(f'relation["natural"="water"]["name"~"Lake.*Ontario|Lake.*Erie|Lake.*Huron|Lake.*Superior|Lake.*Michigan"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["name"="Lake Ontario"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["name"="Lake Erie"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["landuse"="water"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["place"="sea"]({south},{west},{north},{east});')
            parts.append(f'relation["place"="ocean"]({south},{west},{north},{east});')

            # Toronto Islands specific queries in expanded bbox
            # Support both generic island queries and Toronto Islands specific patterns
            parts.append(f'relation["place"="island"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["place"="island"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["name"~"Toronto.*Island|Island.*Toronto|Toronto.*Islands|Islands.*Toronto"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["name"~"Toronto.*Island|Island.*Toronto|Toronto.*Islands|Islands.*Toronto"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["name"~"Centre.*Island|Ward.*Island|Algonquin.*Island|Muggs.*Island|South.*Island"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["name"~"Centre.*Island|Ward.*Island|Algonquin.*Island|Muggs.*Island|South.*Island"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'relation["name"="Toronto Islands"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["name"="Toronto Islands"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')

            # Generic island queries for broader island detection
            parts.append(f'relation["place"="island"]["natural"~"land|ground|grass|forest|wood|scrub|wetland|sand|rock|stone"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
            parts.append(f'way["place"="island"]["natural"~"land|ground|grass|forest|wood|scrub|wetland|sand|rock|stone"]({expanded_south},{expanded_west},{expanded_north},{expanded_east});')
        body = "\n        ".join(parts)
        return (
            "[out:xml][timeout:180];\n"
            "(\n"
            f"        {body}\n"
            ");\n"
            "(._;>;);\n"
            "out body;\n"
        )
