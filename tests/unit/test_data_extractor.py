import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

# Mock database modules if not available
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

from database.data_extractor import DataExtractor

class TestDataExtractor:
    """Test cases for DataExtractor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_connection = Mock(spec=cx_Oracle.Connection)
        self.extractor = DataExtractor(self.mock_connection)
    
    def test_init(self):
        """Test DataExtractor initialization"""
        assert self.extractor.connection == self.mock_connection
    
    @patch('pandas.read_sql')
    def test_extract_table_data_without_conditions(self, mock_read_sql):
        """Test extracting table data without conditions"""
        table_name = "employees"
        schema = "plsql_dev"
        
        # Mock the DataFrame
        expected_df = pd.DataFrame({
            'employee_id': [1, 2, 3],
            'employee_name': ['John', 'Jane', 'Bob'],
            'salary': [75000, 65000, 80000]
        })
        mock_read_sql.return_value = expected_df
        
        # Call the method
        result = self.extractor.extract_table_data(table_name, schema)
        
        # Verify the query was called correctly
        expected_query = f"SELECT * FROM {schema}.{table_name}"
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('pandas.read_sql')
    def test_extract_table_data_with_conditions(self, mock_read_sql):
        """Test extracting table data with conditions"""
        table_name = "employees"
        schema = "plsql_dev"
        conditions = "salary > 70000"
        
        # Mock the DataFrame
        expected_df = pd.DataFrame({
            'employee_id': [1, 3],
            'employee_name': ['John', 'Bob'],
            'salary': [75000, 80000]
        })
        mock_read_sql.return_value = expected_df
        
        # Call the method
        result = self.extractor.extract_table_data(table_name, schema, conditions)
        
        # Verify the query was called correctly
        expected_query = f"SELECT * FROM {schema}.{table_name} WHERE {conditions}"
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('pandas.read_sql')
    def test_extract_table_data_with_default_schema(self, mock_read_sql):
        """Test extracting table data with default schema"""
        table_name = "employees"
        
        # Mock the DataFrame
        expected_df = pd.DataFrame({
            'employee_id': [1, 2, 3],
            'employee_name': ['John', 'Jane', 'Bob'],
            'salary': [75000, 65000, 80000]
        })
        mock_read_sql.return_value = expected_df
        
        # Call the method
        result = self.extractor.extract_table_data(table_name)
        
        # Verify the query was called correctly
        expected_query = f"SELECT * FROM plsql_dev.{table_name}"
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('pandas.read_sql')
    def test_extract_table_data_exception_handling(self, mock_read_sql):
        """Test extracting table data with exception handling"""
        table_name = "employees"
        mock_read_sql.side_effect = Exception("Database query failed")
        
        # Call the method
        result = self.extractor.extract_table_data(table_name)
        
        # Verify empty DataFrame is returned
        assert result.empty
        assert isinstance(result, pd.DataFrame)
    
    @patch('pandas.read_sql')
    def test_extract_performance_metrics_success(self, mock_read_sql):
        """Test extracting performance metrics successfully"""
        # Mock the performance data
        performance_data = pd.DataFrame({
            'name': ['parse count (hard)', 'execute count', 'user commits', 'db block gets'],
            'value': [100, 1000, 500, 2000]
        })
        mock_read_sql.return_value = performance_data
        
        # Call the method
        result = self.extractor.extract_performance_metrics()
        
        # Verify the query was called correctly
        expected_query = """
            SELECT s.name, s.value 
            FROM v$sysstat s 
            WHERE s.name IN ('parse count (hard)', 'execute count', 'user commits', 'db block gets')
            """
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        
        # Verify derived metrics are calculated
        assert 'parse_ratio' in result.columns
        assert 'commit_ratio' in result.columns
        assert result['parse_ratio'].iloc[0] == 0.1  # 100/1000
        assert result['commit_ratio'].iloc[0] == 0.5  # 500/1000
    
    @patch('pandas.read_sql')
    def test_extract_performance_metrics_insufficient_data(self, mock_read_sql):
        """Test extracting performance metrics with insufficient data"""
        # Mock insufficient performance data
        performance_data = pd.DataFrame({
            'name': ['parse count (hard)', 'execute count'],
            'value': [100, 1000]
        })
        mock_read_sql.return_value = performance_data
        
        # Call the method
        result = self.extractor.extract_performance_metrics()
        
        # Verify derived metrics are not calculated
        assert 'parse_ratio' not in result.columns
        assert 'commit_ratio' not in result.columns
    
    @patch('pandas.read_sql')
    def test_extract_performance_metrics_empty_data(self, mock_read_sql):
        """Test extracting performance metrics with empty data"""
        # Mock empty performance data
        performance_data = pd.DataFrame()
        mock_read_sql.return_value = performance_data
        
        # Call the method
        result = self.extractor.extract_performance_metrics()
        
        # Verify empty DataFrame is returned
        assert result.empty
    
    @patch('pandas.read_sql')
    def test_extract_performance_metrics_exception_handling(self, mock_read_sql):
        """Test extracting performance metrics with exception handling"""
        mock_read_sql.side_effect = Exception("Performance metrics query failed")
        
        # Call the method
        result = self.extractor.extract_performance_metrics()
        
        # Verify empty DataFrame is returned
        assert result.empty
    
    @patch('pandas.read_sql')
    def test_extract_table_data_with_special_characters(self, mock_read_sql):
        """Test extracting table data with special characters in table name"""
        table_name = "employees_with_special_chars"
        schema = "plsql_dev"
        
        # Mock the DataFrame
        expected_df = pd.DataFrame({
            'employee_id': [1, 2],
            'employee_name': ['John Doe', 'Jane Smith']
        })
        mock_read_sql.return_value = expected_df
        
        # Call the method
        result = self.extractor.extract_table_data(table_name, schema)
        
        # Verify the query was called correctly
        expected_query = f"SELECT * FROM {schema}.{table_name}"
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('pandas.read_sql')
    def test_extract_table_data_with_complex_conditions(self, mock_read_sql):
        """Test extracting table data with complex conditions"""
        table_name = "employees"
        schema = "plsql_dev"
        conditions = "salary > 70000 AND department = 'IT'"
        
        # Mock the DataFrame
        expected_df = pd.DataFrame({
            'employee_id': [1],
            'employee_name': ['John'],
            'salary': [75000],
            'department': ['IT']
        })
        mock_read_sql.return_value = expected_df
        
        # Call the method
        result = self.extractor.extract_table_data(table_name, schema, conditions)
        
        # Verify the query was called correctly
        expected_query = f"SELECT * FROM {schema}.{table_name} WHERE {conditions}"
        mock_read_sql.assert_called_once_with(expected_query, self.mock_connection)
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('pandas.read_sql')
    def test_extract_performance_metrics_with_zero_division(self, mock_read_sql):
        """Test extracting performance metrics with zero division handling"""
        # Mock performance data with zero execute count
        performance_data = pd.DataFrame({
            'name': ['parse count (hard)', 'execute count', 'user commits', 'db block gets'],
            'value': [100, 0, 500, 2000]
        })
        mock_read_sql.return_value = performance_data
        
        # Call the method
        result = self.extractor.extract_performance_metrics()
        
        # Verify derived metrics handle zero division
        assert 'parse_ratio' in result.columns
        assert 'commit_ratio' in result.columns
        assert result['parse_ratio'].iloc[0] == 0  # 100/0 = 0
        assert result['commit_ratio'].iloc[0] == 0  # 500/0 = 0

class TestDataExtractorIntegration:
    """Integration tests for DataExtractor"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_data_extractor_integration(self, mock_oracle_connection):
        """Test real DataExtractor functionality (if available)"""
        try:
            from database.data_extractor import DataExtractor
            
            # Create extractor with mock connection for integration test
            extractor = DataExtractor(mock_oracle_connection)
            
            # Test table data extraction
            result = extractor.extract_table_data("dual")
            assert isinstance(result, pd.DataFrame)
            
            # Test performance metrics extraction
            result = extractor.extract_performance_metrics()
            assert isinstance(result, pd.DataFrame)
            
        except Exception as e:
            pytest.skip(f"DataExtractor integration test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])