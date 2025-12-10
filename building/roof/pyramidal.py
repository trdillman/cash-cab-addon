from ...util import zAxis
from . import Roof


class RoofPyramidal(Roof):
    """
    A Blender object to deal with buildings or building part with a pyramidal roof
    """
    
    defaultHeight = 3.
    
    def make(self, osm):
        polygon = self.polygon
        verts = self.verts
        roofIndices = self.roofIndices
        indices = polygon.indices
        noWalls = self.noWalls
        
        if not noWalls:
            indexOffset = len(verts)
            # Extrude <polygon> in the direction of <z> axis to bring
            # the extruded part to the height <roofVerticalPosition>
            polygon.extrude(self.roofVerticalPosition, self.wallIndices)
        
        # index for the top vertex
        topIndex = len(verts)
        verts.append(
            polygon.center + (self.z2 - (self.roofVerticalPosition if noWalls else self.z1)) * zAxis
        )
        
        # indices for triangles that form the pyramidal roof
        if noWalls:
            roofIndices.extend(
                (indices[i-1], indices[i], topIndex) for i in range(polygon.n)
            )
        else:
            # the starting triangle
            roofIndices.append((indexOffset + polygon.n - 1, indexOffset, topIndex))
            roofIndices.extend(
                (i - 1, i, topIndex) for i in range(indexOffset + 1, indexOffset + polygon.n)
            )
            
        return True