"""
Route Services Module

This module provides service layer abstraction for route operations.
Services encapsulate business logic and provide clean, testable interfaces
that don't depend directly on Blender's API.

Services available:
- RoutePreparationService: Geocoding and route calculation

Usage:
    from route.services import RoutePreparationService
    from route.config import DEFAULT_CONFIG

    service = RoutePreparationService(DEFAULT_CONFIG)
    result = service.prepare(start_address, end_address, padding_m)
"""

from .base import ServiceResult, ServiceError, IService, ILogger
from .preparation import RoutePreparationService, RoutePreparationResult

__all__ = [
    # Base classes
    'ServiceResult',
    'ServiceError',
    'IService',
    'ILogger',

    # Services
    'RoutePreparationService',
    'RoutePreparationResult',
]
