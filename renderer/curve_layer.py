import os
import bpy
from .layer import MeshLayer
from ..util.blender import appendObjectsFromFile, createDiffuseMaterial, createCollection, addShrinkwrapModifier

_isBlender291 = bpy.app.version[1] >= 91


class CurveLayer(MeshLayer):
    
    # Blender layer index to place a way profile
    profileLayerIndex = 1
    
    # Blender file with way profiles
    assetFile = "way_profiles.blend"
    
    collectionName = "way_profiles"
    
    def __init__(self, layerId, app):
        super().__init__(layerId, app)
        self.assetPath = os.path.join(app.assetPath, self.assetFile)

    def getDefaultZ(self, app):
        return app.wayZ

    def getDefaultSwOffset(self, app):
        return app.swWayOffset

    def finalizeBlenderObject(self, obj):
        """
        Slice Blender MESH object, add modifiers
        """
        # set a bevel object for the curve
        curve = obj.data
        # the name of the bevel object
        bevelName = "profile_%s" % self.id
        bevelObj = bpy.data.objects.get(bevelName)
        if not (bevelObj and bevelObj.type == 'CURVE'):
            bevelObj = appendObjectsFromFile(self.assetPath, None, bevelName)[0]
            if bevelObj:
                collection = bpy.data.collections.get(self.collectionName)
                if not collection:
                    collection = createCollection(
                        self.collectionName,
                        hide_viewport=True,
                        hide_select=True,
                        hide_render=True
                    )
                collection.objects.link(bevelObj)
                bevelObj.hide_viewport = True
                bevelObj.hide_select = True
                bevelObj.hide_render = True
        if bevelObj and bevelObj.type == 'CURVE':
            curve.bevel_object = bevelObj
            if _isBlender291:
                curve.bevel_mode = 'OBJECT'
        # set a material
        # the material name is simply <id> of the layer
        name = self.id
        material = bpy.data.materials.get(name)
        curve.materials.append(
            material or createDiffuseMaterial(name, self.app.colors.get(name, self.app.defaultColor))
        )
        
        if self.modifiers:
            addShrinkwrapModifier(obj, self.app.terrain.terrain, self.swOffset)