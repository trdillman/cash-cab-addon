"""
CashCab Addon Preferences
"""
import bpy

class BlosmPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__.split(".")[0]  # assumes top-level package name

    google_api_key: bpy.props.StringProperty(
        name="Google Maps API Key",
        description="API Key for Google Maps Platform (Geocoding, Directions, Roads)",
        default="",
        subtype='PASSWORD',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Google Maps Platform Integration")
        row = layout.row()
        row.prop(self, "google_api_key")
        if not self.google_api_key:
             layout.label(text="Enter API Key to enable Geocoding and Snapping features", icon='INFO')
