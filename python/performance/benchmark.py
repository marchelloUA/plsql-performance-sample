import time
import statistics
import threading
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
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

class DatabaseBenchmark:
    """Database performance benchmarking tool"""
    
    def __init__(self, connection):
        self.connection = connection
        self.results = []
    
    def run_single_query_test(self, query: str, iterations: int = 100) -> Dict[str, Any]:
        """Test single query performance"""
        try:
            execution_times = []
            
            cursor = self.connection.cursor()
            
            for i in range(iterations):
                start_time = time.time()
                cursor.execute(query)
                cursor.fetchall()
                end_time = time.time()
                
                execution_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            cursor.close()
            
            return {
                'query': query,
                'iterations': iterations,
                'avg_time_ms': statistics.mean(execution_times),
                'min_time_ms': min(execution_times),
                'max_time_ms': max(execution_times),
                'std_dev_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                'total_time_ms': sum(execution_times)
            }
            
        except Exception as e:
            return {
                'query': query,
                'error': str(e),
                'iterations': 0,
                'avg_time_ms': 0,
                'min_time_ms': 0,
                'max_time_ms': 0,
                'std_dev_ms': 0,
                'total_time_ms': 0
            }
    
    def run_concurrent_test(self, query: str, concurrent_users: int = 10, 
                          iterations_per_user: int = 10) -> Dict[str, Any]:
        """Test concurrent query performance"""
        try:
            def execute_user_query(user_id: int) -> List[float]:
                times = []
                cursor = self.connection.cursor()
                
                for i in range(iterations_per_user):
                    start_time = time.time()
                    cursor.execute(query)
                    cursor.fetchall()
                    end_time = time.time()
                    times.append((end_time - start_time) * 1000)
                
                cursor.close()
                return times
            
            all_times = []
            
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(execute_user_query, i) for i in range(concurrent_users)]
                
                for future in as_completed(futures):
                    user_times = future.result()
                    all_times.extend(user_times)
            
            return {
                'query': query,
                'concurrent_users': concurrent_users,
                'iterations_per_user': iterations_per_user,
                'total_iterations': concurrent_users * iterations_per_user,
                'avg_time_ms': statistics.mean(all_times),
                'min_time_ms': min(all_times),
                'max_time_ms': max(all_times),
                'std_dev_ms': statistics.stdev(all_times) if len(all_times) > 1 else 0,
                'total_time_ms': sum(all_times)
            }
            
        except Exception as e:
            return {
                'query': query,
                'concurrent_users': concurrent_users,
                'iterations_per_user': iterations_per_user,
                'error': str(e),
                'total_iterations': 0,
                'avg_time_ms': 0,
                'min_time_ms': 0,
                'max_time_ms': 0,
                'std_dev_ms': 0,
                'total_time_ms': 0
            }
    
    def run_transaction_test(self, transaction_func: Callable, iterations: int = 100) -> Dict[str, Any]:
        """Test custom transaction performance"""
        try:
            execution_times = []
            
            for i in range(iterations):
                start_time = time.time()
                transaction_func()
                end_time = time.time()
                
                execution_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            return {
                'test_type': 'custom_transaction',
                'iterations': iterations,
                'avg_time_ms': statistics.mean(execution_times),
                'min_time_ms': min(execution_times),
                'max_time_ms': max(execution_times),
                'std_dev_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                'total_time_ms': sum(execution_times)
            }
            
        except Exception as e:
            return {
                'test_type': 'custom_transaction',
                'iterations': iterations,
                'error': str(e),
                'avg_time_ms': 0,
                'min_time_ms': 0,
                'max_time_ms': 0,
                'std_dev_ms': 0,
                'total_time_ms': 0
            }
    
    def run_load_test(self, queries: List[str], duration_seconds: int = 60) -> Dict[str, Any]:
        """Run load test for specified duration"""
        try:
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            query_counts = {query: 0 for query in queries}
            execution_times = []
            
            while time.time() < end_time:
                for query in queries:
                    start = time.time()
                    cursor = self.connection.cursor()
                    cursor.execute(query)
                    cursor.fetchall()
                    cursor.close()
                    end = time.time()
                    
                    query_counts[query] += 1
                    execution_times.append((end - start) * 1000)
            
            total_queries = sum(query_counts.values())
            queries_per_second = total_queries / duration_seconds
            
            return {
                'test_type': 'load_test',
                'duration_seconds': duration_seconds,
                'total_queries': total_queries,
                'queries_per_second': queries_per_second,
                'avg_time_ms': statistics.mean(execution_times),
                'min_time_ms': min(execution_times),
                'max_time_ms': max(execution_times),
                'std_dev_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                'query_counts': query_counts
            }
            
        except Exception as e:
            return {
                'test_type': 'load_test',
                'duration_seconds': duration_seconds,
                'error': str(e),
                'total_queries': 0,
                'queries_per_second': 0,
                'avg_time_ms': 0,
                'min_time_ms': 0,
                'max_time_ms': 0,
                'std_dev_ms': 0,
                'query_counts': {}
            }
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate benchmark report"""
        report = []
        report.append("Database Performance Benchmark Report")
        report.append("=" * 50)
        
        for result in results:
            report.append(f"\nTest: {result.get('query', result.get('test_type', 'Unknown'))}")
            report.append(f"Iterations: {result.get('iterations', result.get('total_iterations', 0))}")
            
            if 'error' in result:
                report.append(f"Error: {result['error']}")
            else:
                report.append(f"Average Time: {result.get('avg_time_ms', 0):.2f} ms")
                report.append(f"Min Time: {result.get('min_time_ms', 0):.2f} ms")
                report.append(f"Max Time: {result.get('max_time_ms', 0):.2f} ms")
                report.append(f"Std Dev: {result.get('std_dev_ms', 0):.2f} ms")
                
                if 'queries_per_second' in result:
                    report.append(f"Queries/Second: {result['queries_per_second']:.2f}")
        
        return "\n".join(report)