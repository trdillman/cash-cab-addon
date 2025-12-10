"""
Curve Converter Module
Handles conversion of road coordinates to Blender curves and meshes
"""

import bpy
import bmesh
import mathutils
from typing import Dict, List, Optional, Tuple, Any
import logging
import math

from .config import RoadProcessorConfig
from .processor import RoadSegment

log = logging.getLogger(__name__)

class CurveConverter:
    """Converts road segments to Blender curves and meshes"""

    def __init__(self, config: RoadProcessorConfig):
        """
        Initialize curve converter

        Args:
            config: Road processor configuration
        """
        self.config = config

    def convert_to_mesh(self,
                       context: bpy.types.Context,
                       segment: RoadSegment) -> Optional[bpy.types.Object]:
        """
        Convert road segment to mesh object

        Args:
            context: Blender context
            segment: Road segment data

        Returns:
            Created mesh object or None if conversion failed
        """
        try:
            # Step 1: Create curve from coordinates
            curve_obj = self._create_curve(context, segment)
            if not curve_obj:
                return None

            # Step 2: Convert curve to mesh
            mesh_obj = self._curve_to_mesh(context, curve_obj, segment)

            # Step 3: Clean up curve if not needed
            if mesh_obj and curve_obj != mesh_obj:
                bpy.data.objects.remove(curve_obj, do_unlink=True)

            # Step 4: Set object properties
            if mesh_obj:
                self._set_object_properties(mesh_obj, segment)

            return mesh_obj

        except Exception as e:
            log.error(f"Curve conversion failed for {segment.osm_id}: {str(e)}")
            return None

    def _create_curve(self,
                     context: bpy.types.Context,
                     segment: RoadSegment) -> Optional[bpy.types.Object]:
        """
        Create Blender curve from road coordinates

        Args:
            context: Blender context
            segment: Road segment data

        Returns:
            Curve object or None if creation failed
        """
        try:
            # Create curve data
            curve_data = bpy.data.curves.new(
                name=f"Road_{segment.osm_id}",
                type='CURVE'
            )

            # Set curve properties
            curve_data.dimensions = '3D'
            curve_data.resolution_u = self.config.curve_resolution
            curve_data.render_resolution_u = self.config.curve_resolution

            # Create spline from coordinates
            spline = curve_data.splines.new('NURBS')
            self._populate_spline(spline, segment)

            # Create curve object
            curve_obj = bpy.data.objects.new(
                name=f"Road_{segment.osm_id}",
                object_data=curve_data
            )

            # Link to scene
            context.scene.collection.objects.link(curve_obj)

            return curve_obj

        except Exception as e:
            log.error(f"Curve creation failed for {segment.osm_id}: {str(e)}")
            return None

    def _populate_spline(self, spline: bpy.types.Spline, segment: RoadSegment):
        """
        Populate spline with road coordinates

        Args:
            spline: Blender spline to populate
            segment: Road segment data
        """
        # Add points to spline
        spline.points.add(len(segment.coordinates) - 1)

        # Convert coordinates to 3D
        for i, (lat, lon) in enumerate(segment.coordinates):
            # Convert lat/lon to local coordinates (assuming simple projection)
            x, y, z = self._latlon_to_local(lat, lon)
            spline.points[i].co = (x, y, z, 1.0)  # w = 1.0 for NURBS

        # Set spline properties
        spline.use_cyclic_u = False
        spline.order_u = 2  # Quadratic NURBS

        # Apply smoothness if configured
        if self.config.curve_smoothness < 1.0:
            self._apply_spline_smoothing(spline, segment)

    def _latlon_to_local(self, lat: float, lon: float) -> Tuple[float, float, float]:
        """
        Convert lat/lon to local coordinates (simplified projection)

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            (x, y, z) local coordinates
        """
        # Simple equirectangular projection
        # This is a basic implementation - could use proper projection for better accuracy
        scale = 111320.0  # meters per degree at equator
        x = lon * scale * math.cos(math.radians(lat))
        y = lat * scale
        z = 0.0  # Flat ground level

        return (x, y, z)

    def _apply_spline_smoothing(self, spline: bpy.types.Spline, segment: RoadSegment):
        """
        Apply smoothing to spline based on configuration

        Args:
            spline: Blender spline
            segment: Road segment data
        """
        if len(segment.coordinates) < 3:
            return

        # Smoothness affects the tension of NURBS knots
        # This is a simplified implementation
        target_points = max(3, int(len(segment.coordinates) * self.config.curve_smoothness))

        if len(spline.points) > target_points:
            # Resample spline to reduce points
            self._resample_spline(spline, target_points)

    def _resample_spline(self, spline: bpy.types.Spline, target_points: int):
        """
        Resample spline to target number of points

        Args:
            spline: Blender spline to resample
            target_points: Target number of points
        """
        # Store original points
        original_points = [p.co.copy() for p in spline.points]

        # Clear and recreate points
        spline.points.clear()
        spline.points.add(target_points - 1)

        # Interpolate new points
        for i in range(target_points):
            t = i / (target_points - 1)
            source_index = int(t * (len(original_points) - 1))
            source_index = min(source_index, len(original_points) - 1)
            spline.points[i].co = original_points[source_index]

    def _curve_to_mesh(self,
                      context: bpy.types.Context,
                      curve_obj: bpy.types.Object,
                      segment: RoadSegment) -> Optional[bpy.types.Object]:
        """
        Convert curve to mesh with road width

        Args:
            context: Blender context
            curve_obj: Curve object to convert
            segment: Road segment data

        Returns:
            Mesh object or None if conversion failed
        """
        try:
            # Get curve data
            curve_data = curve_obj.data

            # Add bevel for road width
            if not curve_data.bevel_object:
                bevel_obj = self._create_bevel_object(segment)
                if bevel_obj:
                    curve_data.bevel_object = bevel_obj

            # Convert to mesh
            mesh = bpy.data.meshes.new_from_object(
                curve_obj,
                preserve_all_data_layers=False,
                depsgraph=context.evaluated_depsgraph_get()
            )

            # Create mesh object
            mesh_obj = bpy.data.objects.new(
                name=f"Road_{segment.osm_id}_mesh",
                object_data=mesh
            )

            # Link to scene
            context.scene.collection.objects.link(mesh_obj)

            # Clean up mesh if needed
            if self.config.validate_geometry:
                self._clean_mesh_geometry(mesh_obj)

            return mesh_obj

        except Exception as e:
            log.error(f"Curve to mesh conversion failed for {segment.osm_id}: {str(e)}")
            return None

    def _create_bevel_object(self, segment: RoadSegment) -> Optional[bpy.types.Object]:
        """
        Create bevel object for road width

        Args:
            segment: Road segment data

        Returns:
            Bevel curve object
        """
        try:
            # Create bevel curve (simple rectangle)
            bevel_curve = bpy.data.curves.new(
                name=f"Bevel_{segment.osm_id}",
                type='CURVE'
            )
            bevel_curve.dimensions = '2D'
            bevel_curve.fill_mode = 'FULL'

            # Create rectangular shape for road profile
            spline = bevel_curve.splines.new('POLY')
            spline.points.add(3)  # Rectangle needs 4 points

            half_width = segment.width / 2.0

            # Rectangle points (clockwise)
            spline.points[0].co = (-half_width, 0, 0, 1)
            spline.points[1].co = (half_width, 0, 0, 1)
            spline.points[2].co = (half_width, self.config.mesh_bevel_depth, 0, 1)
            spline.points[3].co = (-half_width, self.config.mesh_bevel_depth, 0, 1)

            # Create bevel object
            bevel_obj = bpy.data.objects.new(
                name=f"Bevel_{segment.osm_id}",
                object_data=bevel_curve
            )

            # Hide bevel object from viewport
            bevel_obj.hide_viewport = True
            bevel_obj.hide_render = True

            return bevel_obj

        except Exception as e:
            log.error(f"Bevel object creation failed for {segment.osm_id}: {str(e)}")
            return None

    def _clean_mesh_geometry(self, mesh_obj: bpy.types.Object):
        """
        Clean and repair mesh geometry

        Args:
            mesh_obj: Mesh object to clean
        """
        try:
            # Get mesh data
            mesh = mesh_obj.data

            if not mesh or len(mesh.polygons) == 0:
                return

            # Create bmesh for cleaning
            bm = bmesh.new()
            bm.from_mesh(mesh)

            # Remove duplicate vertices
            bmesh.ops.remove_doubles(
                bm,
                verts=bm.verts,
                dist=0.001
            )

            # Remove loose geometry
            bmesh.ops.delete(
                bm,
                geom=[v for v in bm.verts if len(v.link_edges) == 0],
                context='VERTS'
            )

            # Recalculate normals
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

            # Update mesh
            bm.to_mesh(mesh)
            bm.free()

        except Exception as e:
            log.warning(f"Mesh cleaning failed: {str(e)}")

    def _set_object_properties(self, obj: bpy.types.Object, segment: RoadSegment):
        """
        Set custom properties on road object

        Args:
            obj: Blender object
            segment: Road segment data
        """
        try:
            # Set custom properties
            obj["osm_id"] = segment.osm_id
            obj["highway_type"] = segment.highway_type
            obj["road_category"] = segment.category.value
            obj["road_width"] = segment.width
            obj["road_priority"] = segment.priority

            if segment.name:
                obj["road_name"] = segment.name

            # Store reference to segment data
            obj.road_category = segment.category

            # Set display properties
            obj.display_type = 'TEXTURED'
            obj.show_shadows = True

        except Exception as e:
            log.warning(f"Failed to set object properties: {str(e)}")

    def optimize_curve(self, curve_obj: bpy.types.Object):
        """
        Optimize curve for performance

        Args:
            curve_obj: Curve object to optimize
        """
        try:
            if not self.config.simplify_geometry:
                return

            curve_data = curve_obj.data

            # Reduce resolution if possible
            if curve_data.resolution_u > self.config.curve_resolution:
                curve_data.resolution_u = self.config.curve_resolution

            # Simplify spline points
            for spline in curve_data.splines:
                if len(spline.points) > self.config.simplification_threshold * 10:
                    self._resample_spline(spline, int(len(spline.points) * self.config.simplification_threshold))

        except Exception as e:
            log.warning(f"Curve optimization failed: {str(e)}")