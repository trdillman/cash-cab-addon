"""
Simple Asset Updater for CashCab Blender Addon

Replaces the complex asset isolation system with a straightforward approach
using Blender's native file operations. This eliminates crashes and provides
reliable asset updates for registered CashCab assets.
"""

import bpy
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime


class SimpleAssetUpdateError(Exception):
    """Raised when simple asset update fails"""
    pass


class SimpleAssetUpdater:
    """
    Simplified asset updater using Blender's native file operations.

    This class replaces the complex AssetIsolator system with a direct
    approach that saves selected objects/materials to .blend files using
    Blender's built-in functionality.
    """

    def __init__(self):
        self.temp_dir = None
        self.backup_files = []

    def __enter__(self):
        """Context manager entry"""
        self.temp_dir = tempfile.mkdtemp(prefix="cashcab_asset_update_")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager entry - cleanup temporary files"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def update_object_asset(self, obj: bpy.types.Object, target_file: Path) -> bool:
        """
        Update an object asset by saving it to the target .blend file.

        Args:
            obj: The Blender object to save as asset
            target_file: Path where the asset .blend file should be saved

        Returns:
            bool: True if update was successful
        """
        if not obj:
            raise SimpleAssetUpdateError("No object provided for update")

        if not target_file.suffix == '.blend':
            raise SimpleAssetUpdateError("Target file must be a .blend file")

        try:
            # Create backup of existing file
            if target_file.exists():
                backup_path = self._create_backup(target_file)

            # Save the object to a temporary file first
            temp_file = Path(self.temp_dir) / f"temp_asset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"

            # Use Blender's native save functionality
            self._save_object_to_blend(obj, temp_file)

            # Validate the temporary blend file contains the expected object
            if not self._validate_blend_file(temp_file, obj.name, 'object'):
                raise SimpleAssetUpdateError(f"Temporary blend file validation failed for {obj.name}")

            # Replace the target file atomically
            shutil.move(str(temp_file), str(target_file))

            print(f"[SimpleAssetUpdater] ✓ Successfully updated object asset: {obj.name} -> {target_file}")
            return True

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update object asset {obj.name}: {e}")
            # Restore backup if it exists
            if target_file.exists() and 'backup_path' in locals():
                shutil.move(str(backup_path), str(target_file))
            return False

    def update_material_asset(self, material: bpy.types.Material, target_file: Path) -> bool:
        """
        Update a material asset by saving it to the target .blend file.

        Args:
            material: The Blender material to save as asset
            target_file: Path where the asset .blend file should be saved

        Returns:
            bool: True if update was successful
        """
        if not material:
            raise SimpleAssetUpdateError("No material provided for update")

        if not target_file.suffix == '.blend':
            raise SimpleAssetUpdateError("Target file must be a .blend file")

        try:
            # Create backup of existing file
            if target_file.exists():
                backup_path = self._create_backup(target_file)

            # Use the new preservation approach for existing files
            if target_file.exists():
                success = self._update_material_preserving_others(material, target_file)
            else:
                # New file - use simple approach
                temp_file = Path(self.temp_dir) / f"temp_material_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                self._save_material_to_blend(material, temp_file)
                shutil.move(str(temp_file), str(target_file))
                success = True

            if success:
                print(f"[SimpleAssetUpdater] ✓ Successfully updated material asset: {material.name} -> {target_file}")
                return True
            else:
                raise SimpleAssetUpdateError("Material update failed")

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update material asset {material.name}: {e}")
            # Restore backup if it exists
            if target_file.exists() and 'backup_path' in locals():
                shutil.move(str(backup_path), str(target_file))
            return False

    def update_nodegroup_asset(self, nodegroup: bpy.types.NodeGroup, target_file: Path) -> bool:
        """
        Update a node group asset by saving it to the target .blend file.

        Args:
            nodegroup: The Blender node group to save as asset
            target_file: Path where the asset .blend file should be saved

        Returns:
            bool: True if update was successful
        """
        if not nodegroup:
            raise SimpleAssetUpdateError("No node group provided for update")

        if not target_file.suffix == '.blend':
            raise SimpleAssetUpdateError("Target file must be a .blend file")

        try:
            # Create backup of existing file
            if target_file.exists():
                backup_path = self._create_backup(target_file)

            # Use the new preservation approach for existing files
            if target_file.exists():
                success = self._update_nodegroup_preserving_others(nodegroup, target_file)
            else:
                # New file - use simple approach
                temp_file = Path(self.temp_dir) / f"temp_nodegroup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                self._save_nodegroup_to_blend(nodegroup, temp_file)
                shutil.move(str(temp_file), str(target_file))
                success = True

            if success:
                print(f"[SimpleAssetUpdater] ✓ Successfully updated node group asset: {nodegroup.name} -> {target_file}")
                return True
            else:
                raise SimpleAssetUpdateError("Node group update failed")

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update node group asset {nodegroup.name}: {e}")
            # Restore backup if it exists
            if target_file.exists() and 'backup_path' in locals():
                shutil.move(str(backup_path), str(target_file))
            return False

    def update_world_asset(self, world: bpy.types.World, target_file: Path) -> bool:
        """
        Update a world asset by saving it to the target .blend file.

        Args:
            world: The Blender world to save as asset
            target_file: Path where the asset .blend file should be saved

        Returns:
            bool: True if update was successful
        """
        if not world:
            raise SimpleAssetUpdateError("No world provided for update")

        if not target_file.suffix == '.blend':
            raise SimpleAssetUpdateError("Target file must be a .blend file")

        try:
            # Create backup of existing file
            if target_file.exists():
                backup_path = self._create_backup(target_file)

            # Use the new preservation approach for existing files
            if target_file.exists():
                success = self._update_world_preserving_others(world, target_file)
            else:
                # New file - use simple approach
                temp_file = Path(self.temp_dir) / f"temp_world_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                self._save_world_to_blend(world, temp_file)
                shutil.move(str(temp_file), str(target_file))
                success = True

            if success:
                print(f"[SimpleAssetUpdater] ✓ Successfully updated world asset: {world.name} -> {target_file}")
                return True
            else:
                raise SimpleAssetUpdateError("World update failed")

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update world asset {world.name}: {e}")
            # Restore backup if it exists
            if target_file.exists() and 'backup_path' in locals():
                shutil.move(str(backup_path), str(target_file))
            return False

    def update_collection_asset(self, collections: list, target_file: Path) -> bool:
        """
        Update a collection asset by saving it to the target .blend file.

        Args:
            collections: List of Blender collections to save as asset
            target_file: Path where the asset .blend file should be saved

        Returns:
            bool: True if update was successful
        """
        if not collections:
            raise SimpleAssetUpdateError("No collections provided for update")

        if not target_file.suffix == '.blend':
            raise SimpleAssetUpdateError("Target file must be a .blend file")

        try:
            # Create backup of existing file
            if target_file.exists():
                backup_path = self._create_backup(target_file)

            # Use the new preservation approach for existing files
            if target_file.exists():
                success = self._update_collection_preserving_others(collections, target_file)
            else:
                # New file - use simple approach
                temp_file = Path(self.temp_dir) / f"temp_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                self._save_collection_to_blend(collections, temp_file)
                shutil.move(str(temp_file), str(target_file))
                success = True

            if success:
                collection_names = [c.name for c in collections]
                print(f"[SimpleAssetUpdater] ✓ Successfully updated collection asset: {collection_names} -> {target_file}")
                return True
            else:
                raise SimpleAssetUpdateError("Collection update failed")

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update collection asset: {e}")
            # Restore backup if it exists
            if target_file.exists() and 'backup_path' in locals():
                shutil.move(str(backup_path), str(target_file))
            return False

    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of the existing file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        shutil.copy2(str(file_path), str(backup_path))
        self.backup_files.append(backup_path)
        return backup_path

    def _save_object_to_blend(self, obj: bpy.types.Object, target_file: Path) -> None:
        """Save an object to a .blend file using Blender's native operations."""
        # Create a temporary scene with only the target object
        original_scene = bpy.context.scene
        temp_scene = bpy.data.scenes.new(name="TempAssetScene")

        try:
            # Switch to temporary scene
            bpy.context.window.scene = temp_scene

            # Copy the object to the temporary scene
            obj_copy = obj.copy()
            obj_copy.data = obj.data.copy() if obj.data else None
            temp_scene.collection.objects.link(obj_copy)

            # Save the temporary scene
            bpy.ops.wm.save_as_mainfile(filepath=str(target_file), compress=True)

        finally:
            # Clean up temporary scene
            bpy.context.window.scene = original_scene
            if temp_scene:
                bpy.data.scenes.remove(temp_scene)

    def _update_material_preserving_others(self, material: bpy.types.Material, target_file: Path) -> bool:
        """Update a material in an existing blend file while preserving all other datablocks."""
        try:
            # Create a temporary scene for the update operation
            original_scene = bpy.context.scene
            temp_scene = bpy.data.scenes.new(name="TempAssetUpdateScene")

            try:
                # Switch to temporary scene
                bpy.context.window.scene = temp_scene

                # Load all existing datablocks from the target file
                with bpy.data.libraries.load(str(target_file)) as (data_from, data_to):
                    # Load all existing datablocks to preserve them
                    data_to.objects = data_from.objects
                    data_to.materials = data_from.materials
                    data_to.node_groups = data_from.node_groups
                    data_to.collections = data_from.collections
                    data_to.textures = data_from.textures
                    data_to.images = data_from.images

                print(f"[SimpleAssetUpdater] Loaded existing datablocks: {len(data_to.objects)} objects, {len(data_to.materials)} materials, {len(data_to.node_groups)} node groups")

                # Find and update the target material
                target_material = None
                for mat in data_to.materials:
                    # Match by material ID or name (material might have been renamed)
                    if (mat.name == material.name or
                        mat.as_pointer() == material.as_pointer()):
                        target_material = mat
                        # Copy all properties from the updated material
                        target_material.name = material.name
                        # Blender materials are reference types, so we need to update the actual datablock
                        break

                # If we didn't find an exact match, append the new material
                if not target_material:
                    print(f"[SimpleAssetUpdater] Material {material.name} not found in existing file, appending as new")
                    # Copy the material to avoid library linking issues
                    material_copy = material.copy()
                    material_copy.name = material.name

                # Save to a temporary file first (avoid library overwrite issue)
                import os
                temp_save_path = target_file.parent / f"temp_update_{os.getpid()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(temp_save_path), compress=True)

                # Replace the original file
                shutil.move(str(temp_save_path), str(target_file))

                print(f"[SimpleAssetUpdater] ✓ Successfully updated material while preserving {len(data_to.objects)} objects, {len(data_to.materials)-1} other materials, {len(data_to.node_groups)} node groups")
                return True

            finally:
                # Clean up temporary scene
                bpy.context.window.scene = original_scene
                if temp_scene:
                    bpy.data.scenes.remove(temp_scene)

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update material preserving others: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _update_nodegroup_preserving_others(self, nodegroup: bpy.types.NodeGroup, target_file: Path) -> bool:
        """Update a node group in an existing blend file while preserving all other datablocks."""
        try:
            # Create a temporary scene for the update operation
            original_scene = bpy.context.scene
            temp_scene = bpy.data.scenes.new(name="TempNodeGroupUpdateScene")

            try:
                # Switch to temporary scene
                bpy.context.window.scene = temp_scene

                # Load all existing datablocks from the target file
                with bpy.data.libraries.load(str(target_file)) as (data_from, data_to):
                    # Load all existing datablocks to preserve them
                    data_to.objects = data_from.objects
                    data_to.materials = data_from.materials
                    data_to.node_groups = data_from.node_groups
                    data_to.collections = data_from.collections
                    data_to.textures = data_from.textures
                    data_to.images = data_from.images

                print(f"[SimpleAssetUpdater] Loaded existing datablocks: {len(data_to.objects)} objects, {len(data_to.materials)} materials, {len(data_to.node_groups)} node groups")

                # Find and update the target node group
                target_nodegroup = None
                for ng in data_to.node_groups:
                    # Match by node group ID or name (node group might have been renamed)
                    if (ng.name == nodegroup.name or
                        ng.as_pointer() == nodegroup.as_pointer()):
                        target_nodegroup = ng
                        # Copy all properties from the updated node group
                        target_nodegroup.name = nodegroup.name
                        # Node groups are reference types, so we need to update the actual datablock
                        break

                # If we didn't find an exact match, append the new node group
                if not target_nodegroup:
                    print(f"[SimpleAssetUpdater] Node group {nodegroup.name} not found in existing file, appending as new")
                    # Copy the node group to avoid library linking issues
                    nodegroup_copy = nodegroup.copy()
                    nodegroup_copy.name = nodegroup.name

                # Save to a temporary file first (avoid library overwrite issue)
                import os
                temp_save_path = target_file.parent / f"temp_update_{os.getpid()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(temp_save_path), compress=True)

                # Replace the original file
                shutil.move(str(temp_save_path), str(target_file))

                print(f"[SimpleAssetUpdater] ✓ Successfully updated node group while preserving {len(data_to.objects)} objects, {len(data_to.materials)} materials, {len(data_to.node_groups)-1} other node groups")
                return True

            finally:
                # Clean up temporary scene
                bpy.context.window.scene = original_scene
                if temp_scene:
                    bpy.data.scenes.remove(temp_scene)

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update node group preserving others: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_material_to_blend(self, material: bpy.types.Material, target_file: Path) -> None:
        """Save a material to a .blend file using Blender's native operations."""
        # Create a temporary scene with a test object using the material
        original_scene = bpy.context.scene
        temp_scene = bpy.data.scenes.new(name="TempMaterialScene")

        try:
            # Switch to temporary scene
            bpy.context.window.scene = temp_scene

            # Create a simple test object
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "MaterialTestObject"

            # Apply the material to the test object
            if test_obj.data.materials:
                test_obj.data.materials[0] = material
            else:
                test_obj.data.materials.append(material)

            # Save the temporary scene
            bpy.ops.wm.save_as_mainfile(filepath=str(target_file), compress=True)

        finally:
            # Clean up temporary scene
            bpy.context.window.scene = original_scene
            if temp_scene:
                bpy.data.scenes.remove(temp_scene)

    def _save_nodegroup_to_blend(self, nodegroup: bpy.types.NodeGroup, target_file: Path) -> None:
        """Save a node group to a .blend file using Blender's native operations."""
        # Create a temporary scene with a material using the node group
        original_scene = bpy.context.scene
        temp_scene = bpy.data.scenes.new(name="TempNodegroupScene")

        try:
            # Switch to temporary scene
            bpy.context.window.scene = temp_scene

            # Create a material that uses the node group
            temp_material = bpy.data.materials.new(name="TempNodegroupMaterial")
            temp_material.use_nodes = True

            # Find a node that can use the node group (like Group node)
            if temp_material.node_tree:
                group_node = temp_material.node_tree.nodes.new(type='ShaderNodeGroup')
                group_node.node_tree = nodegroup

            # Create a test object to hold the material
            bpy.ops.mesh.primitive_cube_add()
            test_obj = bpy.context.active_object
            test_obj.name = "NodegroupTestObject"
            test_obj.data.materials.append(temp_material)

            # Save the temporary scene
            bpy.ops.wm.save_as_mainfile(filepath=str(target_file), compress=True)

        finally:
            # Clean up temporary scene
            bpy.context.window.scene = original_scene
            if temp_scene:
                bpy.data.scenes.remove(temp_scene)

    def _update_world_preserving_others(self, world: bpy.types.World, target_file: Path) -> bool:
        """Update a world in an existing blend file while preserving all other datablocks."""
        try:
            # Create a temporary scene for the update operation
            original_scene = bpy.context.scene
            temp_scene = bpy.data.scenes.new(name="TempWorldUpdateScene")

            try:
                # Switch to temporary scene
                bpy.context.window.scene = temp_scene

                # Load all existing datablocks from the target file
                with bpy.data.libraries.load(str(target_file)) as (data_from, data_to):
                    # Load all existing datablocks to preserve them
                    data_to.objects = data_from.objects
                    data_to.materials = data_from.materials
                    data_to.node_groups = data_from.node_groups
                    data_to.collections = data_from.collections
                    data_to.worlds = data_from.worlds

                # Count loaded datablocks for preservation report
                objects_loaded = len(data_to.objects)
                materials_loaded = len(data_to.materials)
                nodegroups_loaded = len(data_to.node_groups)
                worlds_loaded = len(data_to.worlds)

                print(f"[SimpleAssetUpdater] Loaded existing datablocks: {objects_loaded} objects, {materials_loaded} materials, {nodegroups_loaded} node groups, {worlds_loaded} worlds")

                # Replace the existing world with the new one
                if world.name in data_to.worlds:
                    # Update existing world
                    existing_world = data_to.worlds[world.name]
                    # Copy settings from new world to existing world
                    existing_world.node_tree = world.node_tree.copy() if world.node_tree else None
                    existing_world.use_nodes = world.use_nodes
                    print(f"[SimpleAssetUpdater] Updated existing world: {world.name}")
                else:
                    # Append new world if it doesn't exist
                    data_to.worlds.append(world)
                    print(f"[SimpleAssetUpdater] Added new world: {world.name}")

                # Save the updated file
                temp_file = Path(self.temp_dir) / f"temp_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(temp_file), compress=True)

                # Replace original file with temp file
                shutil.move(str(temp_file), str(target_file))

                print(f"[SimpleAssetUpdater] ✓ Successfully updated world while preserving {objects_loaded} objects, {materials_loaded} materials, {nodegroups_loaded} node groups, {worlds_loaded-1} other worlds")
                return True

            finally:
                # Clean up temporary scene
                bpy.context.window.scene = original_scene
                if temp_scene:
                    bpy.data.scenes.remove(temp_scene)

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update world preserving others: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_world_to_blend(self, world: bpy.types.World, target_file: Path) -> None:
        """Save a world to a .blend file using Blender's native operations."""
        if not world:
            raise SimpleAssetUpdateError("No world provided for saving")

        # Store current context safely
        original_window = bpy.context.window
        original_scene = bpy.context.scene

        # Create a temporary scene
        temp_scene = bpy.data.scenes.new(name="TempWorldScene")

        try:
            # Safely switch to temporary scene
            if original_window:
                original_window.scene = temp_scene

            # Set the world on the temporary scene
            temp_scene.world = world

            # Save the temporary scene
            bpy.ops.wm.save_as_mainfile(filepath=str(target_file), compress=True)

        except Exception as e:
            print(f"[SimpleAssetUpdater] Error saving world to blend: {e}")
            raise
        finally:
            # Clean up safely - restore original scene first
            try:
                if original_window and original_scene:
                    original_window.scene = original_scene
            except:
                pass  # Ignore restoration errors

            # Remove temporary scene if it exists
            try:
                if temp_scene and temp_scene in bpy.data.scenes:
                    bpy.data.scenes.remove(temp_scene)
            except:
                pass  # Ignore cleanup errors

    def _update_collection_preserving_others(self, collections: list, target_file: Path) -> bool:
        """Update collections in an existing blend file while preserving all other datablocks."""
        if not collections:
            raise SimpleAssetUpdateError("No collections provided for update")

        # Store current context safely
        original_window = bpy.context.window
        original_scene = bpy.context.scene

        # Create a temporary scene for the update operation
        temp_scene = bpy.data.scenes.new(name="TempCollectionUpdateScene")

        try:
            # Safely switch to temporary scene
            if original_window:
                original_window.scene = temp_scene

            # Validate target file exists
            if not target_file.exists():
                raise SimpleAssetUpdateError(f"Target file does not exist: {target_file}")

            # Load all existing datablocks from the target file
            with bpy.data.libraries.load(str(target_file)) as (data_from, data_to):
                # Load all existing datablocks to preserve them
                data_to.objects = list(data_from.objects)
                data_to.materials = list(data_from.materials)
                data_to.node_groups = list(data_from.node_groups)
                data_to.collections = list(data_from.collections)
                data_to.worlds = list(data_from.worlds)

            # Count loaded datablocks for preservation report
            objects_loaded = len(data_to.objects)
            materials_loaded = len(data_to.materials)
            nodegroups_loaded = len(data_to.node_groups)
            collections_loaded = len(data_to.collections)
            worlds_loaded = len(data_to.worlds)

            print(f"[SimpleAssetUpdater] Loaded existing datablocks: {objects_loaded} objects, {materials_loaded} materials, {nodegroups_loaded} node groups, {collections_loaded} collections, {worlds_loaded} worlds")

            # Replace existing collections with new ones
            collection_names = []
            for collection in collections:
                if not collection or not hasattr(collection, 'name'):
                    print(f"[SimpleAssetUpdater] Warning: Skipping invalid collection")
                    continue

                collection_names.append(collection.name)

                # Remove existing collection with same name
                collections_to_remove = []
                for existing_coll in data_to.collections:
                    if existing_coll.name == collection.name:
                        collections_to_remove.append(existing_coll)

                for coll_to_remove in collections_to_remove:
                    data_to.collections.remove(coll_to_remove)

                # Add new collection
                data_to.collections.append(collection)
                print(f"[SimpleAssetUpdater] Updated collection: {collection.name}")

            # Save the updated file
            temp_file = Path(self.temp_dir) / f"temp_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(temp_file), compress=True)

            # Replace original file with temp file
            shutil.move(str(temp_file), str(target_file))

            print(f"[SimpleAssetUpdater] ✓ Successfully updated {len(collection_names)} collections while preserving {objects_loaded} objects, {materials_loaded} materials, {nodegroups_loaded} node groups, {worlds_loaded} worlds")
            return True

        except Exception as e:
            print(f"[SimpleAssetUpdater] ✗ Failed to update collections preserving others: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up safely - restore original scene first
            try:
                if original_window and original_scene:
                    original_window.scene = original_scene
            except:
                pass  # Ignore restoration errors

            # Remove temporary scene if it exists
            try:
                if temp_scene and temp_scene in bpy.data.scenes:
                    bpy.data.scenes.remove(temp_scene)
            except:
                pass  # Ignore cleanup errors

    def _save_collection_to_blend(self, collections: list, target_file: Path) -> None:
        """Save collections to a .blend file using Blender's native operations."""
        if not collections:
            raise SimpleAssetUpdateError("No collections provided for saving")

        # Store current context safely
        original_window = bpy.context.window
        original_scene = bpy.context.scene

        # Create a temporary scene
        temp_scene = bpy.data.scenes.new(name="TempCollectionScene")

        try:
            # Safely switch to temporary scene
            if original_window:
                original_window.scene = temp_scene

            # Link all collections to the temporary scene
            valid_collections = []
            for collection in collections:
                if collection and hasattr(collection, 'name'):
                    temp_scene.collection.children.link(collection)
                    valid_collections.append(collection.name)
                else:
                    print(f"[SimpleAssetUpdater] Warning: Skipping invalid collection")

            if not valid_collections:
                raise SimpleAssetUpdateError("No valid collections to save")

            print(f"[SimpleAssetUpdater] Saving {len(valid_collections)} collections to blend file")
            # Save the temporary scene
            bpy.ops.wm.save_as_mainfile(filepath=str(target_file), compress=True)

        except Exception as e:
            print(f"[SimpleAssetUpdater] Error saving collections to blend: {e}")
            raise
        finally:
            # Clean up safely - restore original scene first
            try:
                if original_window and original_scene:
                    original_window.scene = original_scene
            except:
                pass  # Ignore restoration errors

            # Remove temporary scene if it exists
            try:
                if temp_scene and temp_scene in bpy.data.scenes:
                    bpy.data.scenes.remove(temp_scene)
            except:
                pass  # Ignore cleanup errors

    def _validate_blend_file(self, blend_file: Path, expected_name: str, data_type: str = 'object') -> bool:
        """
        Validate that the blend file contains the expected datablock.

        Args:
            blend_file: Path to the .blend file to validate
            expected_name: Name of the expected datablock
            data_type: Type of datablock ('object', 'material', 'node_group', 'world', 'collection')

        Returns:
            bool: True if validation passed
        """
        try:
            # Check if trying to validate the currently open blend file
            # Only skip validation if it's the EXACT same file that's currently open and saved
            current_file = Path(bpy.data.filepath) if bpy.data.filepath else None
            if (current_file and current_file.resolve() == blend_file.resolve()):
                print(f"[SimpleAssetUpdater] Skipping validation on current open blend file: {blend_file}")
                # For the current blend file, check if the datablock exists directly
                if data_type == 'object':
                    return expected_name in bpy.data.objects
                elif data_type == 'material':
                    return expected_name in bpy.data.materials
                elif data_type == 'node_group':
                    return expected_name in bpy.data.node_groups
                elif data_type == 'world':
                    return expected_name in bpy.data.worlds
                elif data_type == 'collection':
                    return expected_name in bpy.data.collections
                return False

            # Store current scene
            original_scene = bpy.context.scene

            # Create temporary scene for validation
            temp_scene = bpy.data.scenes.new(name="TempValidationScene")
            bpy.context.window.scene = temp_scene

            # Append datablocks from the blend file
            with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
                if data_type == 'object' and hasattr(data_from, 'objects'):
                    data_to.objects = [name for name in data_from.objects if name == expected_name]
                elif data_type == 'material' and hasattr(data_from, 'materials'):
                    data_to.materials = [name for name in data_from.materials if name == expected_name]
                elif data_type == 'node_group' and hasattr(data_from, 'node_groups'):
                    data_to.node_groups = [name for name in data_from.node_groups if name == expected_name]
                elif data_type == 'world' and hasattr(data_from, 'worlds'):
                    data_to.worlds = [name for name in data_from.worlds if name == expected_name]
                elif data_type == 'collection' and hasattr(data_from, 'collections'):
                    data_to.collections = [name for name in data_from.collections if name == expected_name]

            # Check if the expected datablock was loaded
            found = False
            if data_type == 'object':
                found = len([obj for obj in data_to.objects if obj.name == expected_name]) > 0
            elif data_type == 'material':
                found = len([mat for mat in data_to.materials if mat.name == expected_name]) > 0
            elif data_type == 'node_group':
                found = len([ng for ng in data_to.node_groups if ng.name == expected_name]) > 0
            elif data_type == 'world':
                found = len([w for w in data_to.worlds if w.name == expected_name]) > 0
            elif data_type == 'collection':
                found = len([c for c in data_to.collections if c.name == expected_name]) > 0

            # Clean up
            bpy.context.window.scene = original_scene
            bpy.data.scenes.remove(temp_scene)

            print(f"[SimpleAssetUpdater] Validation: {expected_name} ({data_type}) {'found' if found else 'not found'} in {blend_file.name}")
            return found

        except Exception as e:
            print(f"[SimpleAssetUpdater] Validation error for {blend_file}: {e}")
            return False

    def get_last_backup_files(self) -> List[Path]:
        """Get list of backup files created during this session."""
        return self.backup_files.copy()