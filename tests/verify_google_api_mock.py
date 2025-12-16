import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import types

# --- HARNESS SETUP ---
# Add repo root to path
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Mock 'bpy' and 'mathutils' to prevent import errors if they are referenced
sys.modules['bpy'] = MagicMock()
sys.modules['mathutils'] = MagicMock()

# Mock 'route' package to prevent __init__.py from running which causes
# 'attempted relative import beyond top-level package' errors in fetch_operator
# because we are running outside of the proper package context.
route_pkg = types.ModuleType('route')
route_pkg.__path__ = [os.path.join(base_path, 'route')]
sys.modules['route'] = route_pkg

# Ensure submodules can be found
# We don't need to mock generic python modules, but we need to ensure local imports work
# We will rely on standard import mechanisms finding the files since 'route' is in path,
# BUT we explicitly suppressed route.__init__ so we must be careful.

# Import dependencies explicitly to register them
try:
    import route.config
    import route.services.base
    import route.utils
except ImportError as e:
    # If this fails, we might need to manually load them or fix sys.path further
    print(f"Harness import error: {e}")
    sys.exit(1)

from route.services.google_maps import GoogleMapsService
from route.services.base import ServiceError

class TestGoogleMapsService(unittest.TestCase):
    def setUp(self):
        self.api_key = "TEST_KEY"
        self.service = GoogleMapsService(self.api_key)

    @patch('route.services.google_maps.request.urlopen')
    def test_geocode_success(self, mock_urlopen):
        # Mock response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "status": "OK",
            "results": [
                {
                    "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
                    "geometry": {
                        "location": {
                            "lat": 37.4224764,
                            "lng": -122.0842499
                        }
                    }
                }
            ]
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.service.geocode("Googleplex")
        
        self.assertTrue(result.success)
        self.assertEqual(result.data.lat, 37.4224764)
        self.assertEqual(result.data.lon, -122.0842499)
        self.assertEqual(result.data.display_name, "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA")

    @patch('route.services.google_maps.request.urlopen')
    def test_geocode_zero_results(self, mock_urlopen):
        # Mock response
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "status": "ZERO_RESULTS",
            "results": []
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        result = self.service.geocode("PlaceThatDoesNotExist")
        
        self.assertFalse(result.success)
        self.assertIn("Address not found", result.error)

    @patch('route.services.google_maps.request.urlopen')
    def test_fetch_route_success(self, mock_urlopen):
        # Mock response for Directions API
        # encoded polyline for a straight line roughly
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "status": "OK",
            "routes": [
                {
                    "legs": [
                        {
                            "distance": {"value": 1000},
                            "duration": {"value": 600}
                        }
                    ],
                    "overview_polyline": {
                        "points": "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
                    }
                }
            ]
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        start = MagicMock(lat=38.5, lon=-120.2)
        end = MagicMock(lat=40.7, lon=-120.95)
        
        result = self.service.fetch_route(start, end)
        
        self.assertTrue(result.success)
        self.assertTrue(len(result.data.points) > 0)
        self.assertEqual(result.data.distance_m, 1000)
        self.assertEqual(result.data.duration_s, 600)

    @patch('route.services.google_maps.request.urlopen')
    def test_snap_to_roads_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "snappedPoints": [
                {
                    "location": {
                        "latitude": 35.123,
                        "longitude": -80.123
                    },
                    "originalIndex": 0,
                    "placeId": "ChIJ..."
                }
            ]
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        points = [(35.1, -80.1)]
        result = self.service.snap_to_roads(points)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0], (35.123, -80.123))

if __name__ == '__main__':
    unittest.main()
