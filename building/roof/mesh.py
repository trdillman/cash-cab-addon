import os
import os
import bpy
from mathutils import Vector
from . import Roof
from ...renderer import Renderer  # Fixed: use ...renderer (3 dots) to reach blosm_clean.renderer
from ...util.blender import loadMeshFromFile


class RoofMesh(Roof):
    """
    A class to deal with buildings or building part
    with roof meshes loaded from a .blend library file
    """
    
    defaultHeight = 5.
    
    def __init__(self, mesh):
        """
        Args:
            mesh (str): Name of the mesh in the .blend library file <self.assetPath>
        """
        super().__init__()
        self.mesh = mesh
    
    def make(self, osm):
        polygon = self.polygon
        
        if not self.noWalls:
            # Extrude <polygon> in the direction of <z> axis to bring
            # the extruded part to the height <roofVerticalPosition>
            polygon.extrude(self.roofVerticalPosition, self.wallIndices)
        
        c = polygon.center
        # location of the Blender mesh for the roof
        self.location = Vector((c[0], c[1], self.roofVerticalPosition))
        
        return True
    
    def render(self):
        r = self.r
        polygon = self.polygon
        app = r.app
        
        scale = (
            ( max(v.x for v in polygon.verts) - min(v.x for v in polygon.verts) )/2.,
            ( max(v.y for v in polygon.verts) - min(v.y for v in polygon.verts) )/2.,
            self.roofHeight
        )
        
        # create building walls
        super().render()
        
        # Now deal with the roof
        # Use the Blender mesh loaded before or load it from the .blend file
        # with the path defined by <app.assetPath> and <self.assetPath>
        # <self.assetPath> is set in the parent class <Roof>
        mesh = bpy.data.meshes.get(self.mesh)\
            if self.mesh in bpy.data.meshes else\
            loadMeshFromFile(os.path.join(app.assetPath, self.assetPath), self.mesh)
        if not mesh.materials:
            # create an empty slot for a Blender material
            mesh.materials.append(None)
        # create a Blender object to host <mesh>
        o = bpy.data.objects.new(self.mesh, mesh.copy())
        o.location = r.getVert(self.location)
        o.scale = scale
        # Link the roof object into the same collection(s) as the parent building object when possible.
        # This avoids headless scene/context mismatches where `bpy.context.scene` can differ from the
        # active ViewLayer scene, causing join/select issues later.
        target_collection = None
        try:
            parent_obj = getattr(r, "obj", None)
            users = list(getattr(parent_obj, "users_collection", []) or []) if parent_obj else []
            if users:
                target_collection = users[0]
        except Exception:
            target_collection = None
        if target_collection is None:
            target_collection = bpy.context.scene.collection
        try:
            if target_collection.objects.get(o.name) is None:
                target_collection.objects.link(o)
        except Exception:
            # Fallback: try linking to the scene collection
            try:
                if bpy.context.scene.collection.objects.get(o.name) is None:
                    bpy.context.scene.collection.objects.link(o)
            except Exception:
                pass
        # perform Blender parenting
        o.parent = r.obj
        # link Blender material to the Blender object <o> instead of <o.data>
        slot = o.material_slots[0]
        slot.link = 'OBJECT'
        self.setMaterial(o, slot)
        # add Blender object <o> for joining with Blender object <r.obj>
        Renderer.addForJoin(o, r.obj)
    
    def setMaterial(self, obj, slot):
        slot.material = self.r.getRoofMaterial(self.element)
