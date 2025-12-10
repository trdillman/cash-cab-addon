"""
Asset File Manager for CashCab Blender Addon

Handles file operations for asset updates including backup, restore,
integrity validation, and cleanup operations.
"""

import bpy
import shutil
import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta


class AssetFileError(Exception):
    """Raised when asset file operations fail"""
    pass


class AssetFileManager:
    """
    Manages file operations for CashCab asset updates.

    Provides safe backup/restore operations, file integrity validation,
    and cleanup functionality for asset .blend files.
    """

    def __init__(self, assets_dir: Path = None):
        self.assets_dir = assets_dir or Path(__file__).parent.parent / "assets"
        self.backup_dir = self.assets_dir.parent / "backup" / "asset_files"
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.ensure_backup_directory()

    def ensure_backup_directory(self) -> None:
        """Ensure backup directory structure exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, asset_file: Path, description: str = "") -> str:
        """
        Create a timestamped backup of an asset file.

        Args:
            asset_file: Path to the asset file to backup
            description: Optional description for the backup

        Returns:
            str: Backup ID for tracking purposes
        """
        if not asset_file.exists():
            raise AssetFileError(f"Asset file does not exist: {asset_file}")

        # Generate backup ID and filename
        timestamp = datetime.now()
        backup_id = f"{asset_file.stem}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}"
        backup_filename = f"{backup_id}{asset_file.suffix}"
        backup_path = self.backup_dir / backup_filename

        try:
            # Copy the file
            shutil.copy2(str(asset_file), str(backup_path))

            # Calculate file hash for integrity checking
            file_hash = self._calculate_file_hash(asset_file)

            # Create backup metadata
            backup_metadata = {
                "backup_id": backup_id,
                "original_file": str(asset_file.relative_to(self.assets_dir.parent)),
                "backup_path": str(backup_path),
                "timestamp": timestamp.isoformat(),
                "file_size": asset_file.stat().st_size,
                "file_hash": file_hash,
                "description": description
            }

            # Save metadata
            self._save_backup_metadata(backup_metadata)

            print(f"[AssetFileManager] ✓ Created backup: {backup_id}")
            return backup_id

        except Exception as e:
            # Clean up failed backup attempt
            if backup_path.exists():
                backup_path.unlink()
            raise AssetFileError(f"Failed to create backup for {asset_file}: {e}")

    def restore_backup(self, backup_id: str, target_path: Path = None) -> bool:
        """
        Restore a backup to its original location or specified target.

        Args:
            backup_id: ID of the backup to restore
            target_path: Optional custom target path (defaults to original location)

        Returns:
            bool: True if restore was successful
        """
        try:
            # Load backup metadata
            metadata = self._load_backup_metadata(backup_id)
            if not metadata:
                raise AssetFileError(f"Backup not found: {backup_id}")

            backup_path = Path(metadata["backup_path"])
            if not backup_path.exists():
                raise AssetFileError(f"Backup file missing: {backup_path}")

            # Determine target path
            if target_path is None:
                # Convert relative path to absolute path
                original_file = Path(metadata["original_file"])
                if not original_file.is_absolute():
                    # The path is relative to assets_dir.parent, so reconstruct it
                    target_path = self.assets_dir.parent / original_file
                else:
                    target_path = original_file

            # Validate backup integrity
            current_hash = self._calculate_file_hash(backup_path)
            if current_hash != metadata["file_hash"]:
                raise AssetFileError(f"Backup integrity check failed for {backup_id}")

            # Create backup of current file before restore
            if target_path.exists():
                pre_restore_backup = f"{target_path.stem}_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}{target_path.suffix}"
                shutil.copy2(str(target_path), str(target_path.parent / pre_restore_backup))
                print(f"[AssetFileManager] Created pre-restore backup: {pre_restore_backup}")

            # Restore the file
            shutil.copy2(str(backup_path), str(target_path))

            print(f"[AssetFileManager] ✓ Restored backup {backup_id} to {target_path}")
            return True

        except Exception as e:
            print(f"[AssetFileManager] ✗ Failed to restore backup {backup_id}: {e}")
            return False

    def validate_asset_file(self, asset_file: Path) -> Tuple[bool, str]:
        """
        Validate the integrity of an asset file.

        Args:
            asset_file: Path to the asset file to validate

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            if not asset_file.exists():
                return False, f"File does not exist: {asset_file}"

            if asset_file.suffix != '.blend':
                return False, f"File is not a .blend file: {asset_file}"

            # Check file size (basic integrity check)
            file_size = asset_file.stat().st_size
            if file_size == 0:
                return False, f"File is empty: {asset_file}"

            # Try to load the blend file in headless mode to validate structure
            try:
                # Store current state
                original_scene = bpy.context.scene

                # Create temporary scene for validation
                temp_scene = bpy.data.scenes.new(name="TempValidationScene")
                bpy.context.window.scene = temp_scene

                # Try to append from the file (basic structure validation)
                with bpy.data.libraries.load(str(asset_file), link=True) as (data_from, data_to):
                    # Just check if we can read the file structure
                    _ = len(data_from.objects) if hasattr(data_from, 'objects') else 0
                    _ = len(data_from.materials) if hasattr(data_from, 'materials') else 0
                    _ = len(data_from.node_groups) if hasattr(data_from, 'node_groups') else 0

                # Clean up
                bpy.context.window.scene = original_scene
                bpy.data.scenes.remove(temp_scene)

            except Exception as e:
                return False, f"Blend file structure validation failed: {e}"

            return True, f"Asset file is valid: {asset_file} ({file_size} bytes)"

        except Exception as e:
            return False, f"Validation error: {e}"

    def list_backups(self, asset_file: Path = None, days_old: int = None) -> List[Dict[str, Any]]:
        """
        List available backups.

        Args:
            asset_file: Optional filter by original asset file
            days_old: Optional filter by maximum age in days

        Returns:
            List of backup metadata dictionaries
        """
        try:
            if not self.metadata_file.exists():
                return []

            with open(self.metadata_file, 'r') as f:
                all_metadata = json.load(f)

            backups = []
            cutoff_date = datetime.now() - timedelta(days=days_old) if days_old else None

            for backup_id, metadata in all_metadata.items():
                # Filter by asset file if specified
                if asset_file:
                    original_file = Path(metadata.get("original_file", ""))
                    if original_file.name != asset_file.name:
                        continue

                # Filter by age if specified
                if cutoff_date:
                    backup_date = datetime.fromisoformat(metadata.get("timestamp", ""))
                    if backup_date < cutoff_date:
                        continue

                # Check if backup file still exists
                backup_path = Path(metadata.get("backup_path", ""))
                if backup_path.exists():
                    backups.append(metadata)

            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return backups

        except Exception as e:
            print(f"[AssetFileManager] Error listing backups: {e}")
            return []

    def cleanup_old_backups(self, days_to_keep: int = 30, asset_file: Path = None) -> int:
        """
        Clean up old backup files.

        Args:
            days_to_keep: Number of days to keep backups
            asset_file: Optional filter by specific asset file

        Returns:
            int: Number of backups cleaned up
        """
        try:
            old_backups = self.list_backups(asset_file=asset_file, days_old=days_to_keep)
            cleaned_count = 0

            # Load current metadata
            all_metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    all_metadata = json.load(f)

            for backup in old_backups:
                backup_id = backup["backup_id"]
                backup_path = Path(backup["backup_path"])

                try:
                    # Remove backup file
                    if backup_path.exists():
                        backup_path.unlink()

                    # Remove from metadata
                    if backup_id in all_metadata:
                        del all_metadata[backup_id]

                    cleaned_count += 1
                    print(f"[AssetFileManager] Cleaned up old backup: {backup_id}")

                except Exception as e:
                    print(f"[AssetFileManager] Failed to cleanup backup {backup_id}: {e}")

            # Save updated metadata
            if cleaned_count > 0:
                with open(self.metadata_file, 'w') as f:
                    json.dump(all_metadata, f, indent=2)

            print(f"[AssetFileManager] ✓ Cleaned up {cleaned_count} old backups")
            return cleaned_count

        except Exception as e:
            print(f"[AssetFileManager] Error during cleanup: {e}")
            return 0

    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific backup.

        Args:
            backup_id: ID of the backup

        Returns:
            Dict with backup metadata or None if not found
        """
        return self._load_backup_metadata(backup_id)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _save_backup_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save backup metadata to the metadata file."""
        try:
            # Load existing metadata
            all_metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    all_metadata = json.load(f)

            # Add new backup metadata
            backup_id = metadata["backup_id"]
            all_metadata[backup_id] = metadata

            # Save updated metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(all_metadata, f, indent=2)

        except Exception as e:
            print(f"[AssetFileManager] Error saving backup metadata: {e}")

    def _load_backup_metadata(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Load backup metadata by ID."""
        try:
            if not self.metadata_file.exists():
                return None

            with open(self.metadata_file, 'r') as f:
                all_metadata = json.load(f)

            return all_metadata.get(backup_id)

        except Exception as e:
            print(f"[AssetFileManager] Error loading backup metadata for {backup_id}: {e}")
            return None

    def get_asset_files(self) -> List[Path]:
        """Get list of all asset .blend files."""
        try:
            if not self.assets_dir.exists():
                return []

            asset_files = []
            for file_path in self.assets_dir.glob("*.blend"):
                asset_files.append(file_path)

            return sorted(asset_files)

        except Exception as e:
            print(f"[AssetFileManager] Error getting asset files: {e}")
            return []