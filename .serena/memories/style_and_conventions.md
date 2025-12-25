# Style and Conventions - CashCab Addon

## Code Architecture Patterns

### Manager-Renderer-Layer Pattern
- **Manager**: Data processing and business logic (e.g., BuildingManager, RouteManager)
- **Renderer**: 3D mesh/curve generation (e.g., BuildingRenderer, CurveRenderer)
- **Layer**: Blender collection/object organization (e.g., BuildingLayer, RenderLayer)

### Multiple Inheritance Pattern
- Classes like `BuildingManager(BaseBuildingManager, Manager)` use multiple inheritance
- Base classes provide core functionality (parseWay, parseRelation, createBuilding)
- Manager classes provide Blender integration

## Object Naming Conventions

### Runtime Objects (created during import)
- `ROUTE`: Main route curve with FOLLOW_PATH constraint
- `CAR_TRAIL`: Derived trail geometry (auto-generated, non-toggleable)
- `ROUTERIG_CAMERA`: Camera rig object
- `RouteTrace`: Geometry Nodes object for route animation
- `_profile_curve`: Bevel object for route visualization

### Object Roles (blosm_role property)
All objects must be tagged with `blosm_role`:
- `route`: Route curves and animation objects
- `road`: Road geometry from OSM
- `building`: Building meshes
- `water`: Water surfaces and Toronto Islands meshes
- `environment`: Environment assets (ground, shoreline)

## Scene Properties (Registered in __init__.py)

### Animation Properties
- `blosm_anim_start/end`: Car animation frame range (default: 15-150)
- `blosm_lead_frames`: Car lead object advance (default: 2)
- `blosm_route_start/end`: Route trace animation frame range
- `blosm_base_start/end`: Custom animation drivers
- `blosm_route_object_name`: Last route curve name

### CAR_TRAIL Adjustment Properties
- `blosm_car_trail_start_adjust`: Driver trim for bevel_factor_start
- `blosm_car_trail_end_adjust`: Driver trim for bevel_factor_end
- `blosm_car_trail_tail_shift`: Shared driver shift

## Code Style

### Type Hints
- Use type hints in newer code (see `asset_manager/single_file_loader.py`)
- Example: `def load_assets(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:`

### Error Handling
- Robust error handling with multiple retry attempts
- Graceful degradation on incomplete data
- Use `[CashCab] Warning:` prefix for recovery messages

### Performance Patterns
- BVH trees for spatial queries (BuildingManager)
- Asset caching (SingleFileAssetLoader.cached_assets)
- Geometry simplification for large datasets

## Naming Patterns

### File Organization
- `manager.py`: Business logic and data processing
- `renderer.py`: 3D generation logic
- `layer.py`: Collection/object organization
- `services/`: Service layer abstractions
- `*_operator.py`: Blender operators

### Class Naming
- Managers: `{Feature}Manager` (e.g., BuildingManager, RouteManager)
- Renderers: `{Feature}Renderer` (e.g., BuildingRenderer, CurveRenderer)
- Operators: `BLOSM_OT_{Action}` (e.g., BLOSM_OT_FetchRouteMap)

### Method Naming
- Public methods: `snake_case` with descriptive names
- Private methods: `_snake_case` prefix
- Callbacks: `_on_event_name` pattern
