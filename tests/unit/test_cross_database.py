import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

# Mock database modules if not available
try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

from cross_database.cross_database_query import query_cross_database

class TestCrossDatabaseQuery:
    """Test cases for cross-database query functionality"""
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_success(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test successful cross-database query"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock data from both databases
        sql_data = pd.DataFrame({
            'oracle_employee_id': [1, 2, 3],
            'local_name': ['John SQL', 'Jane SQL', 'Bob SQL'],
            'local_department': ['IT', 'HR', 'Finance']
        })
        
        oracle_data = pd.DataFrame({
            'employee_id': [1, 2, 4],
            'employee_name': ['John Oracle', 'Jane Oracle', 'Bob Oracle'],
            'department': ['IT', 'HR', 'Finance'],
            'salary': [75000, 65000, 80000]
        })
        
        # Mock read_sql to return appropriate data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify connections were created correctly
        expected_sql_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=plsql_dev_db;"
            "UID=sa;PWD=YourStrongPassword123!"
        )
        mock_sql_connect.assert_called_once_with(expected_sql_conn_str)
        
        expected_oracle_dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREEPDB1")
        expected_oracle_conn_str = (
            "plsql_dev/DevPassword123@localhost:1521/FREEPDB1"
        )
        mock_oracle_connect.assert_called_once_with(
            user="plsql_dev",
            password="DevPassword123",
            dsn=expected_oracle_dsn
        )
        
        # Verify queries were executed
        mock_read_sql.assert_any_call("SELECT * FROM local_employees", mock_sql_conn)
        mock_read_sql.assert_any_call("SELECT * FROM plsql_dev.employees", mock_oracle_conn)
        
        # Verify result
        assert not result.empty
        assert len(result) == 2  # Only employees 1 and 2 exist in both databases
        assert 'employee_id' in result.columns
        assert 'employee_name' in result.columns
        assert 'oracle_employee_id' in result.columns
        
        # Verify connections were closed
        mock_sql_conn.close.assert_called_once()
        mock_oracle_conn.close.assert_called_once()
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_no_matches(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with no matching records"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock data with no overlapping employee IDs
        sql_data = pd.DataFrame({
            'oracle_employee_id': [1, 2],
            'local_name': ['John SQL', 'Jane SQL']
        })
        
        oracle_data = pd.DataFrame({
            'employee_id': [3, 4],
            'employee_name': ['Bob Oracle', 'Alice Oracle']
        })
        
        # Mock read_sql to return appropriate data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify result is empty (no matches)
        assert result.empty
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_sql_error(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with SQL Server error"""
        # Mock SQL Server connection to raise exception
        mock_sql_connect.side_effect = pyodbc.Error("SQL Server connection failed")
        
        # Call the function and expect exception
        with pytest.raises(pyodbc.Error):
            query_cross_database()
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_oracle_error(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with Oracle error"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection to raise exception
        mock_oracle_connect.side_effect = cx_Oracle.DatabaseError("Oracle connection failed")
        
        # Call the function and expect exception
        with pytest.raises(cx_Oracle.DatabaseError):
            query_cross_database()
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_merge_keys(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with different merge keys"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock data with different column names
        sql_data = pd.DataFrame({
            'emp_id': [1, 2, 3],
            'local_name': ['John SQL', 'Jane SQL', 'Bob SQL']
        })
        
        oracle_data = pd.DataFrame({
            'employee_id': [1, 2, 4],
            'employee_name': ['John Oracle', 'Jane Oracle', 'Bob Oracle']
        })
        
        # Mock read_sql to return appropriate data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify merge was performed correctly
        assert not result.empty
        assert len(result) == 2  # Employees 1 and 2 exist in both databases
        assert 'employee_id' in result.columns
        assert 'employee_name' in result.columns
        assert 'emp_id' in result.columns
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_empty_data(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with empty data"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock empty data
        sql_data = pd.DataFrame()
        oracle_data = pd.DataFrame()
        
        # Mock read_sql to return empty data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify result is empty
        assert result.empty
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_partial_merge(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with partial merge"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock data with partial overlap
        sql_data = pd.DataFrame({
            'oracle_employee_id': [1, 2, 3],
            'local_name': ['John SQL', 'Jane SQL', 'Bob SQL']
        })
        
        oracle_data = pd.DataFrame({
            'employee_id': [1, 4, 5],
            'employee_name': ['John Oracle', 'Bob Oracle', 'Alice Oracle']
        })
        
        # Mock read_sql to return appropriate data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify only matching records are returned
        assert not result.empty
        assert len(result) == 1  # Only employee 1 exists in both databases
        assert result['employee_id'].iloc[0] == 1
    
    @patch('pandas.read_sql')
    @patch('pyodbc.connect')
    @patch('cx_Oracle.connect')
    def test_query_cross_database_left_merge(self, mock_oracle_connect, mock_sql_connect, mock_read_sql):
        """Test cross-database query with left merge behavior"""
        # Mock SQL Server connection
        mock_sql_conn = Mock()
        mock_sql_connect.return_value = mock_sql_conn
        
        # Mock Oracle connection
        mock_oracle_conn = Mock()
        mock_oracle_connect.return_value = mock_oracle_conn
        
        # Mock data with left merge behavior
        sql_data = pd.DataFrame({
            'oracle_employee_id': [1, 2, 3],
            'local_name': ['John SQL', 'Jane SQL', 'Bob SQL']
        })
        
        oracle_data = pd.DataFrame({
            'employee_id': [1, 2],
            'employee_name': ['John Oracle', 'Jane Oracle']
        })
        
        # Mock read_sql to return appropriate data
        def mock_read_side_effect(query, conn):
            if 'local_employees' in query:
                return sql_data
            elif 'employees' in query:
                return oracle_data
            else:
                return pd.DataFrame()
        
        mock_read_sql.side_effect = mock_read_side_effect
        
        # Call the function
        result = query_cross_database()
        
        # Verify inner merge behavior (only matching records)
        assert not result.empty
        assert len(result) == 2  # Employees 1 and 2 exist in both databases

class TestCrossDatabaseIntegration:
    """Integration tests for cross-database query functionality"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    @pytest.mark.sqlserver
    def test_cross_database_query_integration(self, oracle_test_config, sqlserver_test_config):
        """Test real cross-database query functionality (if available)"""
        try:
            from cross_database.cross_database_query import query_cross_database
            
            # This test would require actual database connections
            # For now, we'll skip it as it requires both databases to be running
            pytest.skip("Cross-database query integration test requires both databases")
            
        except Exception as e:
            pytest.skip(f"Cross-database query integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])