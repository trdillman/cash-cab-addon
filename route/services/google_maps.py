"""
Google Maps Platform Service Integration

Implements IService interface for Google Maps API, handling:
- Geocoding (Address -> Coordinates)
- Directions (Routing)
- Roads (Snapping to road geometry)

References:
- config.GoogleAPIConfig
- utils.GeocodeResult
- utils.RouteResult
"""

import json
import time
from urllib import request, parse, error
from typing import List, Optional, Tuple, Dict, Any

from .base import IService, ServiceError, ServiceResult
from ..utils import GeocodeResult, RouteResult, decode_polyline, RouteServiceError
from ..config import DEFAULT_CONFIG

class GoogleMapsService(IService):
    """
    Service wrapper for Google Maps Platform APIs.
    """
    
    BASE_URL_GEOCODING = "https://maps.googleapis.com/maps/api/geocode/json"
    BASE_URL_DIRECTIONS = "https://maps.googleapis.com/maps/api/directions/json"
    BASE_URL_ROADS = "https://roads.googleapis.com/v1/snapToRoads"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.config = DEFAULT_CONFIG.google_api

    def validate(self) -> bool:
        """Check if API key is present."""
        return bool(self.api_key and self.api_key.strip())

    def _request(self, url: str, params: Dict[str, Any]) -> dict:
        """Execute HTTP request to Google API."""
        if not self.validate():
            raise ServiceError("Google Maps API Key is missing. Please set it in the CashCab panel.")

        params['key'] = self.api_key
        query_string = parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        # Simple timeout from config
        timeout = self.config.timeout_s

        try:
            with request.urlopen(full_url, timeout=timeout) as resp:
                if resp.status != 200:
                    raise ServiceError(f"HTTP {resp.status} from Google API")
                data = json.loads(resp.read().decode('utf-8'))
                
                # Check for API-level error status
                status = data.get('status')
                if status and status != 'OK' and status != 'ZERO_RESULTS':
                    error_msg = data.get('error_message', 'Unknown API Error')
                    raise ServiceError(f"Google API Error: {status} - {error_msg}")
                    
                return data
        except error.URLError as e:
            raise ServiceError(f"Network error contacting Google API: {e}")
        except json.JSONDecodeError as e:
            raise ServiceError(f"Failed to parse Google API response: {e}")

    def geocode(self, address: str) -> ServiceResult[GeocodeResult]:
        """
        Geocode an address string to coordinates.
        """
        try:
            params = {'address': address}
            data = self._request(self.BASE_URL_GEOCODING, params)
            
            results = data.get('results', [])
            if not results:
                return ServiceResult.fail(f"Address not found: '{address}'")

            # Take the first result
            first = results[0]
            loc = first['geometry']['location']
            formatted_address = first.get('formatted_address', address)
            
            result = GeocodeResult(
                address=address,
                lat=float(loc['lat']),
                lon=float(loc['lng']),
                display_name=formatted_address
            )
            return ServiceResult.ok(result)

        except ServiceError as e:
            return ServiceResult.fail(str(e))
        except Exception as e:
            return ServiceResult.fail(f"Geocoding exception: {e}")

    def fetch_route(self, start: GeocodeResult, end: GeocodeResult, waypoints: List[GeocodeResult] = None) -> ServiceResult[RouteResult]:
        """
        Fetch driving directions.
        """
        try:
            origin = f"{start.lat},{start.lon}"
            destination = f"{end.lat},{end.lon}"
            
            params = {
                'origin': origin,
                'destination': destination,
                'mode': self.config.default_travel_mode,
                'overview_polyline': 'points' # Request encoded polyline
            }

            if waypoints:
                # Optimize waypoints by default? Google charges more for 'optimize:true'.
                # Let's stick to simple ordering for now unless robust user demand.
                # Format: "lat,lng|lat,lng" for stopovers
                waypoint_strs = [f"{wp.lat},{wp.lon}" for wp in waypoints]
                params['waypoints'] = "|".join(waypoint_strs)

            data = self._request(self.BASE_URL_DIRECTIONS, params)
            
            routes = data.get('routes', [])
            if not routes:
                return ServiceResult.fail("No route found between locations.")

            route = routes[0]
            overview_polyline = route['overview_polyline']['points']
            points = decode_polyline(overview_polyline)

            # Calculate total distance/duration from legs
            total_dist_m = 0.0
            total_duration_s = 0.0
            for leg in route.get('legs', []):
                total_dist_m += leg['distance']['value']
                total_duration_s += leg['duration']['value']

            result = RouteResult(
                points=points,
                distance_m=total_dist_m,
                duration_s=total_duration_s
            )
            return ServiceResult.ok(result)

        except ServiceError as e:
            return ServiceResult.fail(str(e))
        except Exception as e:
            return ServiceResult.fail(f"Routing exception: {e}")

    def snap_to_roads(self, points: List[Tuple[float, float]], interpolate: bool = True) -> ServiceResult[List[Tuple[float, float]]]:
        """
        Snap a path of points to the road network.
        Free tier limitation: 100 points per request.
        CashCab usage: This will be used primarily for the start/end point snapping,
        or potentially for smoothing the whole route if needed (though Directions usually gives good geometry).
        
        Using it for single point snapping (start/end) is efficient.
        """
        try:
            # Format path: "lat,lng|lat,lng"
            path_str = "|".join([f"{p[0]},{p[1]}" for p in points])
            
            params = {
                'path': path_str,
                'interpolate': str(interpolate).lower() 
            }

            data = self._request(self.BASE_URL_ROADS, params)
            
            snapped_points = []
            for item in data.get('snappedPoints', []):
                loc = item['location']
                snapped_points.append((float(loc['latitude']), float(loc['longitude'])))
            
            if not snapped_points:
                 # If no snapping occurred (e.g. too far from road), return original or fail?
                 # Returning fail allows caller to fallback to original.
                 return ServiceResult.fail("Points could not be snapped to road.")

            return ServiceResult.ok(snapped_points)

        except ServiceError as e:
            return ServiceResult.fail(str(e))
        except Exception as e:
            return ServiceResult.fail(f"Snap to roads exception: {e}")
