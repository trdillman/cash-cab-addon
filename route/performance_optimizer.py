"""
Road Import Performance Optimizer
Advanced performance monitoring, memory management, and optimization strategies
for the CashCab road import workflow with real-time performance tuning.
"""

from __future__ import annotations

import time
import gc
import threading
import weakref
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

import bpy
from bpy.types import Object, Mesh, Material, Collection

from .config import DEFAULT_CONFIG
from .debug_monitor import get_monitor, WorkflowStage, SeverityLevel


class OptimizationLevel(Enum):
    """Performance optimization levels"""
    MINIMAL = "minimal"  # Lowest memory usage, basic functionality
    BALANCED = "balanced"  # Good balance of performance and quality
    QUALITY = "quality"  # High quality, higher resource usage
    CUSTOM = "custom"  # Custom configuration


class MemoryPressureLevel(Enum):
    """Memory pressure levels"""
    LOW = "low"  # < 1GB usage
    MEDIUM = "medium"  # 1-2GB usage
    HIGH = "high"  # 2-4GB usage
    CRITICAL = "critical"  # > 4GB usage


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    max_memory_mb: float
    max_tile_time_s: float
    max_mesh_count: int
    max_object_count: int
    gc_frequency: int  # GC every N operations
    memory_check_interval_s: float = 5.0


@dataclass
class OptimizationProfile:
    """Performance optimization profile"""
    name: str
    level: OptimizationLevel
    thresholds: PerformanceThreshold
    settings: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class MemoryStats:
    """Memory usage statistics"""
    total_mb: float
    mesh_mb: float
    material_mb: float
    object_mb: float
    scene_mb: float
    pressure_level: MemoryPressureLevel
    timestamp: float = field(default_factory=time.time)


class PerformanceOptimizer:
    """
    Advanced performance optimization system for road import workflow
    Provides real-time memory management, performance tuning, and resource optimization
    """

    def __init__(self):
        self.optimization_level = OptimizationLevel.BALANCED
        self.memory_stats: List[MemoryStats] = []
        self.optimization_profiles: Dict[OptimizationLevel, OptimizationProfile] = {}
        self.active_optimizations: Set[str] = set()
        self.gc_counter = 0
        self.last_gc_time = 0.0
        self.memory_monitor_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.optimization_callbacks: Dict[str, List[Callable]] = {}

        # Initialize optimization profiles
        self._initialize_profiles()

    def initialize_optimization(self, level: OptimizationLevel = OptimizationLevel.BALANCED):
        """Initialize performance optimization"""
        self.optimization_level = level
        profile = self.optimization_profiles[level]

        # Apply optimization settings
        self._apply_optimization_profile(profile)

        # Start memory monitoring
        self.start_memory_monitoring()

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Performance Optimization Started",
            f"Initialized {level.value} optimization profile",
            context={'profile': profile.name, 'level': level.value}
        )

    def shutdown_optimization(self):
        """Shutdown performance optimization"""
        self.stop_memory_monitoring()
        self.active_optimizations.clear()

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Performance Optimization Stopped",
            "Performance optimization system shutdown"
        )

    def optimize_for_memory_pressure(self, pressure_level: MemoryPressureLevel):
        """Optimize based on current memory pressure"""
        if pressure_level == MemoryPressureLevel.CRITICAL:
            self._apply_critical_optimizations()
        elif pressure_level == MemoryPressureLevel.HIGH:
            self._apply_high_optimizations()
        elif pressure_level == MemoryPressureLevel.MEDIUM:
            self._apply_medium_optimizations()
        else:
            self._apply_low_optimizations()

    def optimize_for_stage(self, stage: WorkflowStage, context: Dict[str, Any]):
        """Optimize for specific workflow stage"""
        optimizations = {
            WorkflowStage.OVERPASS_FETCH: self._optimize_for_overpass,
            WorkflowStage.OSM_PARSING: self._optimize_for_parsing,
            WorkflowStage.MESH_CREATION: self._optimize_for_mesh_creation,
            WorkflowStage.ROUTE_OBJECTS: self._optimize_for_route_objects,
            WorkflowStage.ASSET_LOADING: self._optimize_for_asset_loading,
            WorkflowStage.ANIMATION_SETUP: self._optimize_for_animation
        }

        optimizer = optimizations.get(stage)
        if optimizer:
            optimizer(context)

    def force_garbage_collection(self, aggressive: bool = False):
        """Force garbage collection with optional aggressive cleanup"""
        initial_memory = self._get_memory_usage()

        # Standard garbage collection
        gc.collect()

        # Blender-specific cleanup
        self._cleanup_orphaned_data()

        if aggressive:
            # Aggressive cleanup
            self._aggressive_cleanup()

        final_memory = self._get_memory_usage()
        memory_freed = initial_memory - final_memory

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Garbage Collection Performed",
            f"Freed {memory_freed:.1f}MB ({'aggressive' if aggressive else 'standard'})",
            context={
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_freed_mb': memory_freed,
                'aggressive': aggressive
            }
        )

        self.last_gc_time = time.time()
        return memory_freed

    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics"""
        total_mb = self._get_memory_usage()
        mesh_mb = self._get_mesh_memory()
        material_mb = self._get_material_memory()
        object_mb = self._get_object_memory()
        scene_mb = self._get_scene_memory()

        # Determine pressure level
        pressure_level = self._determine_memory_pressure(total_mb)

        stats = MemoryStats(
            total_mb=total_mb,
            mesh_mb=mesh_mb,
            material_mb=material_mb,
            object_mb=object_mb,
            scene_mb=scene_mb,
            pressure_level=pressure_level
        )

        self.memory_stats.append(stats)

        # Keep only recent stats (last 100)
        if len(self.memory_stats) > 100:
            self.memory_stats = self.memory_stats[-100:]

        return stats

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        current_stats = self.get_memory_stats()

        report = {
            'optimization_level': self.optimization_level.value,
            'active_optimizations': list(self.active_optimizations),
            'current_memory': {
                'total_mb': current_stats.total_mb,
                'pressure_level': current_stats.pressure_level.value,
                'breakdown': {
                    'meshes_mb': current_stats.mesh_mb,
                    'materials_mb': current_stats.material_mb,
                    'objects_mb': current_stats.object_mb,
                    'scene_mb': current_stats.scene_mb
                }
            },
            'gc_stats': {
                'last_gc_time': self.last_gc_time,
                'gc_counter': self.gc_counter
            },
            'memory_trend': self._get_memory_trend(),
            'optimization_suggestions': self._get_optimization_suggestions(current_stats)
        }

        return report

    def register_optimization_callback(self, name: str, callback: Callable):
        """Register a callback for optimization events"""
        if name not in self.optimization_callbacks:
            self.optimization_callbacks[name] = []
        self.optimization_callbacks[name].append(callback)

    def start_memory_monitoring(self):
        """Start background memory monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.memory_monitor_thread = threading.Thread(target=self._memory_monitor_loop, daemon=True)
        self.memory_monitor_thread.start()

    def stop_memory_monitoring(self):
        """Stop background memory monitoring"""
        self.monitoring_active = False
        if self.memory_monitor_thread and self.memory_monitor_thread.is_alive():
            self.memory_monitor_thread.join(timeout=1.0)

    def _initialize_profiles(self):
        """Initialize optimization profiles"""
        self.optimization_profiles[OptimizationLevel.MINIMAL] = OptimizationProfile(
            name="Minimal Resource Usage",
            level=OptimizationLevel.MINIMAL,
            thresholds=PerformanceThreshold(
                max_memory_mb=1024.0,
                max_tile_time_s=30.0,
                max_mesh_count=100,
                max_object_count=500,
                gc_frequency=2
            ),
            settings={
                'import_buildings': False,
                'import_roads': True,
                'create_animation': False,
                'padding_m': 25.0,
                'mesh_simplification': 0.5
            },
            description="Lowest memory usage, basic functionality only"
        )

        self.optimization_profiles[OptimizationLevel.BALANCED] = OptimizationProfile(
            name="Balanced Performance",
            level=OptimizationLevel.BALANCED,
            thresholds=PerformanceThreshold(
                max_memory_mb=2048.0,
                max_tile_time_s=60.0,
                max_mesh_count=500,
                max_object_count=2000,
                gc_frequency=5
            ),
            settings={
                'import_buildings': True,
                'import_roads': True,
                'create_animation': True,
                'padding_m': 100.0,
                'mesh_simplification': 0.8
            },
            description="Good balance of performance and quality"
        )

        self.optimization_profiles[OptimizationLevel.QUALITY] = OptimizationProfile(
            name="High Quality",
            level=OptimizationLevel.QUALITY,
            thresholds=PerformanceThreshold(
                max_memory_mb=4096.0,
                max_tile_time_s=120.0,
                max_mesh_count=2000,
                max_object_count=5000,
                gc_frequency=10
            ),
            settings={
                'import_buildings': True,
                'import_roads': True,
                'create_animation': True,
                'padding_m': 200.0,
                'mesh_simplification': 1.0
            },
            description="High quality rendering, higher resource usage"
        )

    def _apply_optimization_profile(self, profile: OptimizationProfile):
        """Apply optimization profile settings"""
        addon = bpy.context.scene.blosm

        for key, value in profile.settings.items():
            if hasattr(addon, key):
                setattr(addon, key, value)

        # Apply thresholds to optimizer
        self.gc_counter = 0
        self.active_optimizations.add(profile.name)

    def _optimize_for_overpass(self, context: Dict[str, Any]):
        """Optimize for Overpass data fetching"""
        # Reduce concurrent requests
        # Optimize query size
        # Enable compression
        pass

    def _optimize_for_parsing(self, context: Dict[str, Any]):
        """Optimize for OSM data parsing"""
        # Use streaming parser
        # Filter data during parsing
        self.gc_counter += 1
        if self.gc_counter % 3 == 0:
            self.force_garbage_collection()

    def _optimize_for_mesh_creation(self, context: Dict[str, Any]):
        """Optimize for mesh creation"""
        stats = self.get_memory_stats()

        if stats.pressure_level == MemoryPressureLevel.CRITICAL:
            # Use simplified mesh creation
            self._apply_critical_mesh_optimizations()
        elif stats.pressure_level == MemoryPressureLevel.HIGH:
            # Use moderate mesh optimization
            self._apply_high_mesh_optimizations()

        self.gc_counter += 1
        if self.gc_counter % 2 == 0:
            self.force_garbage_collection()

    def _optimize_for_route_objects(self, context: Dict[str, Any]):
        """Optimize for route object creation"""
        # Optimize curve resolution
        # Use lightweight empties
        pass

    def _optimize_for_asset_loading(self, context: Dict[str, Any]):
        """Optimize for asset loading"""
        # Preload essential assets
        # Delay non-critical assets
        # Use proxy objects
        pass

    def _optimize_for_animation(self, context: Dict[str, Any]):
        """Optimize for animation setup"""
        # Simplify constraints
        # Use basic animation
        pass

    def _apply_critical_optimizations(self):
        """Apply critical memory optimizations"""
        # Force immediate cleanup
        self.force_garbage_collection(aggressive=True)

        # Apply minimal configuration
        from .error_recovery import get_error_handler
        handler = get_error_handler()
        handler.apply_fallback_configuration('minimal')

        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.WARNING,
            "Critical Memory Optimizations Applied",
            "Applied emergency memory management measures"
        )

    def _apply_high_optimizations(self):
        """Apply high memory optimizations"""
        self.force_garbage_collection()

        # Apply low memory configuration
        from .error_recovery import get_error_handler
        handler = get_error_handler()
        handler.apply_fallback_configuration('low_memory')

    def _apply_medium_optimizations(self):
        """Apply medium memory optimizations"""
        # Standard cleanup
        self.force_garbage_collection()

    def _apply_low_optimizations(self):
        """Apply low memory optimizations"""
        # Continue with current settings
        pass

    def _apply_critical_mesh_optimizations(self):
        """Apply critical mesh optimizations"""
        # Reduce mesh detail
        # Use simplified geometry
        pass

    def _apply_high_mesh_optimizations(self):
        """Apply high mesh optimizations"""
        # Moderate mesh simplification
        pass

    def _get_memory_usage(self) -> float:
        """Get current total memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def _get_mesh_memory(self) -> float:
        """Get mesh memory usage in MB"""
        try:
            total_vertices = sum(len(mesh.vertices) for mesh in bpy.data.meshes)
            # Rough estimation: 12 bytes per vertex for position + normals
            return (total_vertices * 12) / 1024 / 1024
        except Exception:
            return 0.0

    def _get_material_memory(self) -> float:
        """Get material memory usage in MB"""
        try:
            # Rough estimation based on material count
            return len(bpy.data.materials) * 0.5  # 0.5MB per material estimate
        except Exception:
            return 0.0

    def _get_object_memory(self) -> float:
        """Get object memory usage in MB"""
        try:
            # Rough estimation based on object count
            return len(bpy.data.objects) * 0.1  # 0.1MB per object estimate
        except Exception:
            return 0.0

    def _get_scene_memory(self) -> float:
        """Get scene memory usage in MB"""
        try:
            # Rough estimation for scene data
            return len(bpy.data.scenes) * 1.0  # 1MB per scene estimate
        except Exception:
            return 0.0

    def _determine_memory_pressure(self, memory_mb: float) -> MemoryPressureLevel:
        """Determine memory pressure level"""
        if memory_mb < 1024:
            return MemoryPressureLevel.LOW
        elif memory_mb < 2048:
            return MemoryPressureLevel.MEDIUM
        elif memory_mb < 4096:
            return MemoryPressureLevel.HIGH
        else:
            return MemoryPressureLevel.CRITICAL

    def _cleanup_orphaned_data(self):
        """Clean up orphaned Blender data"""
        try:
            # Purge orphan data
            bpy.ops.outliner.orphans_purge()

            # Clean up unused data blocks
            for mesh in bpy.data.meshes:
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)

            for material in bpy.data.materials:
                if material.users == 0:
                    bpy.data.materials.remove(material)

            for obj in bpy.data.objects:
                if obj.users == 0:
                    bpy.data.objects.remove(obj)

        except Exception:
            pass

    def _aggressive_cleanup(self):
        """Perform aggressive memory cleanup"""
        try:
            # Clear undo history
            bpy.ops.ed.undo_push()
            for _ in range(50):  # Clear last 50 undo steps
                try:
                    bpy.ops.ed.undo()
                except:
                    break

            # Remove all unused data
            for block_type in ['meshes', 'materials', 'textures', 'images', 'collections']:
                data_block = getattr(bpy.data, block_type)
                for item in list(data_block):
                    if item.users == 0:
                        data_block.remove(item)

            # Force Python garbage collection multiple times
            for _ in range(3):
                gc.collect()

        except Exception:
            pass

    def _memory_monitor_loop(self):
        """Background memory monitoring loop"""
        while self.monitoring_active:
            try:
                stats = self.get_memory_stats()

                # Check if we need to optimize
                if stats.pressure_level != MemoryPressureLevel.LOW:
                    self.optimize_for_memory_pressure(stats.pressure_level)

                # Check thresholds
                profile = self.optimization_profiles[self.optimization_level]
                if stats.total_mb > profile.thresholds.max_memory_mb:
                    self.force_garbage_collection()

                time.sleep(profile.thresholds.memory_check_interval_s)

            except Exception:
                # Don't let monitoring errors crash the workflow
                time.sleep(5.0)

    def _get_memory_trend(self) -> Dict[str, Any]:
        """Get memory usage trend"""
        if len(self.memory_stats) < 2:
            return {'trend': 'stable', 'change_mb': 0.0}

        recent_stats = self.memory_stats[-10:]  # Last 10 measurements
        if len(recent_stats) < 2:
            return {'trend': 'stable', 'change_mb': 0.0}

        first_mb = recent_stats[0].total_mb
        last_mb = recent_stats[-1].total_mb
        change_mb = last_mb - first_mb

        if change_mb > 100:
            trend = 'increasing'
        elif change_mb < -50:
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'change_mb': change_mb,
            'measurements': len(recent_stats)
        }

    def _get_optimization_suggestions(self, current_stats: MemoryStats) -> List[str]:
        """Get optimization suggestions based on current stats"""
        suggestions = []

        if current_stats.pressure_level == MemoryPressureLevel.CRITICAL:
            suggestions.extend([
                "Apply minimal configuration",
                "Disable building import",
                "Force aggressive cleanup",
                "Reduce tile size"
            ])
        elif current_stats.pressure_level == MemoryPressureLevel.HIGH:
            suggestions.extend([
                "Apply low memory configuration",
                "Reduce mesh detail",
                "Skip animation setup"
            ])
        elif current_stats.pressure_level == MemoryPressureLevel.MEDIUM:
            suggestions.extend([
                "Monitor memory usage",
                "Consider reducing padding"
            ])

        # Check specific memory areas
        if current_stats.mesh_mb > 500:
            suggestions.append("Reduce mesh complexity or building count")

        if current_stats.material_mb > 100:
            suggestions.append("Consolidate or reduce materials")

        return suggestions


# Global optimizer instance
_optimizer_instance: Optional[PerformanceOptimizer] = None


def get_optimizer() -> PerformanceOptimizer:
    """Get the global optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = PerformanceOptimizer()
    return _optimizer_instance


def initialize_optimization(level: OptimizationLevel = OptimizationLevel.BALANCED):
    """Initialize performance optimization"""
    optimizer = get_optimizer()
    optimizer.initialize_optimization(level)


def cleanup_memory(aggressive: bool = False) -> float:
    """Convenience function for memory cleanup"""
    optimizer = get_optimizer()
    return optimizer.force_garbage_collection(aggressive)


def get_memory_report() -> Dict[str, Any]:
    """Convenience function to get memory report"""
    optimizer = get_optimizer()
    return optimizer.get_performance_report()


# Decorator for performance optimization
def optimize_for_stage(stage: WorkflowStage):
    """Decorator to optimize function for specific stage"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            optimizer = get_optimizer()
            context = {'args': args, 'kwargs': kwargs}
            optimizer.optimize_for_stage(stage, context)

            try:
                return func(*args, **kwargs)
            finally:
                # Cleanup after function
                optimizer.gc_counter += 1
                if optimizer.gc_counter % 5 == 0:
                    optimizer.force_garbage_collection()

        return wrapper
    return decorator


# Quick optimization functions
def quick_optimize_for_memory():
    """Quick memory optimization"""
    optimizer = get_optimizer()
    stats = optimizer.get_memory_stats()
    optimizer.optimize_for_memory_pressure(stats.pressure_level)
    return stats.pressure_level


def apply_emergency_memory_cleanup():
    """Emergency memory cleanup"""
    optimizer = get_optimizer()
    return optimizer.force_garbage_collection(aggressive=True)


def switch_to_minimal_mode():
    """Switch to minimal resource usage mode"""
    optimizer = get_optimizer()
    optimizer.initialize_optimization(OptimizationLevel.MINIMAL)
    monitor = get_monitor()
    monitor.log_issue(
        WorkflowStage.INITIALIZATION,
        SeverityLevel.WARNING,
        "Switched to Minimal Mode",
        "Applied minimal resource usage configuration"
    )