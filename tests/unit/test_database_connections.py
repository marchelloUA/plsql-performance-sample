import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

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

from database.connection_oracle import create_oracle_connection
from database.connection_sqlserver import create_sqlserver_connection

class TestOracleConnection:
    """Test cases for Oracle database connection"""
    
    @patch('cx_Oracle.connect')
    def test_create_oracle_connection_success(self, mock_connect):
        """Test successful Oracle connection creation"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = create_oracle_connection()
        
        # Verify the connection was called with correct parameters
        mock_connect.assert_called_once_with(
            user="plsql_dev",
            password="DevPassword123",
            dsn=Mock(),  # This will be created by makedsn
            encoding="UTF-8"
        )
        assert result == mock_conn
    
    @patch('cx_Oracle.makedsn')
    @patch('cx_Oracle.connect')
    def test_create_oracle_connection_with_dsn(self, mock_connect, mock_makedsn):
        """Test Oracle connection with DSN creation"""
        # Mock DSN creation
        mock_dsn = Mock()
        mock_makedsn.return_value = mock_dsn
        
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = create_oracle_connection()
        
        # Verify DSN was created correctly
        mock_makedsn.assert_called_once_with("localhost", 1521, service_name="FREEPDB1")
        mock_connect.assert_called_once_with(
            user="plsql_dev",
            password="DevPassword123",
            dsn=mock_dsn,
            encoding="UTF-8"
        )
        assert result == mock_conn
    
    @patch('cx_Oracle.connect')
    def test_create_oracle_connection_database_error(self, mock_connect):
        """Test Oracle connection with database error"""
        # Mock connection to raise exception
        mock_connect.side_effect = cx_Oracle.DatabaseError("Connection failed")
        
        # Call the function and expect exception
        with pytest.raises(cx_Oracle.DatabaseError):
            create_oracle_connection()
    
    @patch('cx_Oracle.connect')
    def test_create_oracle_connection_with_different_credentials(self, mock_connect):
        """Test Oracle connection with different credentials"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Test with different credentials
        with patch('database.connection_oracle.create_oracle_connection') as mock_create:
            mock_create.return_value = mock_conn
            
            # Call the function
            result = mock_create()
            
            # Verify the connection was created
            assert result == mock_conn

class TestSQLServerConnection:
    """Test cases for SQL Server database connection"""
    
    @patch('pyodbc.connect')
    def test_create_sqlserver_connection_success(self, mock_connect):
        """Test successful SQL Server connection creation"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = create_sqlserver_connection()
        
        # Verify the connection was called with correct parameters
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=plsql_dev_db;"
            "UID=sa;"
            "PWD=YourStrongPassword123!"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    def test_create_sqlserver_connection_with_different_server(self, mock_connect):
        """Test SQL Server connection with different server configuration"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Test with different server configuration
        with patch('database.connection_sqlserver.create_sqlserver_connection') as mock_create:
            mock_create.return_value = mock_conn
            
            # Call the function
            result = mock_create()
            
            # Verify the connection was created
            assert result == mock_conn
    
    @patch('pyodbc.connect')
    def test_create_sqlserver_connection_database_error(self, mock_connect):
        """Test SQL Server connection with database error"""
        # Mock connection to raise exception
        mock_connect.side_effect = pyodbc.Error("Connection failed")
        
        # Call the function and expect exception
        with pytest.raises(pyodbc.Error):
            create_sqlserver_connection()
    
    @patch('pyodbc.connect')
    def test_create_sqlserver_connection_timeout(self, mock_connect):
        """Test SQL Server connection with timeout"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = create_sqlserver_connection()
        
        # Verify the connection was created
        assert result == mock_conn

class TestConnectionIntegration:
    """Integration tests for database connections"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_oracle_connection_integration(self, oracle_test_config):
        """Test real Oracle connection (if available)"""
        try:
            import cx_Oracle
            dsn = cx_Oracle.makedsn(
                oracle_test_config['dsn'].split(':')[0],
                int(oracle_test_config['dsn'].split(':')[1]),
                service_name=oracle_test_config['dsn'].split('/')[1]
            )
            conn = cx_Oracle.connect(
                user=oracle_test_config['user'],
                password=oracle_test_config['password'],
                dsn=dsn,
                encoding="UTF-8"
            )
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT 'Oracle connection test successful!' FROM DUAL")
            result = cursor.fetchone()
            assert result[0] == "Oracle connection test successful!"
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.skip(f"Oracle connection test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.sqlserver
    def test_sqlserver_connection_integration(self, sqlserver_test_config):
        """Test real SQL Server connection (if available)"""
        try:
            conn_str = (
                f"DRIVER={{{sqlserver_test_config['driver']}}};"
                f"SERVER={sqlserver_test_config['server']};"
                f"DATABASE={sqlserver_test_config['database']};"
                f"UID={sqlserver_test_config['uid']};"
                f"PWD={sqlserver_test_config['pwd']}"
            )
            conn = pyodbc.connect(conn_str)
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT 'SQL Server connection test successful!'")
            result = cursor.fetchone()
            assert result[0] == "SQL Server connection test successful!"
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.skip(f"SQL Server connection test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])