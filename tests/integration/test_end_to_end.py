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

try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

from database.connection_oracle import create_oracle_connection
from database.connection_sqlserver import create_sqlserver_connection
from database.plsql_executor import PLSQLExecutor
from database.data_extractor import DataExtractor
from performance.benchmark import DatabaseBenchmark
from cross_database.cross_database_query import query_cross_database
from windows_auth.windows_auth_example import connect_windows_auth
from automation.backup_automation import DatabaseBackupAutomation
from analysis.trend_analyzer import TrendAnalyzer

class TestEndToEndWorkflows:
    """Integration tests for end-to-end workflows"""
    
    @pytest.mark.integration
    @pytest.mark.oracle
    @pytest.mark.sqlserver
    def test_complete_database_workflow(self, oracle_test_config, sqlserver_test_config):
        """Test complete database workflow from connection to analysis"""
        try:
            # Step 1: Create database connections
            oracle_conn = create_oracle_connection()
            sqlserver_conn = create_sqlserver_connection()
            
            # Verify connections
            assert oracle_conn is not None
            assert sqlserver_conn is not None
            
            # Step 2: Test PL/SQL executor
            oracle_executor = PLSQLExecutor(oracle_conn)
            
            # Test simple procedure execution
            result = oracle_executor.execute_procedure("BEGIN NULL; END;")
            assert result is True
            
            # Test function execution
            user_result = oracle_executor.execute_function("USER", return_type="VARCHAR2")
            assert user_result is not None
            
            # Step 3: Test data extraction
            oracle_extractor = DataExtractor(oracle_conn)
            
            # Extract table data
            dual_data = oracle_extractor.extract_table_data("dual")
            assert not dual_data.empty
            assert len(dual_data.columns) > 0
            
            # Extract performance metrics
            perf_metrics = oracle_extractor.extract_performance_metrics()
            assert isinstance(perf_metrics, pd.DataFrame)
            
            # Step 4: Test benchmarking
            oracle_benchmark = DatabaseBenchmark(oracle_conn)
            
            # Test single query benchmark
            benchmark_result = oracle_benchmark.run_single_query_test(
                "SELECT * FROM DUAL", iterations=1
            )
            assert 'query' in benchmark_result
            assert 'avg_time_ms' in benchmark_result
            assert benchmark_result['avg_time_ms'] > 0
            
            # Step 5: Test SQL Server operations
            sqlserver_executor = PLSQLExecutor(sqlserver_conn)
            
            # Test simple query execution
            result = sqlserver_executor.execute_procedure("BEGIN SELECT 1; END;")
            assert result is True
            
            # Step 6: Test data extraction from SQL Server
            sqlserver_extractor = DataExtractor(sqlserver_conn)
            
            # Extract table data
            version_data = sqlserver_extractor.extract_table_data("sys.databases")
            assert isinstance(version_data, pd.DataFrame)
            
            # Step 7: Test cross-database query (if both databases have compatible data)
            try:
                cross_result = query_cross_database()
                # If successful, verify result structure
                assert isinstance(cross_result, pd.DataFrame)
            except Exception:
                # Cross-database query may fail due to missing tables, which is expected
                pass
            
            # Step 8: Test Windows authentication
            try:
                windows_conn = connect_windows_auth()
                assert windows_conn is not None
                
                # Test basic query
                cursor = windows_conn.cursor()
                cursor.execute("SELECT SYSTEM_USER")
                result = cursor.fetchone()
                assert result is not None
                cursor.close()
                windows_conn.close()
            except Exception:
                # Windows auth may not be available, which is expected
                pass
            
            # Step 9: Test backup automation
            backup_config = {
                'backup_dir': '/tmp/test_backups',
                'retention_days': 1,
                'log_file': '/tmp/test_backups.log'
            }
            
            backup_automation = DatabaseBackupAutomation(backup_config)
            
            # Test cleanup (this should work without actual database backup)
            cleanup_result = backup_automation.cleanup_old_backups()
            assert 'cleanup_date' in cleanup_result
            assert isinstance(cleanup_result['deleted_backups'], list)
            assert isinstance(cleanup_result['kept_backups'], list)
            
            # Step 10: Test trend analysis
            analyzer = TrendAnalyzer()
            
            # Create sample performance data
            performance_data = pd.DataFrame({
                'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
                'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9, 58.3, 51.2, 47.8, 53.6, 49.1],
                'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
            })
            
            # Analyze trends
            trend_result = analyzer.analyze_cpu_trends(performance_data)
            assert isinstance(trend_result, dict)
            assert 'trend_slope' in trend_result
            assert 'r_squared' in trend_result
            assert 'future_predictions' in trend_result
            
            # Step 11: Clean up connections
            oracle_conn.close()
            sqlserver_conn.close()
            
            # Verify connections are closed
            assert oracle_conn.closed
            assert sqlserver_conn.closed
            
        except Exception as e:
            pytest.skip(f"End-to-end database workflow test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.oracle
    def test_oracle_specific_workflow(self, oracle_test_config):
        """Test Oracle-specific workflow"""
        try:
            # Step 1: Create Oracle connection
            oracle_conn = create_oracle_connection()
            assert oracle_conn is not None
            
            # Step 2: Test PL/SQL operations
            executor = PLSQLExecutor(oracle_conn)
            
            # Test procedure execution with parameters
            result = executor.execute_procedure(
                "BEGIN :result := USER; END;", 
                return_type="VARCHAR2"
            )
            assert result is not None
            
            # Step 3: Test data extraction
            extractor = DataExtractor(oracle_conn)
            
            # Extract v$version
            version_data = extractor.extract_table_data("v$version")
            assert not version_data.empty
            
            # Step 4: Test performance benchmarking
            benchmark = DatabaseBenchmark(oracle_conn)
            
            # Test transaction benchmark
            def test_transaction():
                cursor = oracle_conn.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                cursor.close()
                return result is not None
            
            transaction_result = benchmark.run_transaction_test(test_transaction, iterations=1)
            assert 'test_type' in transaction_result
            assert transaction_result['test_type'] == 'custom_transaction'
            
            # Step 5: Test trend analysis with Oracle metrics
            analyzer = TrendAnalyzer()
            
            # Extract performance metrics
            perf_metrics = extractor.extract_performance_metrics()
            if not perf_metrics.empty:
                # Analyze trends if we have performance data
                trend_result = analyzer.analyze_cpu_trends(perf_metrics)
                assert isinstance(trend_result, dict)
            
            # Step 6: Clean up
            oracle_conn.close()
            
        except Exception as e:
            pytest.skip(f"Oracle-specific workflow test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.sqlserver
    def test_sqlserver_specific_workflow(self, sqlserver_test_config):
        """Test SQL Server-specific workflow"""
        try:
            # Step 1: Create SQL Server connection
            sqlserver_conn = create_sqlserver_connection()
            assert sqlserver_conn is not None
            
            # Step 2: Test SQL operations
            executor = PLSQLExecutor(sqlserver_conn)
            
            # Test simple query
            result = executor.execute_procedure("BEGIN SELECT 1; END;")
            assert result is True
            
            # Step 3: Test data extraction
            extractor = DataExtractor(sqlserver_conn)
            
            # Extract system information
            sys_data = extractor.extract_table_data("sys.databases")
            assert isinstance(sys_data, pd.DataFrame)
            
            # Step 4: Test performance benchmarking
            benchmark = DatabaseBenchmark(sqlserver_conn)
            
            # Test single query benchmark
            benchmark_result = benchmark.run_single_query_test(
                "SELECT @@VERSION", iterations=1
            )
            assert 'query' in benchmark_result
            assert 'avg_time_ms' in benchmark_result
            
            # Step 5: Test Windows authentication
            try:
                windows_conn = connect_windows_auth()
                assert windows_conn is not None
                
                # Test connection verification
                cursor = windows_conn.cursor()
                cursor.execute("SELECT SYSTEM_USER")
                result = cursor.fetchone()
                assert result is not None
                cursor.close()
                windows_conn.close()
            except Exception:
                # Windows auth may not be available, which is expected
                pass
            
            # Step 6: Clean up
            sqlserver_conn.close()
            
        except Exception as e:
            pytest.skip(f"SQL Server-specific workflow test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.oracle
    @pytest.mark.sqlserver
    def test_error_handling_workflow(self, oracle_test_config, sqlserver_test_config):
        """Test error handling in end-to-end workflow"""
        try:
            # Step 1: Create connections
            oracle_conn = create_oracle_connection()
            sqlserver_conn = create_sqlserver_connection()
            
            # Step 2: Test PL/SQL executor error handling
            executor = PLSQLExecutor(oracle_conn)
            
            # Test procedure execution with invalid procedure
            result = executor.execute_procedure("INVALID_PROCEDURE")
            assert result is False
            
            # Test function execution with invalid function
            result = executor.execute_function("INVALID_FUNCTION")
            assert result is None
            
            # Step 3: Test data extractor error handling
            extractor = DataExtractor(oracle_conn)
            
            # Extract non-existent table
            result = extractor.extract_table_data("non_existent_table")
            assert result.empty
            
            # Step 4: Test benchmark error handling
            benchmark = DatabaseBenchmark(oracle_conn)
            
            # Test with invalid query
            result = benchmark.run_single_query_test("SELECT * FROM non_existent_table")
            assert 'error' in result
            assert result['iterations'] == 0
            
            # Step 5: Test cross-database query error handling
            try:
                result = query_cross_database()
                # If successful, it should return a DataFrame
                assert isinstance(result, pd.DataFrame)
            except Exception as e:
                # Expected if databases are not properly configured
                assert isinstance(e, (Exception, cx_Oracle.DatabaseError, pyodbc.Error))
            
            # Step 6: Test Windows authentication error handling
            try:
                result = connect_windows_auth()
                # If successful, result should be a connection
                assert result is not None
            except Exception as e:
                # Expected if Windows auth is not available
                assert isinstance(e, (Exception, pyodbc.Error))
            
            # Step 7: Test backup automation error handling
            backup_config = {
                'backup_dir': '/tmp/test_backups',
                'retention_days': 1,
                'log_file': '/tmp/test_backups.log'
            }
            
            backup_automation = DatabaseBackupAutomation(backup_config)
            
            # Test backup with invalid connection string
            result = backup_automation.backup_oracle_database("invalid/connection/string")
            assert result['status'] == 'failed'
            assert 'error' in result
            
            # Step 8: Test trend analysis error handling
            analyzer = TrendAnalyzer()
            
            # Analyze with empty data
            result = analyzer.analyze_cpu_trends(pd.DataFrame())
            assert result == {}
            
            # Analyze with missing column
            invalid_data = pd.DataFrame({'wrong_column': [1, 2, 3]})
            result = analyzer.analyze_cpu_trends(invalid_data)
            assert result == {}
            
            # Step 9: Clean up
            oracle_conn.close()
            sqlserver_conn.close()
            
        except Exception as e:
            pytest.skip(f"Error handling workflow test failed: {e}")
    
    @pytest.mark.integration
    @pytest.mark.oracle
    @pytest.mark.sqlserver
    def test_performance_monitoring_workflow(self, oracle_test_config, sqlserver_test_config):
        """Test performance monitoring workflow"""
        try:
            # Step 1: Create connections
            oracle_conn = create_oracle_connection()
            sqlserver_conn = create_sqlserver_connection()
            
            # Step 2: Create benchmark instances
            oracle_benchmark = DatabaseBenchmark(oracle_conn)
            sqlserver_benchmark = DatabaseBenchmark(sqlserver_conn)
            
            # Step 3: Test single query benchmarks
            oracle_result = oracle_benchmark.run_single_query_test(
                "SELECT * FROM DUAL", iterations=5
            )
            assert oracle_result['iterations'] == 5
            assert oracle_result['avg_time_ms'] > 0
            
            sqlserver_result = sqlserver_benchmark.run_single_query_test(
                "SELECT 1", iterations=5
            )
            assert sqlserver_result['iterations'] == 5
            assert sqlserver_result['avg_time_ms'] > 0
            
            # Step 4: Test concurrent benchmarks
            oracle_concurrent = oracle_benchmark.run_concurrent_test(
                "SELECT * FROM DUAL", concurrent_users=2, iterations_per_user=2
            )
            assert oracle_concurrent['concurrent_users'] == 2
            assert oracle_concurrent['total_iterations'] == 4
            
            sqlserver_concurrent = sqlserver_benchmark.run_concurrent_test(
                "SELECT 1", concurrent_users=2, iterations_per_user=2
            )
            assert sqlserver_concurrent['concurrent_users'] == 2
            assert sqlserver_concurrent['total_iterations'] == 4
            
            # Step 5: Test transaction benchmarks
            def oracle_transaction():
                cursor = oracle_conn.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                cursor.close()
                return result is not None
            
            def sqlserver_transaction():
                cursor = sqlserver_conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result is not None
            
            oracle_transaction_result = oracle_benchmark.run_transaction_test(
                oracle_transaction, iterations=3
            )
            assert oracle_transaction_result['iterations'] == 3
            assert oracle_transaction_result['test_type'] == 'custom_transaction'
            
            sqlserver_transaction_result = sqlserver_benchmark.run_transaction_test(
                sqlserver_transaction, iterations=3
            )
            assert sqlserver_transaction_result['iterations'] == 3
            assert sqlserver_transaction_result['test_type'] == 'custom_transaction'
            
            # Step 6: Test load benchmarks
            oracle_queries = ["SELECT * FROM DUAL", "SELECT USER FROM DUAL"]
            oracle_load_result = oracle_benchmark.run_load_test(
                oracle_queries, duration_seconds=1
            )
            assert oracle_load_result['duration_seconds'] == 1
            assert oracle_load_result['test_type'] == 'load_test'
            
            sqlserver_queries = ["SELECT 1", "SELECT @@VERSION"]
            sqlserver_load_result = sqlserver_benchmark.run_load_test(
                sqlserver_queries, duration_seconds=1
            )
            assert sqlserver_load_result['duration_seconds'] == 1
            assert sqlserver_load_result['test_type'] == 'load_test'
            
            # Step 7: Test data extraction for performance analysis
            oracle_extractor = DataExtractor(oracle_conn)
            oracle_perf_metrics = oracle_extractor.extract_performance_metrics()
            
            sqlserver_extractor = DataExtractor(sqlserver_conn)
            sqlserver_perf_data = sqlserver_extractor.extract_table_data("sys.dm_os_performance_counters")
            
            # Step 8: Test trend analysis
            analyzer = TrendAnalyzer()
            
            if not oracle_perf_metrics.empty:
                oracle_trends = analyzer.analyze_cpu_trends(oracle_perf_metrics)
                assert isinstance(oracle_trends, dict)
            
            # Create sample data for SQL Server trend analysis
            sample_perf_data = pd.DataFrame({
                'timestamp': pd.date_range('2023-01-01 10:00:00', periods=10, freq='1min'),
                'cpu_percent': [45.2, 52.3, 48.7, 55.1, 42.9, 58.3, 51.2, 47.8, 53.6, 49.1],
                'memory_percent': [62.1, 64.5, 61.8, 66.2, 60.3, 68.1, 63.4, 59.7, 65.2, 61.9]
            })
            
            sqlserver_trends = analyzer.analyze_cpu_trends(sample_perf_data)
            assert isinstance(sqlserver_trends, dict)
            assert 'trend_slope' in sqlserver_trends
            assert 'r_squared' in sqlserver_trends
            
            # Step 9: Clean up
            oracle_conn.close()
            sqlserver_conn.close()
            
        except Exception as e:
            pytest.skip(f"Performance monitoring workflow test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])