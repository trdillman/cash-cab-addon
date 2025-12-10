from datetime import datetime
from ..building.manager import BuildingManager


class Logger:
    
    def __init__(self, app, osm):
        self.parseStartTime = datetime.now()
        app.logger = self
        self.app = app
        self.osm = osm
        print("Parsing OSM file %s..." % app.osmFilepath)
    
    def processStart(self):
        print("Time for parsing OSM file: %s" % (datetime.now() - self.parseStartTime))
        self.processStartTime = datetime.now()
        print("Processing the parsed OSM data...")

    def processEnd(self):
        self.numBuildings()
        print("Time for processing of the parsed OSM data: %s" % (datetime.now() - self.processStartTime))
    
    def renderStart(self):
        self.renderStartTime = datetime.now()
        print("Creating meshes in Blender...")

    def renderEnd(self):
        t = datetime.now()
        print("Time for mesh creation in Blender: %s" % (t - self.renderStartTime))
        print("Total duration: %s" % (t - self.parseStartTime))
    
    def numBuildings(self):
        app = self.app
        if app.mode is app.twoD or not app.buildings:
            return
        for m in app.managers:
            if isinstance(m, BuildingManager):
                print("The number of buildings: %s" % len(m.buildings))