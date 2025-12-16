
import bpy

# Extracted from gui/operators.py (Archived)
class BLOSM_OT_TestGoogleGeocode(bpy.types.Operator):
    """Test Google Maps Geocoding and Snapping"""
    bl_idname = "blosm.test_google_geocode"
    bl_label = "Test Google Geocode"
    bl_description = "Geocode and snap the test address using Google API"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addon = context.scene.blosm
        # NOTE: API key and test address were removed from properties in the refactor.
        # This code expects them to exist.
        api_key = getattr(addon, "google_api_key", "")
        address = getattr(addon, "google_test_address", "")
        
        if not api_key:
            self.report({'ERROR'}, "API Key required")
            return {'CANCELLED'}
            
        print(f"\n[Google Test] Starting test for: '{address}'")
        
        try:
            from route.services.google_maps import GoogleMapsService
            svc = GoogleMapsService(api_key)
            
            # 1. Geocode
            print(f"[Google Test] Geocoding...")
            geo_res = svc.geocode(address)
            if not geo_res.success:
                self.report({'ERROR'}, f"Geocode failed: {geo_res.error}")
                print(f"[Google Test] Geocode Failed: {geo_res.error}")
                return {'CANCELLED'}
            
            print(f"[Google Test] Geocode Result: {geo_res.data}")
            lat, lon = geo_res.data.lat, geo_res.data.lon
            print(f"[Google Test] Raw Lat/Lon: {lat}, {lon}")
            
            self.report({'INFO'}, f"Geocoded: {lat:.6f}, {lon:.6f}")

            # 2. Snap
            print(f"[Google Test] Snapping ({lat}, {lon}) to roads...")
            snap_res = svc.snap_to_roads([(lat, lon)])
            
            if not snap_res.success:
                print(f"[Google Test] Snap failed/empty: {snap_res.error}")
                self.report({'WARNING'}, f"Snap failed: {snap_res.error}")
            else:
                 print(f"[Google Test] Snap Result: {snap_res.data}")
                 if snap_res.data:
                     s_lat, s_lon = snap_res.data[0]
                     print(f"[Google Test] Snapped Lat/Lon: {s_lat}, {s_lon}")
                     self.report({'INFO'}, f"Snapped: {s_lat:.6f}, {s_lon:.6f}")
                 else:
                     print(f"[Google Test] No snapped points found.")
                     self.report({'INFO'}, "No snapped points returned (too far from road?)")
                     
        except Exception as e:
            self.report({'ERROR'}, f"Exception: {e}")
            print(f"[Google Test] Exception: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
            
        return {'FINISHED'}
