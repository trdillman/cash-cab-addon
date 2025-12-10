# BLOSM GUI Module

Complete GUI module extracted from original BLOSM addon with modular architecture.

## Structure

```
gui/
├── __init__.py       - Main registration and module exports
├── properties.py     - Property groups and property helpers
├── panels.py         - UI panels and layouts
└── operators.py      - GUI-related operators
```

## Usage

### Registration

In your main addon `__init__.py`:

```python
from . import gui

def register():
    gui.register()
    # ... other registrations

def unregister():
    gui.unregister()
    # ... other unregistrations
```

### Accessing Properties

All properties are stored in `bpy.context.scene.blosm`:

```python
addon = bpy.context.scene.blosm
start_address = addon.route_start_address
end_address = addon.route_end_address
```

## Classes

### Properties (properties.py)

- **BlosmDefaultLevelsEntry** - Single entry for default building levels
- **BlosmProperties** - Main property group with 150+ properties for:
  - OSM import settings (extent, data type, mode)
  - Route import settings (addresses, padding, animation)
  - Building settings (levels, roof shapes)
  - Terrain settings (resolution, reduction ratio)
  - Overlay settings (types, URLs)
  - 3D Tiles settings (source, LOD)
  - Material and asset settings

### Operators (operators.py)

- **BLOSM_OT_ReloadAssetPackageList** - Reload asset package list
- **BLOSM_OT_SelectExtent** - Open web browser for extent selection
- **BLOSM_OT_PasteExtent** - Paste extent from clipboard
- **BLOSM_OT_ExtentFromActive** - Get extent from active object
- **BLOSM_OT_ReplaceMaterials** - Replace materials on selected objects
- **BLOSM_OT_Gn2d_Info** - Open info about Geometry Nodes
- **BLOSM_OT_LevelsAdd** - Add default level entry
- **BLOSM_OT_LevelsDelete** - Delete default level entry

### Panels (panels.py)

- **BLOSM_PT_Extent** - Main panel with extent selection and import button
- **BLOSM_PT_Settings** - Settings panel (adapts based on data type)
- **BLOSM_PT_RouteImport** - Route import panel with address inputs
- **BLOSM_PT_RouteImportAdvanced** - Advanced route import options
- **BLOSM_PT_FallbackHeights** - Fallback building height settings
- **BLOSM_PT_Tools** - Tools panel for 3D Tiles
- **BLOSM_PT_Copyright** - Copyright information panel
- **BLOSM_PT_BpyProj** - BpyProj projection integration panel
- **BLOSM_UL_DefaultLevels** - UIList for default levels display

### Helper Functions

#### properties.py
- `getDataTypes()` - Returns available data types
- `getBlenderMaterials(self, context)` - Returns material list based on type
- `getAssetPackages(self, context)` - Returns available asset packages
- `updateGnBlendFile2d(self, context)` - Updates Geometry Nodes file

#### __init__.py
- `addDefaultLevels()` - Initialize default level entries

## Dependencies

### Internal
- `..app.blender` - BlenderApp instance and utilities
- `..defs` - Keys and constants
- `util.transverse_mercator` - TransverseMercator projection class

### External
- `bpy` - Blender Python API
- `os`, `math`, `webbrowser`, `json` - Standard library

## Panel Visibility

Panels are shown in the 3D Viewport sidebar under the "Blosm" category. Some panels have poll() methods to control visibility:

- **BLOSM_PT_Copyright** - Only shows when copyright text exists
- **BLOSM_PT_Tools** - Only shows when data type is "3d-tiles" and objects selected
- **BLOSM_PT_BpyProj** - Only shows when BpyProj addon is installed

## Property Groups

### Main Properties (BlosmProperties)

**Extent:**
- `minLat`, `maxLat`, `minLon`, `maxLon` - Geographic extent bounds

**OSM Import:**
- `dataType` - Type of data to import (osm, terrain, overlay, 3d-tiles)
- `osmSource` - Import from server or file
- `osmFilepath` - Path to OSM file
- `mode` - Import mode (3Drealistic, 3Dsimple, 2D)
- `buildings`, `water`, `forests`, `vegetation`, `highways`, `railways` - Layer toggles

**Route Import:**
- `route_start_address`, `route_end_address` - Route endpoints
- `route_padding_m` - Padding around route in meters
- `route_create_preview_animation` - Create animation toggle
- Auto-import: Roads, Buildings, Water, RouteCam always enabled

**Building Settings:**
- `levelHeight` - Height per building level
- `defaultLevels` - Collection of default level entries
- `defaultRoofShape` - Default roof shape (flat/gabled)

**Advanced:**
- `singleObject` - Import as single object
- `relativeToInitialImport` - Relative positioning
- `setupScript` - Path to custom setup script

## Notes

1. **Registration Pattern**: Only 8 classes are registered (matches original behavior)
2. **Scene Properties**: Route animation properties (blosm_anim_start, etc.) should be registered in main addon __init__.py
3. **Asset Packages**: Requires asset_packages.json in assets directory
4. **Realistic Mode**: Some features require realistic mode addon (conditional imports)

## Future Enhancements

Consider registering these currently unregistered classes:
- BLOSM_OT_ReloadAssetPackageList
- BLOSM_OT_SelectExtent
- BLOSM_OT_PasteExtent
- BLOSM_OT_ExtentFromActive
- BLOSM_OT_ReplaceMaterials
- BLOSM_OT_Gn2d_Info
- BLOSM_PT_Copyright
- BLOSM_PT_Extent
- BLOSM_PT_Settings
- BLOSM_PT_Tools
- BLOSM_PT_BpyProj
- PanelRealisticTools

These are defined but not registered in the original code.
