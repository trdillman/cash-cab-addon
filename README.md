# CashCab Route Import — Blender Addon

A powerful Blender addon for importing routes and OpenStreetMap data to create animated urban scenes for the CashCab animation project.

![Blender Version](https://img.shields.io/badge/Blender-4.5%2B-orange)
![Version](https://img.shields.io/badge/Version-2.2.0-blue)
![Category](https://img.shields.io/badge/Category-Import-green)

## Overview

CashCab Route Import is a comprehensive Blender addon that fetches real-world routes, imports OpenStreetMap data, and automatically creates animated scenes with roads, buildings, water, terrain, and camera paths. Designed specifically for the CashCab animation workflow, it streamlines the process of creating realistic urban environments from geographic data.

## Features

### 🗺️ Route Import
- **Address-based route fetching** - Enter start and end addresses to automatically fetch routes
- **Automatic scene setup** - Creates animated route curves with proper geometry
- **Configurable padding** - Control the area around routes for OSM data import
- **U-turn trimming** - Automatically detects and removes problematic U-turn loops at route endpoints

### 🏙️ OpenStreetMap Integration
- **Automatic asset import** - Roads, buildings, water, and environment assets
- **Toronto Islands support** - Special mesh import for Toronto waterfront areas
- **Configurable layers** - Control which OSM features to import (buildings, water, forests, highways, railways)
- **Multiple import modes** - 3D realistic, 3D simple, and 2D modes

### 🎥 Animation System
- **Route animation** - Automatic keyframe generation for car movement along routes
- **Route trace animation** - Geometry Nodes-driven route reveal effect
- **Configurable timing** - Adjustable start/end frames and lead frames

### 🎨 Scene Assets
- **CAR_TRAIL** - Automatically generated trail geometry following the route
- **Profile curves** - Bevel objects for route visualization
- **Material system** - Integrated material management for roads and buildings
- **Render settings** - Pre-configured render settings with Fast GI, AO, and clamping

## Installation

1. Download the addon as a ZIP file or clone the repository
2. Open Blender (4.5 or later)
3. Go to **Edit → Preferences → Add-ons**
4. Click **Install** and select the addon ZIP file
5. Enable the addon by checking the box next to "Import: CashCab Route Import"

## Quick Start

### Basic Route Import

1. Open the **3D Viewport** sidebar (press `N` if hidden)
2. Navigate to the **CashCab** tab
3. In the **Route Import** panel:
   - Enter your **Start Address**
   - Enter your **End Address**
   - Set **Route Padding** (default: 500m)
4. Click **Fetch Route & Map**
5. Wait for the import to complete (progress shown in console)

The addon will automatically:
- Fetch the route from OpenStreetMap
- Import roads, buildings, and water within the padded area
- Create a `ROUTE` curve object with animation
- Generate a `CAR_TRAIL` object for visualization
- Set up animation keyframes

### Animation Controls

After importing a route, use the **Animation** panel to configure timing:

- **Car Start Frame** - First frame of car animation (default: 15)
- **Car End Frame** - Last frame of car animation (default: 150)
- **Lead Frames** - Frames the lead object stays ahead (default: 2)
- **Route Trace Start/End** - Timing for route reveal animation

Changes to these properties automatically update keyframes.

## Panel Reference

### Route Import Panel
- **Start Address** - Starting point for route
- **End Address** - Ending point for route
- **Route Padding (m)** - Area around route to import OSM data
- **Fetch Route & Map** - Main import operator

### Advanced Route Settings
- **Auto-import Roads** - Always enabled
- **Auto-import Buildings** - Always enabled
- **Auto-import Water** - Always enabled
- **Auto-import Environment** - Optional environment assets

### Animation Panel
- Car animation timing controls
- Route trace animation controls
- Driver variables for custom animations

### Cleanup Panel
- Tools for removing imported objects by type
- Selective cleanup of routes, roads, buildings, water, etc.

## Project Structure

```
cash-cab-addon/
├── __init__.py              # Main addon registration
├── defs.py                  # Constants and definitions
├── app/                     # Application core
├── building/                # Building generation
├── config/                  # Configuration files
├── gui/                     # User interface (panels, properties, operators)
├── material/                # Material management
├── osm/                     # OpenStreetMap import operators
├── parse/                   # OSM data parsing
├── renderer/                # Rendering utilities
├── road/                    # Road generation
├── route/                   # Route fetching and processing
│   ├── fetch_operator.py    # Main route fetch operator
│   ├── curve_simplifier.py  # U-turn trimming and simplification
│   ├── anim.py              # Animation keyframe management
│   ├── assets.py            # Route asset operators
│   └── nodes.py             # Geometry Nodes setup
├── setup/                   # Scene setup and render settings
├── terrain/                 # Terrain generation
└── util/                    # Utility functions
```

## Key Objects and Naming

### Runtime Objects
- **`ROUTE`** - Main route curve object (follows path constraint)
- **`CAR_TRAIL`** - Derived trail geometry (auto-generated, non-toggleable)
- **`RouteTrace`** - Route reveal geometry with Geometry Nodes modifier
- **`_profile_curve`** - Bevel object for route visualization

### Object Roles (`blosm_role` property)
Objects are tagged with roles for identification and cleanup:
- `route` - Route curves
- `road` - Road geometry
- `building` - Building meshes
- `water` - Water surfaces
- `environment` - Environment assets (ground, shoreline)

## Advanced Features

### U-Turn Trimming
The addon automatically detects and removes U-turn loops at route endpoints using configurable parameters:
- **Window fraction** - Portion of route to check (default: 0.15)
- **Corner angle threshold** - Minimum angle for U-turn detection (default: 100°)
- **Direction reversal threshold** - Angle for direction change (default: 135°)
- **Max U-turn length** - Maximum length of U-turn to remove (default: 0.3)

### Geometry Nodes Integration
Route trace animation uses Geometry Nodes for procedural effects:
- Node group: `ASSET_RouteTrace`
- Driver-controlled reveal animation
- Configurable via scene properties

### Render Settings
Pre-configured render settings for optimal quality:
- Fast GI enabled
- Ambient Occlusion enabled
- Indirect light clamping (10.0)
- Direct light clamping (0.0)

Apply via: **Setup → Apply Render Settings** operator

## Development

### Testing
The addon includes comprehensive test coverage:
- `tests/test_curve_simplifier.py` - U-turn trimming tests
- `tests/test_scene_audit_strict.py` - Scene integrity checks
- `tests/test_render_settings_audit.py` - Render settings validation
- `tests/test_final_gate_run.py` - End-to-end integration tests

Run tests within Blender using the test framework.

### Version Information
Current version: **2.2.0**  
Last optimized: 2025-10-12 18:29:35

## Troubleshooting

### Route Import Fails
- Verify internet connection (required for OSM data)
- Check that addresses are valid and geocodable
- Increase route padding if area is too small

### Missing Objects
- Check console for warnings about missing `.blend` files
- Environment assets are optional (warnings are informational)
- Verify `blosm_role` property on objects for proper identification

### Animation Not Working
- Ensure route object exists and is named `ROUTE`
- Check that animation properties are set correctly
- Verify drivers are connected to scene properties
- Use **Force Update Keyframes** if needed

### CAR_TRAIL Issues
- CAR_TRAIL is auto-generated from ROUTE
- Ensure `_profile_curve` exists and is properly linked
- Check that bevel object assignment is correct
- Profile curve should not have `.001` suffix (indicates duplication issue)

## Contributing

This addon is part of the CashCab animation project. For development:

1. Review `TODO.md` for current work items
2. Check `WHATS_NEXT.md` for priorities and guidelines
3. Create diffs in `diffs/` directory for changes
4. Run test suite before committing
5. Follow the stability-first approach (no broad refactors without approval)

## License

Community support addon for Blender.

## Credits

Built on the BLOSM (Blender OpenStreetMap) framework with extensive customizations for the CashCab animation workflow.

## Support

For issues, questions, or feature requests, please refer to:
- `TODO.md` - Current work items and known issues
- `WHATS_NEXT.md` - Development priorities and guidelines
- `gui/README.md` - Detailed GUI module documentation
