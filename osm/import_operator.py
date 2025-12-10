"""CashCab OSM Import Operator - Imports OSM buildings and roads as 3D geometry"""
import os
import bpy
from ..app import blender as blenderApp
from ..parse.osm import Osm

class BLOSM_OT_ImportData(bpy.types.Operator):
    """CashCab: Import OpenStreetMap or terrain data"""
    bl_idname = "blosm.import_data"  # important since its how bpy.ops.blosm.import_data is constructed
    bl_label = "CashCab: Import OSM Data"
    bl_description = "Import data of the selected type (OpenStreetMap, Google 3D Tiles, terrain, etc) for CashCab"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        a = blenderApp.app
        dataType = context.scene.blosm.dataType
        
        self.setup(context, a.addonName)
        
        a.projection = None
        a.setAttributes(context)
        
        if dataType == "osm":
            return self.importOsm(context)
        elif dataType == "terrain":
            return self.importTerrain(context)
        elif dataType == "overlay":
            return self.importOverlay(context)
        elif dataType == "3d-tiles":
            return self.import3dTiles(context)
        elif dataType == "geojson":
            return self.importGeoJson(context)
        
        return {'FINISHED'}
    def setup(self, context, addonName):
        # check if the file <setup_execute.py> is available
        setup_function = self.loadSetupScript(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "setup_execute.py"),
            reportError=False
        )
        if setup_function:
            setup_function(context, addonName)
    
    def importOsm(self, context):
        a = blenderApp.app
        addon = context.scene.blosm
        
        try:
            a.initOsm(self, context)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        createFlatTerrain = a.mode is a.realistic and a.forests
        forceExtentCalculation = createFlatTerrain and a.osmSource == "file"
        
        setupScript = addon.setupScript
        if setupScript:
            setup_function = self.loadSetupScript(setupScript, reportError=True)
            if not setup_function:
                return {'CANCELLED'}
        else:
            if a.mode is a.realistic:
                if a.enableExperimentalFeatures:
                    from ..setup.realistic_dev import setup as setup_function
                else:
                    from ..setup.premium_default import setup as setup_function
            else:
                from ..setup.base import setup as setup_function
        
        scene = context.scene
        
        self.setObjectMode(context)
        bpy.ops.object.select_all(action='DESELECT')
        
        osm = Osm(a)
        print(f"[DEBUG] importOsm: Using setup_function: {setup_function.__module__}.{setup_function.__name__}")
        setup_function(a, osm)
        # Print the conditions added to the OSM object
        print(f"[DEBUG] importOsm: Osm conditions: {[(c[0].__name__, getattr(c[1], 'id', 'None'), getattr(c[2], 'id', 'None'), getattr(c[3], 'id', 'None')) for c in osm.conditions]}")
        print(f"[DEBUG] importOsm: Osm nodeConditions: {[(c[0].__name__, getattr(c[1], 'id', 'None'), getattr(c[2], 'id', 'None'), getattr(c[3], 'id', 'None')) for c in osm.nodeConditions]}")
        a.createLayers(osm)
        
        setLatLon = False
        if "lat" in scene and "lon" in scene and a.relativeToInitialImport:
            osm.setProjection(scene["lat"], scene["lon"])
        elif a.osmSource == "server":
            osm.setProjection( (a.minLat+a.maxLat)/2., (a.minLon+a.maxLon)/2. )
            osm.parse(a.osmFilepath, forceExtentCalculation=forceExtentCalculation)
            setLatLon = True
        elif a.osmSource == "file":
            # Prefer scene property `osmFilepath`; fall back to legacy `osmFilePath` or app.osmFilepath
            file_path = getattr(addon, 'osmFilepath', '') or getattr(addon, 'osmFilePath', '') or getattr(a, 'osmFilepath', '')
            if not file_path:
                self.report({'ERROR'}, "No OSM file path provided for file import")
                return {'CANCELLED'}
            osm.parse(file_path, forceExtentCalculation=forceExtentCalculation)
            setLatLon = True
        else:
            # This is the case if <a.osmSource == "file"> and if the first condition is not true
            # This branch should not lead to osm.parse() without a valid file path
            setLatLon = True

        if a.loadMissingMembers and a.incompleteRelations:
            try:
                a.loadMissingWays(osm)
            except Exception as e:
                self.report({'ERROR'}, str(e))
                a.loadMissingMembers = False
            a.processIncompleteRelations(osm)
            if not osm.projection:
                # <osm.projection> wasn't set so far if there were only incomplete relations that
                # satisfy <osm.conditions>.
                # See also the comments in <parse.osm.__init__.py>
                # at the end of the method <osm.parse(..)>
                osm.setProjection( (osm.minLat+osm.maxLat)/2., (osm.minLon+osm.maxLon)/2. )
        
        if forceExtentCalculation:
            a.minLat = osm.minLat
            a.maxLat = osm.maxLat
            a.minLon = osm.minLon
            a.maxLon = osm.maxLon
        
        # Check if have a terrain Blender object set
        # At this point <a.projection> is set, so we can set the terrain
        a.setTerrain(
            context,
            createFlatTerrain = createFlatTerrain,
            createBvhTree = True
        )
        
        a.initLayers()
        
        a.process()
        a.render()
        
        # Set <lon> and <lat> attributes for <scene> if necessary.
        # <osm.projection> is set in <osm.setProjection(..)> along with <osm.lat> and <osm.lon>
        # So we test if <osm.projection> is set, that also means that <osm.lat> and <osm.lon> are also set.
        if setLatLon and osm.projection:
            # <osm.lat> and <osm.lon> have been set in osm.parse(..)
            self.setCenterLatLon(context, osm.lat, osm.lon)
        
        a.clean()
        
        return {'FINISHED'}
    
    def getCenterLatLon(self, context):
        a = blenderApp.app
        scene = context.scene
        if "lat" in scene and "lon" in scene and a.relativeToInitialImport:
            lat = scene["lat"]
            lon = scene["lon"]
            setLatLon = False
        else:
            lat = (a.minLat+a.maxLat)/2.
            lon = (a.minLon+a.maxLon)/2.
            setLatLon = True
        return lat, lon, setLatLon
    
    def setCenterLatLon(self, context, lat, lon):
        context.scene["lat"] = lat
        context.scene["lon"] = lon
    
    def loadSetupScript(self, setupScript, reportError):
        setupScript = os.path.realpath(bpy.path.abspath(setupScript))
        if not os.path.isfile(setupScript):
            if reportError:
                self.report({'ERROR'},
                    "The script file doesn't exist"
                )
            return None
        import imp
        # remove extension from the path
        setupScript = os.path.splitext(setupScript)[0]
        moduleName = os.path.basename(setupScript)
        try:
            _file, _pathname, _description = imp.find_module(moduleName, [os.path.dirname(setupScript)])
            module = imp.load_module(moduleName, _file, _pathname, _description)
            _file.close()
            return module.setup
        except Exception:
            self.report({'ERROR'},
                "Unable to execute the setup script! See the error message in the Blender console!"
            )
            return None
    
    def importTerrain(self, context):
        a = blenderApp.app
        try:
            a.initTerrain(context)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        lat, lon, setLatLon = self.getCenterLatLon(context)
        a.setProjection(lat, lon)
        
        a.importTerrain(context)
        
        # set the custom parameters <lat> and <lon> to the active scene
        if setLatLon:
            self.setCenterLatLon(context, lat, lon)
        return {'FINISHED'}
    
    def importOverlay(self, context):
        a = blenderApp.app
        blosm = context.scene.blosm
        
        # find the Blender area holding 3D View
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                a.area = area
                break
        else:
            a.area = None
            
        lat, lon, setLatLon = self.getCenterLatLon(context)
        a.setProjection(lat, lon)
        
        try:
            a.initOverlay(context)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        terrainObject = context.scene.objects.get(blosm.terrainObject)
        
        minLon, minLat, maxLon, maxLat = a.getExtentFromObject(terrainObject, context)\
            if terrainObject else\
            (a.minLon, a.minLat, a.maxLon, a.maxLat)
        
        a.overlay.prepareImport(minLon, minLat, maxLon, maxLat)
        
        if blosm.commandLineMode:
            hasTiles = True
            while hasTiles:
                hasTiles = blenderApp.app.overlay.importNextTile()
            if blenderApp.app.overlay.finalizeImport():
                self.report({'INFO'}, "Overlay import is finished!")
            else:
                self.report({'ERROR'}, "Probably something is wrong with the tile server!")
        else:
            bpy.ops.blosm.control_overlay()
        
        # set the custom parameters <lat> and <lon> to the active scene
        if setLatLon:
            self.setCenterLatLon(context, lat, lon)
        
        return {'FINISHED'}
    
    def import3dTiles(self, context):
        from threed_tiles.manager import BaseManager
        from threed_tiles.blender import BlenderRenderer
        
        addon = context.scene.blosm
        google3dTiles = addon.threedTilesSource == "google"
        
        renderer = BlenderRenderer(
            "Google 3D Tiles" if google3dTiles else "3D Tiles",
            addon.join3dTilesObjects,
            addon.instanceName
        )
        manager = BaseManager(
            "https://tile.googleapis.com/v1/3dtiles/root.json" if google3dTiles else addon.threedTilesUrl,
            renderer
        )
        
        manager.cacheJsonFiles = addon.cacheJsonFiles
        manager.cache3dFiles = addon.cache3dFiles
        
        a = blenderApp.app
        try:
            a.init3dTiles(context, manager, "google")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        manager.centerLat, manager.centerLon, setLatLonHeight = self.getCenterLatLon(context)
        
        if not setLatLonHeight and "height_offset" in context.scene:
            renderer.heightOffset = context.scene["height_offset"]
        else:
            renderer.calculateHeightOffset = True
        
        result = manager.render(a.minLon, a.minLat, a.maxLon, a.maxLat)
        
        if len(result) == 1:
            # a critical error happend
            self.report({'ERROR'}, result[0])
            return {'CANCELLED'}
        
        numImportedTiles, errors = result
        if numImportedTiles:
            if setLatLonHeight:
                context.scene["lat"] = manager.centerLat
                context.scene["lon"] = manager.centerLon
            
            if renderer.calculateHeightOffset:
                context.scene["height_offset"] = renderer.heightOffset
                
            self.report(
                {'INFO'},
                "Imported %s 3D Tiles. %s errors occured during the import. " % (numImportedTiles, len(errors)) +\
                "See the System Console."\
                    if errors else\
                    "Successfully Imported %s 3D Tiles." % numImportedTiles
            )
        else:
            self.report(
                {'ERROR'},
                "No 3D tiles were imported. %s errors occured during the import. " % len(errors) +\
                "See the System Console."
            )
        
        if errors:
            for error in errors:
                print(error)
        
        return {'FINISHED'} if numImportedTiles else {'CANCELLED'}
    
    def setObjectMode(self, context):
        scene = context.scene
        # setting active object if there is no active object
        if context.mode != "OBJECT":
            # if there is no object in the scene, only "OBJECT" mode is available
            if not context.view_layer.objects.active:
                context.view_layer.objects.active = scene.objects[0]
            bpy.ops.object.mode_set(mode="OBJECT")
        # Also deselect the active object since the operator
        # <bpy.ops.object.select_all(action='DESELECT')> does not affect hidden objects and
        # the hidden active object
        if context.view_layer.objects.active:
            context.view_layer.objects.active.select_set(False)
