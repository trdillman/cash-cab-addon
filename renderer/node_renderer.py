import bpy
import os, math
from . import Renderer
from ..util.blender import loadCollectionFromFile, loadGroupFromFile
from ..util.osm import parseNumber, assignTags
from ..util.random import RandomNormal, RandomWeighted


class BaseNodeRenderer(Renderer):
    
    def __init__(self, app, path, filename, collectionName, randomizeScale=False, randomizeRotation=False):
        super().__init__(app)
        
        self._initialized = False
        self.app = app
        
        filepath = os.path.realpath( os.path.join(path, filename) )
        if not os.path.isfile(filepath):
            raise Exception("The file %s with assets doesn't exist." % filepath)
        self.filepath = filepath
        self.collectionName = collectionName
        # number of objects in the collection with the name <self.collectionName>
        self.numObjects = 0
        # index of the current object from the colleciton with the name <self.collectionName>
        self.objectIndex = 0
        
        self.randomScale = RandomNormal(1., sigmaRatio=0.2) if randomizeScale else None
        self.randomRotation = RandomWeighted( tuple((math.radians(angle), 1) for angle in range(0, 360)) ) if randomizeRotation else None
    
    def renderNode(self, node, osm):
        tags = node.tags
        layer = node.l
        
        coords = node.getData(osm)
        
        self.init()
        
        collection = bpy.data.collections[self.collectionName]
        
        # calculate z-coordinate of the object
        z = parseNumber(tags["min_height"], 0.) if "min_height" in tags else 0.
        if self.app.terrain:
            terrainOffset = self.app.terrain.project(coords)
            if terrainOffset is None:
                # the point is outside of the terrain
                return
            z += terrainOffset[2]
        
        obj = self.createBlenderObject(
            self.getName(node),
            (coords[0], coords[1], z),
            collection.objects[self.objectIndex].data,
            collection = layer.getCollection(self.collection),
            parent = None
        )
        
        if obj:
            if self.randomRotation:
                obj.rotation_euler[2] = self.randomRotation.value
            if self.randomScale:
                scale = self.randomScale.value
                obj.scale = (scale, scale, scale)
            # assign OSM tags to the blender object
            assignTags(obj, node.tags)
            
            self.objectIndex += 1
            if self.objectIndex == self.numObjects:
                self.objectIndex = 0
    
    def init(self):
        if self._initialized:
            return
        collection = loadCollectionFromFile(self.filepath, self.collectionName)
        self.numObjects = len(collection.objects)
        self._initialized = True
    
    @classmethod
    def createBlenderObject(self, name, location, objectData, collection=None, parent=None):
        obj = bpy.data.objects.new(name, objectData)
        if location:
            obj.location = location
        collection.objects.link(obj)
        if parent:
            # perform parenting
            obj.parent = parent
        return obj


class SingleTreeRenderer(BaseNodeRenderer):
      
    collectionName = "trees"
    
    def __init__(self, app):
        path, filename = os.path.split(app.vegetationFilepath)
        super().__init__(app, path, filename, self.collectionName, randomizeScale=True, randomizeRotation=True)