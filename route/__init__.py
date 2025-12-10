"""
Route fetching and processing functionality for BLOSM
"""
from .fetch_operator import BLOSM_OT_FetchRouteMap, BLOSM_OT_ExtendCityArea
from .utils import RouteServiceError, prepare_route, OverpassFetcher

# Import route functionality
try:
    from . import (
        assets as route_assets,
        anim as route_anim, 
        nodes as route_nodes,
        buildings as route_buildings,
        preview as route_preview,
        pipeline_finalizer as route_pipeline_finalizer,
        resolve as route_resolve
    )
except ImportError:
    # Fallback for partial imports
    pass

__all__ = ['BLOSM_OT_FetchRouteMap', 'BLOSM_OT_ExtendCityArea', 'RouteServiceError', 'prepare_route', 'OverpassFetcher']
