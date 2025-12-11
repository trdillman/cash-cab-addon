# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- End-to-end testing: `python test_final_gate_run.py` (run 3 Toronto routes for release validation)
- Scene integrity: `python test_scene_audit_strict.py` (verifies objects, roles, and relationships)
- Render settings: `python test_render_settings_audit.py` (validates Fast GI, AO, clamping)
- Outliner visibility: `python test_outliner_visibility_audit.py` (checks viewport visibility)
- Individual operator tests: `python test_operator_invoke.py`
- Cleanup audit: `python audit_saved_blend.py` (scene verification after operations)

### Blender Headless Testing
- Use Blender `--factory-startup` flag for headless testing to avoid addon conflicts
- Example: `blender --factory-startup --python test_scene_audit_strict.py`

### Asset Management
- Update asset registry: `python asset_manager/cli.py update`
- Validate assets: `python asset_manager/cli.py validate`
- Extract assets from .blend files: `python asset_manager/asset_extractor.py`

## Architecture Overview

### Core System Design
CashCab is a Blender addon for importing real-world routes and OpenStreetMap data to create animated urban scenes. The system follows a pipeline architecture with distinct phases for route fetching, OSM data import, asset generation, and animation setup.

### Main Components

#### Route System (`route/`)
- **fetch_operator.py**: Main operator (`BLOSM_OT_FetchRouteMap`) that handles address-to-route conversion and OSM data fetching
- **utils.py**: Core route service functions, Overpass API integration, tile-based data fetching
- **anim.py**: Animation keyframe management for car movement and route trace effects
- **nodes.py**: Geometry Nodes setup for RouteTrace procedural animations
- **assets.py**: Route asset operators (ROUTE curve, CAR_TRAIL generation)
- **water_manager.py**: Specialized handling for Toronto Islands waterfront areas

#### Building System (`building/`)
- **manager.py**: Building data processing and OSM building handling
- **renderer.py**: 3D mesh generation from OSM building footprints
- **roof/**: Specialized roof generators (flat, hipped, mansard, etc.)
- **layer.py**: Building layer management and organization

#### OpenStreetMap Integration (`parse/osm/`, `osm/`)
- **import_operator.py**: Core OSM data import functionality
- **parse/**: OSM XML parsing with support for nodes, ways, and relations
- **relation/building.py**: Building-specific OSM relation handling
- **relation/multipolygon.py**: Multipolygon geometry processing

#### Road System (`road/`)
- **processor.py**: Road geometry generation from OSM way data
- **materials.py**: Road material system and shading
- **curve_converter.py**: OSM ways to Blender curve conversion

#### GUI System (`gui/`)
- **panels.py**: Main CashCab sidebar panels (route import, animation, cleanup)
- **operators.py**: Blender operators for various UI actions
- **properties.py**: Scene properties and addon configuration
- **cleanup_operator.py**: Object cleanup by `blosm_role` property

#### Asset System (`asset_manager/`)
- **registry.py**: Asset file registration and management
- **loader.py**: .blend file asset loading system
- **validation.py**: Asset integrity checking
- **schema.py**: Asset metadata schemas

### Key Objects and Naming Conventions

#### Runtime Objects (created during import)
- **`ROUTE`**: Main route curve object with FOLLOW_PATH constraint for car animation
- **`CAR_TRAIL`**: Derived trail geometry automatically generated from ROUTE (non-toggleable)
- **`RouteTrace`**: Geometry Nodes object for procedural route reveal animation
- **`_profile_curve`**: Bevel object for route visualization

#### Object Roles (`blosm_role` property)
All created objects are tagged with roles for identification and cleanup:
- `route`: Route curves and related animation objects
- `road`: Road geometry from OSM data
- `building`: Building meshes
- `water`: Water surfaces and Toronto Islands meshes
- `environment`: Environment assets (ground, shoreline)

### Animation System
- Car animation uses FOLLOW_PATH constraint with keyframes controlled by scene properties
- Route trace animation uses Geometry Nodes with drivers connected to scene properties
- Animation timing controlled by scene properties: `blosm_anim_start/end`, `blosm_route_start/end`, `blosm_lead_frames`
- Driver variables `blosm_base_start/end` available for custom animations

### RouteCam Integration (`routecam/`)
- Unified camera path system for dynamic camera movement
- Engine v2: Core camera path solving and direction
- Engine viz: Visualization and logic for camera paths
- Optional component - addon functions without it

### Development Workflow

#### Making Changes
1. Run relevant test scripts before any changes to establish baseline
2. Use `diffs/` directory to document all changes with dated markdown files
3. For pipeline/UI changes: run `test_scene_audit_strict.py` and `test_render_settings_audit.py`
4. For release candidates: run `test_final_gate_run.py` with 3 Toronto routes

#### Stability Principles
- No broad refactors without approval (stability-first approach)
- Maintain object naming conventions and `blosm_role` property system
- Preserve animation driver connections and scene property relationships
- Keep CAR_TRAIL as auto-generated, non-toggleable derived asset

#### Testing Strategy
- Comprehensive audit coverage for scene integrity, render settings, and animation
- End-to-end validation with real Toronto routes
- Focused unit tests for individual components
- Asset validation and registry integrity checks

## Special Considerations

### Toronto Islands Support
Special handling for Toronto waterfront areas with dedicated mesh import and water management. The water_manager.py handles the unique geography of Toronto Islands.

### U-Turn Trimming
Automatic detection and removal of U-turn loops at route endpoints using configurable parameters:
- Window fraction (default: 0.15)
- Corner angle threshold (default: 100°)
- Direction reversal threshold (default: 135°)
- Max U-turn length (default: 0.3)

### Render Settings
Pre-configured optimal render settings maintained as addon defaults:
- Fast GI enabled
- Ambient Occlusion enabled
- Indirect light clamping (10.0)
- Direct light clamping (0.0)

### Error Recovery
Robust error handling and recovery mechanisms throughout the pipeline, particularly in route fetching and OSM data import phases.