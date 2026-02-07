import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

# Mock database modules if not available
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

@pytest.fixture(scope="session")
def mock_oracle_connection():
    """Mock Oracle database connection for testing"""
    mock_conn = Mock(spec=cx_Oracle.Connection)
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit = Mock()
    mock_conn.rollback = Mock()
    mock_conn.close = Mock()
    return mock_conn

@pytest.fixture(scope="session")
def mock_sqlserver_connection():
    """Mock SQL Server database connection for testing"""
    mock_conn = Mock(spec=pyodbc.Connection)
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit = Mock()
    mock_conn.rollback = Mock()
    mock_conn.close = Mock()
    return mock_conn

@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing"""
    return [
        {
            'employee_id': 1,
            'employee_name': 'John Doe',
            'department': 'IT',
            'salary': 75000,
            'hire_date': '2023-01-15'
        },
        {
            'employee_id': 2,
            'employee_name': 'Jane Smith',
            'department': 'HR',
            'salary': 65000,
            'hire_date': '2023-02-20'
        },
        {
            'employee_id': 3,
            'employee_name': 'Bob Johnson',
            'department': 'Finance',
            'salary': 80000,
            'hire_date': '2023-03-10'
        }
    ]

@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing"""
    return [
        {'timestamp': '2023-01-01 10:00:00', 'cpu_percent': 45.2, 'memory_percent': 62.1},
        {'timestamp': '2023-01-01 10:01:00', 'cpu_percent': 52.3, 'memory_percent': 64.5},
        {'timestamp': '2023-01-01 10:02:00', 'cpu_percent': 48.7, 'memory_percent': 61.8},
        {'timestamp': '2023-01-01 10:03:00', 'cpu_percent': 55.1, 'memory_percent': 66.2},
        {'timestamp': '2023-01-01 10:04:00', 'cpu_percent': 42.9, 'memory_percent': 60.3}
    ]

@pytest.fixture
def sample_database_config():
    """Sample database configuration for testing"""
    return {
        'oracle': {
            'user': 'plsql_dev',
            'password': 'DevPassword123',
            'dsn': 'localhost:1521/FREEPDB1',
            'encoding': 'UTF-8'
        },
        'sqlserver': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'server': 'localhost,1433',
            'database': 'plsql_dev_db',
            'uid': 'sa',
            'pwd': 'YourStrongPassword123!'
        }
    }

@pytest.fixture
def backup_config():
    """Sample backup configuration for testing"""
    return {
        'backup_dir': '/tmp/test_backups',
        'retention_days': 7,
        'log_file': '/tmp/test_backups.log',
        'oracle': {
            'connection_string': 'plsql_dev/DevPassword123@localhost:1521/FREEPDB1'
        },
        'sqlserver': {
            'connection_string': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=plsql_dev_db;UID=sa;PWD=YourStrongPassword123!'
        }
    }

# Database connection fixtures for integration tests
@pytest.fixture(scope="session")
def oracle_test_config():
    """Oracle test configuration (skip if not available)"""
    return {
        'user': 'plsql_dev',
        'password': 'DevPassword123',
        'dsn': 'localhost:1521/FREEPDB1'
    }

@pytest.fixture(scope="session")
def sqlserver_test_config():
    """SQL Server test configuration (skip if not available)"""
    return {
        'driver': 'ODBC Driver 17 for SQL Server',
        'server': 'localhost,1433',
        'database': 'plsql_dev_db',
        'uid': 'sa',
        'pwd': 'YourStrongPassword123!'
    }

# Skip markers for databases that might not be available
def pytest_runtest_setup(item):
    """Setup hook to skip tests if databases are not available"""
    if 'oracle' in item.keywords:
        try:
            import cx_Oracle
            # Try to connect to test Oracle database
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREEPDB1")
            conn = cx_Oracle.connect(user="plsql_dev", password="DevPassword123", dsn=dsn)
            conn.close()
        except:
            pytest.skip("Oracle database not available for testing")
    
    if 'sqlserver' in item.keywords:
        try:
            import pyodbc
            # Try to connect to test SQL Server database
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost,1433;"
                "DATABASE=plsql_dev_db;"
                "UID=sa;"
                "PWD=YourStrongPassword123!"
            )
            conn = pyodbc.connect(conn_str)
            conn.close()
        except:
            pytest.skip("SQL Server database not available for testing")