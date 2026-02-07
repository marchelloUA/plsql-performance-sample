import os
import shutil
import subprocess
import tarfile
import datetime
import json
from typing import Dict, Any, List, Optional
from unittest.mock import Mock

# Mock database modules if not available
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

class DatabaseBackupAutomation:
    """Automated database backup and recovery system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_dir = config.get('backup_dir', '/var/backups/databases')
        self.retention_days = config.get('retention_days', 30)
        self.log_file = config.get('log_file', '/var/log/database_backups.log')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_oracle_database(self, connection_string: str, backup_name: str = None) -> Dict[str, Any]:
        """Backup Oracle database using expdp utility"""
        try:
            if not backup_name:
                backup_name = f"oracle_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            # Generate expdp command
            expdp_command = [
                'expdp',
                connection_string,
                f'DIRECTORY={backup_path}',
                f'DUMPFILE={backup_name}.dmp',
                f'LOGFILE={backup_name}.log',
                'FULL=Y',
                'COMPRESSION=YES'
            ]
            
            # Execute backup
            start_time = datetime.datetime.now()
            result = subprocess.run(expdp_command, capture_output=True, text=True, timeout=3600)
            end_time = datetime.datetime.now()
            
            backup_info = {
                'backup_type': 'oracle',
                'backup_name': backup_name,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'backup_path': backup_path,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'file_size': self._get_directory_size(backup_path)
            }
            
            # Log backup result
            self._log_backup(backup_info)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return backup_info
            
        except Exception as e:
            error_info = {
                'backup_type': 'oracle',
                'backup_name': backup_name,
                'error': str(e),
                'success': False
            }
            self._log_backup(error_info)
            return error_info
    
    def backup_sql_server_database(self, server: str, database: str, 
                                 username: str, password: str, 
                                 backup_name: str = None) -> Dict[str, Any]:
        """Backup SQL Server database using sqlcmd"""
        try:
            if not backup_name:
                backup_name = f"sqlserver_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            # Generate backup script
            backup_script = f"""
BACKUP DATABASE [{database}]
TO DISK = N'{backup_path}/{backup_name}.bak'
WITH NOFORMAT, NOINIT, 
NAME = N'{database}_Full Database Backup', 
SKIP, NOREWIND, NOUNLOAD, 
COMPRESSION, STATS = 10, CHECKSUM, 
DESCRIPTION = N'Automated backup of {database}', 
MEDIANAME = N'{database}_Backup', 
MEDIADESCRIPTION = N'SQL Server Backup', 
SINGLE_USER, NORECOVERY
GO
"""
            
            # Execute backup using sqlcmd
            start_time = datetime.datetime.now()
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE=master;"
                f"UID={username};"
                f"PWD={password}"
            )
            
            connection = pyodbc.connect(conn_str)
            cursor = connection.cursor()
            cursor.execute(backup_script)
            connection.commit()
            cursor.close()
            connection.close()
            
            end_time = datetime.datetime.now()
            
            backup_info = {
                'backup_type': 'sqlserver',
                'backup_name': backup_name,
                'database': database,
                'server': server,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'backup_path': backup_path,
                'success': True,
                'backup_file': f'{backup_path}/{backup_name}.bak'
            }
            
            # Log backup result
            self._log_backup(backup_info)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return backup_info
            
        except Exception as e:
            error_info = {
                'backup_type': 'sqlserver',
                'backup_name': backup_name,
                'database': database,
                'error': str(e),
                'success': False
            }
            self._log_backup(error_info)
            return error_info
    
    def backup_filesystem(self, source_path: str, backup_name: str = None) -> Dict[str, Any]:
        """Backup filesystem directory using tar"""
        try:
            if not backup_name:
                backup_name = f"filesystem_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            # Create tar archive
            tar_path = os.path.join(backup_path, f'{backup_name}.tar.gz')
            start_time = datetime.datetime.now()
            
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(source_path, arcname=os.path.basename(source_path))
            
            end_time = datetime.datetime.now()
            
            backup_info = {
                'backup_type': 'filesystem',
                'backup_name': backup_name,
                'source_path': source_path,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'backup_path': backup_path,
                'success': True,
                'backup_file': tar_path,
                'file_size': os.path.getsize(tar_path)
            }
            
            # Log backup result
            self._log_backup(backup_info)
            
            # Clean up old backups
            self._cleanup_old_backups()
            
            return backup_info
            
        except Exception as e:
            error_info = {
                'backup_type': 'filesystem',
                'backup_name': backup_name,
                'source_path': source_path,
                'error': str(e),
                'success': False
            }
            self._log_backup(error_info)
            return error_info
    
    def schedule_backup(self, backup_config: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule automated backup using cron"""
        try:
            backup_type = backup_config.get('type')
            schedule = backup_config.get('schedule')
            
            if not backup_type or not schedule:
                return {'success': False, 'error': 'Backup type and schedule are required'}
            
            # Generate cron job
            cron_job = f"{schedule} cd /home/ymarkiv/git/pl_sql_sample/plsql-performance-sample && python backup_automation.py --backup-type {backup_type}"
            
            # Add backup-specific parameters
            if backup_type == 'oracle':
                cron_job += f" --connection-string {backup_config.get('connection_string', '')}"
            elif backup_type == 'sqlserver':
                cron_job += f" --server {backup_config.get('server', '')} --database {backup_config.get('database', '')} --username {backup_config.get('username', '')} --password {backup_config.get('password', '')}"
            elif backup_type == 'filesystem':
                cron_job += f" --source-path {backup_config.get('source_path', '')}"
            
            # Write cron job
            cron_file = f"/tmp/database_backup_cron"
            with open(cron_file, 'w') as f:
                f.write(cron_job + '\n')
            
            # Install cron job
            subprocess.run(['crontab', cron_file])
            os.remove(cron_file)
            
            return {
                'success': True,
                'message': f'Backup scheduled with cron: {schedule}',
                'cron_job': cron_job
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restore_oracle_database(self, backup_name: str, connection_string: str) -> Dict[str, Any]:
        """Restore Oracle database from backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                return {'success': False, 'error': f'Backup {backup_name} not found'}
            
            # Generate impdp command
            impdp_command = [
                'impdp',
                connection_string,
                f'DIRECTORY={backup_path}',
                f'DUMPFILE={backup_name}.dmp',
                f'LOGFILE={backup_name}_restore.log',
                'FULL=Y',
                'REUSE_DATAFILES=YES'
            ]
            
            # Execute restore
            start_time = datetime.datetime.now()
            result = subprocess.run(impdp_command, capture_output=True, text=True, timeout=7200)
            end_time = datetime.datetime.now()
            
            restore_info = {
                'restore_type': 'oracle',
                'backup_name': backup_name,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
            
            self._log_backup(restore_info)
            return restore_info
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _log_backup(self, backup_info: Dict[str, Any]):
        """Log backup information"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(backup_info) + '\n')
        except Exception as e:
            print(f"Failed to log backup: {e}")
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            
            for backup_name in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                if os.path.isdir(backup_path):
                    # Check if backup is older than retention period
                    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(backup_path))
                    
                    if creation_time < cutoff_date:
                        shutil.rmtree(backup_path)
                        print(f"Removed old backup: {backup_name}")
                        
        except Exception as e:
            print(f"Failed to cleanup old backups: {e}")
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            print(f"Failed to get directory size: {e}")
        return total_size
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get status of all backups"""
        try:
            backups = []
            
            for backup_name in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                if os.path.isdir(backup_path):
                    backup_info = {
                        'name': backup_name,
                        'path': backup_path,
                        'size': self._get_directory_size(backup_path),
                        'created': datetime.datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat(),
                        'type': 'unknown'
                    }
                    
                    # Determine backup type
                    if any(f.endswith('.dmp') for f in os.listdir(backup_path)):
                        backup_info['type'] = 'oracle'
                    elif any(f.endswith('.bak') for f in os.listdir(backup_path)):
                        backup_info['type'] = 'sqlserver'
                    elif any(f.endswith('.tar.gz') for f in os.listdir(backup_path)):
                        backup_info['type'] = 'filesystem'
                    
                    backups.append(backup_info)
            
            return {
                'total_backups': len(backups),
                'backups': backups,
                'total_size': sum(b['size'] for b in backups),
                'backup_types': {b['type']: len([x for x in backups if x['type'] == b['type']]) for b in backups}
            }
            
        except Exception as e:
            return {'error': str(e)}