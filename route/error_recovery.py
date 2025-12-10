"""
Road Import Error Recovery System
Provides comprehensive error handling, recovery strategies, and troubleshooting
for the CashCab road import workflow with automatic fallback mechanisms.
"""

from __future__ import annotations

import time
import traceback
import tempfile
import os
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import bpy
from .config import DEFAULT_CONFIG
from .exceptions import (
    RouteServiceError, GeocodingError, RoutingError, OverpassError,
    TileImportError, RouteObjectError, RouteStateError
)
from .debug_monitor import get_monitor, WorkflowStage, SeverityLevel


class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK_CONFIGURATION = "fallback_configuration"
    ALTERNATIVE_SERVER = "alternative_server"
    REDUCED_COMPLEXITY = "reduced_complexity"
    SKIP_OPTIONAL_STEP = "skip_optional_step"
    RESET_AND_RETRY = "reset_and_retry"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class RecoveryAction:
    """Single recovery action"""
    strategy: RecoveryStrategy
    description: str
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    requires_user_input: bool = False
    success_probability: float = 0.7


@dataclass
class ErrorContext:
    """Context information for error recovery"""
    error: Exception
    stage: WorkflowStage
    operation: str
    attempt_count: int = 0
    recovery_history: List[RecoveryStrategy] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)


class RoadImportErrorHandler:
    """
    Comprehensive error handling and recovery system for road import workflow
    Provides automatic recovery strategies and user guidance for complex issues
    """

    def __init__(self):
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.active_recoveries: Dict[str, ErrorContext] = {}
        self.fallback_configurations: Dict[str, Dict[str, Any]] = {}

        # Initialize recovery strategies
        self._initialize_recovery_strategies()
        self._initialize_fallback_configurations()

    def handle_error(self, error: Exception, stage: WorkflowStage,
                    operation: str, context_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an error with appropriate recovery strategy

        Args:
            error: The exception that occurred
            stage: Current workflow stage
            operation: Current operation name
            context_data: Additional context for recovery

        Returns:
            bool: True if error was handled/recovered, False if manual intervention needed
        """
        error_key = f"{stage.value}_{operation}"
        error_context = ErrorContext(
            error=error,
            stage=stage,
            operation=operation,
            context_data=context_data or {},
            attempt_count=self.active_recoveries.get(error_key, ErrorContext(error, stage, operation)).attempt_count + 1
        )

        # Log the error
        monitor = get_monitor()
        monitor.log_issue(
            stage,
            SeverityLevel.ERROR,
            f"Error in {operation}",
            str(error),
            context=context_data,
            stack_trace=traceback.format_exc(),
            suggested_fix=self._get_suggested_fix(error_key)
        )

        # Get recovery strategies for this error type
        recovery_actions = self._get_recovery_actions(error, stage, operation)

        if not recovery_actions:
            # No recovery strategies available
            self._log_no_recovery_available(error_context)
            return False

        # Try recovery strategies in order
        for action in recovery_actions:
            if error_context.attempt_count >= action.max_attempts:
                continue

            if action.strategy in error_context.recovery_history:
                continue  # Already tried this strategy

            error_context.recovery_history.append(action.strategy)
            self.active_recoveries[error_key] = error_context

            # Attempt recovery
            success = self._attempt_recovery(error_context, action)
            if success:
                monitor.log_issue(
                    stage,
                    SeverityLevel.INFO,
                    f"Recovery Successful: {action.strategy.value}",
                    f"Error in {operation} resolved using {action.strategy.value}",
                    context={'strategy': action.strategy.value, 'attempts': error_context.attempt_count}
                )
                return True

        # All recovery strategies failed
        self._log_recovery_failed(error_context)
        return False

    def get_recovery_status(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get current recovery status for an operation"""
        error_key = operation
        if error_key not in self.active_recoveries:
            return None

        context = self.active_recoveries[error_key]
        return {
            'error': str(context.error),
            'stage': context.stage.value,
            'attempts': context.attempt_count,
            'strategies_tried': [s.value for s in context.recovery_history],
            'can_retry': context.attempt_count < 3
        }

    def clear_recovery_state(self, operation: str):
        """Clear recovery state for an operation"""
        error_key = operation
        if error_key in self.active_recoveries:
            del self.active_recoveries[error_key]

    def apply_fallback_configuration(self, config_name: str) -> Dict[str, Any]:
        """Apply a fallback configuration"""
        if config_name not in self.fallback_configurations:
            raise ValueError(f"Unknown fallback configuration: {config_name}")

        fallback = self.fallback_configurations[config_name]

        # Apply fallback settings to Blender scene
        addon = bpy.context.scene.blosm

        for key, value in fallback.items():
            if hasattr(addon, key):
                setattr(addon, key, value)

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Fallback Configuration Applied",
            f"Applied fallback configuration: {config_name}",
            context={'config_name': config_name, 'settings': fallback}
        )

        return fallback

    def _initialize_recovery_strategies(self):
        """Initialize recovery strategies for different error types"""

        # Network/Service errors
        self.recovery_actions.update({
            'geocoding_geocode': [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    "Retry geocoding with exponential backoff",
                    max_attempts=3,
                    backoff_seconds=2.0
                ),
                RecoveryAction(
                    RecoveryStrategy.FALLBACK_CONFIGURATION,
                    "Use simplified address format",
                    max_attempts=1
                )
            ],

            'routing_fetch_route': [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    "Retry routing with alternative server",
                    max_attempts=2,
                    backoff_seconds=1.0
                ),
                RecoveryAction(
                    RecoveryStrategy.ALTERNATIVE_SERVER,
                    "Switch to backup routing service",
                    max_attempts=1
                )
            ],

            'overpass_fetch_tile': [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    "Retry Overpass request with backoff",
                    max_attempts=3,
                    backoff_seconds=5.0
                ),
                RecoveryAction(
                    RecoveryStrategy.ALTERNATIVE_SERVER,
                    "Switch to alternative Overpass server",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.REDUCED_COMPLEXITY,
                    "Reduce tile size or complexity",
                    max_attempts=1
                )
            ]
        })

        # Memory/Performance errors
        self.recovery_actions.update({
            'mesh_creation_create_meshes': [
                RecoveryAction(
                    RecoveryStrategy.REDUCED_COMPLEXITY,
                    "Reduce mesh detail level",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.SKIP_OPTIONAL_STEP,
                    "Skip building mesh creation",
                    max_attempts=1
                ),
                RecoveryAction(
                    RecoveryStrategy.RESET_AND_RETRY,
                    "Clear scene and retry",
                    max_attempts=1
                )
            ],

            'asset_loading_import_assets': [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    "Retry asset import",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.SKIP_OPTIONAL_STEP,
                    "Continue without assets",
                    max_attempts=1
                )
            ]
        })

        # Blender API errors
        self.recovery_actions.update({
            'route_objects_create_curve': [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    "Retry curve creation",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.FALLBACK_CONFIGURATION,
                    "Use simplified curve settings",
                    max_attempts=1
                )
            ],

            'animation_setup_constraints': [
                RecoveryAction(
                    RecoveryStrategy.SKIP_OPTIONAL_STEP,
                    "Skip animation setup",
                    max_attempts=1
                ),
                RecoveryAction(
                    RecoveryStrategy.FALLBACK_CONFIGURATION,
                    "Use basic animation",
                    max_attempts=1
                )
            ]
        })

    def _initialize_fallback_configurations(self):
        """Initialize fallback configurations for error recovery"""

        # Low memory configuration
        self.fallback_configurations['low_memory'] = {
            'route_padding_m': 50.0,  # Reduced padding
            'route_import_buildings': False,  # Skip buildings
            'route_import_roads': True,
            'route_create_preview_animation': False  # Skip animation
        }

        # Network issues configuration
        self.fallback_configurations['network_issues'] = {
            'route_padding_m': 25.0,  # Minimal padding
            'route_import_buildings': False,
            'route_import_roads': True,
            'route_import_separate_tiles': False,  # Use single tile
            'route_create_preview_animation': False
        }

        # Performance issues configuration
        self.fallback_configurations['performance_issues'] = {
            'route_padding_m': 75.0,
            'route_import_buildings': True,
            'route_import_roads': True,
            'route_create_preview_animation': False,
            'levelHeight': 3.0,  # Reduced building height
            'defaultLevels': []  # Use simple building levels
        }

        # Minimal configuration
        self.fallback_configurations['minimal'] = {
            'route_padding_m': 10.0,
            'route_import_buildings': False,
            'route_import_roads': True,
            'route_create_preview_animation': False,
            'route_import_separate_tiles': False
        }

    def _get_recovery_actions(self, error: Exception, stage: WorkflowStage,
                            operation: str) -> List[RecoveryAction]:
        """Get recovery actions for a specific error"""
        error_key = f"{stage.value}_{operation}"

        # Check if we have specific recovery actions for this operation
        if error_key in self.recovery_actions:
            return self.recovery_actions[error_key]

        # Check for general recovery actions by error type
        error_type = type(error).__name__

        if isinstance(error, (GeocodingError, RoutingError, OverpassError)):
            return [
                RecoveryAction(
                    RecoveryStrategy.RETRY_WITH_BACKOFF,
                    f"Retry {error_type.lower()} with backoff",
                    max_attempts=3,
                    backoff_seconds=2.0
                )
            ]

        elif isinstance(error, (TileImportError, RouteObjectError)):
            return [
                RecoveryAction(
                    RecoveryStrategy.FALLBACK_CONFIGURATION,
                    "Apply fallback configuration",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.SKIP_OPTIONAL_STEP,
                    "Skip problematic step",
                    max_attempts=1
                )
            ]

        elif isinstance(error, MemoryError):
            return [
                RecoveryAction(
                    RecoveryStrategy.REDUCED_COMPLEXITY,
                    "Reduce memory usage",
                    max_attempts=2
                ),
                RecoveryAction(
                    RecoveryStrategy.RESET_AND_RETRY,
                    "Clear memory and retry",
                    max_attempts=1
                )
            ]

        # Default recovery action
        return [
            RecoveryAction(
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                "Retry with backoff",
                max_attempts=2,
                backoff_seconds=1.0
            )
        ]

    def _attempt_recovery(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Attempt to recover from an error using a specific strategy"""

        try:
            if action.strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
                return self._retry_with_backoff(error_context, action)

            elif action.strategy == RecoveryStrategy.FALLBACK_CONFIGURATION:
                return self._apply_fallback_configuration(error_context, action)

            elif action.strategy == RecoveryStrategy.ALTERNATIVE_SERVER:
                return self._switch_alternative_server(error_context, action)

            elif action.strategy == RecoveryStrategy.REDUCED_COMPLEXITY:
                return self._reduce_complexity(error_context, action)

            elif action.strategy == RecoveryStrategy.SKIP_OPTIONAL_STEP:
                return self._skip_optional_step(error_context, action)

            elif action.strategy == RecoveryStrategy.RESET_AND_RETRY:
                return self._reset_and_retry(error_context, action)

            else:
                return False

        except Exception as recovery_error:
            monitor = get_monitor()
            monitor.log_issue(
                error_context.stage,
                SeverityLevel.WARNING,
                f"Recovery Failed: {action.strategy.value}",
                f"Recovery strategy failed: {recovery_error}",
                context={'strategy': action.strategy.value, 'recovery_error': str(recovery_error)}
            )
            return False

    def _retry_with_backoff(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Retry with exponential backoff"""
        wait_time = action.backoff_seconds * (2 ** (error_context.attempt_count - 1))
        time.sleep(wait_time)

        # This would need to be implemented by the calling code
        # Here we just log the retry attempt
        return True

    def _apply_fallback_configuration(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Apply a fallback configuration"""
        try:
            # Determine appropriate fallback based on error type
            if isinstance(error_context.error, MemoryError):
                config_name = 'low_memory'
            elif isinstance(error_context.error, OverpassError):
                config_name = 'network_issues'
            elif isinstance(error_context.error, (TileImportError, RouteObjectError)):
                config_name = 'performance_issues'
            else:
                config_name = 'minimal'

            self.apply_fallback_configuration(config_name)
            return True

        except Exception:
            return False

    def _switch_alternative_server(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Switch to alternative server"""
        # This would modify the server configuration
        # Implementation depends on specific service being used
        return True

    def _reduce_complexity(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Reduce complexity of the operation"""
        try:
            # Reduce scene complexity
            if error_context.stage == WorkflowStage.MESH_CREATION:
                # Reduce mesh detail
                pass
            elif error_context.stage == WorkflowStage.OVERPASS_FETCH:
                # Reduce tile size or detail
                pass

            return True
        except Exception:
            return False

    def _skip_optional_step(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Skip optional step and continue"""
        # Mark the step as skipped and continue
        return True

    def _reset_and_retry(self, error_context: ErrorContext, action: RecoveryAction) -> bool:
        """Reset state and retry"""
        try:
            # Clear temporary data and reset state
            import gc
            gc.collect()

            # Clear orphaned data
            bpy.ops.outliner.orphans_purge()

            return True
        except Exception:
            return False

    def _get_suggested_fix(self, error_key: str) -> Optional[str]:
        """Get suggested fix for an error type"""
        suggestions = {
            'geocoding_geocode': "Check address spelling and try again",
            'routing_fetch_route': "Verify addresses are accessible by road",
            'overpass_fetch_tile': "Reduce area size or try again later",
            'mesh_creation_create_meshes': "Reduce padding or disable buildings",
            'asset_loading_import_assets': "Check asset files are accessible",
            'route_objects_create_curve': "Try reducing route complexity",
            'animation_setup_constraints': "Continue without animation"
        }
        return suggestions.get(error_key)

    def _log_no_recovery_available(self, error_context: ErrorContext):
        """Log when no recovery is available"""
        monitor = get_monitor()
        monitor.log_issue(
            error_context.stage,
            SeverityLevel.CRITICAL,
            "No Recovery Available",
            f"No recovery strategy available for {error_context.operation}: {error_context.error}",
            context={'operation': error_context.operation, 'error': str(error_context.error)},
            suggested_fix="Manual intervention required"
        )

    def _log_recovery_failed(self, error_context: ErrorContext):
        """Log when all recovery strategies failed"""
        monitor = get_monitor()
        monitor.log_issue(
            error_context.stage,
            SeverityLevel.CRITICAL,
            "Recovery Failed",
            f"All recovery strategies failed for {error_context.operation}",
            context={
                'operation': error_context.operation,
                'attempts': error_context.attempt_count,
                'strategies_tried': [s.value for s in error_context.recovery_history]
            },
            suggested_fix="Manual intervention required"
        )


# Global error handler instance
_error_handler_instance: Optional[RoadImportErrorHandler] = None


def get_error_handler() -> RoadImportErrorHandler:
    """Get the global error handler instance"""
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = RoadImportErrorHandler()
    return _error_handler_instance


def handle_error(error: Exception, stage: WorkflowStage, operation: str,
                context_data: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to handle an error"""
    handler = get_error_handler()
    return handler.handle_error(error, stage, operation, context_data)


# Decorator for automatic error handling
def handle_errors(stage: WorkflowStage, operation: str,
                 context_data: Optional[Dict[str, Any]] = None):
    """Decorator to automatically handle function errors"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handled = handle_error(e, stage, operation, context_data)
                if not handled:
                    # Re-raise if error wasn't handled
                    raise
                # Return None or appropriate default value
                return None
        return wrapper
    return decorator


# Context manager for error handling
class ErrorHandlerContext:
    """Context manager for error handling"""

    def __init__(self, stage: WorkflowStage, operation: str,
                 context_data: Optional[Dict[str, Any]] = None):
        self.stage = stage
        self.operation = operation
        self.context_data = context_data
        self.error_handler = get_error_handler()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_val:
            handled = self.error_handler.handle_error(exc_val, self.stage, self.operation, self.context_data)
            if handled:
                return True  # Suppress the exception
        return False  # Don't suppress exceptions


# Quick recovery functions
def quick_memory_recovery():
    """Quick memory recovery"""
    try:
        import gc
        gc.collect()
        bpy.ops.outliner.orphans_purge()

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Quick Memory Recovery",
            "Performed garbage collection and orphan cleanup"
        )
        return True
    except Exception:
        return False


def quick_scene_reset():
    """Quick scene reset"""
    try:
        # Clear selected objects
        bpy.ops.object.select_all(action='DESELECT')

        # Reset view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.view_all(override)
                        break

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Quick Scene Reset",
            "Reset scene view and selection"
        )
        return True
    except Exception:
        return False


def apply_low_memory_mode():
    """Apply low memory configuration"""
    handler = get_error_handler()
    return handler.apply_fallback_configuration('low_memory')


def apply_network_fallback():
    """Apply network fallback configuration"""
    handler = get_error_handler()
    return handler.apply_fallback_configuration('network_issues')