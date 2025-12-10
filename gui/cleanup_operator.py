"""
BLOSM Clean and Clear Operator
Removes objects and data created by the addon
"""

import bpy
from typing import Set, List

from .cleanup_patterns import (
    OBJECT_PATTERNS,
    COLLECTION_NAMES,
    ASSET_GROUPS,
    MATERIAL_PATTERNS,
    NODE_GROUP_PATTERNS,
    IMAGE_PATTERNS,
    TEXT_PATTERNS,
    WORLD_PATTERNS,
    LIBRARY_PATTERNS
)


class BLOSM_OT_CleanAndClear(bpy.types.Operator):
    """Clean and clear CashCab assets from scene"""

    bl_idname = "blosm.clean_and_clear"
    bl_label = "Clean & Clear"
    bl_description = "Remove CashCab assets from the scene"
    bl_options = {'REGISTER', 'UNDO'}

    action: bpy.props.EnumProperty(
        name="Action",
        description="What to clean",
        items=[
            ('SELECTED', 'Selected Object Only', 'Remove only the selected CashCab object'),
            ('ALL', 'All CashCab Assets', 'Remove all objects and data created by CashCab addon'),
        ],
        default='SELECTED'
    )

    @classmethod
    def poll(cls, context):
        # Enable if there's a selection or if there are any addon objects
        return True

    def invoke(self, context, event):
        # Show dialog with options
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "action", expand=True)

        layout.separator()

        if self.action == 'SELECTED':
            self._draw_selected_preview(context, layout)
        else:
            self._draw_all_preview(context, layout)

    def _draw_selected_preview(self, context, layout):
        """Draw preview for selected objects"""
        selected = context.selected_objects
        if selected:
            all_to_remove = self._get_related_objects_for_selection(selected)
            if all_to_remove:
                layout.label(text=f"Will remove {len(all_to_remove)} related object(s):", icon='INFO')
                self._show_object_list(layout, list(all_to_remove))
            else:
                layout.label(text="Warning: No CashCab objects selected", icon='ERROR')
        else:
            layout.label(text="No objects selected", icon='ERROR')

    def _draw_all_preview(self, context, layout):
        """Draw preview for all objects"""
        addon_objects = self._get_all_addon_objects()
        layout.label(text=f"Will remove {len(addon_objects)} objects", icon='INFO')
        layout.label(text="This includes:", icon='DOT')
        layout.label(text="  • Route, Start, End markers")
        layout.label(text="  • Car and Lead objects")
        layout.label(text="  • Imported buildings and roads")
        layout.label(text="  • All collections and materials")

    def _show_object_list(self, layout, obj_list: List[bpy.types.Object]):
        """Show a list of objects that will be deleted"""
        shown = 0
        for obj in obj_list[:10]:  # Show up to 10 objects
            layout.label(text=f"  • {obj.name}")
            shown += 1

        if len(obj_list) > 10:
            layout.label(text=f"  ... and {len(obj_list) - 10} more")

    def execute(self, context):
        if self.action == 'SELECTED':
            removed = self._clean_selected(context)
            self.report({'INFO'}, f"Removed {removed} CashCab object(s)")
        else:
            removed = self._clean_all(context)
            self.report({'INFO'}, f"Removed {removed} CashCab assets")

        return {'FINISHED'}

    def _is_addon_object(self, obj: bpy.types.Object) -> bool:
        """Check if object was created by addon"""
        if not obj:
            return False

        # Check object name patterns
        if any(pattern in obj.name for pattern in OBJECT_PATTERNS):
            return True

        # Check if in addon collections
        for coll in obj.users_collection:
            if coll.name in COLLECTION_NAMES:
                return True

        # Check for addon custom properties
        if 'address' in obj or 'geocode_lat' in obj or 'route_trace_lead_extra' in obj:
            return True

        # ENHANCED: Check for CashCab identification properties
        if obj.get("cashcab_managed") is True or obj.get("cashcab_asset_type"):
            return True

        # Check if collection is marked as CashCab asset collection
        for coll in obj.users_collection:
            if coll.get("cashcab_asset_collection") is True:
                return True

        return False

    def _get_all_addon_objects(self) -> List[bpy.types.Object]:
        """Get all objects created by addon"""
        return [obj for obj in bpy.data.objects if self._is_addon_object(obj)]

    def _get_related_objects_for_selection(self, selected_objects: List[bpy.types.Object]) -> Set[bpy.types.Object]:
        """Get all objects related to the selected objects"""
        all_to_remove = set()

        for obj in selected_objects:
            if self._is_addon_object(obj):
                related = self._get_related_objects(obj)
                all_to_remove.update(related)

        return all_to_remove

    def _get_related_objects(self, obj: bpy.types.Object) -> Set[bpy.types.Object]:
        """Get all objects related to the selected object's asset group"""
        related = {obj}

        # Determine which asset group this object belongs to
        obj_group = None
        for group_name, patterns in ASSET_GROUPS.items():
            if any(pattern in obj.name for pattern in patterns):
                obj_group = group_name
                break

        # ENHANCED: Check CashCab asset type property
        if not obj_group and obj.get("cashcab_asset_type"):
            asset_type = obj.get("cashcab_asset_type")
            if asset_type in ASSET_GROUPS:
                obj_group = asset_type

        if not obj_group:
            return related

        # Find all objects in the same group
        group_patterns = ASSET_GROUPS[obj_group]
        for check_obj in bpy.data.objects:
            if any(pattern in check_obj.name for pattern in group_patterns) and self._is_addon_object(check_obj):
                related.add(check_obj)

        # Special handling for route group
        if obj_group == 'route':
            for check_obj in bpy.data.objects:
                if 'address' in check_obj or 'geocode_lat' in check_obj or 'route_trace' in check_obj.name.lower():
                    related.add(check_obj)

        # Special handling for car group
        if obj_group == 'car':
            for check_obj in bpy.data.objects:
                if 'ASSET_CAR' in check_obj.name or 'Lead' in check_obj.name:
                    related.add(check_obj)

        # ENHANCED: Special handling for roads group - include all road-related objects
        if obj_group == 'roads':
            for check_obj in bpy.data.objects:
                if (check_obj.get("cashcab_asset_type") == "roads" or
                    'ASSET_ROADS' in check_obj.name or
                    'UnifiedRoadMesh' in check_obj.name):
                    related.add(check_obj)

        return related

    def _clean_selected(self, context) -> int:
        """Clean selected objects and their related asset groups"""
        removed = 0
        selected = list(context.selected_objects)
        all_to_remove = self._get_related_objects_for_selection(selected)

        for obj in all_to_remove:
            if self._safe_remove_object(obj):
                removed += 1

        # Cleanup orphan data
        self._cleanup_orphans()
        return removed

    def _clean_all(self, context) -> int:
        """Clean all addon objects and data"""
        removed = 0

        # Remove objects
        for obj in self._get_all_addon_objects():
            if self._safe_remove_object(obj):
                removed += 1

        # Remove collections
        self._remove_addon_collections()

        # Remove materials
        self._remove_addon_materials()

        # Remove node groups
        self._remove_addon_node_groups()

        # Remove other data types
        self._remove_addon_data()

        # Cleanup orphan data
        self._cleanup_orphans()
        return removed

    def _safe_remove_object(self, obj: bpy.types.Object) -> bool:
        """Safely remove an object with error handling"""
        try:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
            return True
        except Exception as e:
            print(f"[BLOSM] Failed to remove {obj.name}: {e}")
            return False

    def _remove_addon_collections(self) -> None:
        """Remove addon collections"""
        for coll_name in COLLECTION_NAMES:
            coll = bpy.data.collections.get(coll_name)
            if coll:
                try:
                    # Remove from all parent collections
                    for parent in bpy.data.collections:
                        if coll.name in parent.children:
                            parent.children.unlink(coll)
                    bpy.data.collections.remove(coll)
                    print(f"[BLOSM] Removed collection: {coll_name}")
                except Exception as e:
                    print(f"[BLOSM] Failed to remove collection {coll_name}: {e}")

        # ENHANCED: Also remove collections marked with CashCab properties
        for coll in list(bpy.data.collections):
            if coll.get("cashcab_asset_collection") is True:
                try:
                    # Remove from all parent collections
                    for parent in bpy.data.collections:
                        if coll.name in parent.children:
                            parent.children.unlink(coll)
                    bpy.data.collections.remove(coll)
                    print(f"[BLOSM] Removed CashCab collection: {coll.name}")
                except Exception as e:
                    print(f"[BLOSM] Failed to remove CashCab collection {coll.name}: {e}")

    def _remove_addon_materials(self) -> None:
        """Remove addon materials"""
        for mat in bpy.data.materials:
            if (mat.users == 0 or
                any(pattern in mat.name for pattern in MATERIAL_PATTERNS) or
                mat.get("cashcab_managed") is True):
                try:
                    bpy.data.materials.remove(mat)
                    print(f"[BLOSM] Removed material: {mat.name}")
                except:
                    pass  # Skip if in use

    def _remove_addon_node_groups(self) -> None:
        """Remove addon node groups"""
        for ng in bpy.data.node_groups:
            if (ng.users == 0 or
                any(pattern in ng.name for pattern in NODE_GROUP_PATTERNS)):
                try:
                    bpy.data.node_groups.remove(ng)
                    print(f"[BLOSM] Removed node group: {ng.name}")
                except:
                    pass  # Skip if in use

    def _remove_addon_data(self) -> None:
        """Remove other addon data types"""
        # Remove images
        for img in bpy.data.images:
            if img.users == 0 or any(pattern in img.name for pattern in IMAGE_PATTERNS):
                try:
                    bpy.data.images.remove(img)
                except:
                    pass

        # Remove texts
        for txt in bpy.data.texts:
            if any(pattern in txt.name for pattern in TEXT_PATTERNS):
                try:
                    bpy.data.texts.remove(txt)
                except:
                    pass

        # Remove worlds
        for world in bpy.data.worlds:
            if any(pattern in world.name for pattern in WORLD_PATTERNS):
                try:
                    bpy.data.worlds.remove(world)
                except:
                    pass

        # Remove libraries
        for lib in bpy.data.libraries:
            if any(pattern in lib.filepath for pattern in LIBRARY_PATTERNS):
                try:
                    bpy.data.libraries.remove(lib)
                except:
                    pass

    def _cleanup_orphans(self) -> None:
        """Remove orphan data blocks"""
        data_types = [
            bpy.data.meshes,
            bpy.data.curves,
            bpy.data.materials,
            bpy.data.node_groups,
            bpy.data.images,
            bpy.data.texts,
            bpy.data.worlds,
            bpy.data.libraries
        ]

        for data_collection in data_types:
            for item in list(data_collection):
                if item.users == 0:
                    try:
                        data_collection.remove(item)
                    except:
                        pass


__all__ = ['BLOSM_OT_CleanAndClear']