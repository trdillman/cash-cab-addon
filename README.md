# CashCab Route Import — Blender Addon

A powerful Blender addon for importing routes and OpenStreetMap data to create animated urban scenes for the CashCab animation project.

![Blender Version](https://img.shields.io/badge/Blender-4.5%2B-orange)
![Version](https://img.shields.io/badge/Version-3.0.1-blue)
![Category](https://img.shields.io/badge/Category-Import-green)

## Overview

CashCab Route Import is a comprehensive Blender addon that fetches real-world routes, imports OpenStreetMap data, and automatically creates animated scenes with roads, buildings, water, terrain, and camera paths. Designed specifically for the CashCab animation workflow, it streamlines the process of creating realistic urban environments from geographic data.

## Features

### 🗺️ Route Import
- **Address-based route fetching** - Enter start and end addresses to automatically fetch routes.
- **Auto Snap** - Automatically snaps addresses to precise road centerlines using Google Maps API.
- **Automatic scene setup** - Creates animated route curves with proper geometry.
- **Configurable padding** - Control the area around routes for OSM data import.

### 🎥 Route Camera (New)
- **Integrated RouteRig** - Built-in camera rig generation system (no separate addon required).
- **Auto-generate** - Automatically spawns and animates a camera rig upon route import.
- **Manual Controls** - "Spawn Camera" and "Animate Camera" buttons available in the panel.

### 🏙️ OpenStreetMap Integration
- **Automatic asset import** - Roads, buildings, water, and environment assets.
- **Toronto Islands support** - Special mesh import for Toronto waterfront areas.
- **Configurable layers** - Control which OSM features to import.
- **Modes** - 3D realistic, 3D simple, and 2D modes.

### 🎥 Animation System
- **Route animation** - Automatic keyframe generation for car movement along routes.
- **Route trace animation** - Geometry Nodes-driven route reveal effect.
- **Configurable timing** - Adjustable start/end frames and lead frames.

### 🎨 Scene Assets
- **CAR_TRAIL** - Automatically generated trail geometry following the route.
- **Profile curves** - Bevel objects for route visualization.
- **Material system** - Integrated material management for roads and buildings.
- **Auto Render Settings** - Fast GI, AO, and clamping settings are automatically applied during import.

## Installation

1. Download the addon ZIP file.
2. Open Blender (4.5 or later).
3. Go to **Edit → Preferences → Add-ons**.
4. Click **Install** and select the addon ZIP file.
5. Enable the addon: **Import: CashCab Route Import**.

**Note:** The separate `routerig` addon is no longer required and should be uninstalled if present.

## Quick Start

1. Open the **3D Viewport** sidebar (press `N`).
2. Navigate to the **CashCab** tab.
3. **Route Configuration**:
   - Enter **Start Address** and **End Address**.
   - Ensure **Auto Snap** is enabled (default) for precision.
   - Set **Route Padding** (default: 100m; expands for water).
4. **Main Toggles**:
   - Enable **Auto-generate Camera** (default: On).
5. Click **Fetch Route & Map**.

The addon will:
- Fetch route and OSM data.
- Import assets (Roads, Buildings, Water).
- Generate `ROUTE`, `CAR_TRAIL`, and animation.
- Spawn and animate the `ROUTERIG_CAMERA`.
- Apply optimal render settings.

## Panel Reference

### Route Configuration
- **Start/End Address**: Input fields.
- **Auto Snap**: Toggles Google API snapping.
- **Padding**: Import area buffer.

### Main Toggles
- **Create Animated Route**: Generates car/route animation.
- **Auto-generate Camera**: Toggles automatic RouteRig execution.

### Animation Controls
- **Start/End Frame**: Timing for car animation.
- **Lead Frames**: Offset for lead object.

### Route Camera (Collapsible)
- **Spawn Camera**: Manually create the camera rig.
- **Animate Camera**: Manually generate camera keyframes.

### Extra Features (Collapsible)
- **Route Adjuster**: Interactive route editing tools.
- **Street Labels**: Toggle visibility of generated street names (Default: Off).
- **Trim Start/End U-Turns**: Auto-remove loops at endpoints (Default: Off).

## Project Structure

```
cash-cab-addon/
├── __init__.py              # Registration
├── gui/                     # UI Panels & Operators
├── route/                   # Route logic (fetch, snap, utils)
├── routerig/                # Integrated Camera System
├── osm/                     # OSM Import logic
├── road/                    # Road processing
├── building/                # Building generation
├── asset_manager/           # Asset loading system
└── ...
```

## Troubleshooting

- **Camera missing?** Check "Auto-generate Camera" or use the manual buttons in the "Route Camera" section.
- **Bad route alignment?** Ensure "Auto Snap" is on.
- **Import fails?** Check internet connection and API keys.

## Version
**3.0.1** - Integrated RouteRig, Auto Snap, UI Refinement.