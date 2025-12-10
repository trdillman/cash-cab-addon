"""
Road Import Workflow Debug Monitor
Comprehensive monitoring and debugging system for CashCab road import workflow
Provides real-time error detection, performance analysis, and troubleshooting solutions
"""

from __future__ import annotations

import time
import traceback
import gc
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

import bpy
from .config import DEFAULT_CONFIG
from .exceptions import (
    RouteServiceError, GeocodingError, RoutingError, OverpassError,
    TileImportError, RouteObjectError, RouteStateError
)


class WorkflowStage(Enum):
    """Workflow stages for monitoring"""
    INITIALIZATION = "initialization"
    GEOCODING = "geocoding"
    ROUTING = "routing"
    TILE_PLANNING = "tile_planning"
    OVERPASS_FETCH = "overpass_fetch"
    OSM_PARSING = "osm_parsing"
    MESH_CREATION = "mesh_creation"
    ROUTE_OBJECTS = "route_objects"
    ASSET_LOADING = "asset_loading"
    ANIMATION_SETUP = "animation_setup"
    FINALIZATION = "finalization"
    COMPLETE = "complete"


class SeverityLevel(Enum):
    """Issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Single performance metric"""
    stage: WorkflowStage
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def finish(self, success: bool = True, error_message: Optional[str] = None):
        """Mark metric as completed"""
        self.end_time = time.perf_counter()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.success = success
        self.error_message = error_message

        # Capture system metrics
        try:
            process = psutil.Process()
            self.memory_mb = process.memory_info().rss / 1024 / 1024
            self.cpu_percent = process.cpu_percent()
        except Exception:
            pass


@dataclass
class IssueReport:
    """Issue report for debugging"""
    stage: WorkflowStage
    severity: SeverityLevel
    title: str
    description: str
    timestamp: float = field(default_factory=time.time)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None
    auto_fix_available: bool = False


class RoadImportMonitor:
    """
    Comprehensive monitoring system for road import workflow
    Tracks performance, detects issues, and provides debugging insights
    """

    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.issues: List[IssueReport] = []
        self.active_metrics: Dict[str, PerformanceMetric] = {}
        self.workflow_start_time = 0.0
        self.memory_baseline_mb = 0.0
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.checkpoints: Dict[str, Any] = {}

        # Performance thresholds
        self.thresholds = {
            'overpass_timeout_s': DEFAULT_CONFIG.api.overpass_timeout_s,
            'overpass_tile_time_s': 60.0,
            'osm_parse_time_s': 10.0,
            'mesh_creation_time_s': 5.0,
            'memory_growth_mb': 500.0,
            'cpu_usage_percent': 80.0
        }

    def start_monitoring(self):
        """Start performance monitoring"""
        self.workflow_start_time = time.perf_counter()
        self.monitoring_active = True

        # Capture baseline metrics
        try:
            process = psutil.Process()
            self.memory_baseline_mb = process.memory_info().rss / 1024 / 1024
        except Exception:
            self.memory_baseline_mb = 0.0

        # Start background monitoring thread
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()

        self.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            "Monitoring Started",
            f"Road import monitoring initiated. Baseline memory: {self.memory_baseline_mb:.1f}MB"
        )

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)

        total_time = time.perf_counter() - self.workflow_start_time
        self.log_issue(
            WorkflowStage.COMPLETE,
            SeverityLevel.INFO,
            "Monitoring Complete",
            f"Road import monitoring complete. Total time: {total_time:.2f}s"
        )

    def start_metric(self, stage: WorkflowStage, operation: str, **metadata) -> str:
        """Start tracking a performance metric"""
        metric_id = f"{stage.value}_{operation}_{int(time.time() * 1000)}"
        metric = PerformanceMetric(
            stage=stage,
            operation=operation,
            start_time=time.perf_counter(),
            metadata=metadata
        )
        self.active_metrics[metric_id] = metric
        return metric_id

    def finish_metric(self, metric_id: str, success: bool = True,
                     error_message: Optional[str] = None, **additional_metadata):
        """Finish tracking a performance metric"""
        if metric_id not in self.active_metrics:
            return

        metric = self.active_metrics.pop(metric_id)
        metric.metadata.update(additional_metadata)
        metric.finish(success, error_message)
        self.metrics.append(metric)

        # Check for performance issues
        self._check_performance_issues(metric)

    def log_issue(self, stage: WorkflowStage, severity: SeverityLevel,
                  title: str, description: str, context: Optional[Dict[str, Any]] = None,
                  stack_trace: Optional[str] = None, suggested_fix: Optional[str] = None):
        """Log an issue for debugging"""
        issue = IssueReport(
            stage=stage,
            severity=severity,
            title=title,
            description=description,
            context=context or {},
            stack_trace=stack_trace,
            suggested_fix=suggested_fix,
            auto_fix_available=self._can_auto_fix(title)
        )
        self.issues.append(issue)

        # Auto-fix critical issues
        if severity == SeverityLevel.CRITICAL and issue.auto_fix_available:
            self._attempt_auto_fix(issue)

    def set_checkpoint(self, name: str, data: Any):
        """Set a checkpoint for debugging"""
        self.checkpoints[name] = {
            'data': data,
            'timestamp': time.time(),
            'stage': self._get_current_stage()
        }

    def get_checkpoint(self, name: str) -> Optional[Any]:
        """Get checkpoint data"""
        checkpoint = self.checkpoints.get(name)
        return checkpoint['data'] if checkpoint else None

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_time = time.perf_counter() - self.workflow_start_time if self.workflow_start_time else 0

        stage_metrics = {}
        for metric in self.metrics:
            stage = metric.stage.value
            if stage not in stage_metrics:
                stage_metrics[stage] = []
            stage_metrics[stage].append(metric)

        stage_summary = {}
        for stage, stage_mets in stage_metrics.items():
            durations = [m.duration_ms for m in stage_mets if m.duration_ms]
            if durations:
                stage_summary[stage] = {
                    'count': len(stage_mets),
                    'total_time_ms': sum(durations),
                    'avg_time_ms': sum(durations) / len(durations),
                    'max_time_ms': max(durations),
                    'success_rate': sum(1 for m in stage_mets if m.success) / len(stage_mets)
                }

        return {
            'total_time_s': total_time,
            'stage_summary': stage_summary,
            'total_metrics': len(self.metrics),
            'issues_count': len(self.issues),
            'memory_baseline_mb': self.memory_baseline_mb
        }

    def get_issues_report(self, severity_filter: Optional[SeverityLevel] = None) -> List[IssueReport]:
        """Get filtered issues report"""
        if severity_filter:
            return [issue for issue in self.issues if issue.severity == severity_filter]
        return self.issues.copy()

    def export_debug_data(self, filepath: Optional[Path] = None) -> Path:
        """Export complete debug data for analysis"""
        if filepath is None:
            timestamp = int(time.time())
            filepath = Path(__file__).parent.parent.parent / "debug" / f"road_import_debug_{timestamp}.json"

        filepath.parent.mkdir(parents=True, exist_ok=True)

        debug_data = {
            'timestamp': time.time(),
            'performance_summary': self.get_performance_summary(),
            'metrics': [
                {
                    'stage': m.stage.value,
                    'operation': m.operation,
                    'duration_ms': m.duration_ms,
                    'memory_mb': m.memory_mb,
                    'cpu_percent': m.cpu_percent,
                    'success': m.success,
                    'error_message': m.error_message,
                    'metadata': m.metadata
                }
                for m in self.metrics
            ],
            'issues': [
                {
                    'stage': i.stage.value,
                    'severity': i.severity.value,
                    'title': i.title,
                    'description': i.description,
                    'timestamp': i.timestamp,
                    'context': i.context,
                    'suggested_fix': i.suggested_fix,
                    'auto_fix_available': i.auto_fix_available
                }
                for i in self.issues
            ],
            'checkpoints': {
                name: {
                    'timestamp': data['timestamp'],
                    'stage': data['stage'].value if isinstance(data['stage'], WorkflowStage) else data['stage']
                }
                for name, data in self.checkpoints.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(debug_data, f, indent=2)

        return filepath

    def _background_monitor(self):
        """Background monitoring thread"""
        while self.monitoring_active:
            try:
                # Check memory usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_growth = memory_mb - self.memory_baseline_mb

                if memory_growth > self.thresholds['memory_growth_mb']:
                    self.log_issue(
                        WorkflowStage.INITIALIZATION,
                        SeverityLevel.WARNING,
                        "High Memory Usage",
                        f"Memory usage increased by {memory_growth:.1f}MB from baseline",
                        context={'memory_mb': memory_mb, 'growth_mb': memory_growth},
                        suggested_fix="Consider reducing tile count or optimizing mesh complexity"
                    )

                # Check CPU usage
                cpu_percent = process.cpu_percent(interval=1.0)
                if cpu_percent > self.thresholds['cpu_usage_percent']:
                    self.log_issue(
                        WorkflowStage.INITIALIZATION,
                        SeverityLevel.WARNING,
                        "High CPU Usage",
                        f"CPU usage at {cpu_percent:.1f}%",
                        context={'cpu_percent': cpu_percent}
                    )

                time.sleep(5.0)  # Check every 5 seconds

            except Exception:
                # Don't let monitoring errors crash the workflow
                pass

    def _check_performance_issues(self, metric: PerformanceMetric):
        """Check metric for performance issues"""
        if not metric.duration_ms:
            return

        duration_s = metric.duration_ms / 1000.0

        # Check specific stage thresholds
        if metric.stage == WorkflowStage.OVERPASS_FETCH:
            if duration_s > self.thresholds['overpass_tile_time_s']:
                self.log_issue(
                    metric.stage,
                    SeverityLevel.WARNING,
                    "Slow Overpass Tile",
                    f"Overpass tile took {duration_s:.1f}s (threshold: {self.thresholds['overpass_tile_time_s']}s)",
                    context={'duration_s': duration_s, 'operation': metric.operation},
                    suggested_fix="Consider reducing bbox size or checking Overpass server load"
                )

        elif metric.stage == WorkflowStage.OSM_PARSING:
            if duration_s > self.thresholds['osm_parse_time_s']:
                self.log_issue(
                    metric.stage,
                    SeverityLevel.WARNING,
                    "Slow OSM Parsing",
                    f"OSM parsing took {duration_s:.1f}s (threshold: {self.thresholds['osm_parse_time_s']}s)",
                    context={'duration_s': duration_s},
                    suggested_fix="Check OSM data size and complexity"
                )

        elif metric.stage == WorkflowStage.MESH_CREATION:
            if duration_s > self.thresholds['mesh_creation_time_s']:
                self.log_issue(
                    metric.stage,
                    SeverityLevel.WARNING,
                    "Slow Mesh Creation",
                    f"Mesh creation took {duration_s:.1f}s (threshold: {self.thresholds['mesh_creation_time_s']}s)",
                    context={'duration_s': duration_s},
                    suggested_fix="Consider optimizing mesh complexity or reducing building count"
                )

    def _can_auto_fix(self, title: str) -> bool:
        """Check if an issue can be auto-fixed"""
        auto_fixable_titles = [
            "High Memory Usage",
            "High CPU Usage",
            "Slow Overpass Tile",
            "Asset Loading Error",
            "Material Assignment Error"
        ]
        return title in auto_fixable_titles

    def _attempt_auto_fix(self, issue: IssueReport):
        """Attempt to auto-fix an issue"""
        try:
            if issue.title == "High Memory Usage":
                # Force garbage collection
                gc.collect()
                bpy.ops.outliner.orphans_purge()

                self.log_issue(
                    issue.stage,
                    SeverityLevel.INFO,
                    "Auto-fix Applied",
                    "Memory cleanup performed: garbage collection and orphan purge"
                )

            elif issue.title == "Asset Loading Error":
                # Retry asset loading with fallback
                bpy.ops.blosm.import_assets()

                self.log_issue(
                    issue.stage,
                    SeverityLevel.INFO,
                    "Auto-fix Applied",
                    "Asset loading retry performed"
                )

        except Exception as e:
            self.log_issue(
                issue.stage,
                SeverityLevel.WARNING,
                "Auto-fix Failed",
                f"Auto-fix for '{issue.title}' failed: {e}",
                context={'original_issue': issue.title}
            )

    def _get_current_stage(self) -> WorkflowStage:
        """Determine current workflow stage from active metrics"""
        if not self.active_metrics:
            return WorkflowStage.INITIALIZATION

        # Return the stage of the most recent active metric
        latest_metric = max(self.active_metrics.values(), key=lambda m: m.start_time)
        return latest_metric.stage


# Global monitor instance
_monitor_instance: Optional[RoadImportMonitor] = None


def get_monitor() -> RoadImportMonitor:
    """Get the global monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = RoadImportMonitor()
    return _monitor_instance


def reset_monitor():
    """Reset the global monitor instance"""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop_monitoring()
    _monitor_instance = RoadImportMonitor()


# Decorator for automatic metric tracking
def monitor_performance(stage: WorkflowStage, operation: str, **metadata):
    """Decorator to automatically monitor function performance"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            metric_id = monitor.start_metric(stage, operation, **metadata)

            try:
                result = func(*args, **kwargs)
                monitor.finish_metric(metric_id, success=True)
                return result
            except Exception as e:
                monitor.finish_metric(
                    metric_id,
                    success=False,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
                raise

        return wrapper
    return decorator


# Context manager for monitoring
class MonitorContext:
    """Context manager for monitoring code blocks"""

    def __init__(self, stage: WorkflowStage, operation: str, **metadata):
        self.stage = stage
        self.operation = operation
        self.metadata = metadata
        self.monitor = get_monitor()
        self.metric_id = None

    def __enter__(self):
        self.metric_id = self.monitor.start_metric(self.stage, self.operation, **self.metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        stack_trace = traceback.format_exc() if exc_type else None

        self.monitor.finish_metric(self.metric_id, success, error_message)

        if not success:
            self.monitor.log_issue(
                self.stage,
                SeverityLevel.ERROR,
                f"{self.operation} Failed",
                error_message or "Unknown error",
                stack_trace=stack_trace,
                context=self.metadata
            )

        return False  # Don't suppress exceptions


# Quick debugging functions
def debug_memory_usage(label: str = "Memory Check"):
    """Quick memory usage debugging"""
    try:
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        monitor = get_monitor()
        monitor.log_issue(
            WorkflowStage.INITIALIZATION,
            SeverityLevel.INFO,
            f"Memory Debug: {label}",
            f"Current memory usage: {memory_mb:.1f}MB",
            context={'memory_mb': memory_mb}
        )
        return memory_mb
    except Exception:
        return 0.0


def debug_object_count(label: str = "Object Count"):
    """Quick object count debugging"""
    counts = {
        'total_objects': len(bpy.data.objects),
        'meshes': len(bpy.data.meshes),
        'materials': len(bpy.data.materials),
        'collections': len(bpy.data.collections)
    }

    monitor = get_monitor()
    monitor.log_issue(
        WorkflowStage.INITIALIZATION,
        SeverityLevel.INFO,
        f"Object Count: {label}",
        f"Objects: {counts['total_objects']}, Meshes: {counts['meshes']}, Materials: {counts['materials']}",
        context=counts
    )

    return counts


def debug_scene_state(label: str = "Scene State"):
    """Quick scene state debugging"""
    scene = bpy.context.scene

    state = {
        'frame_current': scene.frame_current,
        'frame_start': scene.frame_start,
        'frame_end': scene.frame_end,
        'render_engine': scene.render.engine,
        'objects_selected': len([obj for obj in scene.objects if obj.select_get()])
    }

    monitor = get_monitor()
    monitor.log_issue(
        WorkflowStage.INITIALIZATION,
        SeverityLevel.INFO,
        f"Scene State: {label}",
        f"Frame: {state['frame_current']}/{state['frame_start']}-{state['frame_end']}, Selected: {state['objects_selected']}",
        context=state
    )

    return state