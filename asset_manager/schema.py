"""
Asset schema definitions for BLOSM Asset Manager

Defines Python dataclasses for asset configuration that map to JSON structure.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple


class AssetType(Enum):
    """Types of assets that can be registered"""
    CAR = "car"
    MARKER = "marker"
    BUILDING = "building"
    ROAD = "road"
    MATERIAL = "material"
    NODE_GROUP = "node_group"
    WORLD = "world"
    LIGHT = "light"
    COLLECTION = "collection"


@dataclass
class TransformData:
    """3D transform data for asset placement"""
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_euler: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    def to_dict(self) -> Dict[str, List[float]]:
        """Convert to dictionary for JSON serialization"""
        return {
            "location": list(self.location),
            "rotation_euler": list(self.rotation_euler),
            "scale": list(self.scale)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransformData':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            location=tuple(data.get("location", [0.0, 0.0, 0.0])),
            rotation_euler=tuple(data.get("rotation_euler", [0.0, 0.0, 0.0])),
            scale=tuple(data.get("scale", [1.0, 1.0, 1.0]))
        )


@dataclass
class AssetDefinition:
    """Definition of an asset with all configuration"""

    # Core identification
    id: str
    name: str
    type: AssetType

    # File references
    blend_file: str  # Relative path to .blend file
    datablock_name: str  # Name within the .blend file

    # Default transform
    default_transform: TransformData = field(default_factory=TransformData)

    # Additional metadata
    category: str = "default"
    description: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

    # Collection settings
    collection_name: Optional[str] = None
    hide_viewport: bool = False
    hide_render: bool = False

    # Custom properties
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "blend_file": self.blend_file,
            "datablock_name": self.datablock_name,
            "default_transform": self.default_transform.to_dict(),
            "category": self.category,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "collection_name": self.collection_name,
            "hide_viewport": self.hide_viewport,
            "hide_render": self.hide_render,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetDefinition':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=AssetType(data["type"]),
            blend_file=data["blend_file"],
            datablock_name=data["datablock_name"],
            default_transform=TransformData.from_dict(data.get("default_transform", {})),
            category=data.get("category", "default"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            tags=data.get("tags", []),
            collection_name=data.get("collection_name"),
            hide_viewport=data.get("hide_viewport", False),
            hide_render=data.get("hide_render", False),
            properties=data.get("properties", {})
        )
