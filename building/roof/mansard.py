from .hipped import RoofHipped
from .flat import RoofFlat


class RoofMansard(RoofHipped):
    """
    The mansard roof shape is implemented only for a quadrangle building outline.
    For the other building outlines a flat roof is created.
    """
    
    insetSize = 2.
    
    def make(self, osm):
        if self.makeFlat:
            return RoofFlat.make(self, osm)
        else:
            verts = self.verts
            wallIndices = self.wallIndices
            roofIndices = self.roofIndices
            polygon = self.polygon
            _indices = polygon.indices
            
            if not self.noWalls:
                indexOffset = len(verts)
                polygon.extrude(self.roofVerticalPosition, wallIndices)
                # new values for the polygon indices
                polygon.indices = tuple(indexOffset + i for i in range(polygon.n))
            
            indexOffset = len(verts)
            self.roofHeight /= 2.
            polygon.inset(self.insetSize, roofIndices, self.roofHeight)
            # new values for the polygon indices
            polygon.indices = tuple(indexOffset + i for i in range(polygon.n))
            self.wallIndices = roofIndices
            self.roofVerticalPosition += self.roofHeight
            self.noWalls = True
            super().make(osm)
            self.wallIndices = wallIndices
            
            # restore the original indices
            polygon.indices = _indices
        
        return True