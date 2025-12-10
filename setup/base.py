from ..parse.osm.relation.building import Building

from ..manager import BaseManager, Linestring, Polygon, PolygonAcceptBroken, WayManager
from ..building.gn_2d import GnBldg2dManager
from ..renderer import Renderer2d
# BaseNodeRenderer not needed for route import (commented out usage on line 133)
# from ..renderer.node_renderer import BaseNodeRenderer
from ..renderer.curve_renderer import CurveRenderer

from ..building.manager import BuildingManager, BuildingParts, BuildingRelations
from ..building.layer import BuildingLayer
from ..building.renderer import BuildingRenderer

from ..util.logging import Logger
from ..util.random import RandomWeighted


class EnsureFallbackHeight:
    """Injects fallback building heights when OSM data lacks height/levels."""

    def __init__(self, fallback):
        self._static_height = None
        self._level_height = None
        self._random_levels = None
        self._configure(fallback)

    def _configure(self, fallback):
        distribution = None
        level_height = None

        if isinstance(fallback, dict):
            level_height = fallback.get("level_height")
            distribution = fallback.get("levels")
        elif isinstance(fallback, (list, tuple)) and len(fallback) == 2:
            level_height, distribution = fallback
        else:
            try:
                self._static_height = float(fallback)
            except (TypeError, ValueError):
                self._static_height = None
            return

        try:
            level_height = float(level_height)
        except (TypeError, ValueError):
            level_height = 0.0

        cleaned = []
        if distribution:
            for entry in distribution:
                try:
                    levels, weight = entry
                    levels = int(levels)
                    weight = int(weight)
                except (TypeError, ValueError):
                    continue
                if levels < 1 or weight <= 0:
                    continue
                cleaned.append((levels, weight))
        if cleaned and level_height > 0.0:
            self._level_height = level_height
            self._random_levels = RandomWeighted(tuple(cleaned))
        elif level_height > 0.0:
            self._static_height = level_height

    def _compute_height(self):
        if self._random_levels:
            levels = max(1, int(self._random_levels.value))
            return self._level_height * levels
        return self._static_height

    def do(self, manager):
        for building in manager.buildings:
            self.apply(building.outline)
            for part in building.parts:
                self.apply(part)

    def apply(self, element):
        tags = element.tags
        if not tags:
            return
        if any(key in tags for key in ("height", "building:height", "building:levels")):
            return
        height = self._compute_height()
        if not height or height <= 0.0:
            return
        text = f"{height:.2f}"
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        tags["height"] = text


def tunnel(tags, e):
    if tags.get("tunnel") == "yes":
        e.valid = False
        return True
    return False


def setup(app, osm):
    # comment the next line if logging isn't needed
    Logger(app, osm)

    # create managers
    wayManager = WayManager(osm, CurveRenderer(app))
    linestring = Linestring(osm)
    polygon = Polygon(osm)
    polygonAcceptBroken = PolygonAcceptBroken(osm)

    # conditions for point objects in OSM
    #osm.addNodeCondition(
    #    lambda tags, e: tags.get("natural") == "tree",
    #    "trees",
    #    None,
    #    BaseNodeRenderer(app, path, filename, collection)
    #)

    if app.buildings:
        if app.mode is app.twoD:
            osm.addCondition(
                lambda tags, e: "building" in tags,
                "buildings",
                GnBldg2dManager(app)
            )
        else: # 3D
            buildingParts = BuildingParts()
            buildingRelations = BuildingRelations()
            buildings = BuildingManager(osm, app, buildingParts, BuildingLayer)

            # Important: <buildingRelation> beform <building>,
            # since there may be a tag building=* in an OSM relation of the type 'building'
            osm.addCondition(
                lambda tags, e: isinstance(e, Building),
                None,
                buildingRelations
            )
            osm.addCondition(
                lambda tags, e: "building" in tags,
                "buildings",
                buildings
            )
            osm.addCondition(
                lambda tags, e: "building:part" in tags,
                None,
                buildingParts
            )
            buildings.setRenderer(
                BuildingRenderer(app)
            )
            fallback_height = getattr(app, "route_fallback_height", None)
            if fallback_height:
                buildings.addAction(EnsureFallbackHeight(fallback_height))

    if app.highways or app.railways:
        osm.addCondition(tunnel)

    if app.highways:
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("motorway", "motorway_link"),
            "roads_motorway",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("trunk", "trunk_link"),
            "roads_trunk",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("primary", "primary_link"),
            "roads_primary",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("secondary", "secondary_link"),
            "roads_secondary",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("tertiary", "tertiary_link"),
            "roads_tertiary",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "unclassified",
            "roads_unclassified",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("residential", "living_street"),
            "roads_residential",
            wayManager
        )
        # footway to optimize the walk through conditions
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("footway", "path"),
            "paths_footway",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "service",
            "roads_service",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "pedestrian",
            "roads_pedestrian",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "track",
            "roads_track",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "steps",
            "paths_steps",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "cycleway",
            "paths_cycleway",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") == "bridleway",
            "paths_bridleway",
            wayManager
        )
        osm.addCondition(
            lambda tags, e: tags.get("highway") in ("road", "escape", "raceway"),
            "roads_other",
            wayManager
        )
    if app.railways:
        osm.addCondition(
            lambda tags, e: "railway" in tags,
            "railways",
            wayManager
        )
    if app.water:
        osm.addCondition(
            lambda tags, e: tags.get("natural") == "water" or tags.get("waterway") == "riverbank" or tags.get("landuse") == "reservoir",
            "water",
            polygonAcceptBroken
        )
        osm.addCondition(
            lambda tags, e: tags.get("natural") == "coastline",
            "coastlines",
            linestring
        )
        # Enhanced island processing for Toronto Islands mesh import
        # Process islands as land masses with appropriate natural surface types
        osm.addCondition(
            lambda tags, e: (
                (tags.get("place") == "island" and
                 tags.get("natural") in (None, "land", "ground", "grass", "forest", "wood", "scrub", "wetland", "sand", "rock", "stone")) or
                (tags.get("name") and any(island_name in tags.get("name", "").lower()
                    for island_name in ["toronto island", "centre island", "ward island", "algonquin island", "muggs island", "south island", "toronto islands"]))
            ),
            "islands",
            polygonAcceptBroken
        )
    if app.forests:
        osm.addCondition(
            lambda tags, e: tags.get("natural") == "wood" or tags.get("landuse") == "forest",
            "forest",
            polygon
        )
    if app.vegetation:
        osm.addCondition(
            lambda tags, e: ("landuse" in tags and tags["landuse"] in ("grass", "meadow", "farmland")) or ("natural" in tags and tags["natural"] in ("scrub", "grassland", "heath")),
            "vegetation",
            polygon
        )

    numConditions = len(osm.conditions)
    if not app.mode is app.twoD and app.buildings:
        # 3D buildings aren't processed by BaseManager
        numConditions -= 1
    if numConditions:
        m = BaseManager(osm)
        m.setRenderer(Renderer2d(app))
        app.addManager(m)