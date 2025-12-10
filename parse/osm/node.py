class Node:
    """
    A class to represent an OSM node
    
    Some attributes:
        l (app.Layer): layer used to place the related geometry to a specific Blender object
        tags (dict): OSM tags
        m: A manager used during the rendering; if None, <manager.BaseManager> applies defaults
            during the rendering
        rr: A special renderer for the OSM node
        b (dict): Here we store building indices (i.e. the indices of instances of
            the wrapper class <building.manager.Building> in Python list <buildings> of an instance
            of <building.manager.BuildingManager>)
        w (dict): Here we store ids of OSM that represent real ways. It is used only by the
            RealWayManager responsible for real ways
        rr: A renderer for the OSM node
    """
    __slots__ = ("l", "tags", "lat", "lon", "coords", "b", "w", "rr", "valid", "m")
    
    def __init__(self, lat, lon, tags):
        self.tags = tags
        self.lat = lat
        self.lon = lon
        self.b = dict()
        self.w = dict()
        # projected coordinates
        self.coords = None
        self.rr = None
        self.valid = True
    
    def getData(self, osm):
        """
        Get projected coordinates
        """
        if not self.coords:
            # preserve coordinates in the local system of reference for a future use
            self.coords = osm.projection.fromGeographic(self.lat, self.lon)
        return self.coords