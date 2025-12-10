"""
Materials Module
Handles creation and management of road materials
"""

import bpy
from typing import Dict, List, Optional, Any, Tuple
import logging

from .config import RoadProcessorConfig, RoadCategory
from .processor import RoadSegment

log = logging.getLogger(__name__)

class MaterialManager:
    """Manages road materials and texturing"""

    def __init__(self, config: RoadProcessorConfig):
        """
        Initialize material manager

        Args:
            config: Road processor configuration
        """
        self.config = config

        # Material cache
        self._material_cache = {}

        # Material presets
        self._material_presets = self._create_material_presets()

    def apply_materials(self,
                       context: bpy.types.Context,
                       obj: bpy.types.Object,
                       segment: RoadSegment) -> bool:
        """
        Apply materials to road object

        Args:
            context: Blender context
            obj: Road object
            segment: Road segment data

        Returns:
            True if materials applied successfully
        """
        try:
            if not self.config.create_materials:
                return True

            # Get appropriate material
            material = self._get_or_create_material(context, segment)
            if not material:
                log.warning(f"Failed to create material for {segment.osm_id}")
                return False

            # Apply material to object
            if obj.data and hasattr(obj.data, 'materials'):
                # Clear existing materials
                obj.data.materials.clear()
                # Apply new material
                obj.data.materials.append(material)

            # Apply layered materials if configured
            if self.config.use_layered_materials:
                self._apply_layered_materials(context, obj, segment)

            return True

        except Exception as e:
            log.error(f"Material application failed for {segment.osm_id}: {str(e)}")
            return False

    def _get_or_create_material(self,
                               context: bpy.types.Context,
                               segment: RoadSegment) -> Optional[bpy.types.Material]:
        """
        Get existing material or create new one

        Args:
            context: Blender context
            segment: Road segment data

        Returns:
            Material object
        """
        try:
            # Generate material name
            material_name = self.config.material_naming_convention.format(
                type=segment.highway_type
            )

            # Check cache first
            if material_name in self._material_cache:
                return self._material_cache[material_name]

            # Check if material already exists
            if material_name in bpy.data.materials:
                material = bpy.data.materials[material_name]
                self._material_cache[material_name] = material
                return material

            # Create new material
            material = self._create_material(context, material_name, segment)
            if material:
                self._material_cache[material_name] = material

            return material

        except Exception as e:
            log.error(f"Material creation failed: {str(e)}")
            return None

    def _create_material(self,
                        context: bpy.types.Context,
                        name: str,
                        segment: RoadSegment) -> Optional[bpy.types.Material]:
        """
        Create new material for road segment

        Args:
            context: Blender context
            name: Material name
            segment: Road segment data

        Returns:
            Created material
        """
        try:
            # Create material
            material = bpy.data.materials.new(name=name)
            material.use_nodes = True

            # Get material preset
            preset = self._get_material_preset(segment)

            # Setup material nodes
            self._setup_material_nodes(material, preset)

            return material

        except Exception as e:
            log.error(f"Material creation failed: {str(e)}")
            return None

    def _get_material_preset(self, segment: RoadSegment) -> Dict[str, Any]:
        """
        Get material preset for road segment

        Args:
            segment: Road segment data

        Returns:
            Material preset configuration
        """
        # Base material config from category
        base_config = self.config.get_material_config('base')

        # Customize based on highway type
        highway_presets = {
            'motorway': {'color': (0.1, 0.1, 0.1, 1.0), 'roughness': 0.7},
            'trunk': {'color': (0.15, 0.15, 0.15, 1.0), 'roughness': 0.75},
            'primary': {'color': (0.2, 0.2, 0.2, 1.0), 'roughness': 0.8},
            'secondary': {'color': (0.25, 0.25, 0.25, 1.0), 'roughness': 0.8},
            'tertiary': {'color': (0.3, 0.3, 0.3, 1.0), 'roughness': 0.85},
            'residential': {'color': (0.35, 0.35, 0.35, 1.0), 'roughness': 0.9},
            'service': {'color': (0.25, 0.25, 0.25, 1.0), 'roughness': 0.9},
            'footway': {'color': (0.5, 0.4, 0.3, 1.0), 'roughness': 0.95},
            'cycleway': {'color': (0.3, 0.3, 0.2, 1.0), 'roughness': 0.9},
            'pedestrian': {'color': (0.45, 0.45, 0.45, 1.0), 'roughness': 0.85}
        }

        # Merge preset with base config
        preset = base_config.copy()
        if segment.highway_type in highway_presets:
            preset.update(highway_presets[segment.highway_type])

        return preset

    def _setup_material_nodes(self,
                             material: bpy.types.Material,
                             preset: Dict[str, Any]):
        """
        Setup material nodes for road material

        Args:
            material: Blender material
            preset: Material preset configuration
        """
        try:
            # Clear default nodes
            material.node_tree.nodes.clear()

            # Create main shader node
            principled_bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

            # Set material properties
            principled_bsdf.inputs['Base Color'].default_value = preset['color']
            principled_bsdf.inputs['Roughness'].default_value = preset['roughness']
            principled_bsdf.inputs['Metallic'].default_value = preset.get('metallic', 0.0)
            principled_bsdf.inputs['Specular'].default_value = preset.get('specular', 0.1)

            # Create output node
            material_output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            # Link nodes
            material.node_tree.links.new(
                principled_bsdf.outputs['BSDF'],
                material_output.inputs['Surface']
            )

            # Add procedural details if configured
            if self.config.generate_road_markings:
                self._add_road_marking_nodes(material, preset)

        except Exception as e:
            log.error(f"Material node setup failed: {str(e)}")

    def _add_road_marking_nodes(self,
                               material: bpy.types.Material,
                               preset: Dict[str, Any]):
        """
        Add procedural road marking nodes

        Args:
            material: Blender material
            preset: Material preset configuration
        """
        try:
            # Create texture coordinate node
            tex_coord = material.node_tree.nodes.new(type='ShaderNodeTexCoord')

            # Create separate XYZ node for UV manipulation
            separate_xyz = material.node_tree.nodes.new(type='ShaderNodeSeparateXYZ')
            material.node_tree.links.new(
                tex_coord.outputs['UV'],
                separate_xyz.inputs['Vector']
            )

            # Create math nodes for stripe pattern
            multiply_x = material.node_tree.nodes.new(type='ShaderNodeMath')
            multiply_x.operation = 'MULTIPLY'
            multiply_x.inputs[1].default_value = 10.0  # Stripe frequency
            material.node_tree.links.new(
                separate_xyz.outputs['X'],
                multiply_x.inputs[0]
            )

            # Modulo for repeating pattern
            modulo = material.node_tree.nodes.new(type='ShaderNodeMath')
            modulo.operation = 'MODULO'
            modulo.inputs[1].default_value = 1.0
            material.node_tree.links.new(
                multiply_x.outputs['Value'],
                modulo.inputs[0]
            )

            # Greater than for mask
            greater_than = material.node_tree.nodes.new(type='ShaderNodeMath')
            greater_than.operation = 'GREATER_THAN'
            greater_than.inputs[1].default_value = 0.5
            material.node_tree.links.new(
                modulo.outputs['Value'],
                greater_than.inputs[0]
            )

            # Mix shader for markings
            mix_shader = material.node_tree.nodes.new(type='ShaderNodeMixShader')
            mix_shader.inputs['Fac'].default_value = greater_than.outputs['Value']

            # Create marking material
            marking_material = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            marking_material.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            marking_material.inputs['Roughness'].default_value = 0.3

            # Get main shader
            main_shader = None
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED' and node != marking_material:
                    main_shader = node
                    break

            if main_shader:
                # Connect mix shader
                material.node_tree.links.new(
                    main_shader.outputs['BSDF'],
                    mix_shader.inputs[1]
                )
                material.node_tree.links.new(
                    marking_material.outputs['BSDF'],
                    mix_shader.inputs[2]
                )

                # Update output connection
                material_output = None
                for node in material.node_tree.nodes:
                    if node.type == 'OUTPUT_MATERIAL':
                        material_output = node
                        break

                if material_output:
                    material.node_tree.links.new(
                        mix_shader.outputs['Shader'],
                        material_output.inputs['Surface']
                    )

        except Exception as e:
            log.warning(f"Road marking nodes setup failed: {str(e)}")

    def _apply_layered_materials(self,
                                context: bpy.types.Context,
                                obj: bpy.types.Object,
                                segment: RoadSegment):
        """
        Apply layered materials for advanced road surface

        Args:
            context: Blender context
            obj: Road object
            segment: Road segment data
        """
        try:
            # This is a placeholder for advanced layered material system
            # Could implement separate material layers for:
            # - Base asphalt
            # - Road markings
            # - Wear and tear
            # - Surface texture

            log.debug(f"Layered materials not implemented for {segment.osm_id}")

        except Exception as e:
            log.warning(f"Layered material application failed: {str(e)}")

    def _create_material_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Create predefined material presets

        Returns:
            Dictionary of material presets
        """
        presets = {
            'asphalt_dark': {
                'color': (0.1, 0.1, 0.1, 1.0),
                'roughness': 0.8,
                'metallic': 0.0,
                'specular': 0.1
            },
            'asphalt_medium': {
                'color': (0.2, 0.2, 0.2, 1.0),
                'roughness': 0.8,
                'metallic': 0.0,
                'specular': 0.1
            },
            'concrete': {
                'color': (0.4, 0.4, 0.4, 1.0),
                'roughness': 0.9,
                'metallic': 0.0,
                'specular': 0.2
            },
            'gravel': {
                'color': (0.3, 0.25, 0.2, 1.0),
                'roughness': 0.95,
                'metallic': 0.0,
                'specular': 0.05
            },
            'pavement': {
                'color': (0.5, 0.4, 0.3, 1.0),
                'roughness': 0.85,
                'metallic': 0.0,
                'specular': 0.1
            }
        }

        return presets

    def cleanup_materials(self):
        """Clean up unused materials"""
        try:
            # Remove materials with no users
            for material in bpy.data.materials:
                if material.users == 0:
                    bpy.data.materials.remove(material)

            log.info("Material cleanup completed")

        except Exception as e:
            log.warning(f"Material cleanup failed: {str(e)}")

    def get_material_statistics(self) -> Dict[str, Any]:
        """
        Get material usage statistics

        Returns:
            Material statistics dictionary
        """
        stats = {
            'total_materials': len(bpy.data.materials),
            'cached_materials': len(self._material_cache),
            'road_materials': 0,
            'material_list': []
        }

        for material in bpy.data.materials:
            if 'Road_' in material.name:
                stats['road_materials'] += 1
                stats['material_list'].append({
                    'name': material.name,
                    'users': material.users,
                    'node_count': len(material.node_tree.nodes) if material.use_nodes else 0
                })

        return stats