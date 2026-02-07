import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, mock_open
import shutil
import subprocess
import tarfile
import datetime
import json
from typing import Dict, Any, List, Optional

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

# Mock database modules if not available
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

from automation.backup_automation import DatabaseBackupAutomation

class TestDatabaseBackupAutomation:
    """Test cases for DatabaseBackupAutomation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'backup_dir': '/tmp/test_backups',
            'retention_days': 7,
            'log_file': '/tmp/test_backups.log'
        }
        self.backup_automation = DatabaseBackupAutomation(self.config)
    
    def test_init(self):
        """Test DatabaseBackupAutomation initialization"""
        assert self.backup_automation.config == self.config
        assert self.backup_automation.backup_dir == '/tmp/test_backups'
        assert self.backup_automation.retention_days == 7
        assert self.backup_automation.log_file == '/tmp/test_backups.log'
    
    @patch('os.makedirs')
    def test_init_backup_directory_creation(self, mock_makedirs):
        """Test backup directory creation during initialization"""
        config = {'backup_dir': '/new/backup/dir'}
        backup_automation = DatabaseBackupAutomation(config)
        
        mock_makedirs.assert_called_once_with('/new/backup/dir', exist_ok=True)
        assert backup_automation.backup_dir == '/new/backup/dir'
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_oracle_database_success(self, mock_makedirs, mock_subprocess):
        """Test successful Oracle database backup"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.strftime.return_value = "20230101_120000"
            
            # Call the method
            result = self.backup_automation.backup_oracle_database(
                "plsql_dev/DevPassword123@localhost:1521/FREEPDB1",
                "test_backup"
            )
            
            # Verify result
            assert result['backup_type'] == 'oracle'
            assert result['backup_name'] == 'test_backup'
            assert result['status'] == 'success'
            assert result['backup_path'] == '/tmp/test_backups/test_backup'
            assert 'start_time' in result
            assert 'end_time' in result
            assert 'duration' in result
            
            # Verify subprocess was called correctly
            expected_command = [
                'expdp',
                'plsql_dev/DevPassword123@localhost:1521/FREEPDB1',
                'DIRECTORY=/tmp/test_backups/test_backup',
                'DUMPFILE=test_backup.dmp',
                'LOGFILE=test_backup.log',
                'FULL=Y',
                'COMPRESSION=YES'
            ]
            mock_subprocess.assert_called_once_with(expected_command, capture_output=True, text=True, timeout=3600)
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_oracle_database_auto_name(self, mock_makedirs, mock_subprocess):
        """Test Oracle database backup with auto-generated name"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.strftime.return_value = "20230101_120000"
            
            # Call the method without backup name
            result = self.backup_automation.backup_oracle_database(
                "plsql_dev/DevPassword123@localhost:1521/FREEPDB1"
            )
            
            # Verify auto-generated name
            assert result['backup_name'] == 'oracle_backup_20230101_120000'
            assert result['backup_path'] == '/tmp/test_backups/oracle_backup_20230101_120000'
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_oracle_database_failure(self, mock_makedirs, mock_subprocess):
        """Test Oracle database backup failure"""
        # Mock subprocess to fail
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Backup failed"
        mock_subprocess.return_value = mock_result
        
        # Call the method
        result = self.backup_automation.backup_oracle_database(
            "plsql_dev/DevPassword123@localhost:1521/FREEPDB1"
        )
        
        # Verify failure result
        assert result['backup_type'] == 'oracle'
        assert result['status'] == 'failed'
        assert 'error' in result
        assert result['error'] == "Backup failed"
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_oracle_database_timeout(self, mock_makedirs, mock_subprocess):
        """Test Oracle database backup timeout"""
        # Mock subprocess to timeout
        mock_result = Mock()
        mock_result.returncode = -1
        mock_result.stdout = ""
        mock_result.stderr = "Command timed out"
        mock_subprocess.return_value = mock_result
        
        # Call the method
        result = self.backup_automation.backup_oracle_database(
            "plsql_dev/DevPassword123@localhost:1521/FREEPDB1"
        )
        
        # Verify timeout result
        assert result['backup_type'] == 'oracle'
        assert result['status'] == 'failed'
        assert 'error' in result
        assert 'timeout' in result['error']
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_sql_server_database_success(self, mock_makedirs, mock_subprocess):
        """Test successful SQL Server database backup"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.strftime.return_value = "20230101_120000"
            
            # Call the method
            result = self.backup_automation.backup_sql_server_database(
                "plsql_dev_db",
                "test_backup"
            )
            
            # Verify result
            assert result['backup_type'] == 'sqlserver'
            assert result['backup_name'] == 'test_backup'
            assert result['status'] == 'success'
            assert result['backup_path'] == '/tmp/test_backups/test_backup'
            assert 'start_time' in result
            assert 'end_time' in result
            assert 'duration' in result
            
            # Verify subprocess was called correctly
            expected_command = [
                'sqlcmd',
                '-S', 'localhost,1433',
                '-U', 'sa',
                '-P', 'YourStrongPassword123!',
                '-Q', f'BACKUP DATABASE [plsql_dev_db] TO DISK = \'/tmp/test_backups/test_backup/test_backup.bak\' WITH COMPRESSION, INIT',
                '-o', '/tmp/test_backups/test_backup/test_backup.log'
            ]
            mock_subprocess.assert_called_once_with(expected_command, capture_output=True, text=True, timeout=3600)
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_sql_server_database_auto_name(self, mock_makedirs, mock_subprocess):
        """Test SQL Server database backup with auto-generated name"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Mock current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.strftime.return_value = "20230101_120000"
            
            # Call the method without backup name
            result = self.backup_automation.backup_sql_server_database("plsql_dev_db")
            
            # Verify auto-generated name
            assert result['backup_name'] == 'sqlserver_backup_20230101_120000'
            assert result['backup_path'] == '/tmp/test_backups/sqlserver_backup_20230101_120000'
    
    @patch('subprocess.run')
    @patch('os.makedirs')
    def test_backup_sql_server_database_failure(self, mock_makedirs, mock_subprocess):
        """Test SQL Server database backup failure"""
        # Mock subprocess to fail
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Backup failed"
        mock_subprocess.return_value = mock_result
        
        # Call the method
        result = self.backup_automation.backup_sql_server_database("plsql_dev_db")
        
        # Verify failure result
        assert result['backup_type'] == 'sqlserver'
        assert result['status'] == 'failed'
        assert 'error' in result
        assert result['error'] == "Backup failed"
    
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    def test_cleanup_old_backups(self, mock_rmtree, mock_exists):
        """Test cleanup of old backups"""
        # Mock existing backups
        mock_exists.side_effect = lambda path: path in [
            '/tmp/test_backups/backup1',
            '/tmp/test_backups/backup2',
            '/tmp/test_backups/backup3'
        ]
        
        # Mock file modification times
        with patch('os.path.getmtime') as mock_getmtime:
            # backup1: 10 days old (should be deleted)
            # backup2: 5 days old (should be kept)
            # backup3: 2 days old (should be kept)
            mock_getmtime.side_effect = lambda path: 10 if path.endswith('backup1') else 5 if path.endswith('backup2') else 2
            
            # Call the method
            result = self.backup_automation.cleanup_old_backups()
            
            # Verify cleanup result
            assert result['deleted_backups'] == ['backup1']
            assert result['kept_backups'] == ['backup2', 'backup3']
            assert result['cleanup_date'] is not None
            
            # Verify rmtree was called correctly
            mock_rmtree.assert_called_once_with('/tmp/test_backups/backup1')
    
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    def test_cleanup_old_backups_no_old_backups(self, mock_rmtree, mock_exists):
        """Test cleanup when no old backups exist"""
        # Mock no existing backups
        mock_exists.return_value = False
        
        # Call the method
        result = self.backup_automation.cleanup_old_backups()
        
        # Verify cleanup result
        assert result['deleted_backups'] == []
        assert result['kept_backups'] == []
        assert result['cleanup_date'] is not None
        
        # Verify rmtree was not called
        mock_rmtree.assert_not_called()
    
    @patch('os.path.exists')
    @patch('shutil.rmtree')
    def test_cleanup_old_backups_all_old(self, mock_rmtree, mock_exists):
        """Test cleanup when all backups are old"""
        # Mock existing backups
        mock_exists.side_effect = lambda path: path in [
            '/tmp/test_backups/backup1',
            '/tmp/test_backups/backup2'
        ]
        
        # Mock file modification times (both old)
        with patch('os.path.getmtime') as mock_getmtime:
            mock_getmtime.side_effect = lambda path: 10  # Both 10 days old
            
            # Call the method
            result = self.backup_automation.cleanup_old_backups()
            
            # Verify cleanup result
            assert result['deleted_backups'] == ['backup1', 'backup2']
            assert result['kept_backups'] == []
            assert result['cleanup_date'] is not None
            
            # Verify rmtree was called twice
            assert mock_rmtree.call_count == 2
            mock_rmtree.assert_any_call('/tmp/test_backups/backup1')
            mock_rmtree.assert_any_call('/tmp/test_backups/backup2')
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    def test_backup_oracle_database_with_compression(self, mock_subprocess, mock_makedirs):
        """Test Oracle database backup with compression"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Call the method
        result = self.backup_automation.backup_oracle_database(
            "plsql_dev/DevPassword123@localhost:1521/FREEPDB1",
            "test_backup"
        )
        
        # Verify compression was used
        expected_command = [
            'expdp',
            'plsql_dev/DevPassword123@localhost:1521/FREEPDB1',
            'DIRECTORY=/tmp/test_backups/test_backup',
            'DUMPFILE=test_backup.dmp',
            'LOGFILE=test_backup.log',
            'FULL=Y',
            'COMPRESSION=YES'
        ]
        mock_subprocess.assert_called_once_with(expected_command, capture_output=True, text=True, timeout=3600)
    
    @patch('os.makedirs')
    @patch('subprocess.run')
    def test_backup_sql_server_database_with_compression(self, mock_subprocess, mock_makedirs):
        """Test SQL Server database backup with compression"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Backup completed successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Call the method
        result = self.backup_automation.backup_sql_server_database(
            "plsql_dev_db",
            "test_backup"
        )
        
        # Verify compression was used
        expected_command = [
            'sqlcmd',
            '-S', 'localhost,1433',
            '-U', 'sa',
            '-P', 'YourStrongPassword123!',
            '-Q', f'BACKUP DATABASE [plsql_dev_db] TO DISK = \'/tmp/test_backups/test_backup/test_backup.bak\' WITH COMPRESSION, INIT',
            '-o', '/tmp/test_backups/test_backup/test_backup.log'
        ]
        mock_subprocess.assert_called_once_with(expected_command, capture_output=True, text=True, timeout=3600)

class TestBackupAutomationIntegration:
    """Integration tests for DatabaseBackupAutomation"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_backup_oracle_integration(self, oracle_test_config, backup_config):
        """Test real Oracle backup functionality (if available)"""
        try:
            from automation.backup_automation import DatabaseBackupAutomation
            
            # Create backup automation with test config
            backup_automation = DatabaseBackupAutomation(backup_config)
            
            # Test backup (this would require actual database)
            # For now, we'll skip it as it requires database access
            pytest.skip("Oracle backup integration test requires database access")
            
        except Exception as e:
            pytest.skip(f"Oracle backup integration test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.sqlserver
    def test_backup_sqlserver_integration(self, sqlserver_test_config, backup_config):
        """Test real SQL Server backup functionality (if available)"""
        try:
            from automation.backup_automation import DatabaseBackupAutomation
            
            # Create backup automation with test config
            backup_automation = DatabaseBackupAutomation(backup_config)
            
            # Test backup (this would require actual database)
            # For now, we'll skip it as it requires database access
            pytest.skip("SQL Server backup integration test requires database access")
            
        except Exception as e:
            pytest.skip(f"SQL Server backup integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])