"""
Backup System for ValidoAI

This module provides comprehensive backup functionality including:
- Database backup and restoration
- File system backup
- Configuration backup
- Automated backup scheduling
- Backup verification and integrity checks
"""

import os
import shutil
import zipfile
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path
import hashlib
import tarfile
import gzip

logger = logging.getLogger(__name__)


class BackupManager:
    """Main backup management class"""
    
    def __init__(self, backup_dir: str = "backups", max_backups: int = 10):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.backup_dir / "database").mkdir(exist_ok=True)
        (self.backup_dir / "files").mkdir(exist_ok=True)
        (self.backup_dir / "config").mkdir(exist_ok=True)
        (self.backup_dir / "logs").mkdir(exist_ok=True)
    
    def create_full_backup(self, db_path: str, files_to_backup: List[str] = None) -> Dict:
        """Create a complete backup of the system"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"backup_{timestamp}"
        
        backup_info = {
            'backup_id': backup_id,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'type': 'full',
            'components': [],
            'status': 'in_progress',
            'errors': []
        }
        
        try:
            # Database backup
            db_backup_path = self._backup_database(db_path, backup_id)
            if db_backup_path:
                backup_info['components'].append({
                    'type': 'database',
                    'path': str(db_backup_path),
                    'size': os.path.getsize(db_backup_path)
                })
            
            # Files backup
            if files_to_backup:
                files_backup_path = self._backup_files(files_to_backup, backup_id)
                if files_backup_path:
                    backup_info['components'].append({
                        'type': 'files',
                        'path': str(files_backup_path),
                        'size': os.path.getsize(files_backup_path)
                    })
            
            # Configuration backup
            config_backup_path = self._backup_config(backup_id)
            if config_backup_path:
                backup_info['components'].append({
                    'type': 'config',
                    'path': str(config_backup_path),
                    'size': os.path.getsize(config_backup_path)
                })
            
            # Logs backup
            logs_backup_path = self._backup_logs(backup_id)
            if logs_backup_path:
                backup_info['components'].append({
                    'type': 'logs',
                    'path': str(logs_backup_path),
                    'size': os.path.getsize(logs_backup_path)
                })
            
            # Create backup manifest
            manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            backup_info['status'] = 'completed'
            backup_info['manifest_path'] = str(manifest_path)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            logger.info(f"Full backup completed: {backup_id}")
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['errors'].append(str(e))
            logger.error(f"Backup failed: {str(e)}")
        
        return backup_info
    
    def _backup_database(self, db_path: str, backup_id: str) -> Optional[Path]:
        """Backup SQLite database"""
        try:
            if not os.path.exists(db_path):
                logger.warning(f"Database file not found: {db_path}")
                return None
            
            backup_path = self.backup_dir / "database" / f"{backup_id}_database.db"
            
            # Create a copy of the database
            shutil.copy2(db_path, backup_path)
            
            # Verify backup integrity
            if self._verify_database_backup(back_path):
                logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                logger.error("Database backup verification failed")
                backup_path.unlink(missing_ok=True)
                return None
                
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            return None
    
    def _verify_database_backup(self, backup_path: Path) -> bool:
        """Verify database backup integrity"""
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if we can read the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            return len(tables) > 0
            
        except Exception as e:
            logger.error(f"Database verification failed: {str(e)}")
            return False
    
    def _backup_files(self, files_to_backup: List[str], backup_id: str) -> Optional[Path]:
        """Backup specified files"""
        try:
            backup_path = self.backup_dir / "files" / f"{backup_id}_files.tar.gz"
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in files_to_backup:
                    if os.path.exists(file_path):
                        tar.add(file_path, arcname=os.path.basename(file_path))
                    else:
                        logger.warning(f"File not found: {file_path}")
            
            logger.info(f"Files backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Files backup failed: {str(e)}")
            return None
    
    def _backup_config(self, backup_id: str) -> Optional[Path]:
        """Backup configuration files"""
        try:
            config_files = [
                '.env',
                'config.py',
                'requirements.txt',
                'app.py'
            ]
            
            backup_path = self.backup_dir / "config" / f"{backup_id}_config.tar.gz"
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for config_file in config_files:
                    if os.path.exists(config_file):
                        tar.add(config_file)
                    else:
                        logger.warning(f"Config file not found: {config_file}")
            
            logger.info(f"Config backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Config backup failed: {str(e)}")
            return None
    
    def _backup_logs(self, backup_id: str) -> Optional[Path]:
        """Backup log files"""
        try:
            log_dir = Path("logs")
            if not log_dir.exists():
                logger.warning("Logs directory not found")
                return None
            
            backup_path = self.backup_dir / "logs" / f"{backup_id}_logs.tar.gz"
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for log_file in log_dir.glob("*.log"):
                    tar.add(log_file, arcname=f"logs/{log_file.name}")
            
            logger.info(f"Logs backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Logs backup failed: {str(e)}")
            return None
    
    def restore_backup(self, backup_id: str, restore_path: str = None) -> Dict:
        """Restore from a backup"""
        restore_info = {
            'backup_id': backup_id,
            'restored_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'errors': [],
            'restored_components': []
        }
        
        try:
            # Load backup manifest
            manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
            if not manifest_path.exists():
                raise FileNotFoundError(f"Backup manifest not found: {backup_id}")
            
            with open(manifest_path, 'r') as f:
                backup_info = json.load(f)
            
            # Restore each component
            for component in backup_info.get('components', []):
                try:
                    if component['type'] == 'database':
                        self._restore_database(component['path'], restore_path)
                        restore_info['restored_components'].append('database')
                    
                    elif component['type'] == 'files':
                        self._restore_files(component['path'], restore_path)
                        restore_info['restored_components'].append('files')
                    
                    elif component['type'] == 'config':
                        self._restore_config(component['path'], restore_path)
                        restore_info['restored_components'].append('config')
                    
                    elif component['type'] == 'logs':
                        self._restore_logs(component['path'], restore_path)
                        restore_info['restored_components'].append('logs')
                
                except Exception as e:
                    restore_info['errors'].append(f"Failed to restore {component['type']}: {str(e)}")
            
            restore_info['status'] = 'completed' if not restore_info['errors'] else 'partial'
            
        except Exception as e:
            restore_info['status'] = 'failed'
            restore_info['errors'].append(str(e))
        
        return restore_info
    
    def _restore_database(self, backup_path: str, restore_path: str = None):
        """Restore database from backup"""
        target_path = restore_path or "data/sqlite/app.db"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Restore database
        shutil.copy2(backup_path, target_path)
        logger.info(f"Database restored to: {target_path}")
    
    def _restore_files(self, backup_path: str, restore_path: str = None):
        """Restore files from backup"""
        target_dir = restore_path or "."
        
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(target_dir)
        
        logger.info(f"Files restored to: {target_dir}")
    
    def _restore_config(self, backup_path: str, restore_path: str = None):
        """Restore configuration from backup"""
        target_dir = restore_path or "."
        
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(target_dir)
        
        logger.info(f"Configuration restored to: {target_dir}")
    
    def _restore_logs(self, backup_path: str, restore_path: str = None):
        """Restore logs from backup"""
        target_dir = restore_path or "logs"
        os.makedirs(target_dir, exist_ok=True)
        
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(target_dir)
        
        logger.info(f"Logs restored to: {target_dir}")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for manifest_file in self.backup_dir.glob("*_manifest.json"):
            try:
                with open(manifest_file, 'r') as f:
                    backup_info = json.load(f)
                
                # Calculate total size
                total_size = sum(comp.get('size', 0) for comp in backup_info.get('components', []))
                backup_info['total_size'] = total_size
                
                backups.append(backup_info)
            
            except Exception as e:
                logger.error(f"Error reading manifest {manifest_file}: {str(e)}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return backups
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """Get detailed information about a specific backup"""
        manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                backup_info = json.load(f)
            
            # Calculate total size
            total_size = sum(comp.get('size', 0) for comp in backup_info.get('components', []))
            backup_info['total_size'] = total_size
            
            return backup_info
        
        except Exception as e:
            logger.error(f"Error reading backup info: {str(e)}")
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup"""
        try:
            # Load manifest to get component paths
            manifest_path = self.backup_dir / f"{backup_id}_manifest.json"
            if not manifest_path.exists():
                return False
            
            with open(manifest_path, 'r') as f:
                backup_info = json.load(f)
            
            # Delete all component files
            for component in backup_info.get('components', []):
                component_path = Path(component['path'])
                if component_path.exists():
                    component_path.unlink()
            
            # Delete manifest
            manifest_path.unlink()
            
            logger.info(f"Backup deleted: {backup_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting backup: {str(e)}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove old backups to stay within the limit"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            # Remove oldest backups
            backups_to_remove = backups[self.max_backups:]
            
            for backup in backups_to_remove:
                self.delete_backup(backup['backup_id'])
    
    def verify_backup_integrity(self, backup_id: str) -> Dict:
        """Verify the integrity of a backup"""
        verification_result = {
            'backup_id': backup_id,
            'verified_at': datetime.now().isoformat(),
            'status': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        try:
            backup_info = self.get_backup_info(backup_id)
            if not backup_info:
                verification_result['status'] = 'failed'
                verification_result['errors'].append("Backup not found")
                return verification_result
            
            # Check if all component files exist
            for component in backup_info.get('components', []):
                component_path = Path(component['path'])
                if not component_path.exists():
                    verification_result['errors'].append(f"Component file missing: {component_path}")
                else:
                    # Check file size
                    actual_size = component_path.stat().st_size
                    expected_size = component.get('size', 0)
                    
                    if actual_size != expected_size:
                        verification_result['warnings'].append(
                            f"Size mismatch for {component['type']}: expected {expected_size}, got {actual_size}"
                        )
            
            # Verify database integrity if present
            for component in backup_info.get('components', []):
                if component['type'] == 'database':
                    if not self._verify_database_backup(Path(component['path'])):
                        verification_result['errors'].append("Database integrity check failed")
            
            if verification_result['errors']:
                verification_result['status'] = 'failed'
            elif verification_result['warnings']:
                verification_result['status'] = 'warning'
            else:
                verification_result['status'] = 'passed'
        
        except Exception as e:
            verification_result['status'] = 'failed'
            verification_result['errors'].append(str(e))
        
        return verification_result


# Global backup manager instance
backup_manager = BackupManager()
