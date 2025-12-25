# CashCab Addon - Project Overview

## Project Purpose

CashCab is a Blender addon for importing real-world routes with OpenStreetMap (OSM) data to produce animated 3D scenes with studio-ready render settings. The addon transforms addresses into complete animated scenes with routes, buildings, roads, and camera animation.

## Core Functionality

### Primary Operator
**`bpy.ops.blosm.fetch_route_map`** (`route/fetch_operator.py`)

The main operator handles the complete pipeline:
1. Address input → Google Maps API geocoding
2. Route calculation between addresses
3. OSM data fetch (buildings, roads, water)
4. 3D scene generation with animation
5. Render settings application

### Key Outputs
- **ROUTE curve**: Main path for car animation with FOLLOW_PATH constraint
- **CAR_TRAIL**: Derived trail geometry auto-generated from ROUTE
- **ROUTERIG_CAMERA**: Auto-generated camera rig with animation
- **RouteTrace**: Geometry Nodes object for procedural route reveal
- **Building meshes**: 3D buildings from OSM footprints
- **Road geometry**: Road network from OSM ways
- **Water surfaces**: Toronto Islands specialized handling

## Data Flow Architecture

```
User Input (Addresses)
        ↓
[Google Maps API] → Geocode & Snap to Road Centerlines
        ↓
[Route Calculation] → Generate Route Path
        ↓
[Overpass API] → Fetch OSM Data (buildings, roads, water)
        ↓
[Parse OSM XML] → Nodes, Ways, Relations
        ↓
├─→ [Building System] → 3D Building Meshes
├─→ [Road System] → Road Geometry
├─→ [Route System] → ROUTE Curve + CAR_TRAIL
└─→ [RouteRig] → Camera Rig Generation
        ↓
[Animation System] → Keyframes + Geometry Nodes
        ↓
[Render Settings] → Fast GI, AO, Clamping
        ↓
Final 3D Scene (.blend)
```

## Major Systems

### Route System (`route/`)
**Purpose:** Handle address-to-route conversion and animation

**Key Components:**
- `fetch_operator.py`: Main operator BLOSM_OT_FetchRouteMap
- `utils.py`: Core route service functions, Overpass API integration
- `anim.py`: Animation keyframe management
- `nodes.py`: Geometry Nodes setup for RouteTrace
- `assets.py`: ROUTE and CAR_TRAIL generation
- `water_manager.py`: Toronto Islands waterfront specialized handling
- `uturn_trim.py`: Automatic U-turn detection and removal

**Services Layer (`route/services/`):**
- `base.py`: Base service abstractions
- `preparation.py`: Route preparation and validation

**Performance & Diagnostics:**
- `performance_optimizer.py`: Performance optimization
- `performance_tracker.py`: Metrics tracking
- `diagnostics.py`: Diagnostic tools
- `debug_monitor.py`: Debug monitoring
- `error_recovery.py`: Error recovery
- `exceptions.py`: Custom exceptions
- `state_manager.py`: State management
- `geometry_simplifier.py`: Geometry simplification
- `route_trace_check.py`: Route trace validation

### Building System (`building/`)
**Purpose:** Generate 3D building meshes from OSM footprints

**Architecture:** Manager-Renderer-Layer pattern
- `manager.py`: Data processing from OSM (BVH tree for spatial queries)
- `renderer.py`: 3D mesh generation
- `layer.py`: Layer management
- `roof/`: Specialized roof generators (flat, hipped, mansard, pyramidal, skillion)

**Key Pattern:** Multiple inheritance
```python
class BuildingManager(BaseBuildingManager, Manager):
    def __init__(self, osm, app, buildingParts, layerClass):
        self.osm = osm
        Manager.__init__(self, osm)
        BaseBuildingManager.__init__(self, osm, app, buildingParts, layerClass)
```

### Road System (`road/`)
**Purpose:** Generate road geometry from OSM ways

**Components:**
- `processor.py`: Road geometry generation
- `materials.py`: Road material system and shading
- `curve_converter.py`: OSM ways to Blender curves
- `street_labels.py`: Street label generation (default: hidden)
- `detection.py`: Road type detection
- `config.py`: Road configuration

### Renderer System (`renderer/`)
**Purpose:** Manage rendering pipeline and layers

**Components:**
- `curve_renderer.py`: Curve-based rendering
- `node_renderer.py`: Node-based rendering
- `layer.py`: Rendering layer management
- `curve_layer.py`: Curve layer handling
- `node_layer.py`: Node layer handling

### RouteRig Camera System (`routerig/`)
**Purpose:** Auto-generate and animate camera rigs

**Components:**
- `ops.py`: Camera operators (spawn, animate)
- `camera_spawn.py`: Core camera rig creation
- `camera_anim.py`: Camera path animation

### OSM Integration (`osm/`, `parse/`)
**Purpose:** Import and parse OpenStreetMap XML data

**Components:**
- `import_operator.py`: Core OSM data import (BLOSM_OT_ImportData)
- `parse/osm/`: OSM XML parsing (nodes, ways, relations)
- `parse/relation/building.py`: Building-specific OSM relations
- `parse/relation/multipolygon.py`: Multipolygon geometry processing

### GUI System (`gui/`)
**Purpose:** Blender UI integration and user interaction

**Components:**
- `panels.py`: Main CashCab sidebar panels
- `operators.py`: Blender operators for UI actions
- `properties.py`: Scene properties and addon config
- `cleanup_operator.py`: Object cleanup by blosm_role
- `cleanup_patterns.py`: Cleanup pattern definitions

### Asset System (`asset_manager/`)
**Purpose:** Manage external asset files (blend libraries)

**Components:**
- `registry.py`: Asset file registration
- `loader.py`: .blend file asset loading
- `validation.py`: Asset integrity checking
- `schema.py`: Asset metadata schemas
- `cli.py`: Command-line interface

**Key Pattern:**
```python
class SingleFileAssetLoader:
    def __init__(self, blend_file_path: Optional[Path] = None):
        self.cached_assets: Optional[Dict[str, Any]] = None
    
    def load_assets(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        # Caching logic with validation
```

### Bulk System (`bulk/`)
**Purpose:** Process multiple routes in batch

**Architecture:** Native bulk import using headless workers
- Each route runs in fresh Blender process
- Manifest source: Google Sheet URL or local CSV
- Per-route logging in %TEMP%\cashcab_bulk_native\<timestamp>\*.log

**Components:**
- `panels.py`: Bulk import UI panel
- `properties.py`: Bulk settings properties
- `google_sheet.py`: Google Sheets integration

## Object Naming Conventions

### Runtime Objects
- **ROUTE**: Main route curve with FOLLOW_PATH constraint
- **CAR_TRAIL**: Derived trail (non-toggleable)
- **ROUTERIG_CAMERA**: Camera rig object
- **RouteTrace**: Geometry Nodes for route reveal
- **_profile_curve**: Bevel object for route visualization

### Object Roles (blosm_role property)
All created objects tagged with roles:
- `route`: Route curves and animation objects
- `road`: Road geometry from OSM
- `building`: Building meshes
- `water`: Water surfaces and Toronto Islands
- `environment`: Ground, shoreline assets

## Animation System

### Scene Properties
**Animation Properties:**
- `blosm_anim_start/end`: Car animation frame range (default: 15-150)
- `blosm_lead_frames`: Car lead object advance (default: 2)
- `blosm_route_start/end`: Route trace animation frame range (default: 15-150)
- `blosm_base_start/end`: Custom animation drivers (default: 0.0-1.0)
- `blosm_route_object_name`: Last route curve name

**CAR_TRAIL Adjustment Properties:**
- `blosm_car_trail_start_adjust`: Driver trim for bevel_factor_start
- `blosm_car_trail_end_adjust`: Driver trim for bevel_factor_end
- `blosm_car_trail_tail_shift`: Shared driver shift

### Animation Mechanism
- Car: FOLLOW_PATH constraint with keyframes
- Route trace: Geometry Nodes with drivers
- Timing: Controlled by scene properties
- Drivers: Connected to blosm_* properties

## Special Features

### Toronto Islands Support
Special handling for Toronto waterfront with:
- Dedicated mesh import
- Water management
- Minimum 500m route padding expansion

### U-Turn Trimming
Automatic U-turn detection and removal:
- Window fraction: 0.15
- Corner angle threshold: 100°
- Direction reversal threshold: 135°
- Max U-turn length: 0.3

### Render Settings
Pre-configured optimal defaults (v3.0.1+):
- Fast GI: enabled
- Ambient Occlusion: enabled
- Indirect light clamping: 10.0
- Direct light clamping: 0.0

## External Dependencies

- **Blender**: 4.5.0+ required
- **Google Maps API**: Geocoding and route snapping
- **Overpass API**: OpenStreetMap data fetching

## Project Structure

```
cash-cab-addon-dev-folder/
├── cash-cab-addon/          # Main Blender addon
├── bulk-pipeline-v2/        # Advanced bulk processing
├── test-and-audit/          # Root-level test harnesses
├── batch-script/            # Batch processing scripts
├── coordination-tools/      # Large-scale import management
├── build-scripts/           # Build and packaging utilities
├── spec/                    # Feature specifications
├── diffs/                   # Change documentation
├── worktrees/               # Git worktrees for parallel dev
├── tmp/                     # Temporary files (avoid for tests)
└── reports/                 # Audit reports and output
```

## Testing Strategy

**Use `test-and-audit/` scripts** (maintained test harnesses):
- `test_final_gate_run.py`: End-to-end with 3 Toronto routes
- `test_scene_audit_strict.py`: Scene integrity validation
- `test_render_settings_audit.py`: Render settings validation
- `test_operator_invoke.py`: Operator testing
- `test_e2e_camera_integration.py`: Camera integration testing

**Headless Testing:**
```bash
blender --factory-startup -b --python test-and-audit/test_scene_audit_strict.py
```

## Known Code Quality Issues

### God Object Problem
`BLOSM_OT_FetchRouteMap` class is 1,756 lines - targeted for refactoring into 4 focused services.

### Duplicate Property Registration
As of v3.0.1, `blosm_car_trail_*` properties registered twice in `__init__.py` (lines 121-149 and 177-205) - oversight but doesn't cause runtime errors.
