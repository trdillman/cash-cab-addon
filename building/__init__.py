from .. import parse
from mathutils import Vector


class Building:
    """
    A wrapper for a OSM building
    """
    
    __slots__ = ("outline", "parts")
    
    def __init__(self, element, buildingIndex, osm):
        self.outline = element
        self.parts = []
        self.markUsedNodes(buildingIndex, osm)
    
    def addPart(self, part):
        self.parts.append(part)

    def markUsedNodes(self, buildingIndex, osm):
        """
        For each OSM node of <self.element> (OSM way or OSM relation) add the related
        <buildingIndex> (i.e. the index of <self> in Python list <buildings> of an instance
        of <BuildingManager>) to Python set <b> of the node 
        """
        for nodeId in self.outline.nodeIds(osm):
            osm.nodes[nodeId].b[buildingIndex] = 1