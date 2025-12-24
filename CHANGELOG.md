# Changelog

All notable changes to this addon will be documented in this file.

## Unreleased

### Added
- Native **Bulk Import** workflow (`bulk/`) with Google Sheet (CSV export) + local CSV support.
- Headless-per-route execution for Bulk Import (fresh Blender process per route) for improved stability.

### Changed
- Google Maps API key resolution now supports `CASHCAB_GOOGLE_API_KEY` for headless/testing runs (no hardcoded fallback key).
- Street labels default to hidden (viewport hidden + never render).
- Render resolution percentage forced to 100% on import.

### Fixed
- Cancelling the single import confirmation dialog no longer leaves “Fetch Route & Map” in a broken state.

## 3.0.1
- Integrated RouteRig camera system.
- Auto Snap support (Google API).
- UI refinement and pipeline hardening.

