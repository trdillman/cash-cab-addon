"""
Custom exceptions for the BLOSM Asset Manager.
"""

from __future__ import annotations


class AssetValidationError(Exception):
    """Raised when asset validation fails."""


class RegistryLoadError(Exception):
    """Raised when loading a registry file fails."""


class RegistrySaveError(Exception):
    """Raised when saving a registry file fails."""

