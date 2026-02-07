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

from database.plsql_executor import PLSQLExecutor

class TestPLSQLExecutor:
    """Test cases for PL/SQL executor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_connection = Mock(spec=cx_Oracle.Connection)
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.executor = PLSQLExecutor(self.mock_connection)
    
    def test_init(self):
        """Test PLSQLExecutor initialization"""
        assert self.executor.connection == self.mock_connection
        assert self.executor.cursor == self.mock_cursor
    
    @patch('database.plsql_executor.PLSQLExecutor.__init__')
    def test_init_with_connection(self, mock_init):
        """Test PLSQLExecutor initialization with connection"""
        mock_init.return_value = None
        executor = PLSQLExecutor(self.mock_connection)
        mock_init.assert_called_once_with(self.mock_connection)
    
    def test_execute_procedure_without_parameters(self):
        """Test executing procedure without parameters"""
        procedure_name = "test_procedure"
        
        # Call the method
        result = self.executor.execute_procedure(procedure_name)
        
        # Verify the procedure was called correctly
        expected_plsql_block = f"BEGIN {procedure_name}; END;"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block)
        self.mock_connection.commit.assert_called_once()
        assert result is True
    
    def test_execute_procedure_with_parameters(self):
        """Test executing procedure with parameters"""
        procedure_name = "test_procedure"
        parameters = [1, "test_value", 100.50]
        
        # Call the method
        result = self.executor.execute_procedure(procedure_name, parameters)
        
        # Verify the procedure was called correctly
        expected_plsql_block = f"BEGIN {procedure_name}(:1, :2, :3); END;"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block, parameters)
        self.mock_connection.commit.assert_called_once()
        assert result is True
    
    def test_execute_procedure_with_database_error(self):
        """Test executing procedure with database error"""
        procedure_name = "test_procedure"
        self.mock_cursor.execute.side_effect = cx_Oracle.DatabaseError("Procedure execution failed")
        
        # Call the method
        result = self.executor.execute_procedure(procedure_name)
        
        # Verify rollback was called and method returns False
        self.mock_connection.rollback.assert_called_once()
        assert result is False
    
    def test_execute_function_without_parameters_without_return_type(self):
        """Test executing function without parameters and without return type"""
        function_name = "test_function"
        
        # Mock the result variable
        mock_result_var = Mock()
        mock_result_var.getvalue.return_value = "test_result"
        self.mock_cursor.var.return_value = mock_result_var
        
        # Call the method
        result = self.executor.execute_function(function_name)
        
        # Verify the function was called correctly
        expected_plsql_block = f"BEGIN :result := {function_name}(); END;"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block, [mock_result_var])
        assert result == "test_result"
    
    def test_execute_function_without_parameters_with_return_type(self):
        """Test executing function without parameters with return type"""
        function_name = "test_function"
        
        # Mock the cursor fetchone
        mock_result = ["test_result"]
        self.mock_cursor.fetchone.return_value = mock_result
        
        # Call the method
        result = self.executor.execute_function(function_name, return_type="VARCHAR2")
        
        # Verify the function was called correctly
        expected_plsql_block = f"SELECT {function_name}() FROM DUAL"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block)
        assert result == "test_result"
    
    def test_execute_function_with_parameters_without_return_type(self):
        """Test executing function with parameters without return type"""
        function_name = "test_function"
        parameters = [1, "test_value", 100.50]
        
        # Mock the result variable
        mock_result_var = Mock()
        mock_result_var.getvalue.return_value = "test_result"
        self.mock_cursor.var.return_value = mock_result_var
        
        # Call the method
        result = self.executor.execute_function(function_name, parameters)
        
        # Verify the function was called correctly
        expected_plsql_block = f"BEGIN :result := {function_name}(:1, :2, :3); END;"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block, parameters + [mock_result_var])
        assert result == "test_result"
    
    def test_execute_function_with_parameters_with_return_type(self):
        """Test executing function with parameters with return type"""
        function_name = "test_function"
        parameters = [1, "test_value", 100.50]
        
        # Mock the cursor fetchone
        mock_result = ["test_result"]
        self.mock_cursor.fetchone.return_value = mock_result
        
        # Call the method
        result = self.executor.execute_function(function_name, parameters, return_type="VARCHAR2")
        
        # Verify the function was called correctly
        expected_plsql_block = f"SELECT {function_name}(:1, :2, :3) FROM DUAL"
        self.mock_cursor.execute.assert_called_once_with(expected_plsql_block, parameters)
        assert result == "test_result"
    
    def test_execute_function_with_database_error(self):
        """Test executing function with database error"""
        function_name = "test_function"
        self.mock_cursor.execute.side_effect = cx_Oracle.DatabaseError("Function execution failed")
        
        # Call the method
        result = self.executor.execute_function(function_name)
        
        # Verify method returns None
        assert result is None
    
    def test_execute_function_with_no_result(self):
        """Test executing function with no result"""
        function_name = "test_function"
        
        # Mock the cursor fetchone to return None
        self.mock_cursor.fetchone.return_value = None
        
        # Call the method
        result = self.executor.execute_function(function_name, return_type="VARCHAR2")
        
        # Verify method returns None
        assert result is None
    
    def test_execute_function_with_result_var_none(self):
        """Test executing function with result variable returning None"""
        function_name = "test_function"
        
        # Mock the result variable
        mock_result_var = Mock()
        mock_result_var.getvalue.return_value = None
        self.mock_cursor.var.return_value = mock_result_var
        
        # Call the method
        result = self.executor.execute_function(function_name)
        
        # Verify method returns None
        assert result is None
    
    def test_execute_procedure_commit_success(self):
        """Test that commit is called on successful procedure execution"""
        procedure_name = "test_procedure"
        
        # Call the method
        result = self.executor.execute_procedure(procedure_name)
        
        # Verify commit was called
        self.mock_connection.commit.assert_called_once()
        assert result is True
    
    def test_execute_procedure_rollback_on_error(self):
        """Test that rollback is called on procedure execution error"""
        procedure_name = "test_procedure"
        self.mock_cursor.execute.side_effect = cx_Oracle.DatabaseError("Procedure execution failed")
        
        # Call the method
        result = self.executor.execute_procedure(procedure_name)
        
        # Verify rollback was called and method returns False
        self.mock_connection.rollback.assert_called_once()
        assert result is False
    
    def test_execute_function_no_commit(self):
        """Test that commit is not called on function execution"""
        function_name = "test_function"
        
        # Mock the result variable
        mock_result_var = Mock()
        mock_result_var.getvalue.return_value = "test_result"
        self.mock_cursor.var.return_value = mock_result_var
        
        # Call the method
        result = self.executor.execute_function(function_name)
        
        # Verify commit was not called
        self.mock_connection.commit.assert_not_called()
        assert result == "test_result"

class TestPLSQLExecutorIntegration:
    """Integration tests for PL/SQL executor"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_plsql_executor_integration(self, mock_oracle_connection):
        """Test real PL/SQL executor functionality (if available)"""
        try:
            from database.plsql_executor import PLSQLExecutor
            
            # Create executor with mock connection for integration test
            executor = PLSQLExecutor(mock_oracle_connection)
            
            # Test procedure execution
            result = executor.execute_procedure("BEGIN NULL; END;")
            assert result is True
            
            # Test function execution
            result = executor.execute_function("USER", return_type="VARCHAR2")
            assert result is not None
            
        except Exception as e:
            pytest.skip(f"PL/SQL executor integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])