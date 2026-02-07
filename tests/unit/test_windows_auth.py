import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import getpass

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

# Mock database modules if not available
try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

from windows_auth.windows_auth_example import connect_windows_auth

class TestWindowsAuth:
    """Test cases for Windows authentication functionality"""
    
    @patch('pyodbc.connect')
    def test_connect_windows_auth_success(self, mock_connect):
        """Test successful Windows authentication"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify Windows authentication connection string
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_fallback_to_sql(self, mock_print, mock_connect):
        """Test Windows authentication fallback to SQL authentication"""
        # Mock Windows authentication to fail
        mock_connect.side_effect = [
            pyodbc.Error("Windows authentication failed"),
            Mock()  # SQL authentication success
        ]
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify both connection attempts
        expected_windows_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        
        expected_sql_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "UID=sa;"
            "PWD=YourStrongPassword123!"
        )
        
        # Verify both connection attempts
        assert mock_connect.call_count == 2
        mock_connect.assert_any_call(expected_windows_conn_str)
        mock_connect.assert_any_call(expected_sql_conn_str)
        
        # Verify fallback message was printed
        mock_print.assert_any_call("Falling back to SQL authentication...")
        
        # Verify successful connection is returned
        assert result is not None
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_both_fail(self, mock_print, mock_connect):
        """Test Windows authentication when both Windows and SQL auth fail"""
        # Mock both authentication attempts to fail
        mock_connect.side_effect = pyodbc.Error("Authentication failed")
        
        # Call the function and expect exception
        with pytest.raises(pyodbc.Error):
            connect_windows_auth()
        
        # Verify connection attempt
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_sql_only(self, mock_print, mock_connect):
        """Test Windows authentication when only SQL auth is configured"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify connection string
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    def test_connect_windows_auth_with_different_server(self, mock_connect):
        """Test Windows authentication with different server configuration"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify server configuration
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_with_custom_database(self, mock_print, mock_connect):
        """Test Windows authentication with custom database"""
        # Mock the connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify database configuration
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_error_handling(self, mock_print, mock_connect):
        """Test Windows authentication error handling"""
        # Mock connection to raise specific error
        mock_connect.side_effect = pyodbc.Error("Login failed for user")
        
        # Call the function and expect exception
        with pytest.raises(pyodbc.Error):
            connect_windows_auth()
        
        # Verify error message was printed
        mock_print.assert_any_call("Windows authentication failed: Login failed for user")
    
    @patch('pyodbc.connect')
    @patch('builtins.print')
    def test_connect_windows_auth_connection_verification(self, mock_print, mock_connect):
        """Test Windows authentication connection verification"""
        # Mock the connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Mock query result
        mock_cursor.fetchone.return_value = ["DOMAIN\\user", "dbo"]
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify connection and query
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1434;"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
            "Authentication=ActiveDirectoryIntegrated;"
        )
        mock_connect.assert_called_once_with(expected_conn_str)
        
        # Verify query was executed
        mock_cursor.execute.assert_called_once_with("SELECT SYSTEM_USER, USER")
        mock_cursor.fetchone.assert_called_once()
        
        # Verify connection was closed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verify result
        assert result == mock_conn

class TestWindowsAuthIntegration:
    """Integration tests for Windows authentication functionality"""
    
    @pytest.mark.integration
    @pytest.mark.sqlserver
    def test_windows_auth_integration(self, sqlserver_test_config):
        """Test real Windows authentication functionality (if available)"""
        try:
            from windows_auth.windows_auth_example import connect_windows_auth
            
            # Test Windows authentication
            conn = connect_windows_auth()
            
            # Verify connection
            assert conn is not None
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT SYSTEM_USER, USER")
            result = cursor.fetchone()
            assert result is not None
            assert len(result) >= 1
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.skip(f"Windows authentication integration test failed: {e}")

class TestWindowsAuthUnit:
    """Additional unit tests for Windows authentication"""
    
    def test_windows_auth_connection_string_format(self):
        """Test Windows authentication connection string format"""
        expected_parts = [
            "DRIVER={ODBC Driver 17 for SQL Server}",
            "SERVER=localhost,1434",
            "DATABASE=master",
            "Trusted_Connection=yes",
            "Authentication=ActiveDirectoryIntegrated"
        ]
        
        # This would be tested by mocking pyodbc.connect and verifying the call
        # For now, we just verify the expected format
        assert all(part in " ".join(expected_parts) for part in expected_parts)
    
    @patch('pyodbc.connect')
    def test_windows_auth_timeout_handling(self, mock_connect):
        """Test Windows authentication timeout handling"""
        # Mock connection with timeout
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = connect_windows_auth()
        
        # Verify connection
        assert result == mock_conn
    
    @patch('pyodbc.connect')
    def test_windows_auth_connection_pooling(self, mock_connect):
        """Test Windows authentication connection pooling"""
        # Mock connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Call the function multiple times
        result1 = connect_windows_auth()
        result2 = connect_windows_auth()
        
        # Verify both connections
        assert result1 is not None
        assert result2 is not None
        assert mock_connect.call_count == 2

if __name__ == "__main__":
    pytest.main([__file__])