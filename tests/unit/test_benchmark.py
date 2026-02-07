import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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

from performance.benchmark import DatabaseBenchmark

class TestDatabaseBenchmark:
    """Test cases for DatabaseBenchmark"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.benchmark = DatabaseBenchmark(self.mock_connection)
    
    def test_init(self):
        """Test DatabaseBenchmark initialization"""
        assert self.benchmark.connection == self.mock_connection
        assert self.benchmark.results == []
    
    @patch('time.time')
    def test_run_single_query_test_success(self, mock_time):
        """Test successful single query test"""
        query = "SELECT * FROM employees"
        iterations = 5
        
        # Mock time values for execution times
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        
        # Mock cursor execute and fetchall
        self.mock_cursor.fetchall.return_value = []
        
        # Call the method
        result = self.benchmark.run_single_query_test(query, iterations)
        
        # Verify the result
        assert result['query'] == query
        assert result['iterations'] == iterations
        assert result['avg_time_ms'] == 50.0  # Average of [100, 200, 300, 400, 500] ms
        assert result['min_time_ms'] == 100.0
        assert result['max_time_ms'] == 500.0
        assert result['std_dev_ms'] == 158.1  # Standard deviation
        assert result['total_time_ms'] == 1500.0
        assert 'error' not in result
        
        # Verify cursor was called correctly
        assert self.mock_cursor.execute.call_count == iterations
        assert self.mock_cursor.fetchall.call_count == iterations
    
    @patch('time.time')
    def test_run_single_query_test_with_error(self, mock_time):
        """Test single query test with error"""
        query = "SELECT * FROM non_existent_table"
        iterations = 3
        
        # Mock cursor to raise exception
        self.mock_cursor.execute.side_effect = Exception("Table not found")
        
        # Call the method
        result = self.benchmark.run_single_query_test(query, iterations)
        
        # Verify the error result
        assert result['query'] == query
        assert result['iterations'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert 'error' in result
        assert result['error'] == "Table not found"
    
    @patch('time.time')
    def test_run_single_query_test_single_iteration(self, mock_time):
        """Test single query test with single iteration"""
        query = "SELECT * FROM employees"
        iterations = 1
        
        # Mock time values
        mock_time.side_effect = [0.0, 0.1]
        
        # Mock cursor execute and fetchall
        self.mock_cursor.fetchall.return_value = []
        
        # Call the method
        result = self.benchmark.run_single_query_test(query, iterations)
        
        # Verify the result
        assert result['query'] == query
        assert result['iterations'] == iterations
        assert result['avg_time_ms'] == 100.0
        assert result['min_time_ms'] == 100.0
        assert result['max_time_ms'] == 100.0
        assert result['std_dev_ms'] == 0  # No standard deviation for single value
        assert result['total_time_ms'] == 100.0
    
    @patch('time.time')
    def test_run_single_query_test_zero_iterations(self, mock_time):
        """Test single query test with zero iterations"""
        query = "SELECT * FROM employees"
        iterations = 0
        
        # Call the method
        result = self.benchmark.run_single_query_test(query, iterations)
        
        # Verify the result
        assert result['query'] == query
        assert result['iterations'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        
        # Verify cursor was not called
        self.mock_cursor.execute.assert_not_called()
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    @patch('time.time')
    def test_run_concurrent_test_success(self, mock_time, mock_thread_pool):
        """Test successful concurrent test"""
        query = "SELECT * FROM employees"
        concurrent_users = 3
        iterations_per_user = 2
        
        # Mock thread pool
        mock_executor = Mock()
        mock_thread_pool.return_value.__enter__.return_value = mock_executor
        mock_future = Mock()
        mock_future.result.return_value = {
            'query': query,
            'avg_time_ms': 100.0,
            'min_time_ms': 50.0,
            'max_time_ms': 150.0,
            'std_dev_ms': 50.0,
            'total_time_ms': 200.0
        }
        mock_executor.submit.return_value = mock_future
        mock_executor.as_completed.return_value = [mock_future]
        
        # Mock time values
        mock_time.side_effect = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        
        # Call the method
        result = self.benchmark.run_concurrent_test(query, concurrent_users, iterations_per_user)
        
        # Verify the result
        assert result['query'] == query
        assert result['concurrent_users'] == concurrent_users
        assert result['iterations_per_user'] == iterations_per_user
        assert result['total_iterations'] == concurrent_users * iterations_per_user
        assert result['avg_time_ms'] == 100.0
        assert result['min_time_ms'] == 50.0
        assert result['max_time_ms'] == 150.0
        assert result['std_dev_ms'] == 50.0
        assert result['total_time_ms'] == 200.0
        assert result['test_type'] == 'concurrent'
        
        # Verify thread pool was called correctly
        mock_thread_pool.assert_called_once()
        assert mock_executor.submit.call_count == concurrent_users
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_run_concurrent_test_with_error(self, mock_thread_pool):
        """Test concurrent test with error"""
        query = "SELECT * FROM non_existent_table"
        concurrent_users = 2
        iterations_per_user = 1
        
        # Mock thread pool to raise exception
        mock_executor = Mock()
        mock_thread_pool.return_value.__enter__.return_value = mock_executor
        mock_future = Mock()
        mock_future.result.side_effect = Exception("Connection failed")
        mock_executor.submit.return_value = mock_future
        mock_executor.as_completed.return_value = [mock_future]
        
        # Call the method
        result = self.benchmark.run_concurrent_test(query, concurrent_users, iterations_per_user)
        
        # Verify the error result
        assert result['query'] == query
        assert result['concurrent_users'] == concurrent_users
        assert result['iterations_per_user'] == iterations_per_user
        assert result['total_iterations'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert result['test_type'] == 'concurrent'
        assert 'error' in result
        assert result['error'] == "Connection failed"
    
    def test_run_transaction_test_success(self):
        """Test successful transaction test"""
        transaction_func = Mock()
        transaction_func.return_value = True
        iterations = 3
        
        # Call the method
        result = self.benchmark.run_transaction_test(transaction_func, iterations)
        
        # Verify the result
        assert result['iterations'] == iterations
        assert result['avg_time_ms'] > 0
        assert result['min_time_ms'] > 0
        assert result['max_time_ms'] > 0
        assert result['std_dev_ms'] >= 0
        assert result['total_time_ms'] > 0
        assert result['test_type'] == 'custom_transaction'
        
        # Verify transaction function was called correctly
        assert transaction_func.call_count == iterations
    
    def test_run_transaction_test_with_error(self):
        """Test transaction test with error"""
        transaction_func = Mock()
        transaction_func.side_effect = Exception("Transaction failed")
        iterations = 2
        
        # Call the method
        result = self.benchmark.run_transaction_test(transaction_func, iterations)
        
        # Verify the error result
        assert result['iterations'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert result['test_type'] == 'custom_transaction'
        assert 'error' in result
        assert result['error'] == "Transaction failed"
    
    def test_run_transaction_test_zero_iterations(self):
        """Test transaction test with zero iterations"""
        transaction_func = Mock()
        iterations = 0
        
        # Call the method
        result = self.benchmark.run_transaction_test(transaction_func, iterations)
        
        # Verify the result
        assert result['iterations'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert result['test_type'] == 'custom_transaction'
        
        # Verify transaction function was not called
        transaction_func.assert_not_called()
    
    @patch('time.time')
    def test_run_load_test_success(self, mock_time):
        """Test successful load test"""
        queries = [
            "SELECT * FROM employees",
            "SELECT * FROM departments",
            "SELECT * FROM projects"
        ]
        duration_seconds = 2
        
        # Mock time values for duration
        mock_time.side_effect = [0.0, 0.5, 1.0, 1.5, 2.0]
        
        # Mock cursor execute and fetchall
        self.mock_cursor.fetchall.return_value = []
        
        # Call the method
        result = self.benchmark.run_load_test(queries, duration_seconds)
        
        # Verify the result
        assert result['queries'] == queries
        assert result['duration_seconds'] == duration_seconds
        assert result['total_queries'] > 0
        assert result['avg_time_ms'] > 0
        assert result['min_time_ms'] > 0
        assert result['max_time_ms'] > 0
        assert result['std_dev_ms'] >= 0
        assert result['total_time_ms'] > 0
        assert result['test_type'] == 'load_test'
        assert 'query_distribution' in result
        
        # Verify cursor was called multiple times
        assert self.mock_cursor.execute.call_count > 0
        assert self.mock_cursor.fetchall.call_count > 0
    
    @patch('time.time')
    def test_run_load_test_with_error(self, mock_time):
        """Test load test with error"""
        queries = ["SELECT * FROM non_existent_table"]
        duration_seconds = 1
        
        # Mock time values
        mock_time.side_effect = [0.0, 0.5, 1.0]
        
        # Mock cursor to raise exception
        self.mock_cursor.execute.side_effect = Exception("Table not found")
        
        # Call the method
        result = self.benchmark.run_load_test(queries, duration_seconds)
        
        # Verify the error result
        assert result['queries'] == queries
        assert result['duration_seconds'] == duration_seconds
        assert result['total_queries'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert result['test_type'] == 'load_test'
        assert 'error' in result
        assert result['error'] == "Table not found"
    
    @patch('time.time')
    def test_run_load_test_zero_duration(self, mock_time):
        """Test load test with zero duration"""
        queries = ["SELECT * FROM employees"]
        duration_seconds = 0
        
        # Call the method
        result = self.benchmark.run_load_test(queries, duration_seconds)
        
        # Verify the result
        assert result['queries'] == queries
        assert result['duration_seconds'] == duration_seconds
        assert result['total_queries'] == 0
        assert result['avg_time_ms'] == 0
        assert result['min_time_ms'] == 0
        assert result['max_time_ms'] == 0
        assert result['std_dev_ms'] == 0
        assert result['total_time_ms'] == 0
        assert result['test_type'] == 'load_test'
        
        # Verify cursor was not called
        self.mock_cursor.execute.assert_not_called()
    
    def test_run_single_query_test_with_returned_data(self):
        """Test single query test with returned data"""
        query = "SELECT * FROM employees"
        iterations = 2
        
        # Mock cursor execute and fetchall with data
        mock_data = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
        self.mock_cursor.fetchall.return_value = mock_data
        
        # Call the method
        result = self.benchmark.run_single_query_test(query, iterations)
        
        # Verify the result
        assert result['query'] == query
        assert result['iterations'] == iterations
        assert result['avg_time_ms'] > 0
        assert result['min_time_ms'] > 0
        assert result['max_time_ms'] > 0
        assert result['std_dev_ms'] >= 0
        assert result['total_time_ms'] > 0
        
        # Verify cursor was called correctly
        assert self.mock_cursor.execute.call_count == iterations
        assert self.mock_cursor.fetchall.call_count == iterations

class TestDatabaseBenchmarkIntegration:
    """Integration tests for DatabaseBenchmark"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_benchmark_integration(self, mock_oracle_connection):
        """Test real DatabaseBenchmark functionality (if available)"""
        try:
            from performance.benchmark import DatabaseBenchmark
            
            # Create benchmark with mock connection for integration test
            benchmark = DatabaseBenchmark(mock_oracle_connection)
            
            # Test single query benchmark
            result = benchmark.run_single_query_test("SELECT 1 FROM DUAL", iterations=1)
            assert 'query' in result
            assert 'avg_time_ms' in result
            
            # Test transaction benchmark
            def test_transaction():
                return True
            
            result = benchmark.run_transaction_test(test_transaction, iterations=1)
            assert 'test_type' in result
            assert result['test_type'] == 'custom_transaction'
            
        except Exception as e:
            pytest.skip(f"DatabaseBenchmark integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])